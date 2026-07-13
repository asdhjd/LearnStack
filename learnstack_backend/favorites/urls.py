from django.urls import path
from .views import (
    FavoriteListView,
    FavoriteDeleteView,
    FavoriteUpdateView,
    FavoriteCategoryListView,
    FavoriteCategoryDetailView
)

urlpatterns = [
    # 收藏相关端点
    path('', FavoriteListView.as_view(), name='favorite-list'),
    path('delete/', FavoriteDeleteView.as_view(), name='favorite-delete'),
    path('<int:pk>/update/', FavoriteUpdateView.as_view(), name='favorite-update'),
    
    # 收藏夹分类相关端点
    path('categories/', FavoriteCategoryListView.as_view(), name='favorite-category-list'),
    path('categories/<int:pk>/', FavoriteCategoryDetailView.as_view(), name='favorite-category-detail'),
]