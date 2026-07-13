from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/categories/', include('categories.urls')),
    path('api/resources/', include('resources.urls')),
    path('api/users/', include('users.urls')),
    path('api/favorites/', include('favorites.urls')),
    path('api/learningpaths/', include('learning_paths.urls')),
    path('api/community/', include('community.urls')),
    # JWT token刷新端点
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
