from rest_framework import generics
from .models import TechnologyCategory
from .serializers import CategorySerializer


class CategoryList(generics.ListAPIView):
    """
    仅获取一级分类（parent为null）
    """
    queryset = TechnologyCategory.objects.filter(parent__isnull=True,is_hot=True)  #只取一级分类
    serializer_class = CategorySerializer
    
    def get_serializer_context(self):
        """传递request context给序列化器"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class CategoryAllList(generics.ListAPIView):
    """
    仅获取所有一级分类
    """
    serializer_class = CategorySerializer
    queryset = TechnologyCategory.objects.filter(parent__isnull=True)
    
    def get_serializer_context(self):
        """传递request context给序列化器"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class HotSubcategoryList(generics.ListAPIView):
    """获取所有热门子分类（is_hot=True 且有父分类）"""
    serializer_class = CategorySerializer

    def get_queryset(self):
        return TechnologyCategory.objects.filter(
            parent__isnull=False,  # 排除一级分类，只取子分类
            is_hot=True  # 热门标记
        ).order_by('-created_at')  # 按创建时间倒序排列
    
    def get_serializer_context(self):
        """传递request context给序列化器"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class AllTechnologiesList(generics.ListAPIView):
    """
    获取所有子分类
    """
    queryset = TechnologyCategory.objects.filter(parent__isnull=False)
    serializer_class = CategorySerializer
    
    def get_serializer_context(self):
        """传递request context给序列化器"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class CategoryDetailView(generics.RetrieveAPIView):

    queryset = TechnologyCategory.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'id'  # 匹配URL中的id参数

    def get_queryset(self):
        # 预加载子分类，优化查询性能
        return super().get_queryset().prefetch_related('subcategories')
    
    def get_serializer_context(self):
        """传递request context给序列化器"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context