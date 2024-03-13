# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： chat_cookie_middleware.py
    @date：2024/3/13 20:13
    @desc:
"""
from django.core import cache
from django.core import signing
from django.db.models import QuerySet
from django.utils.deprecation import MiddlewareMixin

from application.models.api_key_model import ApplicationAccessToken
from common.exception.app_exception import AppEmbedIdentityFailed
from common.response import result
from common.util.common import set_embed_identity_cookie, getRestSeconds
from common.util.rsa_util import decrypt

chat_cache = cache.caches['chat_cache']


class ChatCookieMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        if request.path.startswith('/api/application/chat_message') or request.path.startswith(
                '/api/application/authentication') or request.path.startswith('/api/application/profile'):
            set_embed_identity_cookie(request, response)
            if 'embed_identity' in request.COOKIES and request.path.__contains__('/api/application/chat_message/'):
                embed_identity = request.COOKIES['embed_identity']
                try:
                    # 如果无法解密 说明embed_identity并非系统颁发
                    value = decrypt(embed_identity)
                except Exception as e:
                    raise AppEmbedIdentityFailed(1004, '嵌入cookie不正确')
                # 对话次数+1
                try:
                    if not chat_cache.incr(value):
                        # 如果修改失败则设置为1
                        chat_cache.set(value, 1,
                                       timeout=getRestSeconds())
                except Exception as e:
                    # 如果修改失败则设置为1 证明 key不存在
                    chat_cache.set(value, 1,
                                   timeout=getRestSeconds())
        return response

    def process_request(self, request):
        if 'embed_identity' in request.COOKIES and request.path.__contains__('/api/application/chat_message/'):
            auth = request.META.get('HTTP_AUTHORIZATION', None
                                    )
            auth_details = signing.loads(auth)
            application_access_token = QuerySet(ApplicationAccessToken).filter(
                application_id=auth_details.get('application_id')).first()
            embed_identity = request.COOKIES['embed_identity']
            try:
                # 如果无法解密 说明embed_identity并非系统颁发
                value = decrypt(embed_identity)
            except Exception as e:
                return result.Result(1003,
                                     message='访问次数超过今日访问量', response_status=460)
            embed_identity_number = chat_cache.get(value)
            if embed_identity_number is not None:
                if application_access_token.access_num <= embed_identity_number:
                    return result.Result(1003,
                                         message='访问次数超过今日访问量', response_status=461)
