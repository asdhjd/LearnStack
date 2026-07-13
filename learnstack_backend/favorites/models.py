from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

User = get_user_model()

class FavoriteCategory(models.Model):
    """收藏夹分类模型"""
    name = models.CharField(max_length=50, verbose_name="分类名称")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorite_categories")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "收藏夹分类"
        verbose_name_plural = "收藏夹分类"
        unique_together = (('user', 'name'),)  # 确保用户的分类名称唯一

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # 资源类型（如表名）
    object_id = models.PositiveIntegerField()  # 资源ID
    content_object = GenericForeignKey('content_type', 'object_id')  # 关联资源对象
    category = models.ForeignKey(
        'FavoriteCategory',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='favorites'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')  # 防止重复收藏