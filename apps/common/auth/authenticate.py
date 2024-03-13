# coding=utf-8
"""
    @project: qabot
    @Author：虎
    @file： authenticate.py
    @date：2023/9/4 11:16
    @desc:  认证类
"""
import datetime
import traceback
from urllib.parse import urlparse

from django.core import cache
from django.core import signing
from django.db.models import QuerySet
from ipware import get_client_ip
from rest_framework.authentication import TokenAuthentication

from application.models.api_key_model import ApplicationAccessToken, ApplicationApiKey
from common.constants.authentication_type import AuthenticationType
from common.constants.permission_constants import Auth, get_permission_list_by_role, RoleConstants, Permission, Group, \
    Operate
from common.exception.app_exception import AppAuthenticationFailed, AppEmbedIdentityFailed, AppChatNumOutOfBoundsFailed
from common.util.common import getRestSeconds
from common.util.rsa_util import decrypt
from smartdoc.settings import JWT_AUTH
from users.models.user import User, get_user_dynamics_permission

token_cache = cache.caches['token_cache']
chat_cache = cache.caches['chat_cache']


class AnonymousAuthentication(TokenAuthentication):
    def authenticate(self, request):
        return None, None


class TokenAuth(TokenAuthentication):
    # 重新 authenticate 方法，自定义认证规则
    def authenticate(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION', None
                                )
        # 未认证
        if auth is None:
            raise AppAuthenticationFailed(1003, '未登录,请先登录')
        try:
            if str(auth).startswith("application-"):
                application_api_key = QuerySet(ApplicationApiKey).filter(secret_key=auth).first()
                if application_api_key is None:
                    raise AppAuthenticationFailed(500, "secret_key 无效")
                if not application_api_key.is_active:
                    raise AppAuthenticationFailed(500, "secret_key 无效")
                permission_list = [Permission(group=Group.APPLICATION,
                                              operate=Operate.USE,
                                              dynamic_tag=str(
                                                  application_api_key.application_id)),
                                   Permission(group=Group.APPLICATION,
                                              operate=Operate.MANAGE,
                                              dynamic_tag=str(
                                                  application_api_key.application_id))
                                   ]
                return application_api_key.user, Auth(role_list=[RoleConstants.APPLICATION_KEY],
                                                      permission_list=permission_list,
                                                      application_id=application_api_key.application_id)
            # 解析 token
            auth_details = signing.loads(auth)
            cache_token = token_cache.get(auth)
            if cache_token is None:
                raise AppAuthenticationFailed(1002, "登录过期")
            if 'id' in auth_details and auth_details.get('type') == AuthenticationType.USER.value:
                user = QuerySet(User).get(id=auth_details['id'])
                # 续期
                token_cache.touch(auth, timeout=JWT_AUTH['JWT_EXPIRATION_DELTA'].total_seconds())
                rule = RoleConstants[user.role]
                permission_list = get_permission_list_by_role(RoleConstants[user.role])
                # 获取用户的应用和知识库的权限
                permission_list += get_user_dynamics_permission(str(user.id))
                return user, Auth(role_list=[rule],
                                  permission_list=permission_list)
            if 'application_id' in auth_details and 'access_token' in auth_details and auth_details.get(
                    'type') == AuthenticationType.APPLICATION_ACCESS_TOKEN.value:
                application_access_token = QuerySet(ApplicationAccessToken).filter(
                    application_id=auth_details.get('application_id')).first()
                if application_access_token is None:
                    raise AppAuthenticationFailed(1002, "身份验证信息不正确")
                if not application_access_token.is_active:
                    raise AppAuthenticationFailed(1002, "身份验证信息不正确")
                if not application_access_token.access_token == auth_details.get('access_token'):
                    raise AppAuthenticationFailed(1002, "身份验证信息不正确")
                if application_access_token.white_active:
                    referer = request.META.get('HTTP_REFERER')
                    if referer is not None:
                        client_ip = urlparse(referer).hostname
                    else:
                        client_ip = get_client_ip(request)
                    if not application_access_token.white_list.__contains__(client_ip):
                        raise AppAuthenticationFailed(1002, "身份验证信息不正确")
                if 'embed_identity' in request.COOKIES and request.path.__contains__('/api/application/chat_message/'):
                    embed_identity = request.COOKIES['embed_identity']
                    try:
                        # 如果无法解密 说明embed_identity并非系统颁发
                        value = decrypt(embed_identity)
                    except Exception as e:
                        raise AppEmbedIdentityFailed(1004, '嵌入cookie不正确')
                    embed_identity_number = chat_cache.get(value)
                    if embed_identity_number is not None:
                        if application_access_token.access_num <= embed_identity_number:
                            raise AppChatNumOutOfBoundsFailed(1003, '访问次数超过今日访问量')
                    # 对话次数+1
                    try:
                        if not chat_cache.incr(value):
                            # 如果修改失败则设置为1
                            chat_cache.set(value, 1,
                                           timeout=getRestSeconds())
                    except Exception as e:
                        # 如果修改失败则设置为1 证明 key不存在
                        chat_cache.add(value, 1,
                                       timeout=getRestSeconds())
                return application_access_token.application.user, Auth(
                    role_list=[RoleConstants.APPLICATION_ACCESS_TOKEN],
                    permission_list=[
                        Permission(group=Group.APPLICATION,
                                   operate=Operate.USE,
                                   dynamic_tag=str(
                                       application_access_token.application_id))],
                    application_id=application_access_token.application_id
                )

            else:
                raise AppAuthenticationFailed(1002, "身份验证信息不正确！非法用户")

        except Exception as e:
            traceback.format_exc()
            if isinstance(e, AppEmbedIdentityFailed) or isinstance(e, AppChatNumOutOfBoundsFailed):
                raise e
            raise AppAuthenticationFailed(1002, "身份验证信息不正确！非法用户")
