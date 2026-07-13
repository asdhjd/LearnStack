from django.urls import path
from .views import (
    ResourceListView, ResourceDetailView, ResourceSubmissionView,
    ResourceModerationListView, approve_resource, reject_resource,
    fetch_article_content, fetch_bilibili_sections,
    ResourceRequestListView,
    AdminResourceRequestListView, update_resource_request_status,
    download_resource_file
)
from .admin_views import (
    AdminResourceListCreateView,
    AdminResourceDetailUpdateDeleteView
)

urlpatterns = [
    # 普通用户资源API
    path('', ResourceListView.as_view(), name='resource-list'),
    path('<int:pk>/', ResourceDetailView.as_view(), name='resource-detail'),
    path('<int:resource_id>/download/', download_resource_file, name='download-resource-file'),
    path('submit/', ResourceSubmissionView.as_view(), name='resource-submit'),
    path('fetch-content/', fetch_article_content, name='fetch-article-content'),
    path('fetch-bilibili-sections/', fetch_bilibili_sections, name='fetch-bilibili-sections'),
    path('requests/', ResourceRequestListView.as_view(), name='resource-request-list'),
    
    # 管理员资源审核API
    path('moderation/', ResourceModerationListView.as_view(), name='resource-moderation'),
    path('moderation/<int:resource_id>/approve/', approve_resource, name='approve-resource'),
    path('moderation/<int:resource_id>/reject/', reject_resource, name='reject-resource'),
    
    # 管理员资源管理API（List, Create, Retrieve, Update, Delete 都在这里）
    path('admin/', AdminResourceListCreateView.as_view(), name='admin-resource-list-create'),
    path('admin/<int:pk>/', AdminResourceDetailUpdateDeleteView.as_view(), name='admin-resource-detail-update-delete'),
    
    # 管理员资源申请管理API
    path('admin/requests/', AdminResourceRequestListView.as_view(), name='admin-resource-request-list'),
    path('admin/requests/<int:request_id>/status/', update_resource_request_status, name='admin-resource-request-status'),
]