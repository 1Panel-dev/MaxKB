# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_chat.py
    @date：2025/6/10 11:00
    @desc:
"""
import uuid_utils.compat as uuid
from django.db.models import QuerySet

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.api.application_chat import ApplicationChatQueryAPI, ApplicationChatQueryPageAPI, \
    ApplicationChatExportAPI
from application.models import ChatUserType, Application
from application.serializers.application_chat import ApplicationChatQuerySerializers
from chat.api.chat_api import ChatAPI, PromptGenerateAPI
from chat.api.chat_authentication_api import ChatOpenAPI
from chat.serializers.chat import OpenChatSerializers, ChatSerializers, DebugChatSerializers, PromptGenerateSerializer
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants, ViewPermission, CompareConstants
from common.log.log import log
from common.result import result
from common.utils.common import query_params_to_single_dict

def get_application_operation_object(application_id):
    application_model = QuerySet(model=Application).filter(id=application_id).first()
    if application_model is not None:
        return {
            'name': application_model.name
        }
    return {}

class ApplicationChat(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_("Get the conversation list"),
        summary=_("Get the conversation list"),
        operation_id=_("Get the conversation list"),  # type: ignore
        request=ApplicationChatQueryAPI.get_request(),
        parameters=ApplicationChatQueryAPI.get_parameters(),
        responses=ApplicationChatQueryAPI.get_response(),
        tags=[_("Application/Conversation Log")]  # type: ignore
    )
    @has_permissions(PermissionConstants.APPLICATION_CHAT_LOG_READ.get_workspace_application_permission(),
                     PermissionConstants.APPLICATION_CHAT_LOG_READ.get_workspace_permission_workspace_manage_role(),
                     ViewPermission([RoleConstants.USER.get_workspace_role()],
                                    [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                    CompareConstants.AND),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def get(self, request: Request, workspace_id: str, application_id: str):
        return result.success(ApplicationChatQuerySerializers(
            data={**query_params_to_single_dict(request.query_params), 'workspace_id': workspace_id,
                  'application_id': application_id,
                  }).list())

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_("Get the conversation list by page"),
            summary=_("Get the conversation list by page"),
            operation_id=_("Get the conversation list by page"),  # type: ignore
            request=ApplicationChatQueryPageAPI.get_request(),
            parameters=ApplicationChatQueryPageAPI.get_parameters(),
            responses=ApplicationChatQueryPageAPI.get_response(),
            tags=[_("Application/Conversation Log")]  # type: ignore
        )
        @has_permissions(PermissionConstants.APPLICATION_CHAT_LOG_READ.get_workspace_application_permission(),
                         PermissionConstants.APPLICATION_CHAT_LOG_READ.get_workspace_permission_workspace_manage_role(),
                         ViewPermission([RoleConstants.USER.get_workspace_role()],
                                        [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                        CompareConstants.AND),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        def get(self, request: Request, workspace_id: str, application_id: str, current_page: int, page_size: int):
            return result.success(ApplicationChatQuerySerializers(
                data={**query_params_to_single_dict(request.query_params), 'workspace_id': workspace_id,
                      'application_id': application_id,
                      }).page(current_page=current_page,
                              page_size=page_size))

    class Export(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['POST'],
            description=_("Export conversation"),
            summary=_("Export conversation"),
            operation_id=_("Export conversation"),  # type: ignore
            request=ApplicationChatExportAPI.get_request(),
            parameters=ApplicationChatExportAPI.get_parameters(),
            responses=ApplicationChatExportAPI.get_response(),
            tags=[_("Application/Conversation Log")]  # type: ignore
        )
        @has_permissions(PermissionConstants.APPLICATION_CHAT_LOG_EXPORT.get_workspace_application_permission(),
                         PermissionConstants.APPLICATION_CHAT_LOG_EXPORT.get_workspace_permission_workspace_manage_role(),
                         ViewPermission([RoleConstants.USER.get_workspace_role()],
                                        [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                        CompareConstants.AND),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        def post(self, request: Request, workspace_id: str, application_id: str):
            return ApplicationChatQuerySerializers(
                data={**query_params_to_single_dict(request.query_params), 'workspace_id': workspace_id,
                      'application_id': application_id,
                      }).export(request.data)


class OpenView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_("Get a temporary session id based on the application id"),
        summary=_("Get a temporary session id based on the application id"),
        operation_id=_("Get a temporary session id based on the application id"),  # type: ignore
        parameters=ChatOpenAPI.get_parameters(),
        responses=None,
        tags=[_('Application')]  # type: ignore
    )
    @has_permissions(PermissionConstants.APPLICATION_EDIT.get_workspace_application_permission(),
                     PermissionConstants.APPLICATION_EDIT.get_workspace_permission_workspace_manage_role(),
                     ViewPermission([RoleConstants.USER.get_workspace_role()],
                                    [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                    CompareConstants.AND),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def get(self, request: Request, workspace_id: str, application_id: str):
        return result.success(OpenChatSerializers(
            data={'workspace_id': workspace_id, 'application_id': application_id,
                  'chat_user_id': str(uuid.uuid7()), 'chat_user_type': ChatUserType.ANONYMOUS_USER,
                  'debug': True}).open())


class ChatView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_("dialogue"),
        summary=_("dialogue"),
        operation_id=_("dialogue"),  # type: ignore
        request=ChatAPI.get_request(),
        parameters=ChatAPI.get_parameters(),
        responses=None,
        tags=[_('Application')]  # type: ignore
    )
    def post(self, request: Request, chat_id: str):
        return DebugChatSerializers(data={'chat_id': chat_id}).chat(request.data)

class PromptGenerateView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_("generate prompt"),
        summary=_("generate prompt"),
        operation_id=_("generate prompt"),  # type: ignore
        request=PromptGenerateAPI.get_request(),
        parameters=PromptGenerateAPI.get_parameters(),
        responses=None,
        tags=[_('Application')]  # type: ignore
    )
    @has_permissions(PermissionConstants.APPLICATION_EDIT.get_workspace_application_permission(),
                     PermissionConstants.APPLICATION_EDIT.get_workspace_permission_workspace_manage_role(),
                     ViewPermission([RoleConstants.USER.get_workspace_role()],
                                    [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                    CompareConstants.AND),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    @log(menu='Application', operate='Generate prompt',
         get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')))
    def post(self, request: Request, workspace_id: str, model_id:str, application_id: str):
        return PromptGenerateSerializer(data={'workspace_id': workspace_id, 'model_id': model_id, 'application_id': application_id}).generate_prompt(instance=request.data)