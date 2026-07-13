from rest_framework import serializers
from .models import Question, Answer, AnswerLike, CommunityReport
from users.serializers import UserSerializer
from django.utils import timezone

class AnswerSerializer(serializers.ModelSerializer):
    author_info = serializers.SerializerMethodField()
    
    def get_author_info(self, obj):
        return {"nickname": obj.author.nickname or obj.author.username, "id": obj.author.id}
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # 格式化时间
        data['created_at'] = timezone.localtime(instance.created_at).strftime('%Y-%m-%d %H:%M')
        return data
    
    class Meta:
        model = Answer
        fields = [
            'id', 'question', 'content', 'author', 'author_info',
            'created_at', 'likes_count', 'dislikes_count',
            'is_accepted'
        ]
        read_only_fields = ['author', 'likes_count', 'dislikes_count']

class QuestionSerializer(serializers.ModelSerializer):
    author_info = serializers.SerializerMethodField()
    answers = AnswerSerializer(many=True, read_only=True, source='answer_set')
    
    def get_author_info(self, obj):
        return {"nickname": obj.author.nickname or obj.author.username, "id": obj.author.id}
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # 格式化时间
        data['created_at'] = timezone.localtime(instance.created_at).strftime('%Y-%m-%d %H:%M')
        # 确保answers字段存在，即使为空
        if 'answers' not in data or data['answers'] is None:
            data['answers'] = []
        return data
    
    class Meta:
        model = Question
        fields = [
            'id', 'title', 'description', 'content', 'author', 'author_info',
            'created_at', 'updated_at', 'views_count', 'likes_count', 'answers_count',
            'tags', 'answers'
        ]
        read_only_fields = ['author', 'views_count', 'likes_count', 'answers_count', 'answers']
        extra_kwargs = {
            'title': {'required': True},
            'description': {'required': True},
            'tags': {'required': False, 'allow_blank': True, 'allow_null': True}
        }

class QuestionListSerializer(serializers.ModelSerializer):
    """问题列表专用序列化器，包含更少的字段"""
    author_info = serializers.SerializerMethodField()
    
    def get_author_info(self, obj):
        return {"nickname": obj.author.nickname or obj.author.username}
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_at'] = timezone.localtime(instance.created_at).strftime('%Y-%m-%d %H:%M')
        return data
    
    class Meta:
        model = Question
        fields = [
            'id', 'title', 'description', 'author_info', 'created_at',
            'views_count', 'answers_count', 'tags'
        ]


class CommunityReportSerializer(serializers.ModelSerializer):
    reporter_info = serializers.SerializerMethodField()
    processed_by_info = serializers.SerializerMethodField()
    question_title = serializers.SerializerMethodField()
    answer_excerpt = serializers.SerializerMethodField()
    question = serializers.IntegerField(read_only=True, source='question.id', allow_null=True)
    answer = serializers.IntegerField(read_only=True, source='answer.id', allow_null=True)
    target_id = serializers.IntegerField(write_only=True, required=False)
    target_type = serializers.ChoiceField(choices=CommunityReport.TARGET_CHOICES, required=False)

    class Meta:
        model = CommunityReport
        fields = [
            'id',
            'target_type',
            'target_id',
            'question',
            'answer',
            'reason',
            'description',
            'status',
            'created_at',
            'processed_at',
            'processed_by_info',
            'resolution_notes',
            'reporter_info',
            'question_title',
            'answer_excerpt',
        ]
        read_only_fields = [
            'created_at',
            'processed_at',
            'reporter_info',
            'question_title',
            'answer_excerpt',
        ]

    def get_reporter_info(self, obj):
        return {
            "id": obj.reporter.id,
            "nickname": obj.reporter.nickname or obj.reporter.username
        }

    def get_question_title(self, obj):
        if obj.question:
            return obj.question.title
        # 如果帖子已被删除，返回提示信息
        if obj.target_type == 'question':
            return '[该帖子已被删除]'
        return None

    def get_processed_by_info(self, obj):
        if not obj.processed_by:
            return None
        return {
            "id": obj.processed_by.id,
            "nickname": obj.processed_by.nickname or obj.processed_by.username
        }

    def get_answer_excerpt(self, obj):
        if obj.answer:
            return obj.answer.content[:80]
        # 如果评论已被删除，返回提示信息
        if obj.target_type == 'answer':
            return '[该评论已被删除]'
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # 格式化时间
        if instance.created_at:
            data['created_at'] = timezone.localtime(instance.created_at).strftime('%Y-%m-%d %H:%M')
        if instance.processed_at:
            data['processed_at'] = timezone.localtime(instance.processed_at).strftime('%Y-%m-%d %H:%M')
        return data

    def validate(self, attrs):
        # 只在创建时验证 target_id 和 target_type
        if self.instance is None:  # 创建操作
            target_type = attrs.get('target_type')
            target_id = attrs.get('target_id')
            request = self.context.get('request')
            if not target_id:
                raise serializers.ValidationError("target_id 字段必填")
            if not target_type:
                raise serializers.ValidationError("target_type 字段必填")
            if request is None or not request.user.is_authenticated:
                raise serializers.ValidationError("需要登录后才能举报")
            if target_type == 'question':
                try:
                    question = Question.objects.get(pk=target_id)
                except Question.DoesNotExist:
                    raise serializers.ValidationError("指定的帖子不存在")
                if question.author_id == request.user.id:
                    raise serializers.ValidationError("不能举报自己发布的帖子")
                attrs['question'] = question
                attrs['answer'] = None
            else:
                try:
                    answer = Answer.objects.select_related('question').get(pk=target_id)
                except Answer.DoesNotExist:
                    raise serializers.ValidationError("指定的评论不存在")
                if answer.author_id == request.user.id:
                    raise serializers.ValidationError("不能举报自己发布的评论")
                attrs['answer'] = answer
                attrs['question'] = answer.question
        # 更新操作不需要验证 target_id 和 target_type
        return attrs

    def create(self, validated_data):
        validated_data['reporter'] = self.context['request'].user
        validated_data.pop('target_id', None)
        validated_data.pop('status', None)
        validated_data.pop('resolution_notes', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('target_id', None)
        validated_data.pop('target_type', None)
        return super().update(instance, validated_data)