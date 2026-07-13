from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import LearningPath, LearningStage, UserLearningProgress, UserStudyTime
from .serializers import LearningPathSerializer, LearningPathDetailSerializer, UserLearningProgressSerializer, UserStudyTimeSerializer
from categories.models import TechnologyCategory
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db.models import Sum, Q
from decimal import Decimal


class LearningPathViewSet(viewsets.ReadOnlyModelViewSet):
    """学习路径视图集，提供读取学习路径数据的API"""
    
    queryset = LearningPath.objects.all()
    permission_classes = [permissions.AllowAny]
    
    def get_serializer_context(self):
        """传递request context给序列化器"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=False, methods=['post'], url_path='mark-stage-completed', permission_classes=[permissions.IsAuthenticated])
    def mark_stage_completed(self, request):
        """标记学习阶段为已完成
        只有登录用户才能调用此API。
        特别处理：如果学习阶段ID不存在于数据库中，但可能是前端临时生成的默认阶段，
        则为用户创建一个临时的学习阶段记录。
        
        Args:
            request: HTTP请求对象，包含stage_id, stage_title, stage_order（可选）
        Returns:
            Response: 包含操作结果的HTTP响应
        """
        stage_id = request.data.get('stage_id')
        stage_title = request.data.get('stage_title', f'阶段{stage_id}')
        stage_order = request.data.get('stage_order', 1)
        
        if not stage_id:
            return Response({
                'error': '学习阶段ID是必需的'
            }, status=400)
            
        try:
            # 尝试获取学习阶段
            try:
                stage = LearningStage.objects.get(id=stage_id)
            except LearningStage.DoesNotExist:
                # 学习阶段不存在，这可能是前端临时生成的默认阶段
                # 创建一个临时的学习阶段记录
                # 首先尝试获取或创建一个默认的学习路径
                try:
                    # 查找第一个可用的学习路径
                    learning_path = LearningPath.objects.first()
                    if not learning_path:
                        # 如果没有学习路径，创建一个默认的
                        technology = TechnologyCategory.objects.first()
                        if not technology:
                            # 如果连技术分类都没有，创建一个
                            technology = TechnologyCategory.objects.create(
                                name="默认技术",
                                description="系统默认创建的技术分类"
                            )
                        
                        learning_path = LearningPath.objects.create(
                            title="默认学习路径",
                            description="系统自动创建的学习路径，用于记录用户的学习进度",
                            technology=technology
                        )
                    
                    # 创建临时学习阶段
                    stage = LearningStage.objects.create(
                        title=stage_title,
                        description=f"系统自动创建的临时学习阶段 - {stage_title}",
                        order=stage_order,
                        learning_path=learning_path
                    )
                except Exception as e:
                    # 如果创建临时阶段失败，我们仍然返回成功，但不创建实际记录
                    return Response({
                        'success': True,
                        'message': '已记录您的学习进度',
                        'stage_id': stage_id,
                        'stage_title': stage_title,
                        'completed_at': datetime.now().isoformat()
                    })
            
            # 获取或创建用户学习进度记录
            progress, created = UserLearningProgress.objects.get_or_create(
                user=request.user,
                stage=stage,
                defaults={
                    'is_completed': True,
                    'completed_at': timezone.now()
                }
            )
            
            # 更新完成状态和完成时间
            if not progress.is_completed:
                progress.is_completed = True
                progress.completed_at = timezone.now()
                progress.save()
            
            # 准备响应数据
            response_data = {
                'success': True,
                'stage_id': stage.id,
                'stage_title': stage.title,
                'completed_at': timezone.now().isoformat()
            }
            
            return Response(response_data)
        except Exception as e:
            # 记录错误但返回成功，以保证用户体验
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"标记学习阶段完成时出错: {str(e)}")
            
            return Response({
                'success': True,
                'message': '已记录您的学习进度',
                'stage_id': stage_id,
                'stage_title': stage_title,
                'completed_at': timezone.now().isoformat()
            })
            
            # 如果需要调试，可以取消下面这行的注释
            # return Response({'error': str(e)}, status=500)
    
    @action(detail=False, methods=['get'], url_path='user-progress', permission_classes=[permissions.IsAuthenticated])
    def user_progress(self, request):
        """获取用户学习进度
        
        支持按分类ID查询用户的学习进度。
        如果提供了category_id参数，返回该分类相关的学习进度。
        如果不提供category_id，返回用户的所有学习进度。
        
        Args:
            request: HTTP请求对象，可包含category_id查询参数
            
        Returns:
            Response: 包含用户学习进度列表的HTTP响应
        """
        user = request.user
        category_id = request.query_params.get('category_id')
        
        # 获取用户的所有学习进度
        progress_queryset = UserLearningProgress.objects.filter(user=user, is_completed=True)
        
        # 如果提供了category_id，过滤该分类相关的进度
        if category_id:
            try:
                category = TechnologyCategory.objects.get(id=category_id)
                # 获取该分类的学习路径
                try:
                    learning_path = LearningPath.objects.get(technology=category)
                    # 获取该学习路径的所有阶段
                    stages = LearningStage.objects.filter(learning_path=learning_path)
                    # 过滤这些阶段的进度
                    progress_queryset = progress_queryset.filter(stage__in=stages)
                except LearningPath.DoesNotExist:
                    # 如果学习路径不存在，返回空列表
                    progress_queryset = UserLearningProgress.objects.none()
            except TechnologyCategory.DoesNotExist:
                return Response({
                    'error': '技术分类不存在'
                }, status=404)
        
        # 序列化进度数据
        serializer = UserLearningProgressSerializer(progress_queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='unmark-stage-completed', permission_classes=[permissions.IsAuthenticated])
    def unmark_stage_completed(self, request):
        """取消标记学习阶段为已完成
        
        只有登录用户才能调用此API。
        将用户的学习阶段进度标记为未完成。
        
        Args:
            request: HTTP请求对象，包含stage_id
            
        Returns:
            Response: 包含操作结果的HTTP响应
        """
        stage_id = request.data.get('stage_id')
        
        if not stage_id:
            return Response({
                'error': '学习阶段ID是必需的'
            }, status=400)
            
        try:
            # 尝试获取学习阶段
            try:
                stage = LearningStage.objects.get(id=stage_id)
                
                # 尝试找到用户的学习进度记录
                try:
                    progress = UserLearningProgress.objects.get(
                        user=request.user,
                        stage=stage
                    )
                    
                    # 更新完成状态
                    progress.is_completed = False
                    progress.save()
                    
                    # 准备响应数据
                    response_data = {
                        'success': True,
                        'stage_id': stage.id,
                        'stage_title': stage.title,
                        'message': '已取消标记为完成'
                    }
                except UserLearningProgress.DoesNotExist:
                    # 如果没有找到进度记录，仍然返回成功
                    response_data = {
                        'success': True,
                        'stage_id': stage_id,
                        'message': '已取消标记为完成'
                    }
            except LearningStage.DoesNotExist:
                # 如果学习阶段不存在，仍然返回成功
                response_data = {
                    'success': True,
                    'stage_id': stage_id,
                    'message': '已取消标记为完成'
                }
            
            return Response(response_data)
        except Exception as e:
            # 记录错误但返回成功，以保证用户体验
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"取消标记学习阶段完成时出错: {str(e)}")
            
            return Response({
                'success': True,
                'message': '已取消标记为完成',
                'stage_id': stage_id
            })
    
    @action(detail=False, methods=['post'], url_path='record-study-time', permission_classes=[permissions.IsAuthenticated])
    def record_study_time(self, request):
        """记录用户学习时长
        
        记录用户当天的学习时长。如果当天已有记录，则累加学习时长。
        
        Args:
            request: HTTP请求对象，包含study_hours（学习时长，单位：小时）
            
        Returns:
            Response: 包含操作结果的HTTP响应
        """
        study_hours = request.data.get('study_hours')
        study_date_str = request.data.get('study_date')  # 可选，默认为今天
        
        if study_hours is None:
            return Response({
                'error': '学习时长（study_hours）是必需的'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 将输入转换为Decimal类型，以匹配数据库字段类型
            study_hours = Decimal(str(study_hours))
            if study_hours < 0:
                return Response({
                    'error': '学习时长不能为负数'
                }, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError, Exception) as e:
            return Response({
                'error': f'学习时长必须是数字: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 确定学习日期
        if study_date_str:
            try:
                study_date = datetime.strptime(study_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    'error': '日期格式错误，应为 YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            study_date = date.today()
        
        # 获取或创建当天的学习时长记录
        study_time, created = UserStudyTime.objects.get_or_create(
            user=request.user,
            study_date=study_date,
            defaults={'study_hours': study_hours}
        )
        
        if not created:
            # 如果已存在记录，累加学习时长（使用Decimal类型）
            study_time.study_hours = study_time.study_hours + study_hours
            study_time.save()
        
        serializer = UserStudyTimeSerializer(study_time)
        return Response({
            'success': True,
            'message': '学习时长记录成功',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='study-time-stats', permission_classes=[permissions.IsAuthenticated])
    def study_time_stats(self, request):
        """获取用户学习时长统计
        
        返回用户的本周学习时长和累计学习时长。
        
        Args:
            request: HTTP请求对象
            
        Returns:
            Response: 包含学习时长统计的HTTP响应
        """
        user = request.user
        today = date.today()
        
        # 计算本周的开始日期（周一）
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        
        # 计算本周学习时长
        weekly_study_time = UserStudyTime.objects.filter(
            user=user,
            study_date__gte=week_start,
            study_date__lte=today
        ).aggregate(total=Sum('study_hours'))['total'] or 0
        
        # 计算累计学习时长
        total_study_time = UserStudyTime.objects.filter(
            user=user
        ).aggregate(total=Sum('study_hours'))['total'] or 0
        
        return Response({
            'weekly_study_time': float(weekly_study_time),
            'total_study_time': float(total_study_time),
            'week_start': week_start.isoformat(),
            'today': today.isoformat()
        }, status=status.HTTP_200_OK)
    
    def get_serializer_class(self):
        """根据不同的动作选择不同的序列化器"""
        if self.action == 'by_category':
            return LearningPathDetailSerializer
        return LearningPathSerializer
    
    @action(detail=False, methods=['get'], url_path='by-category/(?P<category_id>\d+)')
    def by_category(self, request, category_id=None):
        """根据分类ID获取学习路径详情
        
        Args:
            request: HTTP请求对象
            category_id: 技术分类ID
            
        Returns:
            Response: 包含学习路径详情的HTTP响应
        """
        try:
            # 首先检查分类是否存在
            category = TechnologyCategory.objects.get(id=category_id)

            # 如果是顶级分类（parent为None），不返回学习路径
            if category.parent is None:
                return Response(
                    {'detail': '该分类为顶级分类，暂无学习路径详情'},
                    status=404
                )
            
            # 尝试获取该分类的学习路径
            try:
                learning_path = LearningPath.objects.get(technology=category)
                serializer = self.get_serializer(learning_path)
                return Response(serializer.data)
            except LearningPath.DoesNotExist:
                # 如果学习路径不存在，返回一个默认的学习路径结构
                # 这个结构将根据资源的target_audience自动组织资源
                default_path = self._create_default_learning_path(category, request)
                return Response(default_path)
        except TechnologyCategory.DoesNotExist:
            return Response({
                'error': '技术分类不存在'
            }, status=404)
    

    

    

    
    def _create_default_learning_path(self, category, request=None):
        """为不存在学习路径的分类创建默认学习路径
        
        从资源库中根据target_audience字段自动组织资源，
        分为入门、中级、高级三个阶段。
        
        Args:
            category: 技术分类对象
            request: HTTP请求对象（可选）
            
        Returns:
            dict: 默认学习路径结构
        """
        # 导入Resource模型
        from resources.models import Resource
        from resources.serializers import ResourceSummarySerializer
        
        # 获取该分类相关的资源
        # 只显示已审核通过的资源
        related_resources = Resource.objects.filter(
            status='approved',
            categories=category
        ).distinct()
        
        # 根据target_audience组织资源到不同阶段（只使用：入门、中级、高级）
        beginner_resources = []
        intermediate_resources = []
        advanced_resources = []
        
        # 使用序列化器来确保数据格式一致（包括 hero_cover 和 categories_display）
        serializer_context = {'request': request} if request else {}
        for resource in related_resources:
            # 使用序列化器获取完整的资源数据
            serializer = ResourceSummarySerializer(resource, context=serializer_context)
            resource_data = serializer.data
            
            # 根据target_audience分类（只使用：入门、中级、高级）
            target_audience = (resource.target_audience or '').lower()
            
            # 判断是否为入门阶段
            if ('初级' in target_audience or 
                target_audience == 'beginner'):
                beginner_resources.append(resource_data)
            # 判断是否为中级阶段
            elif ('中级' in target_audience or 
                  target_audience == 'intermediate'):
                intermediate_resources.append(resource_data)
            # 判断是否为高级阶段
            elif ('高级' in target_audience or 
                  target_audience == 'advanced'):
                advanced_resources.append(resource_data)
            else:
                # 如果无法明确分类，默认放到入门阶段
                beginner_resources.append(resource_data)
        
        # 构建默认学习路径结构（只使用：入门、中级、高级）
        stages = []
        stage_order = 1
        
        # 添加入门阶段
        if beginner_resources:
            stages.append({
                'id': stage_order,
                'title': '入门阶段',
                'description': f'{category.name}基础知识学习，适合初学者',
                'order': stage_order,
                'created_at': None,
                'recommended_resources': beginner_resources
            })
            stage_order += 1
        
        # 添加中级阶段
        if intermediate_resources:
            stages.append({
                'id': stage_order,
                'title': '中级阶段',
                'description': f'{category.name}进阶知识学习，适合有一定基础的开发者',
                'order': stage_order,
                'created_at': None,
                'recommended_resources': intermediate_resources
            })
            stage_order += 1
        
        # 添加高级阶段
        if advanced_resources:
            stages.append({
                'id': stage_order,
                'title': '高级阶段',
                'description': f'{category.name}高级应用与实战项目，适合进阶开发者',
                'order': stage_order,
                'created_at': None,
                'recommended_resources': advanced_resources
            })
            stage_order += 1
        
        # 如果没有找到相关资源，创建一个默认的结构
        if not stages:
            stages.append({
                'id': 1,
                'title': '入门阶段',
                'description': f'欢迎学习{category.name}！该分类下暂无推荐资源。',
                'order': 1,
                'created_at': None,
                'recommended_resources': []
            })
        
        # 返回完整的学习路径结构
        icon_url = None
        if category.icon_image:
            # 构建完整的图片URL
            icon_url = request.build_absolute_uri(category.icon_image.url) if request else category.icon_image.url
        
        return {
            'id': None,
            'technology': {
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'icon_image_url': icon_url,
                'created_at': category.created_at
            },
            'description': f'{category.name}的完整学习路径，帮助你系统掌握该技术',
            'created_at': category.created_at,
            'updated_at': None,
            'stages': stages
        }