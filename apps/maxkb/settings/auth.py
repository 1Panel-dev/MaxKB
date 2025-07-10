# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： auth.py
    @date：2024/7/9 18:47
    @desc:
"""
USER_TOKEN_AUTH = 'common.auth.handle.impl.user_token.UserToken'
CHAT_ANONYMOUS_USER_AURH = 'common.auth.handle.impl.chat_anonymous_user_token.ChatAnonymousUserToken'
APPLICATION_KEY_AUTH = 'common.auth.handle.impl.application_key.ApplicationKey'
AUTH_HANDLES = [
    USER_TOKEN_AUTH,
    CHAT_ANONYMOUS_USER_AURH,
    APPLICATION_KEY_AUTH
]
