# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： user.py
    @date：2025/4/14 19:25
    @desc:
"""
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _
from rest_framework.request import Request

from common.auth import TokenAuth
from common.result import result
from users.api.user import UserProfileAPI
from users.serializers.user import UserProfileSerializer


class UserProfileView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['GET'],
                   description=_("Get current user information"),
                   operation_id=_("Get current user information"),
                   tags=[_("User management")],
                   responses=UserProfileAPI.get_response())
    def get(self, request: Request):
        return result.success(UserProfileSerializer().profile(request.user))
