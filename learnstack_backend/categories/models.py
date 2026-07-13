from django.db import models

class TechnologyCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_hot = models.BooleanField(default=False)  # 是否热门分类
    icon_image = models.ImageField(
        upload_to='category_icons/', 
        blank=True, 
        null=True,
        help_text='分类图标图片，建议尺寸：64x64px 或 128x128px，支持 PNG、SVG 格式'
    )
    created_at = models.DateTimeField(auto_now_add=True)  # 新增字段

    # 新增自关联外键（用于子分类）
    parent = models.ForeignKey(
        'self',  # 指向自身模型
        null=True,  # 允许一级分类无父级
        blank=True,
        on_delete=models.CASCADE,
        related_name='subcategories'  # 反向关联名（通过 parent.subcategories 访问子分类）
    )

    def __str__(self):
        return self.name