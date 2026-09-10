# coding=utf-8
"""
@project: MaxKB
@Author：虎虎
@file： common.py
@date：2025/6/6 19:55
@desc:
"""

from django.core import signing

from common.constants.authentication_type import AuthenticationType
from common.exception.app_exception import AppAuthenticationFailed


class SystemToken:
    def __init__(self, user_id, _type: AuthenticationType, **kwargs):
        self.id = user_id
        self.type = _type
        self.kwargs = kwargs

    def to_dict(self):
        if self.kwargs:
            return {"user_id": self.id, "type": str(self.type.value), "kwargs": self.kwargs}
        return {"id": str(self.id), "type": str(self.type.value)}

    def to_token(self):
        return signing.dumps(self.to_dict())


class ChatToken:
    def __init__(self, user_id, _type: AuthenticationType, login_type: str, **kwargs):
        self.id = user_id
        self.type = _type
        self.login_type = login_type
        self.kwargs = kwargs

    def to_dict(self):
        if self.kwargs:
            return {
                "id": str(self.id),
                "type": str(self.type.value),
                "login_type": str(self.login_type),
                "kwargs": self.kwargs,
            }
        return {
            "id": str(self.id),
            "type": str(self.type.value),
            "login_type": str(self.login_type),
        }

    def to_token(self):
        return signing.dumps(self.to_dict())


def parse_token(token):
    details = signing.loads(token)
    _type = details.get("type")
    if _type:
        if _type == AuthenticationType.SYSTEM_USER.value:
            return SystemToken(details.get("id"), details.get("type"), **details.get("kwargs", {}))
        return ChatToken(details.get("id"), details.get("type"), details.get("login_type"), **details.get("kwargs", {}))
    raise AppAuthenticationFailed(1001, "")
