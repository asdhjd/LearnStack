from django.db import models
from categories.models import TechnologyCategory
from users.models import CustomUser


def default_list():
    return []


def default_dict():
    return {}


class Resource(models.Model):
    RESOURCE_TYPE_CHOICES = [
        ('book', '书籍'),
        ('course', '课程'),
        ('article', '文章'),
        ('project', '项目'),
        ('tool', '工具'),
        ('document', '文档')
    ]

    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    ]

    CONTENT_SOURCE_CHOICES = [
        ('original', '站内原创/上传'),
        ('embedded', '外部导入')
    ]

    TARGET_AUDIENCE_CHOICES = [
        ('beginner', '入门阶段'),
        ('intermediate', '中级阶段'),
        ('advanced', '高级阶段'),
    ]

    title = models.CharField(max_length=200, verbose_name="资源名称")
    description = models.TextField(blank=True, verbose_name="资源描述")
    url = models.URLField(blank=True, verbose_name="资源链接")
    resource_type = models.CharField(
        max_length=20,
        choices=RESOURCE_TYPE_CHOICES,
        default='book',
        verbose_name="资源类型"
    )
    rating = models.PositiveIntegerField(default=0, verbose_name="评分（1-5）")  # 保留评分
    target_audience = models.CharField(
        max_length=20,
        choices=TARGET_AUDIENCE_CHOICES,
        blank=True,
        verbose_name="适用人群"
    )
    content_source = models.CharField(
        max_length=20,
        choices=CONTENT_SOURCE_CHOICES,
        default='original',
        verbose_name="内容来源"
    )
    hero_cover = models.URLField(blank=True, verbose_name="封面图")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    # 投稿相关字段
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='approved',
        verbose_name="审核状态"
    )
    submitted_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="投稿人",
        related_name='submitted_resources'
    )
    reviewed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="审核人",
        related_name='reviewed_resources'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="审核时间")
    admin_notes = models.TextField(blank=True, verbose_name="管理员反馈", help_text="管理员审核时的反馈意见")

    categories = models.ManyToManyField(
        TechnologyCategory,
        verbose_name="关联技术分类",
        related_name='related_resources'
    )

    def __str__(self):
        return self.title


class ResourceContent(models.Model):
    BODY_FORMAT_CHOICES = [
        ('markdown', 'Markdown'),
        ('html', 'HTML'),
        ('plaintext', '纯文本'),
    ]

    resource = models.OneToOneField(
        Resource,
        related_name='content',
        on_delete=models.CASCADE,
        verbose_name="资源"
    )
    body_markdown = models.TextField(blank=True, verbose_name="正文 Markdown")
    body_html = models.TextField(blank=True, verbose_name="正文 HTML")
    body_format = models.CharField(
        max_length=20,
        choices=BODY_FORMAT_CHOICES,
        default='markdown',
        verbose_name="正文格式"
    )
    sections = models.JSONField(default=default_list, blank=True, verbose_name="章节/目录结构")
    embed_provider = models.CharField(max_length=50, blank=True, verbose_name="嵌入提供方")
    embed_url = models.URLField(blank=True, verbose_name="嵌入地址")
    embed_meta = models.JSONField(default=default_dict, blank=True, verbose_name="嵌入元信息")
    document_html = models.TextField(blank=True, verbose_name="文档 HTML")
    document_toc = models.JSONField(default=default_list, blank=True, verbose_name="文档目录")
    download_url = models.URLField(blank=True, verbose_name="下载链接")
    # 书籍文件字段（存储在服务器）
    book_file = models.FileField(
        upload_to='books/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="书籍文件",
        help_text="支持PDF、EPUB、MOBI等格式"
    )
    extra_links = models.JSONField(default=default_list, blank=True, verbose_name="附加链接")
    extra_data = models.JSONField(default=default_dict, blank=True, verbose_name="扩展数据")
    last_synced_at = models.DateTimeField(null=True, blank=True, verbose_name="最后同步时间")

    class Meta:
        verbose_name = "资源内容"
        verbose_name_plural = "资源内容"

    def __str__(self):
        return f"{self.resource.title} 内容"


class ResourceRequest(models.Model):
    """用户申请管理员添加资源的请求"""
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('rejected', '已拒绝'),
    ]
    
    RESOURCE_TYPE_CHOICES = [
        ('book', '书籍'),
        ('course', '课程'),
        ('article', '文章'),
        ('project', '项目'),
        ('tool', '工具'),
        ('document', '文档')
    ]
    
    # 申请人信息
    requested_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="申请人",
        related_name='resource_requests'
    )
    
    # 资源基本信息
    title = models.CharField(max_length=200, verbose_name="资源标题")
    description = models.TextField(blank=True, verbose_name="资源描述")
    url = models.URLField(verbose_name="资源链接")
    resource_type = models.CharField(
        max_length=20,
        choices=RESOURCE_TYPE_CHOICES,
        verbose_name="资源类型"
    )
    target_audience = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="适用人群"
    )
    
    # 申请原因
    reason = models.TextField(verbose_name="申请理由", help_text="说明为什么无法使用自动抓取功能")
    
    # 状态和审核信息
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="处理状态"
    )
    processed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="处理人",
        related_name='processed_requests'
    )
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="处理时间")
    admin_notes = models.TextField(blank=True, verbose_name="管理员备注")
    
    # 如果申请被处理并创建了资源，关联到资源
    created_resource = models.ForeignKey(
        Resource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="创建的资源",
        related_name='source_request'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="申请时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "资源添加申请"
        verbose_name_plural = "资源添加申请"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"