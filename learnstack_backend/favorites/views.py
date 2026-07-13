from rest_framework import generics, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Favorite, FavoriteCategory
from .serializers import FavoriteSerializer, FavoriteCategorySerializer
from django.db import IntegrityError

# 收藏夹分类管理视图
class FavoriteCategoryListView(generics.ListCreateAPIView):
    """获取用户的所有分类或创建新分类"""
    serializer_class = FavoriteCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 确保只返回当前用户的分类
        return FavoriteCategory.objects.filter(user=self.request.user).order_by('created_at')

    def perform_create(self, serializer):
        # 确保创建的分类属于当前用户
        serializer.save(user=self.request.user)

class FavoriteCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """获取、更新或删除特定分类"""
    serializer_class = FavoriteCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 确保只能操作当前用户的分类
        return FavoriteCategory.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        # 删除分类前，将该分类下的收藏移至默认收藏夹
        default_category, _ = FavoriteCategory.objects.get_or_create(
            user=self.request.user,
            name='默认收藏夹'
        )
        instance.favorites.update(category=default_category)
        instance.delete()

# 收藏管理视图
class FavoriteListView(generics.ListCreateAPIView):
    """获取用户的收藏列表或创建新收藏"""
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            queryset = Favorite.objects.filter(user=self.request.user).order_by('-created_at')
            # 支持按分类筛选
            category_id = self.request.query_params.get('category')
            if category_id:
                queryset = queryset.filter(category_id=category_id)
            return queryset
        except IntegrityError as e:
            from rest_framework.exceptions import APIException
            raise APIException("收藏记录存在无效关联资源")

class FavoriteDeleteView(generics.DestroyAPIView):
    """批量删除收藏"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        favorite_ids = request.data.get('ids', [])
        Favorite.objects.filter(id__in=favorite_ids, user=request.user).delete()
        return Response({'message': '删除成功'}, status=status.HTTP_200_OK)

class FavoriteUpdateView(generics.UpdateAPIView):
    """更新收藏（主要用于更改分类）"""
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    queryset = Favorite.objects.all()

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        # 如果更新分类，确保分类属于当前用户
        if 'category_id' in serializer.validated_data:
            category_id = serializer.validated_data['category_id']
            if category_id:
                try:
                    category = FavoriteCategory.objects.get(id=category_id, user=self.request.user)
                    serializer.save(category=category)
                except FavoriteCategory.DoesNotExist:
                    from rest_framework.exceptions import ValidationError
                    raise ValidationError('分类不存在或无权访问')
            else:
                # 如果设置为None，移至默认收藏夹
                default_category, _ = FavoriteCategory.objects.get_or_create(
                    user=self.request.user,
                    name='默认收藏夹'
                )
                serializer.save(category=default_category)
        else:
            serializer.save()