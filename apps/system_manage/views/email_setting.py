# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： system_setting.py
    @date：2024/3/19 16:01
    @desc:
"""
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants

from django.utils.translation import gettext_lazy as _

from common.log.log import log
from common.result import result
from common.utils.common import encryption
from models_provider.api.model import DefaultModelResponse
from system_manage.api.email_setting import EmailSettingAPI
from system_manage.serializers.email_setting import EmailSettingSerializer


def encryption_str(_value):
    if isinstance(_value, str):
        return encryption(_value)
    return _value


def get_email_details(request):
    path = request.path
    body = request.data
    query = request.query_params
    email_host_password = body.get('email_host_password', '')
    return {
        'path': path,
        'body': {**body, 'email_host_password': encryption_str(email_host_password)},
        'query': query
    }


class SystemSetting(APIView):
    class Email(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['PUT'],
                       summary=_('Create or update email settings'),
                       description=_('Create or update email settings'),
                       operation_id=_('Create or update email settings'),  # type: ignore
                       request=EmailSettingAPI.get_request(),
                       responses=EmailSettingAPI.get_response(),
                       tags=[_('Email Settings')])  # type: ignore
        @log(menu='Email settings', operate='Create or update email settings',
             get_details=get_email_details)
        @has_permissions(PermissionConstants.EMAIL_SETTING_EDIT, RoleConstants.ADMIN)
        def put(self, request: Request):
            return result.success(
                EmailSettingSerializer.Create(
                    data=request.data).update_or_save())

        @extend_schema(
            methods=['POST'],
            summary=_('Test email settings'),
            operation_id=_('Test email settings'),  # type: ignore
            request=EmailSettingAPI.get_request(),
            responses=DefaultModelResponse.get_response(),
            tags=[_('Email Settings')]  # type: ignore
        )
        @has_permissions(PermissionConstants.EMAIL_SETTING_EDIT, RoleConstants.ADMIN)
        @log(menu='Email settings', operate='Test email settings',
             get_details=get_email_details
             )
        def post(self, request: Request):
            return result.success(
                EmailSettingSerializer.Create(
                    data=request.data).is_valid())

        @extend_schema(methods=['GET'],
                       summary=_('Get email settings'),
                       description=_('Get email settings'),
                       operation_id=_('Get email settings'),  # type: ignore
                       responses=DefaultModelResponse.get_response(),
                       tags=[_('Email Settings')])  # type: ignore
        @has_permissions(PermissionConstants.EMAIL_SETTING_READ, RoleConstants.ADMIN)
        def get(self, request: Request):
            return result.success(
                EmailSettingSerializer.one())
