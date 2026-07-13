from rest_framework import generics, permissions, status
from rest_framework import serializers
from rest_framework.response import Response
from categories.models import TechnologyCategory
from categories.serializers import CategorySerializer


class AdminPermission(permissions.BasePermission):
    """检查用户是否是管理员"""
    
    def has_permission(self, request, view):
        # 必须登录且是管理员
        return request.user.is_authenticated and request.user.is_superuser


class AdminCategoryListView(generics.ListCreateAPIView):
    """管理员获取分类列表和创建新分类API"""
    queryset = TechnologyCategory.objects.all().order_by('id')
    serializer_class = CategorySerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 支持分页参数
        page = self.request.query_params.get('page', 1)
        page_size = self.request.query_params.get('page_size', 10)
        
        # 支持搜索
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
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
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        
        # 返回带总数的分页数据
        return Response({
            'results': serializer.data,
            'count': getattr(self, 'total_count', len(serializer.data))
        })
    
    def perform_create(self, serializer):
        """创建分类时检查名称唯一性"""
        name = serializer.validated_data.get('name')
        if name:
            existing = TechnologyCategory.objects.filter(name=name)
            if existing.exists():
                raise serializers.ValidationError({'name': '分类名称已存在'})
        serializer.save()
    
    def get_serializer_context(self):
        """传递request context给序列化器"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class AdminCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """管理员获取、更新、删除单个分类API（整合热门状态切换功能）"""
    queryset = TechnologyCategory.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AdminPermission]
    lookup_field = 'id'
    
    def perform_update(self, serializer):
        """更新分类时检查名称唯一性"""
        name = serializer.validated_data.get('name')
        if name:
            # 排除当前分类的其他记录
            existing = TechnologyCategory.objects.filter(name=name).exclude(id=self.get_object().id)
            if existing.exists():
                raise serializers.ValidationError({'name': '分类名称已存在'})
        
        serializer.save()
    
    def get_serializer_context(self):
        """传递request context给序列化器"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def patch(self, request, *args, **kwargs):
        """
        处理部分更新请求（PATCH）
        支持更新热门状态或其他字段
        """
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()
        
        # 如果是仅更新热门状态
        if 'is_hot' in data and len(data) == 1:
            is_hot = data.get('is_hot')
            if is_hot is not None:
                instance.is_hot = bool(is_hot)
                instance.save()
                return Response({
                    'id': instance.id,
                    'is_hot': instance.is_hot,
                    'message': f'分类热门状态已更新为{"热门" if instance.is_hot else "普通"}'
                })
        
        # 其他更新操作使用标准的 update 方法
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """删除分类时检查是否有子分类"""
        instance = self.get_object()
        
        # 检查是否有子分类
        if instance.subcategories.exists():
            return Response(
                {'error': '该分类下有子分类，无法删除'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)