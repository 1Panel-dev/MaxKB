# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： static_headers_middleware.py
    @date：2024/3/13 18:26
    @desc:
"""
from django.utils.deprecation import MiddlewareMixin

from common.cache_data.application_access_token_cache import get_application_access_token
from maxkb.const import CONFIG


class ChatHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):

        if request.path.startswith(CONFIG.get_chat_path()) and not request.path.startswith(
                CONFIG.get_chat_path() + '/api'):
            access_token = request.path.replace(CONFIG.get_chat_path() + '/', '')
            if access_token.__contains__('/') or access_token == 'undefined':
                return response
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
                    '<link rel="icon" href="./favicon.ico"/>',
                    f'<link rel="icon" href="{application_icon}" />')
                .replace('<title>MaxKB</title>', f'<title>{application_name}</title>').encode(
                    "utf-8"))
        return response
