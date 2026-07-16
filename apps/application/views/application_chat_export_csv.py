# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_chat_export_csv.py
    @date：2025/7/14 11:00
    @desc:
"""
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.api.application_chat_export_csv import ApplicationChatCsvExportAPI
from application.serializers.export_chat_record_csv import ApplicationChatExportCsvSerializer
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, ViewPermission, CompareConstants, RoleConstants


class ApplicationChatCsvExport(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description="Export conversation logs as CSV",
        summary="Export conversation logs as CSV",
        operation_id="Export conversation logs as CSV",
        request=ApplicationChatCsvExportAPI.get_request(),
        parameters=ApplicationChatCsvExportAPI.get_parameters(),
        responses=ApplicationChatCsvExportAPI.get_response(),
        tags=["Application/Conversation Log"]
    )
    @has_permissions(
        PermissionConstants.APPLICATION_CHAT_LOG_EXPORT.get_workspace_application_permission(),
        PermissionConstants.APPLICATION_CHAT_LOG_EXPORT.get_workspace_permission_workspace_manage_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [PermissionConstants.APPLICATION.get_workspace_application_permission()],
            CompareConstants.AND
        ),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role()
    )
    def post(self, request: Request, workspace_id: str, application_id: str):
        from common.utils.common import query_params_to_single_dict

        serializer = ApplicationChatExportCsvSerializer(
            data={
                **query_params_to_single_dict(request.query_params),
                'application_id': application_id,
                'fields': request.data.get('fields', [])
            }
        )
        serializer.is_valid(raise_exception=True)
        return serializer.export()
