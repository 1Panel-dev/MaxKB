# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： static_headers_middleware.py
    @date：2024/3/13 18:26
    @desc:
"""
from django.db.models import QuerySet
from django.utils.deprecation import MiddlewareMixin

from application.models.api_key_model import ApplicationAccessToken


class StaticHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.path.startswith('/ui/chat/'):
            access_token = request.path.replace('/ui/chat/', '')
            application_access_token = QuerySet(ApplicationAccessToken).filter(access_token=access_token).first()
            if application_access_token is not None:
                if application_access_token.white_active:
                    # 添加自定义的响应头
                    response[
                        'Content-Security-Policy'] = f'frame-ancestors {" ".join(application_access_token.white_list)}'
                response.content = (response.content.decode('utf-8').replace(
                    '<link rel="icon" href="/ui/favicon.ico" />',
                    f'<link rel="icon" href="{application_access_token.application.icon}" />')
                .replace('<title>MaxKB</title>', f'<title>{application_access_token.application.name}</title>').encode(
                    "utf-8"))
        return response
