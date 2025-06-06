# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： chat_authentication_api.py
    @date：2025/6/6 19:59
    @desc:
"""
from chat.serializers.chat_authentication import AuthenticationSerializer
from common.mixins.api_mixin import APIMixin


class ChatAuthenticationAPI(APIMixin):
    @staticmethod
    def get_request():
        return AuthenticationSerializer()

    @staticmethod
    def get_parameters():
        pass

    @staticmethod
    def get_response():
        pass
