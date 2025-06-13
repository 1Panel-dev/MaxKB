"""
URL configuration for maxkb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.http import HttpResponse
from django.urls import path, re_path, include
from django.views import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework import status

from common.result import Result
from maxkb import settings
from maxkb.conf import PROJECT_DIR

urlpatterns = [
    path("api/", include("users.urls")),
    path("api/", include("tools.urls")),
    path("api/", include("models_provider.urls")),
    path("api/", include("folders.urls")),
    path("api/", include("knowledge.urls")),
    path("api/", include("system_manage.urls")),
    path("api/", include("application.urls")),
    path("chat/api/", include("chat.urls")),
    path('oss/', include('oss.urls')),
]
urlpatterns += [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),  # schema的配置文件的路由，下面两个ui也是根据这个配置文件来生成的
    path('doc/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),  # swagger-ui的路由
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),  # redoc的路由
]
urlpatterns.append(
    re_path(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT}, name='static'),
)


def pro():
    # 暴露静态主要是swagger资源
    urlpatterns.append(
        re_path(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT}, name='static'),
    )
    # 暴露ui静态资源
    urlpatterns.append(
        re_path(r'^ui/(?P<path>.*)$', static.serve, {'document_root': os.path.join(settings.STATIC_ROOT, "ui")},
                name='ui'),
    )
    # 暴露ui静态资源
    urlpatterns.append(
        re_path(r'^chat/(?P<path>.*)$', static.serve, {'document_root': os.path.join(settings.STATIC_ROOT, "chat")},
                name='chat'),
    )


if not settings.DEBUG:
    pro()


def get_index_html(index_path):
    file = open(index_path, "r", encoding='utf-8')
    content = file.read()
    file.close()
    return content


def page_not_found(request, exception):
    """
    页面不存在处理
    """
    if request.path.startswith("/api/"):
        return Result(response_status=status.HTTP_404_NOT_FOUND, code=404, message="HTTP_404_NOT_FOUND")
    if request.path.startswith("/chat/api/"):
        return Result(response_status=status.HTTP_404_NOT_FOUND, code=404, message="HTTP_404_NOT_FOUND")
    if request.path.startswith('/chat'):
        index_path = os.path.join(PROJECT_DIR, 'apps', "static", 'chat', 'index.html')
    else:
        index_path = os.path.join(PROJECT_DIR, 'apps', "static", 'ui', 'index.html')
    if not os.path.exists(index_path):
        return HttpResponse("页面不存在", status=404)
    content = get_index_html(index_path)
    return HttpResponse(content, status=200)


handler404 = page_not_found
