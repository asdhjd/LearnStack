from rest_framework import serializers
from .models import LearningPath, LearningStage, UserLearningProgress, UserStudyTime
from resources.serializers import ResourceSerializer


class LearningStageSerializer(serializers.ModelSerializer):
    """学习阶段序列化器"""
    
    # 嵌套序列化推荐资源（动态生成，不依赖数据库关联）
    recommended_resources = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningStage
        fields = [
            'id', 'title', 'description', 'order', 
            'created_at', 'recommended_resources'
        ]
    
    def get_recommended_resources(self, obj):
        # 动态生成推荐资源，根据资源的 target_audience 字段自动组织
        # 不再从数据库的 ManyToMany 关联中读取
        from resources.models import Resource
        from resources.serializers import ResourceSummarySerializer
        
        # 获取该学习阶段所属的学习路径的技术分类
        category = obj.learning_path.technology
        
        # 根据阶段标题判断适用人群
        stage_title = obj.title.lower()
        if '入门' in stage_title or '初级' in stage_title:
            target_audience_keywords = ['初级', 'beginner']
        elif '进阶' in stage_title or '中级' in stage_title:
            target_audience_keywords = ['中级', 'intermediate']
        elif '高级' in stage_title:
            target_audience_keywords = ['高级', 'advanced']
        else:
            # 默认返回所有相关资源
            target_audience_keywords = []
        
        # 获取该分类相关的已审核通过的资源
        related_resources = Resource.objects.filter(
            status='approved',
            categories=category
        ).distinct()
        
        # 根据 target_audience 过滤资源
        if target_audience_keywords:
            from django.db.models import Q
            query = Q()
            for keyword in target_audience_keywords:
                query |= Q(target_audience__icontains=keyword)
            related_resources = related_resources.filter(query)
        
        # 使用序列化器返回资源数据
        return ResourceSummarySerializer(related_resources, many=True, context=self.context).data


class LearningPathSerializer(serializers.ModelSerializer):
    """学习路径序列化器"""
    
    # 嵌套序列化学习阶段
    stages = LearningStageSerializer(many=True)
    
    # 关联的技术分类信息
    technology_id = serializers.ReadOnlyField(source='technology.id')
    technology_name = serializers.ReadOnlyField(source='technology.name')
    technology_description = serializers.ReadOnlyField(source='technology.description')
    technology_icon_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningPath
        fields = [
            'id', 'technology_id', 'technology_name', 'technology_description', 
            'technology_icon_image_url', 'description', 'created_at', 
            'updated_at', 'stages'
        ]
    
    def get_technology_icon_image_url(self, obj):
        """返回技术分类图标图片URL"""
        if obj.technology.icon_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.technology.icon_image.url)
            return obj.technology.icon_image.url
        return None


class LearningPathDetailSerializer(serializers.ModelSerializer):
    """学习路径详情序列化器，用于学习路径详情页"""
    
    # 嵌套序列化学习阶段（确保按 order 排序）
    stages = serializers.SerializerMethodField()
    
    # 关联的技术分类详细信息
    technology = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningPath
        fields = [
            'id', 'technology', 'description', 'created_at', 
            'updated_at', 'stages'
        ]
    
    def get_technology(self, obj):
        request = self.context.get('request')
        icon_url = None
        if obj.technology.icon_image:
            if request:
                icon_url = request.build_absolute_uri(obj.technology.icon_image.url)
            else:
                icon_url = obj.technology.icon_image.url
        return {
            'id': obj.technology.id,
            'name': obj.technology.name,
            'description': obj.technology.description,
            'icon_image_url': icon_url
        }
    
    def get_stages(self, obj):
        # 确保按 order 排序，并返回所有阶段（即使没有资源）
        stages = obj.stages.all().order_by('order')
        return LearningStageSerializer(stages, many=True).data


class UserLearningProgressSerializer(serializers.ModelSerializer):
    """用户学习进度序列化器"""
    
    # 嵌套序列化学习阶段信息
    stage_id = serializers.ReadOnlyField(source='stage.id')
    stage_title = serializers.ReadOnlyField(source='stage.title')
    stage_order = serializers.ReadOnlyField(source='stage.order')
    
    # 嵌套序列化用户信息
    user_id = serializers.ReadOnlyField(source='user.id')
    username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = UserLearningProgress
        fields = [
            'id', 'user_id', 'username', 'stage_id', 'stage_title', 'stage_order',
            'is_completed', 'completed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'stage']


class UserStudyTimeSerializer(serializers.ModelSerializer):
    """用户学习时长序列化器"""
    
    class Meta:
        model = UserStudyTime
        fields = [
            'id', 'study_date', 'study_hours', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user']