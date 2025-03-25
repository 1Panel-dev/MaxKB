# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： system_setting.py
    @date：2024/3/19 16:01
    @desc:
"""

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import RoleConstants
from common.log.log import log
from common.response import result
from setting.serializers.system_setting import SystemSettingSerializer
from setting.swagger_api.system_setting import SystemSettingEmailApi
from django.utils.translation import gettext_lazy as _

from setting.views.common import get_email_details


class SystemSetting(APIView):
    class Email(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_('Create or update email settings'),
                             operation_id=_('Create or update email settings'),
                             request_body=SystemSettingEmailApi.get_request_body_api(), tags=[_('Email settings')],
                             responses=result.get_api_response(SystemSettingEmailApi.get_response_body_api()))
        @has_permissions(RoleConstants.ADMIN)
        @log(menu='Email settings', operate='Create or update email settings',
             get_details=get_email_details
             )
        def put(self, request: Request):
            return result.success(
                SystemSettingSerializer.EmailSerializer.Create(
                    data=request.data).update_or_save())

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_('Test email settings'),
                             operation_id=_('Test email settings'),
                             request_body=SystemSettingEmailApi.get_request_body_api(),
                             responses=result.get_default_response(),
                             tags=[_('Email settings')])
        @has_permissions(RoleConstants.ADMIN)
        @log(menu='Email settings', operate='Test email settings',
             get_details=get_email_details
             )
        def post(self, request: Request):
            return result.success(
                SystemSettingSerializer.EmailSerializer.Create(
                    data=request.data).is_valid())

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('Get email settings'),
                             operation_id=_('Get email settings'),
                             responses=result.get_api_response(SystemSettingEmailApi.get_response_body_api()),
                             tags=[_('Email settings')])
        @has_permissions(RoleConstants.ADMIN)
        def get(self, request: Request):
            return result.success(
                SystemSettingSerializer.EmailSerializer.one())
