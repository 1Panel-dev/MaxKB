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

from django.http import HttpResponse,HttpResponseRedirect
from django.urls import path, re_path, include
from django.views import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework import status

from common.result import Result
from maxkb import settings
from maxkb.conf import PROJECT_DIR
from maxkb.const import CONFIG

admin_api_prefix = CONFIG.get_admin_path()[1:] + '/api/'
admin_ui_prefix = CONFIG.get_admin_path()
chat_api_prefix = CONFIG.get_chat_path()[1:] + '/api/'
chat_ui_prefix = CONFIG.get_chat_path()
urlpatterns = [
    path(admin_api_prefix, include("users.urls")),
    path(admin_api_prefix, include("tools.urls")),
    path(admin_api_prefix, include("models_provider.urls")),
    path(admin_api_prefix, include("folders.urls")),
    path(admin_api_prefix, include("knowledge.urls")),
    path(admin_api_prefix, include("system_manage.urls")),
    path(admin_api_prefix, include("application.urls")),
    path(chat_api_prefix, include("chat.urls")),
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
        re_path(rf"^{CONFIG.get_admin_path()[1:]}/(?P<path>.*)$", static.serve,
                {'document_root': os.path.join(settings.STATIC_ROOT, "admin")},
                name='admin'),
    )
    # 暴露ui静态资源
    urlpatterns.append(
        re_path(rf'^{CONFIG.get_chat_path()[1:]}/(?P<path>.*)$', static.serve,
                {'document_root': os.path.join(settings.STATIC_ROOT, "chat")},
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
    if request.path.startswith(admin_ui_prefix + '/api/'):
        return Result(response_status=status.HTTP_404_NOT_FOUND, code=404, message="HTTP_404_NOT_FOUND")
    if request.path.startswith(chat_ui_prefix + '/api/'):
        return Result(response_status=status.HTTP_404_NOT_FOUND, code=404, message="HTTP_404_NOT_FOUND")
    if request.path.startswith(chat_ui_prefix):
        index_path = os.path.join(PROJECT_DIR, 'apps', "static", 'chat', 'index.html')
        content = get_index_html(index_path)
        content.replace("prefix: '/chat'", f"prefix: {CONFIG.get_chat_path()}")
        if not os.path.exists(index_path):
            return HttpResponse("页面不存在", status=404)
        return HttpResponse(content, status=200)
    elif request.path.startswith(admin_ui_prefix):
        index_path = os.path.join(PROJECT_DIR, 'apps', "static", 'admin', 'index.html')
        if not os.path.exists(index_path):
            return HttpResponse("页面不存在", status=404)
        content = get_index_html(index_path)
        content = content.replace("prefix: '/admin'", f"prefix: '{CONFIG.get_admin_path()}'")
        return HttpResponse(content, status=200)
    else:
        return HttpResponseRedirect(admin_ui_prefix+'/')


handler404 = page_not_found
