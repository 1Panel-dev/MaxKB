# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_token.py
    @date：2025/6/9 17:42
    @desc:
"""
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.api.application_access_token import ApplicationAccessTokenAPI
from application.models import Application
from application.serializers.application_access_token import AccessTokenSerializer
from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants, ViewPermission, CompareConstants
from common.log.log import log

def get_application_operation_object(application_id):
    application_model = QuerySet(model=Application).filter(id=application_id).first()
    if application_model is not None:
        return {
            "name": application_model.name
        }
    return {}


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
    @log(menu='Application', operate="Modify application access token",
         get_operation_object= lambda r,k: get_application_operation_object((k.get('application_id')))
         )
    @has_permissions(PermissionConstants.APPLICATION_OVERVIEW_ACCESS.get_workspace_application_permission(),
                     PermissionConstants.APPLICATION_OVERVIEW_ACCESS.get_workspace_permission_workspace_manage_role(),
                     ViewPermission([RoleConstants.USER.get_workspace_role()],
                                    [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                    CompareConstants.AND),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def put(self, request: Request, workspace_id: str, application_id: str):
        return result.success(
            AccessTokenSerializer(data={'workspace_id': workspace_id, 'application_id': application_id}).edit(
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
                     PermissionConstants.APPLICATION_READ.get_workspace_permission_workspace_manage_role(),
                     ViewPermission([RoleConstants.USER.get_workspace_role()],
                                    [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                    CompareConstants.AND),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role()
                     )
    def get(self, request: Request, workspace_id: str, application_id: str):
        return result.success(
            AccessTokenSerializer(data={'workspace_id': workspace_id, 'application_id': application_id}).one())
