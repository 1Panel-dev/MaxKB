# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_token.py
    @date：2025/6/9 17:42
    @desc:
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.api.application_access_token import ApplicationAccessTokenAPI
from application.serializers.application_access_token import AccessTokenSerializer
from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants


class AccessToken(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['PUT'],
        description=_("Modify application access restriction information"),
        summary=_("Modify application access restriction information"),
        operation_id=_("Modify application access restriction information"),  # type: ignore
        parameters=ApplicationAccessTokenAPI.get_parameters(),
        request=ApplicationAccessTokenAPI.get_request(),
        tags=[_('Application')]  # type: ignore
    )
    @has_permissions(PermissionConstants.APPLICATION_OVERVIEW_ACCESS.get_workspace_application_permission(),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def put(self, request: Request, workspace_id: str, application_id: str):
        return result.success(
            AccessTokenSerializer(data={'application_id': application_id}).edit(
                request.data))

    @extend_schema(
        methods=['GET'],
        description=_("Get application access restriction information"),
        summary=_("Get application access restriction information"),
        operation_id=_("Get application access restriction information"),  # type: ignore
        parameters=ApplicationAccessTokenAPI.get_parameters(),
        tags=[_('Application')]  # type: ignore
    )
    @has_permissions(PermissionConstants.APPLICATION_READ.get_workspace_application_permission(),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role()
                     )
    def get(self, request: Request, workspace_id: str, application_id: str):
        return result.success(AccessTokenSerializer(data={'application_id': application_id}).one())
