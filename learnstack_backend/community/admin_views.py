from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Question, Answer
from .serializers import QuestionSerializer, AnswerSerializer, QuestionListSerializer


class AdminQuestionListView(generics.ListAPIView):
    """管理员获取问题列表"""
    queryset = Question.objects.all().order_by('-created_at')
    serializer_class = QuestionListSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        
        if search:
            queryset = queryset.filter(
                title__icontains=search
            ) | queryset.filter(
                description__icontains=search
            ) | queryset.filter(
                content__icontains=search
            ).distinct()
        
        return queryset


class AdminQuestionDetailView(generics.RetrieveDestroyAPIView):
    """管理员获取、删除问题详情"""
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminAnswerListView(generics.ListAPIView):
    """管理员获取回答列表"""
    queryset = Answer.objects.all().order_by('-created_at')
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        question_id = self.request.query_params.get('question_id', None)
        search = self.request.query_params.get('search', None)
        
        if question_id:
            queryset = queryset.filter(question_id=question_id)
        
        if search:
            queryset = queryset.filter(content__icontains=search)
        
        return queryset


class AdminAnswerDetailView(generics.RetrieveDestroyAPIView):
    """管理员获取、删除回答详情"""
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAdminUser]

