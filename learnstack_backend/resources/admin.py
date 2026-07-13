from django.contrib import admin
from .models import Resource, ResourceContent, ResourceRequest
from categories.models import TechnologyCategory


class ResourceContentInline(admin.StackedInline):
    model = ResourceContent
    extra = 0
    min_num = 0
    max_num = 1
    can_delete = True
    fieldsets = (
        ('正文内容', {
            'fields': ('body_format', 'body_markdown', 'body_html'),
            'description': '📝 用于存储书籍、文章、项目、工具等资源的正文内容。\n\n⚠️ 重要区分：\n- **正文内容**：用于书籍、文章、项目、工具、课程介绍\n- **文档内容**：仅用于文档类型（document），见下方"文档内容"字段\n\n使用说明：\n1. **正文格式**：选择内容格式\n   - Markdown：填写 Markdown 格式的内容（会自动转换为 HTML）\n   - HTML：填写 HTML 格式的内容（直接显示）\n   - 纯文本：填写纯文本内容（会自动格式化，识别标题、列表、标签等）\n\n2. **正文 Markdown**：填写 Markdown 格式的内容（当格式选择为 Markdown 时使用）\n\n3. **正文 HTML**：填写 HTML 格式的内容（当格式选择为 HTML 时使用）\n\n💡 提示：\n- 系统优先使用"正文 HTML"，如果没有则使用"正文 Markdown"\n- 如果选择"纯文本"格式，系统会自动识别并格式化内容（如标题、列表、标签行等）\n- **文章类型**使用此字段，不是"文档内容"字段'
        }),
        ('嵌入内容（主要用于文档）', {
            'fields': ('embed_provider', 'embed_url'),
            'classes': ('collapse',),
            'description': '⚠️ 注意：视频内容请使用下方的"课程章节"字段添加，不要使用此字段。\n\n此字段主要用于嵌入外部文档（如 Ant Design、React 等官方文档）：\n- embed_provider 填写如: antd, react, vue 等文档提供方名称\n- embed_url 填写完整的文档页面 URL（如 https://ant.design/docs/react/getting-started-cn）\n\n视频内容请通过"课程章节"字段添加 JSON 数据来管理。'
        }),
        ('文档内容', {
            'fields': ('document_html', 'document_toc'),
            'classes': ('collapse',),
            'description': '📄 仅用于文档类型（document）资源。\n\n⚠️ 重要区分：\n- **文档内容**：仅用于文档类型（document）\n- **正文内容**：用于书籍、文章、项目、工具、课程介绍\n\n使用说明：\n\n1. **文档 HTML**：\n   - 填写完整的 HTML 内容（包括标题、段落、代码块等）\n   - 可以直接粘贴从网页复制的 HTML 代码\n   - 或者手动编写 HTML，例如：\n   ```html\n   <h1>Jupyter Notebook 入门教程</h1>\n   <p>Jupyter notebook 是一个很强大的交互式工具...</p>\n   <h2>1. 安装</h2>\n   <p>最简单的安装方式就是通过 Anaconda...</p>\n   <pre><code class="language-shell">pip install jupyter</code></pre>\n   ```\n\n2. **文档目录**（JSON 格式）：\n   - 用于生成左侧导航目录\n   - 格式示例：\n   ```json\n   [\n     {\n       "id": "installation",\n       "title": "1. 安装",\n       "level": 1\n     },\n     {\n       "id": "first-notebook",\n       "title": "2. 创建你的第一个 Notebook",\n       "level": 1,\n       "children": [\n         {\n           "id": "run-jupyter",\n           "title": "运行 Jupyter",\n           "level": 2\n         },\n         {\n           "id": "ipynb-file",\n           "title": "ipynb 文件",\n           "level": 2\n         }\n       ]\n     }\n   ]\n   ```\n   - `id`：用于跳转的锚点 ID（必填，建议使用英文）\n   - `title`：目录标题（必填）\n   - `level`：标题层级，1=h1, 2=h2, 3=h3（必填）\n   - `children`：子目录（可选）\n\n💡 提示：\n- 文档 HTML 中的标题会自动添加 id（基于 document_toc）\n- 如果 HTML 中已有 id，会优先使用\n- 文章类型应使用"正文内容"字段，不要使用此字段\n- 文档类型优先使用此字段，如果没有则使用 embed_url 嵌入外部文档'
        }),
        ('iframe 裁剪配置（仅嵌入中间部分）', {
            'fields': (),
            'classes': ('collapse',),
            'description': '如果使用 embed_url 嵌入外部文档，可以在"扩展数据"字段中添加 iframe_clip 配置来只显示中间部分（隐藏导航栏和页脚）。\n\n配置示例：\n{\n  "iframe_clip": {\n    "height": "800px",        // 容器显示高度（中间部分的高度）\n    "marginTop": "-80px",    // 向上偏移，隐藏顶部导航栏（负值）\n    "marginBottom": "-200px", // 底部要隐藏的高度（负值，用于计算 iframe 总高度）\n    "iframeHeight": "1080px" // iframe 总高度（可选，不填会自动计算）\n  }\n}\n\n工作原理：\n1. 容器高度固定为 height（如 800px）\n2. iframe 高度为 height + |marginTop| + |marginBottom|（如 800 + 80 + 200 = 1080px）\n3. iframe 通过 marginTop 向上移动，隐藏顶部导航栏\n4. 容器使用 overflow: hidden 自动裁剪底部页脚\n\n这样就能只显示网页的中间内容部分。'
        }),
        ('下载与链接', {
            'fields': ('download_url',),
            'classes': ('collapse',),
            'description': 'download_url 用于书籍、项目、工具等资源的下载链接'
        }),
        ('课程章节（视频内容）', {
            'fields': ('sections',),
            'classes': ('collapse',),
            'description': '📹 用于添加课程视频的章节结构（JSON 格式）。\n\n示例格式：\n[\n  {\n    "title": "第一章：Python基础",\n    "summary": "介绍Python基本语法",\n    "video_url": "https://www.bilibili.com/video/BV1gq1sBPECH?p=1",\n    "embed_url": "https://player.bilibili.com/player.html?bvid=BV1gq1sBPECH&page=1"\n  },\n  {\n    "title": "第二章：数据类型",\n    "summary": "学习Python数据类型",\n    "video_url": "https://www.bilibili.com/video/BV1gq1sBPECH?p=2",\n    "embed_url": "https://player.bilibili.com/player.html?bvid=BV1gq1sBPECH&page=2"\n  }\n]\n\n说明：\n- title: 章节标题（必填）\n- summary: 章节简介（可选）\n- video_url: 视频原始链接（可选，用于显示）\n- embed_url: 视频嵌入链接（必填，用于播放）\n- 每个章节可以有自己的视频链接，系统会自动在课程页面显示章节列表和视频播放器'
        }),
        ('高级选项', {
            'fields': ('embed_meta', 'extra_links', 'extra_data', 'last_synced_at'),
            'classes': ('collapse',),
            'description': '这些字段为 JSON 格式，请使用有效的 JSON 语法'
        }),
    )


class ResourceAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'title',
        'resource_type',
        'rating',
        'target_audience',
        'content_source',
        'status',
        'created_at'
    ]
    list_filter = [
        'resource_type', 
        'status',
        'content_source',
        'created_at'
    ]
    search_fields = ['title', 'description', 'target_audience']
    ordering = ['-created_at']
    inlines = [ResourceContentInline]
    filter_horizontal = ['categories']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'description', 'resource_type', 'url', 'rating', 'target_audience'),
            'description': '适用人群选项：入门阶段、中级阶段、高级阶段'
        }),
        ('内容来源', {
            'fields': ('content_source', 'hero_cover')
        }),
        ('分类', {
            'fields': ('categories',)
        }),
        ('审核信息', {
            'fields': ('status', 'submitted_by', 'reviewed_by', 'reviewed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        重写方法，限制分类选择只显示子分类（parent不为空的分类）
        """
        if db_field.name == 'categories':
            # 只显示子分类（parent不为空的分类）
            kwargs['queryset'] = TechnologyCategory.objects.filter(parent__isnull=False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(ResourceContent)
class ResourceContentAdmin(admin.ModelAdmin):
    list_display = ['resource', 'body_format', 'embed_provider', 'last_synced_at']
    search_fields = ['resource__title', 'embed_provider']
    list_filter = ['body_format', 'embed_provider']
    readonly_fields = ['last_synced_at']
    
    fieldsets = (
        ('正文内容', {
            'fields': ('resource', 'body_format', 'body_markdown', 'body_html')
        }),
        ('嵌入内容（主要用于文档）', {
            'fields': ('embed_provider', 'embed_url', 'embed_meta'),
            'classes': ('collapse',),
            'description': '⚠️ 注意：视频内容请使用"课程章节"字段添加，不要使用此字段。\n\n此字段主要用于嵌入外部文档（如 Ant Design、React 等官方文档）：\n- embed_provider 填写如: antd, react, vue 等文档提供方名称\n- embed_url 填写完整的文档页面 URL\n- embed_meta 存储嵌入相关的元信息（JSON 格式）'
        }),
        ('文档内容', {
            'fields': ('document_html', 'document_toc'),
            'classes': ('collapse',)
        }),
        ('下载与链接', {
            'fields': ('download_url', 'extra_links'),
            'classes': ('collapse',)
        }),
        ('课程章节', {
            'fields': ('sections',),
            'classes': ('collapse',)
        }),
        ('其他', {
            'fields': ('extra_data', 'last_synced_at'),
            'classes': ('collapse',)
        }),
    )


admin.site.register(Resource, ResourceAdmin)


@admin.register(ResourceRequest)
class ResourceRequestAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'title', 'resource_type', 'requested_by', 
        'status', 'created_at', 'processed_by'
    ]
    list_filter = ['status', 'resource_type', 'created_at']
    search_fields = ['title', 'description', 'url', 'reason']
    readonly_fields = ['requested_by', 'created_at', 'updated_at']
    fieldsets = (
        ('申请信息', {
            'fields': ('requested_by', 'title', 'description', 'url', 'resource_type', 'target_audience', 'reason')
        }),
        ('处理信息', {
            'fields': ('status', 'processed_by', 'processed_at', 'admin_notes', 'created_resource')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            if obj.status in ['processing', 'completed', 'rejected']:
                obj.processed_by = request.user
                from django.utils import timezone
                obj.processed_at = timezone.now()
        super().save_model(request, obj, form, change)