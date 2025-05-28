# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application.py
    @date：2025/5/26 16:51
    @desc:
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.api.application_api import ApplicationCreateAPI, ApplicationQueryAPI
from application.serializers.application import ApplicationSerializer, Query
from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants


class Application(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Create an application'),
        summary=_('Create an application'),
        operation_id=_('Create an application'),  # type: ignore
        parameters=ApplicationCreateAPI.get_parameters(),
        request=ApplicationCreateAPI.get_request(),
        responses=ApplicationCreateAPI.get_response(),
        tags=[_('Application')]  # type: ignore
    )
    @has_permissions(PermissionConstants.APPLICATION_READ.get_workspace_permission())
    def post(self, request: Request, workspace_id: str):
        return result.success(
            ApplicationSerializer(data={'workspace_id': workspace_id, 'user_id': request.user.id}).insert(request.data))

    @extend_schema(
        methods=['GET'],
        description=_('Get the application list'),
        summary=_('Get the application list'),
        operation_id=_('Get the application list'),  # type: ignore
        parameters=ApplicationQueryAPI.get_parameters(),
        responses=ApplicationQueryAPI.get_response(),
        tags=[_('Application')]  # type: ignore
    )
    @has_permissions(PermissionConstants.APPLICATION_READ.get_workspace_permission())
    def get(self, request: Request, workspace_id: str):
        return result.success(Query(data={'workspace_id': workspace_id, 'user_id': request.user.id}).list(request.data))

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Get the application list by page'),
            summary=_('Get the application list by page'),
            operation_id=_('Get the application list by page'),  # type: ignore
            parameters=ApplicationQueryAPI.get_parameters(),
            responses=ApplicationQueryAPI.get_page_response(),
            tags=[_('Application')]  # type: ignore
        )
        @has_permissions(PermissionConstants.APPLICATION_READ.get_workspace_permission())
        def get(self, request: Request, workspace_id: str, current_page: int, page_size: int):
            return result.success(
                Query(data={'workspace_id': workspace_id, 'user_id': request.user.id}).page(current_page, page_size,
                                                                                            request.query_params))
