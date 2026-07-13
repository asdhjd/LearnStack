from django.db import models
from categories.models import TechnologyCategory
from resources.models import Resource
from users.models import CustomUser


class LearningPath(models.Model):
    """学习路径模型，代表某一技术的完整学习路径"""
    
    # 关联到技术分类
    technology = models.OneToOneField(
        'categories.TechnologyCategory',
        on_delete=models.CASCADE,
        related_name='learning_path',
        verbose_name="关联技术分类",
        db_column="technology_id",
        null=True,  # 允许为null，以便Django可以为现有行提供默认值
        blank=True
    )
    
    description = models.TextField(blank=True, verbose_name="学习路径描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    def __str__(self):
        return f"{self.technology.name} 学习路径"


class LearningStage(models.Model):
    """学习阶段模型，代表学习路径中的一个阶段"""
    
    # 关联到学习路径
    learning_path = models.ForeignKey(
        LearningPath,
        on_delete=models.CASCADE,
        related_name='stages',
        verbose_name="所属学习路径"
    )
    
    title = models.CharField(max_length=100, verbose_name="阶段标题")
    description = models.TextField(blank=True, verbose_name="阶段描述")
    order = models.PositiveIntegerField(verbose_name="阶段顺序")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    # 注意：推荐资源通过动态生成，不存储在数据库中
    # 系统根据资源的 target_audience 字段自动组织资源到对应阶段
    
    class Meta:
        ordering = ['order']  # 按阶段顺序排序
    
    def __str__(self):
        return f"{self.learning_path.technology.name} - {self.title}"


class UserLearningProgress(models.Model):
    """用户学习进度模型，记录用户在每个学习阶段的进度"""
    
    # 关联到用户
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='learning_progresses',
        verbose_name="用户"
    )
    
    # 关联到学习阶段
    stage = models.ForeignKey(
        LearningStage,
        on_delete=models.CASCADE,
        related_name='user_progresses',
        verbose_name="学习阶段"
    )
    
    # 是否完成该阶段
    is_completed = models.BooleanField(default=False, verbose_name="是否完成")
    
    # 完成时间
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完成时间")
    
    # 创建时间和更新时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "用户学习进度"
        verbose_name_plural = "用户学习进度"
        # 确保一个用户在一个学习阶段只能有一条进度记录
        unique_together = ('user', 'stage')
    
    def __str__(self):
        completion_status = "已完成" if self.is_completed else "未完成"
        return f"{self.user.username} - {self.stage.title} - {completion_status}"


class UserStudyTime(models.Model):
    """用户学习时长模型，记录用户每天的学习时长"""
    
    # 关联到用户
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='study_times',
        verbose_name="用户"
    )
    
    # 学习日期（只记录日期，不记录时间）
    study_date = models.DateField(verbose_name="学习日期")
    
    # 学习时长（单位：小时，支持小数）
    study_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="学习时长（小时）"
    )
    
    # 创建时间和更新时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "用户学习时长"
        verbose_name_plural = "用户学习时长"
        # 确保一个用户在同一天只能有一条记录
        unique_together = ('user', 'study_date')
        ordering = ['-study_date']  # 按日期倒序排列
    
    def __str__(self):
        return f"{self.user.username} - {self.study_date} - {self.study_hours}小时"