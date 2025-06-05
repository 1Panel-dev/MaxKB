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

from application.serializers.application_version import ApplicationVersionSerializer
from application.views import get_application_operation_object
from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants
from common.log.log import log


class ApplicationVersionView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_("Get the application list"),
        summary=_("Get the application list"),
        operation_id=_("Get the application list"),  # type: ignore
        # parameters=ApplicationCreateAPI.get_parameters(),
        # request=ApplicationCreateAPI.get_request(),
        # responses=ApplicationCreateAPI.get_response(),
        tags=[_('Application/Version')]  # type: ignore
    )
    @has_permissions(PermissionConstants.APPLICATION_READ)
    def get(self, request: Request, workspace_id, application_id: str):
        return result.success(
            ApplicationVersionSerializer.Query(
                data={'name': request.query_params.get('name'), 'user_id': request.user.id,
                      'application_id': application_id}).list(request.data))

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'
                     ''],
            description=_("Get the list of application versions by page"),
            summary=_("Get the list of application versions by page"),
            operation_id=_("Get the list of application versions by page"),  # type: ignore
            # parameters=ApplicationCreateAPI.get_parameters(),
            # request=ApplicationCreateAPI.get_request(),
            # responses=ApplicationCreateAPI.get_response(),
            tags=[_('Application/Version')]  # type: ignore
        )
        @has_permissions(PermissionConstants.APPLICATION_READ)
        def get(self, request: Request, application_id: str, current_page: int, page_size: int):
            return result.success(
                ApplicationVersionSerializer.Query(
                    data={'name': request.query_params.get('name'), 'user_id': request.user,
                          'application_id': application_id}).page(
                    current_page, page_size))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_("Get application version details"),
            summary=_("Get application version details"),
            operation_id=_("Get application version details"),  # type: ignore
            # parameters=ApplicationCreateAPI.get_parameters(),
            # request=ApplicationCreateAPI.get_request(),
            # responses=ApplicationCreateAPI.get_response(),
            tags=[_('Application/Version')]  # type: ignore
        )
        @has_permissions(PermissionConstants.APPLICATION_READ)
        def get(self, request: Request, application_id: str, work_flow_version_id: str):
            return result.success(
                ApplicationVersionSerializer.Operate(
                    data={'user_id': request.user,
                          'application_id': application_id, 'work_flow_version_id': work_flow_version_id}).one())

        @extend_schema(
            methods=['PUT'],
            description=_("Modify application version information"),
            summary=_("Modify application version information"),
            operation_id=_("Modify application version information"),  # type: ignore
            # parameters=ApplicationCreateAPI.get_parameters(),
            # request=ApplicationCreateAPI.get_request(),
            # responses=ApplicationCreateAPI.get_response(),
            tags=[_('Application/Version')]  # type: ignore
        )
        @log(menu='Application', operate="Modify application version information",
             get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')))

        def put(self, request: Request, application_id: str, work_flow_version_id: str):
            return result.success(
                ApplicationVersionSerializer.Operate(
                    data={'application_id': application_id, 'work_flow_version_id': work_flow_version_id,
                          'user_id': request.user.id}).edit(
                    request.data))
