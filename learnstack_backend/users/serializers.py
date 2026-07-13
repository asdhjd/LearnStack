from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)  # 密码最小长度限制
    username = serializers.CharField(required=True, max_length=150)  # 新增：用户名必填
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)  # 邮箱可选
    is_superuser = serializers.BooleanField(default=False, required=False)  # 添加管理员权限字段，默认为False

    class Meta:
        model = User
        # 包含用户名（必填）、邮箱（可选）、密码（必填）和管理员权限
        fields = ('username', 'email', 'password', 'is_superuser')  
    
    def validate_username(self, value):
        # 验证用户名唯一性
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("该用户名已被使用，请选择其他用户名")
        return value
    
    def validate_email(self, value):
        # 如果邮箱为空字符串，返回None
        if value == '':
            return None
        return value

    def create(self, validated_data):
        # 提取管理员权限标志
        is_superuser = validated_data.pop('is_superuser', False)
        
        # 提取并处理邮箱（如果为空字符串或None，不传递该字段）
        email = validated_data.pop('email', None)
        if email in ['', None]:
            email = None
        
        # 使用用户名创建用户（邮箱可选）
        # 如果email为None，create_user会自动处理
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=email
        )
        
        # 设置管理员权限
        user.is_superuser = is_superuser
        user.save()
        
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # 合并字段声明，包含昵称、头像和管理员状态以及注册时间
        fields = ('id', 'username', 'email', 'nickname', 'avatar', 'is_superuser', 'date_joined')  # 添加date_joined字段
        

class LoginSerializer(serializers.Serializer):
    """登录专用序列化器，明确要求 username 和 password"""
    username = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(required=True, write_only=True, min_length=6)