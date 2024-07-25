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
from common.constants.cache_code_constants import CacheCodeConstants
from common.util.cache_util import get_cache


@get_cache(cache_key=lambda access_token, use_get_data: access_token,
           use_get_data=lambda access_token, use_get_data: use_get_data,
           version=CacheCodeConstants.APPLICATION_ACCESS_TOKEN_CACHE.value)
def get_application_access_token(access_token, use_get_data):
    application_access_token = QuerySet(ApplicationAccessToken).filter(access_token=access_token).first()
    if application_access_token is None:
        return None
    return {'white_active': application_access_token.white_active,
            'white_list': application_access_token.white_list,
            'application_icon': application_access_token.application.icon,
            'application_name': application_access_token.application.name}


class StaticHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.path.startswith('/ui/chat/'):
            access_token = request.path.replace('/ui/chat/', '')
            application_access_token = get_application_access_token(access_token, True)
            if application_access_token is not None:
                white_active = application_access_token.get('white_active', False)
                white_list = application_access_token.get('white_list', [])
                application_icon = application_access_token.get('application_icon')
                application_name = application_access_token.get('application_name')
                if white_active:
                    # 添加自定义的响应头
                    response[
                        'Content-Security-Policy'] = f'frame-ancestors {" ".join(white_list)}'
                response.content = (response.content.decode('utf-8').replace(
                    '<link rel="icon" href="/ui/favicon.ico" />',
                    f'<link rel="icon" href="{application_icon}" />')
                .replace('<title>MaxKB</title>', f'<title>{application_name}</title>').encode(
                    "utf-8"))
        return response
