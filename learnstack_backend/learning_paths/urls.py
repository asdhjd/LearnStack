from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LearningPathViewSet

router = DefaultRouter()
router.register(r'paths', LearningPathViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # 额外的学习路径API路由可以在这里添加
]