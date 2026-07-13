from django.contrib import admin
from .models import TechnologyCategory  # 导入模型

admin.site.register(TechnologyCategory)  # 注册模型到管理后台