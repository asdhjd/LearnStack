from django.db import models
from users.models import CustomUser

class Question(models.Model):
    """问题模型"""
    title = models.CharField(max_length=200, verbose_name="问题标题")
    description = models.TextField(verbose_name="问题描述")
    content = models.TextField(blank=True, verbose_name="详细内容")
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="提问者"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    views_count = models.PositiveIntegerField(default=0, verbose_name="浏览量")
    likes_count = models.PositiveIntegerField(default=0, verbose_name="点赞数")
    answers_count = models.PositiveIntegerField(default=0, verbose_name="回答数")
    
    # 标签
    tags = models.CharField(max_length=200, blank=True, verbose_name="标签")
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "问题"
        verbose_name_plural = "问题"
        ordering = ['-created_at']

class Answer(models.Model):
    """回答模型"""
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="所属问题"
    )
    content = models.TextField(verbose_name="回答内容")
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="回答者"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    likes_count = models.PositiveIntegerField(default=0, verbose_name="点赞数")
    dislikes_count = models.PositiveIntegerField(default=0, verbose_name="反对数")
    is_accepted = models.BooleanField(default=False, verbose_name="是否被采纳")
    
    def __str__(self):
        return f"回答 {self.id} - {self.question.title}"
    
    class Meta:
        verbose_name = "回答"
        verbose_name_plural = "回答"
        ordering = ['-likes_count', '-created_at']

# QuestionLike 模型已移除，系统只支持评论的点赞和反对功能

class AnswerLike(models.Model):
    """回答点赞记录"""
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='answer_likes'
    )
    is_like = models.BooleanField(default=True)  # True: 点赞, False: 踩
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('answer', 'user')


class CommunityReport(models.Model):
    """社区举报记录"""
    TARGET_CHOICES = (
        ('question', '帖子'),
        ('answer', '评论'),
    )
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('resolved', '已处理'),
        ('dismissed', '已驳回'),
    )

    reporter = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='community_reports',
        verbose_name="举报人"
    )
    target_type = models.CharField(max_length=20, choices=TARGET_CHOICES, verbose_name="对象类型")
    question = models.ForeignKey(
        Question,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reports',
        verbose_name="被举报帖子"
    )
    answer = models.ForeignKey(
        Answer,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reports',
        verbose_name="被举报评论"
    )
    reason = models.CharField(max_length=255, verbose_name="举报原因")
    description = models.TextField(blank=True, verbose_name="补充说明")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="处理状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="举报时间")
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="处理时间")
    processed_by = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='processed_reports',
        verbose_name="处理人"
    )
    resolution_notes = models.TextField(blank=True, verbose_name="处理备注")

    class Meta:
        verbose_name = "社区举报"
        verbose_name_plural = "社区举报"
        ordering = ['-created_at']

    def __str__(self):
        target = self.question or self.answer
        return f"{self.get_target_type_display()}举报 - {target}"

    def clean(self):
        from django.core.exceptions import ValidationError
        # 已处理的举报记录允许 question/answer 为 null（内容可能已被删除）
        if self.status in ['resolved', 'dismissed']:
            # 已处理的记录允许关联内容为空
            return
        
        # 待处理的举报记录必须有关联内容
        if self.target_type == 'question' and not self.question:
            raise ValidationError("帖子举报必须关联问题记录")
        if self.target_type == 'answer' and not self.answer:
            raise ValidationError("评论举报必须关联回答记录")
        if self.target_type == 'answer' and self.answer and not self.question:
            self.question = self.answer.question
        if self.target_type == 'question' and self.answer:
            raise ValidationError("帖子举报不应关联评论")
        if self.target_type == 'answer' and self.question and self.answer and self.answer.question_id != self.question_id:
            raise ValidationError("评论举报的帖子和评论不匹配")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)