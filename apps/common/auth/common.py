# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： common.py
    @date：2025/6/6 19:55
    @desc:
"""
import json

from django.core import signing

from common.utils.rsa_util import encrypt, decrypt


class ChatAuthentication:
    def __init__(self, auth_type: str | None):
        self.auth_type = auth_type

    def to_dict(self):
        return {'auth_type': self.auth_type}

    def to_string(self):
        return encrypt(json.dumps(self.to_dict()))

    @staticmethod
    def new_instance(authentication: str):
        auth = json.loads(decrypt(authentication))
        return ChatAuthentication(auth.get('auth_type'))


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
