# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： user.py
    @date：2025/4/14 10:22
    @desc:
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common import result
from users.api.login import LoginAPI, CaptchaAPI
from users.serializers.login import LoginSerializer, CaptchaSerializer


class LoginView(APIView):
    @extend_schema(methods=['POST'],
                   description=_("Log in"),
                   operation_id=_("Log in"),
                   tags=[_("User management")],
                   request=LoginAPI.get_request(),
                   responses=LoginAPI.get_response())
    def post(self, request: Request):
        return result.success(LoginSerializer().login(request.data))


class CaptchaView(APIView):
    @extend_schema(methods=['GET'],
                   description=_("Get captcha"),
                   operation_id=_("Get captcha"),
                   tags=[_("User management")],
                   responses=CaptchaAPI.get_response())
    def get(self, request: Request):
        return result.success(CaptchaSerializer().generate())
