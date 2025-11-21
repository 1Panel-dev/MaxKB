# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： common.py
    @date：2025/6/6 19:55
    @desc:
"""
import hashlib
import json
import threading

from django.core import signing, cache

from common.constants.cache_version import Cache_Version
from common.utils.rsa_util import encrypt, decrypt

authentication_cache = cache.cache
lock = threading.Lock()


def _decrypt(authentication: str):
    cache_key = hashlib.sha256(authentication.encode()).hexdigest()
    result = authentication_cache.get(key=cache_key, version=Cache_Version.CHAT.value)
    if result is None:
        with lock:
            result = authentication_cache.get(cache_key, version=Cache_Version.CHAT.value)
            if result is None:
                result = decrypt(authentication)
                authentication_cache.set(cache_key, result, version=Cache_Version.CHAT.value, timeout=60 * 60 * 2)

    return result


class ChatAuthentication:
    def __init__(self, auth_type: str | None, **kwargs):
        self.auth_type = auth_type
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    def to_dict(self):
        return self.__dict__

    def to_string(self):
        value = json.dumps(self.to_dict())
        authentication = encrypt(value)
        cache_key = hashlib.sha256(authentication.encode()).hexdigest()
        authentication_cache.set(cache_key, value, version=Cache_Version.CHAT.get_version(), timeout=60 * 60 * 2)
        return authentication

    @staticmethod
    def new_instance(authentication: str):
        auth = json.loads(_decrypt(authentication))
        return ChatAuthentication(**auth)


class ChatUserToken:
    def __init__(self, application_id, user_id, access_token, _type, chat_user_type, chat_user_id,
                 authentication: ChatAuthentication):
        self.application_id = application_id
        self.user_id = user_id
        self.access_token = access_token
        self.type = _type
        self.chat_user_type = chat_user_type
        self.chat_user_id = chat_user_id
        self.authentication = authentication

    def to_dict(self):
        return {
            'application_id': str(self.application_id),
            'user_id': str(self.user_id),
            'access_token': self.access_token,
            'type': str(self.type.value),
            'chat_user_type': str(self.chat_user_type),
            'chat_user_id': str(self.chat_user_id),
            'authentication': self.authentication.to_string()
        }

    def to_token(self):
        return signing.dumps(self.to_dict())

    @staticmethod
    def new_instance(token_dict):
        return ChatUserToken(token_dict.get('application_id'), token_dict.get('user_id'),
                             token_dict.get('access_token'), token_dict.get('type'), token_dict.get('chat_user_type'),
                             token_dict.get('chat_user_id'),
                             ChatAuthentication.new_instance(token_dict.get('authentication')))
