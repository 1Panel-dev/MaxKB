# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_version.py.py
    @date：2025/6/3 15:46
    @desc:
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.api.application_version import ApplicationVersionListAPI, ApplicationVersionPageAPI, \
    ApplicationVersionOperateAPI
from application.serializers.application_version import ApplicationVersionSerializer
from application.views import get_application_operation_object
from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants, ViewPermission, CompareConstants
from common.log.log import log


class ApplicationVersionView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_("Get the application version list"),
        summary=_("Get the application version list"),
        operation_id=_("Get the application version list"),  # type: ignore
        parameters=ApplicationVersionListAPI.get_parameters(),
        responses=ApplicationVersionListAPI.get_response(),
        tags=[_('Application/Version')]  # type: ignore
    )
    @has_permissions(PermissionConstants.APPLICATION_READ.get_workspace_application_permission(),
                     PermissionConstants.APPLICATION_READ.get_workspace_permission_workspace_manage_role(),
                     ViewPermission([RoleConstants.USER.get_workspace_role()],
                                    [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                    CompareConstants.AND),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def get(self, request: Request, workspace_id, application_id: str):
        return result.success(
            ApplicationVersionSerializer.Query(
                data={'workspace_id': workspace_id}).list(
                {'name': request.query_params.get("name"), 'application_id': application_id}))

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_("Get the list of application versions by page"),
            summary=_("Get the list of application versions by page"),
            operation_id=_("Get the list of application versions by page"),  # type: ignore
            parameters=ApplicationVersionPageAPI.get_parameters(),
            responses=ApplicationVersionPageAPI.get_response(),
            tags=[_('Application/Version')]  # type: ignore
        )
        @has_permissions(PermissionConstants.APPLICATION_READ.get_workspace_application_permission(),
                         PermissionConstants.APPLICATION_READ.get_workspace_permission_workspace_manage_role(),
                         ViewPermission([RoleConstants.USER.get_workspace_role()],
                                        [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                        CompareConstants.AND),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        def get(self, request: Request, workspace_id: str, application_id: str, current_page: int, page_size: int):
            return result.success(
                ApplicationVersionSerializer.Query(
                    data={'workspace_id': workspace_id}).page(
                    {'name': request.query_params.get("name"), 'application_id': application_id},
                    current_page, page_size))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_("Get application version details"),
            summary=_("Get application version details"),
            operation_id=_("Get application version details"),  # type: ignore
            parameters=ApplicationVersionOperateAPI.get_parameters(),
            responses=ApplicationVersionOperateAPI.get_response(),
            tags=[_('Application/Version')]  # type: ignore
        )
        @has_permissions(PermissionConstants.APPLICATION_EDIT.get_workspace_application_permission(),
                         PermissionConstants.APPLICATION_EDIT.get_workspace_permission_workspace_manage_role(),
                         ViewPermission([RoleConstants.USER.get_workspace_role()],
                                        [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                        CompareConstants.AND),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        def get(self, request: Request, workspace_id: str, application_id: str, application_version_id: str):
            return result.success(
                ApplicationVersionSerializer.Operate(
                    data={'user_id': request.user, 'workspace_id': workspace_id,
                          'application_id': application_id, 'application_version_id': application_version_id}).one())

        @extend_schema(
            methods=['PUT'],
            description=_("Modify application version information"),
            summary=_("Modify application version information"),
            operation_id=_("Modify application version information"),  # type: ignore
            parameters=ApplicationVersionOperateAPI.get_parameters(),
            request=None,
            responses=ApplicationVersionOperateAPI.get_response(),
            tags=[_('Application/Version')]  # type: ignore
        )
        @has_permissions(PermissionConstants.APPLICATION_EDIT.get_workspace_application_permission(),
                         PermissionConstants.APPLICATION_EDIT.get_workspace_permission_workspace_manage_role(),
                         ViewPermission([RoleConstants.USER.get_workspace_role()],
                                        [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                        CompareConstants.AND),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        @log(menu='Application', operate="Modify application version information",
             get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')),
             )
        def put(self, request: Request, workspace_id: str, application_id: str, application_version_id: str):
            return result.success(
                ApplicationVersionSerializer.Operate(
                    data={'application_id': application_id, 'workspace_id': workspace_id,
                          'application_version_id': application_version_id,
                          'user_id': request.user.id}).edit(
                    request.data))
