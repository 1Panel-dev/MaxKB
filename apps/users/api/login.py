# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： login.py
    @date：2025/4/14 10:30
    @desc:
"""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer
from users.serializers.login import LoginResponse, LoginRequest, CaptchaResponse


class ApiLoginResponse(ResultSerializer):
    def get_data(self):
        return LoginResponse()


"""
Request 和Response 都可以使用此方法
使用serializers.Serializer
class LoginRequest(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=64, help_text=_("Username"), label=_("Username"))
    password = serializers.CharField(required=True, max_length=128, label=_("Password"))
使用serializers.ModelSerializer Request不要使用serializers.ModelSerializer的方式
class LoginRequest(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

"""


class LoginAPI(APIMixin):
    @staticmethod
    def get_request():
        return LoginRequest

    @staticmethod
    def get_response():
        return ApiLoginResponse

    @staticmethod
    def get_parameters():
        return [OpenApiParameter(
            name="code",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            required=True,
        )]


class ApiCaptchaResponse(ResultSerializer):
    def get_data(self):
        return CaptchaResponse()


class CaptchaAPI(APIMixin):
    @staticmethod
    def get_response():
        return ApiCaptchaResponse
