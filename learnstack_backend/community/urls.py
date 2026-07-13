from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuestionViewSet, AnswerViewSet, CommunityReportViewSet
from .admin_views import (
    AdminQuestionListView,
    AdminQuestionDetailView,
    AdminAnswerListView,
    AdminAnswerDetailView
)

router = DefaultRouter()
router.register(r'questions', QuestionViewSet)
router.register(r'answers', AnswerViewSet)
router.register(r'reports', CommunityReportViewSet, basename='community-report')

urlpatterns = [
    path('', include(router.urls)),
    # Admin endpoints
    path('admin/questions/', AdminQuestionListView.as_view(), name='admin-question-list'),
    path('admin/questions/<int:pk>/', AdminQuestionDetailView.as_view(), name='admin-question-detail'),
    path('admin/answers/', AdminAnswerListView.as_view(), name='admin-answer-list'),
    path('admin/answers/<int:pk>/', AdminAnswerDetailView.as_view(), name='admin-answer-detail'),
]