# coding=utf-8
"""
@project: MaxKB
@Author：虎虎
@file： chat_user_key.py
@date：2025/10/29 11:30
@desc: 对话用户api key认证
"""

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from application.models import ChatUserType
from common.auth.handle.auth_base_handle import AuthBaseHandle
from common.auth.handle.impl.chat_user_token import get_auth
from common.auth.struct.auth import Principal
from common.exception.app_exception import AppAuthenticationFailed
from system_manage.models import ChatUser, ChatUserApiKey


class ChatUserKey(AuthBaseHandle):
    def handle(self, request, token: str, get_token_details):
        chat_user_api_key = QuerySet(ChatUserApiKey).filter(secret_key=token).first()
        if chat_user_api_key is None:
            raise AppAuthenticationFailed(500, _("Secret key is invalid"))
        if not chat_user_api_key.is_active:
            raise AppAuthenticationFailed(500, _("Secret key is invalid"))
        chat_user = QuerySet(ChatUser).filter(id=chat_user_api_key.user_id).first()
        if chat_user is None or not chat_user.is_active:
            raise AppAuthenticationFailed(500, _("Secret key is invalid"))
        auth = get_auth(chat_user.source, chat_user.id, None)
        return Principal(str(chat_user.id), ChatUserType.CHAT_USER, profile=chat_user), auth

    def support(self, request, token: str, get_token_details):
        return str(token).startswith("chat-")
