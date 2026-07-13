from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .serializers import UserSerializer, RegisterSerializer

User = get_user_model()


class AdminPermission(permissions.BasePermission):
    """检查用户是否是管理员"""
    
    def has_permission(self, request, view):
        # 必须登录且是管理员
        return request.user.is_authenticated and request.user.is_superuser


class AdminUserListView(generics.ListAPIView):
    """管理员获取用户列表API"""
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 支持分页参数
        page = self.request.query_params.get('page', 1)
        page_size = self.request.query_params.get('page_size', 10)
        
        try:
            page = int(page)
            page_size = int(page_size)
            start = (page - 1) * page_size
            end = start + page_size
            
            # 计算总数
            self.total_count = queryset.count()
            
            # 返回分页后的数据
            return queryset[start:end]
        except (ValueError, TypeError):
            return queryset[:10]  # 默认返回前10条
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        # 返回带总数的分页数据
        return Response({
            'results': serializer.data,
            'count': getattr(self, 'total_count', len(serializer.data))
        })


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """管理员获取、更新、删除单个用户API"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AdminPermission]
    
    def perform_update(self, serializer):
        # 确保只有管理员可以修改管理员权限
        if 'is_superuser' in serializer.validated_data and not self.request.user.is_superuser:
            raise permissions.PermissionDenied("您没有权限修改管理员权限")
        
        # 保存用户对象
        user = serializer.save()
        
        # 特殊处理密码字段 - 如果提供了密码，使用set_password进行哈希处理
        if 'password' in self.request.data:
            user.set_password(self.request.data['password'])
            user.save()


class AdminUserCreateView(generics.CreateAPIView):
    """管理员创建新用户API"""
    serializer_class = RegisterSerializer
    permission_classes = [AdminPermission]
    
    def perform_create(self, serializer):
        # 创建用户时设置密码
        user = serializer.save()
        if 'password' in self.request.data:
            user.set_password(self.request.data['password'])
            user.save()


class AdminDashboardStatsView(APIView):
    """管理员仪表盘统计数据API"""
    permission_classes = [AdminPermission]
    
    def get(self, request):
        # 用户统计
        total_users = User.objects.count()
        new_users_today = User.objects.filter(date_joined__date=timezone.now().date()).count()
        new_users_this_week = User.objects.filter(
            date_joined__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # 社区互动统计
        from community.models import Question, Answer
        total_questions = Question.objects.count()
        total_answers = Answer.objects.count()
        total_views = Question.objects.aggregate(Sum('views_count'))['views_count__sum'] or 0
        
        # 本周新增的问题和回答
        week_ago = timezone.now() - timedelta(days=7)
        new_questions_this_week = Question.objects.filter(created_at__gte=week_ago).count()
        new_answers_this_week = Answer.objects.filter(created_at__gte=week_ago).count()
        
        # 今日新增的问题和回答
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        new_questions_today = Question.objects.filter(created_at__gte=today_start).count()
        new_answers_today = Answer.objects.filter(created_at__gte=today_start).count()
        
        # 资源统计
        from resources.models import Resource
        total_resources = Resource.objects.count()
        approved_resources = Resource.objects.filter(status='approved').count()
        pending_resources = Resource.objects.filter(status='pending').count()
        
        # 本周新增的资源
        new_resources_this_week = Resource.objects.filter(created_at__gte=week_ago).count()
        
        # 今日新增的资源
        new_resources_today = Resource.objects.filter(created_at__gte=today_start).count()
        
        return Response({
            'user_stats': {
                'total_users': total_users,
                'new_users_today': new_users_today,
                'new_users_this_week': new_users_this_week
            },
            'community_stats': {
                'total_questions': total_questions,
                'total_answers': total_answers,
                'total_views': total_views,
                'new_questions_this_week': new_questions_this_week,
                'new_answers_this_week': new_answers_this_week,
                'new_questions_today': new_questions_today,
                'new_answers_today': new_answers_today
            },
            'resource_stats': {
                'total_resources': total_resources,
                'approved_resources': approved_resources,
                'pending_resources': pending_resources,
                'new_resources_this_week': new_resources_this_week,
                'new_resources_today': new_resources_today
            },

        })