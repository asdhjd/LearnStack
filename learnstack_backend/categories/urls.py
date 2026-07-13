from django.urls import path
from .views import CategoryList, HotSubcategoryList, CategoryAllList, AllTechnologiesList, CategoryDetailView
from .admin_views import AdminCategoryListView, AdminCategoryDetailView

urlpatterns = [
    # 公共接口
    path('', CategoryList.as_view(), name='category-list'),
    path('AllList', CategoryAllList.as_view(), name='category-all-list'),
    path('allTechnologies', AllTechnologiesList.as_view(), name='alltechnologies-list'),
    path('hotsubcategories', HotSubcategoryList.as_view(), name='hot-subcategories'),
    path('<int:id>/', CategoryDetailView.as_view(), name='category-detail'),
    
    # 管理员接口（简化为 2 个端点：List+Create 和 Retrieve+Update+Delete）
    path('admin/categories/', AdminCategoryListView.as_view(), name='admin_category_list'),
    path('admin/categories/<int:id>/', AdminCategoryDetailView.as_view(), name='admin_category_detail'),
]