from rest_framework import serializers
from .models import Favorite, FavoriteCategory
from django.contrib.contenttypes.models import ContentType
from resources.serializers import ResourceSerializer  # 引入资源库的序列化器（根据实际路径调整）

class FavoriteCategorySerializer(serializers.ModelSerializer):
    """收藏夹分类序列化器"""
    favorite_count = serializers.SerializerMethodField()

    class Meta:
        model = FavoriteCategory
        fields = ('id', 'name', 'created_at', 'updated_at', 'favorite_count')

    def get_favorite_count(self, obj):
        """获取分类下的收藏数量"""
        return obj.favorites.count()

class FavoriteSerializer(serializers.ModelSerializer):
    """收藏序列化器"""
    resource_type = serializers.CharField(write_only=True)  # 如"resources.Resource"
    resource_id = serializers.IntegerField(write_only=True)
    content_object = serializers.SerializerMethodField()  # 获取关联资源详情
    category = FavoriteCategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Favorite
        fields = ('id', 'resource_type', 'resource_id', 'created_at', 'content_object', 'category', 'category_id')

    def get_content_object(self, obj):
        # 根据资源类型动态序列化（示例：仅处理资源库类型，可扩展其他类型）
        if obj.content_type.model == 'resource':  # 对应resources应用的Resource模型
            return ResourceSerializer(obj.content_object).data
        return None  # 其他类型可补充

    def create(self, validated_data):
        user = self.context['request'].user
        app_label, model = validated_data['resource_type'].split('.')
        content_type = ContentType.objects.get(app_label=app_label, model=model)
        
        # 检查是否已收藏
        if Favorite.objects.filter(user=user, content_type=content_type, object_id=validated_data['resource_id']).exists():
            raise serializers.ValidationError('已收藏')
        
        # 获取分类（如果提供）
        category_id = validated_data.get('category_id')
        category = None
        if category_id:
            # 确保分类属于当前用户
            try:
                category = FavoriteCategory.objects.get(id=category_id, user=user)
            except FavoriteCategory.DoesNotExist:
                raise serializers.ValidationError('分类不存在或无权访问')
        
        # 如果没有指定分类，检查是否有默认分类
        if not category:
            default_category, _ = FavoriteCategory.objects.get_or_create(
                user=user,
                name='默认收藏夹'
            )
            category = default_category
        
        return Favorite.objects.create(
            user=user,
            content_type=content_type,
            object_id=validated_data['resource_id'],
            category=category
        )