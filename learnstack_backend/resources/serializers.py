from rest_framework import serializers
from .models import Resource, ResourceContent, ResourceRequest
from categories.models import TechnologyCategory
import json


class ResourceContentSerializer(serializers.ModelSerializer):
    """资源内容序列化"""
    book_file_url = serializers.SerializerMethodField()

    class Meta:
        model = ResourceContent
        fields = [
            'body_markdown',
            'body_html',
            'body_format',
            'sections',
            'embed_provider',
            'embed_url',
            'embed_meta',
            'document_html',
            'document_toc',
            'download_url',
            'book_file',
            'book_file_url',
            'extra_links',
            'extra_data',
            'last_synced_at',
        ]
        read_only_fields = ['book_file_url']
    
    def get_book_file_url(self, obj):
        """返回书籍文件的完整URL"""
        if obj.book_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.book_file.url)
            return obj.book_file.url
        return None


class ResourceBaseSerializer(serializers.ModelSerializer):
    """公共字段序列化"""

    categories_display = serializers.SerializerMethodField()
    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=TechnologyCategory.objects.all(),
        required=True
    )
    submitted_by_username = serializers.SerializerMethodField()
    reviewed_by_username = serializers.SerializerMethodField()
    target_audience_display = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = [
            'id', 'title', 'description', 'url', 'resource_type',
            'rating', 'target_audience', 'target_audience_display', 'content_source', 'hero_cover',
            'created_at', 'categories', 'categories_display',
            'status', 'submitted_by', 'submitted_by_username',
            'reviewed_by', 'reviewed_by_username', 'reviewed_at', 'admin_notes'
        ]
        read_only_fields = ['submitted_by', 'reviewed_by', 'reviewed_at', 'admin_notes', 'target_audience_display']

    def get_categories_display(self, obj):
        request = self.context.get('request')
        result = []
        for category in obj.categories.all():
            icon_url = None
            if category.icon_image:
                if request:
                    icon_url = request.build_absolute_uri(category.icon_image.url)
                else:
                    icon_url = category.icon_image.url
            result.append({
                'id': category.id,
                'name': category.name,
                'icon_image_url': icon_url
            })
        return result

    def get_submitted_by_username(self, obj):
        return obj.submitted_by.username if obj.submitted_by else None

    def get_reviewed_by_username(self, obj):
        return obj.reviewed_by.username if obj.reviewed_by else None

    def get_target_audience_display(self, obj):
        """返回适用人群的显示值"""
        return obj.get_target_audience_display() if obj.target_audience else ''


class ResourceDetailSerializer(ResourceBaseSerializer):
    """包含内容的序列化"""

    content = ResourceContentSerializer(required=False, allow_null=True)

    class Meta(ResourceBaseSerializer.Meta):
        fields = ResourceBaseSerializer.Meta.fields + ['content']
    
    def to_internal_value(self, data):
        """处理嵌套的content字段，支持文件上传"""
        # 处理嵌套的content字段（如 content[book_file], content[body_markdown]）
        # 将 QueryDict 或 MultiValueDict 转换为普通字典
        if hasattr(data, 'dict'):
            data = data.dict()
        
        if isinstance(data, dict):
            # 提取所有 content.* 字段
            content_data = {}
            keys_to_remove = []
            
            for key, value in list(data.items()):
                if key.startswith('content[') and ']' in key:
                    # 处理 content[field] 格式
                    # 提取 content[ 和 ] 之间的内容
                    start = key.find('[') + 1
                    end = key.find(']')
                    if start > 0 and end > start:
                        new_key = key[start:end]
                        content_data[new_key] = value
                        keys_to_remove.append(key)
                elif key.startswith('content.'):
                    # 处理 content.field 格式
                    new_key = key.replace('content.', '')
                    content_data[new_key] = value
                    keys_to_remove.append(key)
            
            # 移除已提取的字段
            for key in keys_to_remove:
                if key in data:
                    data.pop(key)
            
            # 如果有content数据，添加到data中
            if content_data:
                # 处理 JSON 字符串字段（如 sections, document_toc）
                for key in ['sections', 'document_toc']:
                    if key in content_data and isinstance(content_data[key], str):
                        try:
                            content_data[key] = json.loads(content_data[key])
                        except (json.JSONDecodeError, TypeError):
                            pass
                
                data['content'] = content_data
        
        return super().to_internal_value(data)

    def create(self, validated_data):
        content_data = validated_data.pop('content', None)
        categories = validated_data.pop('categories', [])
        resource = super().create(validated_data)
        if categories:
            resource.categories.set(categories)
        if content_data:
            # 在创建资源内容时，自动更新 last_synced_at
            from django.utils import timezone
            content_data['last_synced_at'] = timezone.now()
            ResourceContent.objects.update_or_create(
                resource=resource,
                defaults=content_data
            )
        return resource

    def update(self, instance, validated_data):
        content_data = validated_data.pop('content', None)
        categories = validated_data.pop('categories', None)
        resource = super().update(instance, validated_data)

        if categories is not None:
            resource.categories.set(categories)

        if content_data is not None:
            # 在更新资源内容时，自动更新 last_synced_at
            from django.utils import timezone
            content_data['last_synced_at'] = timezone.now()
            ResourceContent.objects.update_or_create(
                resource=resource,
                defaults=content_data
            )
        return resource


class ResourceSummarySerializer(ResourceBaseSerializer):
    """列表/概要序列化（无 content 字段）"""

    class Meta(ResourceBaseSerializer.Meta):
        fields = ResourceBaseSerializer.Meta.fields


class ResourceSerializer(ResourceDetailSerializer):
    """向后兼容：旧代码仍引用 ResourceSerializer 名称"""

    class Meta(ResourceDetailSerializer.Meta):
        fields = ResourceDetailSerializer.Meta.fields


class ResourceSubmissionSerializer(serializers.ModelSerializer):
    """用户投稿资源序列化器（支持完整内容字段和文件上传）"""
    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=TechnologyCategory.objects.all(),
        required=True
    )
    # 嵌套内容字段（可选）
    content = ResourceContentSerializer(required=False, allow_null=True)
    
    def to_internal_value(self, data):
        """处理嵌套的content字段，支持文件上传"""
        # 处理嵌套的content字段（如 content.book_file, content.body_markdown）
        if isinstance(data, dict):
            # 提取所有 content.* 字段
            content_data = {}
            keys_to_remove = []
            for key, value in data.items():
                if key.startswith('content.'):
                    new_key = key.replace('content.', '')
                    content_data[new_key] = value
                    keys_to_remove.append(key)
            
            # 移除已提取的字段
            for key in keys_to_remove:
                data.pop(key)
            
            # 如果有content数据，添加到data中
            if content_data:
                data['content'] = content_data
        
        return super().to_internal_value(data)

    class Meta:
        model = Resource
        fields = [
            'title', 'description', 'url', 'resource_type',
            'rating', 'target_audience', 'categories', 'hero_cover',
            'content_source', 'content'
        ]

    def validate(self, data):
        """根据资源类型验证必需字段"""
        # 验证封面图片（必填）
        hero_cover = data.get('hero_cover', '')
        if not hero_cover or not str(hero_cover).strip():
            raise serializers.ValidationError({
                'hero_cover': '封面图片是必填项，请提供封面图片URL'
            })
        
        # 验证资源链接（外部导入时必须填写）
        content_source = data.get('content_source', 'original')
        url = data.get('url', '')
        if content_source == 'embedded':
            if not url or not str(url).strip():
                raise serializers.ValidationError({
                    'url': '外部导入的资源必须填写资源链接'
                })
        
        resource_type = data.get('resource_type')
        content_data = data.get('content', {})
        
        # 根据内容来源验证字段
        # 站内原创/上传的资源需要填写内容
        if content_source == 'original':
            # 根据资源类型验证内容字段
            if resource_type == 'book':
                # 书籍需要 body_format 和 body_markdown/body_html，以及 download_url
                if not content_data.get('body_format'):
                    raise serializers.ValidationError({
                        'content': {'body_format': '书籍类型需要指定正文格式'}
                    })
                if content_data.get('body_format') == 'markdown' and not content_data.get('body_markdown'):
                    raise serializers.ValidationError({
                        'content': {'body_markdown': 'Markdown 格式需要提供正文内容'}
                    })
                if content_data.get('body_format') == 'html' and not content_data.get('body_html'):
                    raise serializers.ValidationError({
                        'content': {'body_html': 'HTML 格式需要提供正文内容'}
                    })
                # 书籍需要上传文件或提供下载链接（至少一个）
                if not content_data.get('book_file') and not content_data.get('download_url'):
                    raise serializers.ValidationError({
                        'content': '书籍类型需要上传文件或提供下载链接'
                    })
            elif resource_type == 'course':
                # 课程需要 sections（章节列表）
                if not content_data.get('sections'):
                    raise serializers.ValidationError({
                        'content': {'sections': '课程类型需要提供章节列表'}
                    })
            elif resource_type == 'article':
                # 文章需要 body_format 和 body_markdown/body_html
                if not content_data.get('body_format'):
                    raise serializers.ValidationError({
                        'content': {'body_format': '文章类型需要指定正文格式'}
                    })
                if content_data.get('body_format') == 'markdown' and not content_data.get('body_markdown'):
                    raise serializers.ValidationError({
                        'content': {'body_markdown': 'Markdown 格式需要提供正文内容'}
                    })
                if content_data.get('body_format') == 'html' and not content_data.get('body_html'):
                    raise serializers.ValidationError({
                        'content': {'body_html': 'HTML 格式需要提供正文内容'}
                    })
            elif resource_type in ['project', 'tool']:
                # 项目和工具需要 body_format 和 body_markdown/body_html
                if not content_data.get('body_format'):
                    raise serializers.ValidationError({
                        'content': {'body_format': f'{resource_type}类型需要指定正文格式'}
                    })
                if content_data.get('body_format') == 'markdown' and not content_data.get('body_markdown'):
                    raise serializers.ValidationError({
                        'content': {'body_markdown': 'Markdown 格式需要提供正文内容'}
                    })
                if content_data.get('body_format') == 'html' and not content_data.get('body_html'):
                    raise serializers.ValidationError({
                        'content': {'body_html': 'HTML 格式需要提供正文内容'}
                    })
            elif resource_type == 'document':
                # 文档需要 document_html 或 embed_url
                if not content_data.get('document_html') and not content_data.get('embed_url'):
                    raise serializers.ValidationError({
                        'content': '文档类型需要提供 document_html 或 embed_url'
                    })
        # 外部导入的资源只需要资源链接，不需要填写内容
        
        return data

    def create(self, validated_data):
        validated_data['status'] = 'pending'
        validated_data['submitted_by'] = self.context['request'].user
        # 设置默认的 content_source
        if 'content_source' not in validated_data:
            validated_data['content_source'] = 'original'
        
        categories = validated_data.pop('categories', [])
        content_data = validated_data.pop('content', None)
        
        resource = super().create(validated_data)
        resource.categories.set(categories)
        
        # 创建 ResourceContent（如果提供了内容数据）
        if content_data:
            # 在创建资源内容时，自动更新 last_synced_at
            from django.utils import timezone
            content_data['last_synced_at'] = timezone.now()
            ResourceContent.objects.create(
                resource=resource,
                **content_data
            )
        
        return resource


class ResourceRequestSerializer(serializers.ModelSerializer):
    """资源添加申请序列化器"""
    requested_by_username = serializers.SerializerMethodField()
    processed_by_username = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    resource_type_display = serializers.CharField(source='get_resource_type_display', read_only=True)
    
    class Meta:
        model = ResourceRequest
        fields = [
            'id', 'title', 'description', 'url', 'resource_type', 'resource_type_display',
            'target_audience', 'reason', 'status', 'status_display',
            'requested_by', 'requested_by_username', 'processed_by', 'processed_by_username',
            'processed_at', 'admin_notes', 'created_resource', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'requested_by', 'processed_by', 'processed_at', 
            'created_resource', 'created_at', 'updated_at'
        ]
    
    def get_requested_by_username(self, obj):
        return obj.requested_by.username if obj.requested_by else None
    
    def get_processed_by_username(self, obj):
        return obj.processed_by.username if obj.processed_by else None


class ResourceRequestCreateSerializer(serializers.ModelSerializer):
    """创建资源申请序列化器（用户提交时使用）"""
    
    class Meta:
        model = ResourceRequest
        fields = [
            'id', 'title', 'description', 'url', 'resource_type',
            'target_audience', 'reason', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'created_at']
        extra_kwargs = {
            'title': {'required': True, 'allow_blank': False},
            'url': {'required': True, 'allow_blank': False},
            'resource_type': {'required': True},
            'reason': {'required': True, 'allow_blank': False},
        }
    
    def validate(self, data):
        """验证数据"""
        # 确保必填字段不为空
        if not data.get('title', '').strip():
            raise serializers.ValidationError({'title': '资源标题不能为空'})
        if not data.get('url', '').strip():
            raise serializers.ValidationError({'url': '资源链接不能为空'})
        if not data.get('resource_type'):
            raise serializers.ValidationError({'resource_type': '请选择资源类型'})
        if not data.get('reason', '').strip():
            raise serializers.ValidationError({'reason': '申请理由不能为空'})
        return data
    
    def create(self, validated_data):
        validated_data['requested_by'] = self.context['request'].user
        instance = super().create(validated_data)
        return instance
