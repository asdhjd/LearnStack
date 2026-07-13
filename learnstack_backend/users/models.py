from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # 恢复username字段（Django默认字段，无需显式定义，但需设为必填）
    email = models.EmailField(blank=True, null=True, verbose_name='邮箱')  # 邮箱可选
    nickname = models.CharField(max_length=150, blank=True, verbose_name='昵称')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    # 登录凭证
    USERNAME_FIELD = 'username'  #使用用户名登录
    REQUIRED_FIELDS = [] 

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'