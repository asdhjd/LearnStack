from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer
from django.contrib.auth import authenticate
from rest_framework.parsers import MultiPartParser
import logging

logger = logging.getLogger(__name__)

class RegisterAPIView(generics.CreateAPIView):
    """用户注册接口"""
    serializer_class = RegisterSerializer
    permission_classes = []  # 公开接口
    
    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            logger.info(f'User registration successful: {request.data.get("username")}')
            return response
        except Exception as e:
            logger.error(f'User registration failed: {str(e)}')
            return Response(
                {'error': f'注册失败: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class UserMeView(generics.RetrieveUpdateAPIView):
    """当前用户信息接口"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]  # 新增：配置文件解析器

    def get_object(self):
        return self.request.user  # 返回当前登录用户


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer  # 关键修改：使用登录专用序列化器
    permission_classes = []  # 登录接口公开

    def post(self, request, *args, **kwargs):
        username = request.data.get('username', '')  # 获取用户名
        password = request.data.get('password', '')  # 获取密码（关键字段）
        user = authenticate(username=username, password=password)  # 使用用户名+密码认证
        if user:
            logger.info(f'User {username} authenticated successfully')
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        logger.warning(f'No active account found for Username: {username}')
        return Response({'error': '无效的用户名或密码'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """修改密码接口"""
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    
    if not old_password or not new_password:
        return Response(
            {'error': '请提供旧密码和新密码'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(new_password) < 6:
        return Response(
            {'error': '新密码长度至少为6位'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = request.user
    
    # 验证旧密码
    if not user.check_password(old_password):
        return Response(
            {'error': '旧密码不正确'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 设置新密码
    user.set_password(new_password)
    user.save()
    
    logger.info(f'User {user.username} changed password successfully')
    return Response(
        {'message': '密码修改成功'}, 
        status=status.HTTP_200_OK
    )