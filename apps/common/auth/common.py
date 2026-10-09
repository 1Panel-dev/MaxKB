# coding=utf-8
"""
@project: MaxKB
@Author：虎虎
@file： common.py
@date：2025/6/6 19:55
@desc:
"""

import hashlib

from django.core import signing

from common.constants.authentication_type import AuthenticationType
from common.exception.app_exception import AppAuthenticationFailed

_key = None


def get_key():
    global _key
    if _key:
        return _key
    from common.utils.rsa_util import get_key_pair

    value = get_key_pair().get("value")
    _key = hashlib.md5(value.encode("utf-8")).hexdigest()
    return _key


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
        return signing.dumps(self.to_dict(), key=get_key())


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
        return signing.dumps(self.to_dict(), key=get_key())


def parse_token(token):
    details = signing.loads(token, key=get_key())
    _type = details.get("type")
    if _type:
        if _type == AuthenticationType.SYSTEM_USER.value:
            return SystemToken(details.get("id"), details.get("type"), **details.get("kwargs", {}))
        return ChatToken(details.get("id"), details.get("type"), details.get("login_type"), **details.get("kwargs", {}))
    raise AppAuthenticationFailed(1001, "")
