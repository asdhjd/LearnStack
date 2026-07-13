from rest_framework import serializers
from.models import TechnologyCategory


class CategorySerializer(serializers.ModelSerializer):
    # 添加图片 URL 字段
    icon_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = TechnologyCategory
        fields = [
            'id', 'name', 'description', 'icon_image', 'icon_image_url',
            'created_at', 'parent_id', 'parent', 'subcategories', 'is_hot'
        ]
        read_only_fields = ['icon_image_url']
        
    def get_icon_image_url(self, obj):
        """返回图片的完整 URL"""
        if obj.icon_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.icon_image.url)
            return obj.icon_image.url
        return None
        
    # 修复：允许parent_id字段可写入，确保创建二级分类时能正确设置父分类
    parent_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    # 添加parent字段用于返回父分类ID
    parent = serializers.IntegerField(source='parent.id', read_only=True, allow_null=True)

    # 新增：嵌套子分类序列化器（递归处理层级）
    subcategories = serializers.SerializerMethodField()

    def get_subcategories(self, obj):
        # 获取当前分类的所有子分类（parent_id=当前分类ID）
        subcategories = TechnologyCategory.objects.filter(parent=obj.id)
        # 递归使用当前序列化器处理子分类，生成嵌套JSON，传递context
        return CategorySerializer(subcategories, many=True, context=self.context).data
    
    def create(self, validated_data):
        # 处理parent_id字段
        parent_id = validated_data.pop('parent_id', None)
        # 创建分类实例
        category = TechnologyCategory(**validated_data)
        # 如果有parent_id，设置父分类关系
        if parent_id is not None:
            try:
                parent_category = TechnologyCategory.objects.get(id=parent_id)
                category.parent = parent_category
            except TechnologyCategory.DoesNotExist:
                raise serializers.ValidationError({'parent_id': '父分类不存在'})
        # 保存分类
        category.save()
        return category