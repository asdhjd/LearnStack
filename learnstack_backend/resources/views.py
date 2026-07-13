from rest_framework import generics, permissions, status, pagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from django.http import StreamingHttpResponse, HttpResponse
from .models import Resource, ResourceRequest
import os
from .serializers import (
    ResourceDetailSerializer,
    ResourceSubmissionSerializer,
    ResourceSummarySerializer,
    ResourceRequestSerializer,
    ResourceRequestCreateSerializer,
)
from .utils import get_article_content

class ResourcePagination(pagination.PageNumberPagination):
    """资源列表分页类"""
    page_size = 12  # 每页显示的资源数量
    page_size_query_param = 'page_size'  # 允许客户端通过查询参数指定每页大小
    max_page_size = 100  # 客户端最大可请求的每页大小

class ResourceListView(generics.ListAPIView):
    """
    获取资源列表的API视图
    支持搜索功能：根据标题、描述、分类进行搜索
    支持分页功能
    """
    queryset = Resource.objects.filter(status='approved').order_by('-created_at')
    serializer_class = ResourceSummarySerializer
    pagination_class = ResourcePagination  # 使用自定义分页类
    
    def get_queryset(self):
        """
        重写get_queryset方法，添加搜索过滤功能
        """
        queryset = super().get_queryset()
        # 获取搜索参数
        search_query = self.request.query_params.get('search', '').strip()
        if search_query:
            # 使用Q对象进行多字段搜索
            from django.db.models import Q
            
            # 搜索标题、描述、分类名称
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(categories__name__icontains=search_query)
            ).distinct()

        return queryset

    def get_serializer_context(self):
        """传递request context给序列化器"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class ResourceDetailView(generics.RetrieveAPIView):
    """
    获取单个资源详情的API视图
    """
    queryset = Resource.objects.filter(status='approved')
    
    def get_serializer_context(self):
        """传递request context给序列化器"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    serializer_class = ResourceDetailSerializer


class ResourceSubmissionView(generics.CreateAPIView):
    """
    用户投稿资源的API视图
    支持文件上传（使用multipart/form-data）
    """
    from rest_framework.parsers import MultiPartParser, JSONParser
    serializer_class = ResourceSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]  # 支持文件上传和JSON
    
    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)


class ResourceModerationListView(generics.ListAPIView):
    """
    管理员查看所有资源的API视图
    普通用户可以通过此API查看自己投稿的资源
    """
    serializer_class = ResourceDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Resource.objects.all().order_by('-created_at')
        # 如果用户不是管理员，只返回自己投稿的资源
        if not self.request.user.is_superuser:
            queryset = queryset.filter(submitted_by=self.request.user)
        return queryset


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def approve_resource(request, resource_id):
    """
    管理员审核通过资源
    """
    try:
        resource = Resource.objects.get(id=resource_id, status='pending')
        resource.status = 'approved'
        resource.reviewed_by = request.user
        resource.reviewed_at = timezone.now()
        # 允许管理员添加反馈
        admin_notes = request.data.get('admin_notes', '')
        if admin_notes:
            resource.admin_notes = admin_notes
        resource.save()
        
        return Response({
            'success': True,
            'message': '资源审核通过'
        })
    except Resource.DoesNotExist:
        return Response({
            'error': '资源不存在或已审核'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def reject_resource(request, resource_id):
    """
    管理员拒绝资源
    """
    try:
        resource = Resource.objects.get(id=resource_id, status='pending')
        resource.status = 'rejected'
        resource.reviewed_by = request.user
        resource.reviewed_at = timezone.now()
        # 允许管理员添加反馈（拒绝时建议添加拒绝原因）
        admin_notes = request.data.get('admin_notes', '')
        if admin_notes:
            resource.admin_notes = admin_notes
        resource.save()
        
        return Response({
            'success': True,
            'message': '资源已拒绝'
        })
    except Resource.DoesNotExist:
        return Response({
            'error': '资源不存在或已审核'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def fetch_article_content(request):
    """
    从URL抓取文章内容（用户投稿时使用）
    """
    url = request.data.get('url')
    if not url:
        return Response({
            'success': False,
            'error': '请提供URL'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        result = get_article_content(url)
        return Response(result)
    except Exception as e:
        return Response({
            'success': False,
            'error': f'抓取内容失败: {str(e)}',
            'title': '',
            'content': '',
            'cover': ''
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def fetch_bilibili_sections(request):
    """
    从Bilibili视频URL抓取章节信息（用户投稿课程时使用）
    """
    import re
    import requests
    
    url = request.data.get('url')
    if not url:
        return Response({
            'success': False,
            'error': '请提供Bilibili视频URL'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 提取BV号
        bv_match = re.search(r'BV[a-zA-Z0-9]+', url)
        if not bv_match:
            return Response({
                'success': False,
                'error': '无法从URL中提取BV号'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        bvid = bv_match.group(0)
        
        # 使用Bilibili API获取视频信息
        api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': f'https://www.bilibili.com/video/{bvid}'
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return Response({
                'success': False,
                'error': '无法访问Bilibili API'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = response.json()
        if data.get('code') != 0:
            return Response({
                'success': False,
                'error': data.get('message', '获取视频信息失败')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        video_data = data.get('data', {})
        pages = video_data.get('pages', [])
        
        if not pages:
            return Response({
                'success': False,
                'error': '该视频没有章节信息'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        sections = []
        for page in pages:
            page_num = page.get('page', 1)
            title = page.get('part', '')
            
            # 构建视频URL
            if page_num == 1:
                video_url = f"https://www.bilibili.com/video/{bvid}"
            else:
                video_url = f"https://www.bilibili.com/video/{bvid}?p={page_num}"
            
            # 构建嵌入URL
            embed_url = f"https://player.bilibili.com/player.html?bvid={bvid}&page={page_num}"
            
            sections.append({
                'title': title,
                'summary': '',
                'video_url': video_url,
                'embed_url': embed_url
            })
        
        return Response({
            'success': True,
            'sections': sections
        })
            
    except Exception as e:
        return Response({
            'success': False,
            'error': f'抓取Bilibili章节失败: {str(e)}',
            'sections': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import base64
import json

@csrf_exempt
@require_http_methods(["POST"])  # 只允许 POST，避免 IDM 识别 GET 下载
def download_resource_file(request, resource_id):
    """
    下载资源文件的接口（伪装成普通 API，避免 IDM 拦截）
    使用 POST + JSON 响应 + Base64 编码，让 IDM 无法识别为文件下载
    """
    try:
        # 获取资源
        resource = Resource.objects.get(id=resource_id, status='approved')
        
        # 检查是否有服务器存储的文件
        if not resource.content or not resource.content.book_file:
            return HttpResponse(
                json.dumps({'error': '该资源没有可下载的文件'}),
                status=404,
                content_type='application/json; charset=utf-8'
            )
        
        file_path = resource.content.book_file.path
        if not os.path.exists(file_path):
            return HttpResponse(
                json.dumps({'error': '文件不存在'}),
                status=404,
                content_type='application/json; charset=utf-8'
            )
        
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # 读取文件并转换为 Base64（对于大文件，可以考虑分块传输）
        # 为了性能，如果文件太大（>50MB），使用流式 Base64 编码
        max_size_for_direct = 50 * 1024 * 1024  # 50MB
        
        if file_size > max_size_for_direct:
            # 大文件：返回文件信息和下载令牌，前端分块请求
            import hashlib
            import time
            # 生成临时下载令牌（实际应用中应该使用更安全的机制）
            token = hashlib.md5(f"{resource_id}_{filename}_{time.time()}".encode()).hexdigest()
            
            return HttpResponse(
                json.dumps({
                    'success': True,
                    'filename': filename,
                    'size': file_size,
                    'chunked': True,
                    'token': token,
                    'chunk_size': 1024 * 1024,  # 1MB per chunk
                }),
                content_type='application/json; charset=utf-8'
            )
        else:
            # 小文件：直接返回 Base64 编码的文件内容
            with open(file_path, 'rb') as f:
                file_data = f.read()
                file_base64 = base64.b64encode(file_data).decode('utf-8')
            
            # 返回 JSON 格式，伪装成普通 API 响应
            response_data = {
                'success': True,
                'data': file_base64,  # Base64 编码的文件数据
                'filename': filename,
                'size': file_size,
                'type': 'file_data'  # 标识这是文件数据
            }
            
            return HttpResponse(
                json.dumps(response_data),
                content_type='application/json; charset=utf-8'  # 伪装成 JSON API
            )
        
    except Resource.DoesNotExist:
        return HttpResponse(
            json.dumps({'error': '资源不存在'}),
            status=404,
            content_type='application/json; charset=utf-8'
        )
    except Exception as e:
        return HttpResponse(
            json.dumps({'error': f'服务器错误: {str(e)}'}),
            status=500,
            content_type='application/json; charset=utf-8'
        )


class ResourceRequestListView(generics.ListCreateAPIView):
    """
    资源添加申请列表和创建API
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # 普通用户只能看到自己的申请
        if self.request.user.is_superuser:
            return ResourceRequest.objects.all().order_by('-created_at')
        return ResourceRequest.objects.filter(requested_by=self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ResourceRequestCreateSerializer
        return ResourceRequestSerializer
    
    def perform_create(self, serializer):
        # requested_by 已经在序列化器的 create 方法中设置，这里不需要重复设置
        serializer.save()


class AdminResourceRequestListView(generics.ListAPIView):
    """
    管理员查看所有资源添加申请的API视图
    """
    queryset = ResourceRequest.objects.all().order_by('-created_at')
    serializer_class = ResourceRequestSerializer
    permission_classes = [permissions.IsAdminUser]


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def update_resource_request_status(request, request_id):
    """
    管理员更新申请状态
    """
    try:
        resource_request = ResourceRequest.objects.get(id=request_id)
        new_status = request.data.get('status')
        admin_notes = request.data.get('admin_notes', '')
        
        if new_status not in ['pending', 'processing', 'completed', 'rejected']:
            return Response({
                'error': '无效的状态值'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        resource_request.status = new_status
        resource_request.processed_by = request.user
        resource_request.processed_at = timezone.now()
        if admin_notes:
            resource_request.admin_notes = admin_notes
        resource_request.save()
        
        return Response({
            'success': True,
            'message': '申请状态已更新',
            'data': ResourceRequestSerializer(resource_request).data
        })
    except ResourceRequest.DoesNotExist:
        return Response({
            'error': '申请不存在'
        }, status=status.HTTP_404_NOT_FOUND)