# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： workspace_user_resource_permission.py
    @date：2025/4/28 16:38
    @desc:
"""
from urllib.request import Request

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView

from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants
from system_manage.api.user_resource_permission import UserResourcePermissionAPI
from system_manage.serializers.user_resource_permission import UserResourcePermissionSerializer


class WorkSpaceUserResourcePermissionView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_('Obtain resource authorization list'),
        operation_id=_('Obtain resource authorization list'),
        parameters=UserResourcePermissionAPI.get_parameters(),
        responses=UserResourcePermissionAPI.get_response(),
        tags=[_('Resources authorization')]
    )
    @has_permissions(PermissionConstants.WORKSPACE_USER_RESOURCE_PERMISSION_READ.get_workspace_permission())
    def get(self, request: Request, workspace_id: str):
        return result.success(UserResourcePermissionSerializer(
            data={'workspace_id': workspace_id}
        ).list())
