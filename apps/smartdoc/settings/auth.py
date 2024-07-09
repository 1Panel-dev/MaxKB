# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： auth.py
    @date：2024/7/9 18:47
    @desc:
"""
USER_TOKEN_AUTH = 'common.auth.handle.impl.user_token.UserToken'

PUBLIC_ACCESS_TOKEN_AUTH = 'common.auth.handle.impl.public_access_token.PublicAccessToken'

APPLICATION_KEY_AUTH = 'common.auth.handle.impl.application_key.ApplicationKey'

AUTH_HANDLES = [
    USER_TOKEN_AUTH,
    PUBLIC_ACCESS_TOKEN_AUTH,
    APPLICATION_KEY_AUTH
]
