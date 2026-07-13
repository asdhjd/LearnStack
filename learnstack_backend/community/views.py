from rest_framework import viewsets, filters, status, pagination, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.utils import timezone
from .models import Question, Answer, AnswerLike, CommunityReport
from .serializers import QuestionSerializer, AnswerSerializer, QuestionListSerializer, CommunityReportSerializer
from django.db.models import F, Sum

# 自定义分页类
class QuestionPagination(pagination.PageNumberPagination):
    page_size = 10  # 每页显示的问题数量
    page_size_query_param = 'page_size'  # 允许客户端通过查询参数指定每页大小
    max_page_size = 100  # 客户端最大可请求的每页大小

class QuestionViewSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'content', 'tags']
    pagination_class = QuestionPagination  # 使用自定义分页类
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return QuestionListSerializer
        return QuestionSerializer
    
    def list(self, request, *args, **kwargs):
        sort_by = request.query_params.get('sort', 'latest')
        
        queryset = self.get_queryset()
        
        user_id = request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(author_id=user_id)
        
        if sort_by == 'hot':
            queryset = queryset.order_by('-views_count')
        else:
            queryset = queryset.order_by('-created_at')
        
        total_stats = queryset.aggregate(
            total_answers=Sum('answers_count'),
            total_views=Sum('views_count')
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['total_answers'] = total_stats['total_answers'] or 0
            response.data['total_views'] = total_stats['total_views'] or 0
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'total_answers': total_stats['total_answers'] or 0,
            'total_views': total_stats['total_views'] or 0
        })
    
    def retrieve(self, request, *args, **kwargs):
        # 增加浏览量
        question = self.get_object()
        question.views_count = F('views_count') + 1
        question.save()
        question.refresh_from_db()
        return super().retrieve(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """创建问题"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        # 保存问题
        serializer.save(author=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        # 获取要删除的问题
        question = self.get_object()
        
        # 检查是否是问题作者或是管理员
        if question.author != request.user and not request.user.is_superuser:
            return Response({'detail': '只有问题作者或管理员可以删除帖子'}, status=status.HTTP_403_FORBIDDEN)
        
        # 执行删除
        return super().destroy(request, *args, **kwargs)
    
    # 问题点赞功能已移除，系统只支持评论的点赞和反对

class AnswerViewSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    pagination_class = QuestionPagination
    
    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        question_id = self.request.query_params.get('question_id')
        if question_id:
            queryset = queryset.filter(question_id=question_id).order_by('-likes_count', '-created_at')
        else:
            queryset = queryset.order_by('-created_at')
        return queryset
    
    def perform_create(self, serializer):
        answer = serializer.save(author=self.request.user)
        # 更新问题的回答数 - 使用直接计数而非F表达式，确保准确性
        question = answer.question
        question.answers_count = Answer.objects.filter(question=question).count()
        question.save()
        question.refresh_from_db()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        answer = self.get_object()
        user = request.user
        is_like = request.data.get('is_like', True)
        
        # 检查是否已经有记录
        like_record, created = AnswerLike.objects.get_or_create(answer=answer, user=user)
        
        if created:
            # 新记录
            like_record.is_like = is_like
            like_record.save()
            if is_like:
                answer.likes_count = F('likes_count') + 1
            else:
                answer.dislikes_count = F('dislikes_count') + 1
        else:
            # 已存在记录，检查是否需要更新
            if like_record.is_like != is_like:
                # 改变了态度
                if like_record.is_like:
                    answer.likes_count = F('likes_count') - 1
                    answer.dislikes_count = F('dislikes_count') + 1
                else:
                    answer.dislikes_count = F('dislikes_count') - 1
                    answer.likes_count = F('likes_count') + 1
                like_record.is_like = is_like
                like_record.save()
            else:
                # 取消操作
                like_record.delete()
                if is_like:
                    answer.likes_count = F('likes_count') - 1
                else:
                    answer.dislikes_count = F('dislikes_count') - 1
        
        answer.save()
        answer.refresh_from_db()
        return Response({
            'likes_count': answer.likes_count,
            'dislikes_count': answer.dislikes_count
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def accept(self, request, pk=None):
        answer = self.get_object()
        question = answer.question
        
        # 检查是否是问题作者
        if question.author != request.user:
            return Response({'detail': '只有问题作者可以采纳回答'}, status=status.HTTP_403_FORBIDDEN)
        
        # 取消之前的采纳
        Answer.objects.filter(question=question, is_accepted=True).update(is_accepted=False)
        
        # 采纳当前回答
        answer.is_accepted = True
        answer.save()
        
        return Response({'status': 'accepted'})
    
    def destroy(self, request, *args, **kwargs):
        # 获取要删除的回答
        answer = self.get_object()
        
        # 检查是否是回答作者或是管理员
        if answer.author != request.user and not request.user.is_superuser:
            return Response({'detail': '只有回答作者或管理员可以删除回答'}, status=status.HTTP_403_FORBIDDEN)
        
        # 获取关联的问题
        question = answer.question
        
        # 执行删除
        response = super().destroy(request, *args, **kwargs)
        
        # 更新问题的回答数 - 使用直接计数而非F表达式，确保准确性
        if response.status_code == status.HTTP_204_NO_CONTENT:
            # 直接计算实际的回答数量
            question.answers_count = Answer.objects.filter(question=question).count()
            question.save()
            question.refresh_from_db()
        
        return response


class CommunityReportViewSet(viewsets.ModelViewSet):
    queryset = CommunityReport.objects.select_related('question', 'answer', 'reporter', 'processed_by')
    serializer_class = CommunityReportSerializer
    pagination_class = QuestionPagination

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_queryset(self):
        queryset = super().get_queryset()
        # 如果不是管理员，只返回当前用户的举报记录
        if not self.request.user.is_staff:
            queryset = queryset.filter(reporter=self.request.user)
        # 管理员可以查看所有举报记录，并支持筛选
        status_param = self.request.query_params.get('status')
        target_type = self.request.query_params.get('target_type')
        if status_param:
            queryset = queryset.filter(status=status_param)
        if target_type:
            queryset = queryset.filter(target_type=target_type)
        return queryset

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        status_before = serializer.instance.status
        report = serializer.save(
            processed_by=self.request.user if self.request.user.is_staff else serializer.instance.processed_by,
        )
        if report.status != 'pending' and status_before == 'pending':
            report.processed_at = timezone.now()
            report.save(update_fields=['processed_at'])
