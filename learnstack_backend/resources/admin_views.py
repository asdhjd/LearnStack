from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Resource
from .serializers import ResourceDetailSerializer
from categories.models import TechnologyCategory
from django.contrib.contenttypes.models import ContentType


class AdminResourceListCreateView(generics.ListCreateAPIView):
    """
    管理员资源列表和创建视图
    支持搜索、过滤和创建新资源
    """
    queryset = Resource.objects.all().order_by('-created_at')
    serializer_class = ResourceDetailSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        """
        支持按搜索关键词和分类ID过滤资源
        """
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        category_id = self.request.query_params.get('category_id', None)
        
        if search:
            queryset = queryset.filter(
                title__icontains=search
            ) | queryset.filter(
                description__icontains=search
            ) | queryset.filter(
                categories__name__icontains=search
            ).distinct()
        
        if category_id:
            queryset = queryset.filter(categories__id=category_id)
            
        return queryset
    
    def perform_create(self, serializer):
        """
        处理创建操作，确保分类字段的正确处理
        """
        data = self.request.data.copy()
        
        # 处理分类数据
        if 'categories' in data and isinstance(data['categories'], list):
            valid_categories = TechnologyCategory.objects.filter(id__in=data['categories'])
            # 为serializer的validated_data设置分类
            serializer.save()
            serializer.instance.categories.set(valid_categories)
        else:
            serializer.save()


class AdminResourceDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    管理员资源详情、更新和删除视图
    整合了详情、更新、删除三种操作，避免代码重复
    """
    queryset = Resource.objects.all()
    serializer_class = ResourceDetailSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def update(self, request, *args, **kwargs):
        """
        重写更新方法，确保分类字段的正确处理
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # 处理分类数据
        # 如果是 QueryDict 或 MultiValueDict，转换为普通字典
        if hasattr(request.data, 'dict'):
            data = request.data.dict()
        else:
            data = request.data.copy()
        
        # 处理分类：FormData 中 categories 可能是多个同名字段
        if 'categories' in data:
            categories = data['categories']
            # 如果是列表，直接使用
            if isinstance(categories, list):
                valid_categories = TechnologyCategory.objects.filter(id__in=categories)
                data['categories'] = [cat.id for cat in valid_categories]
            # 如果是单个值，转换为列表
            elif categories:
                try:
                    cat_id = int(categories) if isinstance(categories, str) else categories
                    valid_categories = TechnologyCategory.objects.filter(id=cat_id)
                    data['categories'] = [cat.id for cat in valid_categories]
                except (ValueError, TypeError):
                    data['categories'] = []
            else:
                data['categories'] = []
        
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        重写删除方法，安全地清理所有关联关系
        """
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)