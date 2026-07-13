from django.urls import path
from .views import RegisterAPIView, LoginAPIView, UserMeView, change_password
from .admin_views import (
    AdminUserListView, AdminUserDetailView, 
    AdminUserCreateView,
    AdminDashboardStatsView
)

urlpatterns = [
    # 普通用户接口
    path('register/', RegisterAPIView.as_view(), name='register'),  # 注册接口
    path('login/', LoginAPIView.as_view(), name='login'),            # 登录接口
    path('me/', UserMeView.as_view(), name='me'),
    path('change-password/', change_password, name='change_password'),  # 修改密码接口
    
    # 管理员接口
    path('admin/users/', AdminUserListView.as_view(), name='admin_user_list'),
    path('admin/users/<int:pk>/', AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('admin/users/create/', AdminUserCreateView.as_view(), name='admin_user_create'),
    path('admin/dashboard/stats/', AdminDashboardStatsView.as_view(), name='admin_dashboard_stats'),
]