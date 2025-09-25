# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： init_doc.py
    @date：2024/5/24 14:11
    @desc:
"""
import hashlib

from django.urls import path, URLPattern
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from maxkb.const import CONFIG

chat_api_prefix = CONFIG.get_chat_path()[1:] + '/api/'


def init_app_doc(system_urlpatterns):
    system_urlpatterns += [
        path(f'{CONFIG.get_admin_path()[1:]}/api-doc/schema/', SpectacularAPIView.as_view(), name='schema'),
        # schema的配置文件的路由，下面两个ui也是根据这个配置文件来生成的
        path(f'{CONFIG.get_admin_path()[1:]}/api-doc/', SpectacularSwaggerView.as_view(url_name='schema'),
             name='swagger-ui'),  # swagger-ui的路由
    ]


class ChatSpectacularSwaggerView(SpectacularSwaggerView):
    @staticmethod
    def _swagger_ui_resource(filename):
        return f'{CONFIG.get_chat_path()}/api-doc/swagger-ui-dist/{filename}'

    @staticmethod
    def _swagger_ui_favicon():
        return f'{CONFIG.get_chat_path()}/api-doc/swagger-ui-dist/favicon-32x32.png'


def init_chat_doc(system_urlpatterns, chat_urlpatterns):
    system_urlpatterns += [
        path(f'{CONFIG.get_chat_path()[1:]}/api-doc/schema/',
             SpectacularAPIView.as_view(patterns=[
                 URLPattern(pattern=f'{chat_api_prefix}{str(url.pattern)}', callback=url.callback,
                            default_args=url.default_args,
                            name=url.name) for url in chat_urlpatterns if
                 ['chat', 'open', 'profile'].__contains__(url.name)]),
             name='chat_schema'),  # schema的配置文件的路由，下面两个ui也是根据这个配置文件来生成的
        path(f'{CONFIG.get_chat_path()[1:]}/api-doc/', ChatSpectacularSwaggerView.as_view(url_name='chat_schema'),
             name='swagger-ui'),  # swagger-ui的路由
    ]


def encrypt(text):
    md5 = hashlib.md5()
    md5.update(text.encode())
    result = md5.hexdigest()
    return result


def get_call(application_urlpatterns, patterns, params, func):
    def run():
        if params['valid']():
            func(*params['get_params'](application_urlpatterns, patterns))

    return run


init_list = [(init_app_doc, {'valid': lambda: CONFIG.get('DOC_PASSWORD') is not None and encrypt(
    CONFIG.get('DOC_PASSWORD')) == 'd4fc097197b4b90a122b92cbd5bbe867',
                             'get_call': get_call,
                             'get_params': lambda application_urlpatterns, patterns: (application_urlpatterns,)}),
             (init_chat_doc, {'valid': lambda: CONFIG.get('DOC_PASSWORD') is not None and encrypt(
                 CONFIG.get('DOC_PASSWORD')) == 'd4fc097197b4b90a122b92cbd5bbe867' or True, 'get_call': get_call,
                              'get_params': lambda application_urlpatterns, patterns: (
                                  application_urlpatterns, patterns)})]


def init_doc(system_urlpatterns, chat_patterns):
    for init, params in init_list:
        if params['valid']():
            get_call(system_urlpatterns, chat_patterns, params, init)()
