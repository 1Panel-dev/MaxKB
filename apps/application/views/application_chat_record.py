# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_chat_record.py
    @date：2025/6/10 15:08
    @desc:
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.api.application_chat_record import ApplicationChatRecordQueryAPI, \
    ApplicationChatRecordImproveParagraphAPI, ApplicationChatRecordAddKnowledgeAPI
from application.serializers.application_chat_record import ApplicationChatRecordQuerySerializers, \
    ApplicationChatRecordImproveSerializer, ChatRecordImproveSerializer, ApplicationChatRecordAddKnowledgeSerializer
from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants
from common.utils.common import query_params_to_single_dict


class ApplicationChatRecord(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_("Get the conversation record list"),
        summary=_("Get the conversation record list"),
        operation_id=_("Get the conversation record list"),  # type: ignore
        request=ApplicationChatRecordQueryAPI.get_request(),
        parameters=ApplicationChatRecordQueryAPI.get_parameters(),
        responses=ApplicationChatRecordQueryAPI.get_response(),
        tags=[_("Application/Conversation Log")]  # type: ignore
    )
    @has_permissions(PermissionConstants.APPLICATION_CHAT_LOG.get_workspace_application_permission(),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def get(self, request: Request, workspace_id: str, application_id: str, chat_id: str):
        return result.success(ApplicationChatRecordQuerySerializers(
            data={**query_params_to_single_dict(request.query_params), 'application_id': application_id,
                  'chat_id': chat_id
                  }).list())

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_("Get the conversation record list by page"),
            summary=_("Get the conversation record list by page"),
            operation_id=_("Get the conversation record list by page"),  # type: ignore
            request=ApplicationChatRecordQueryAPI.get_request(),
            parameters=ApplicationChatRecordQueryAPI.get_parameters(),
            responses=ApplicationChatRecordQueryAPI.get_response(),
            tags=[_("Application/Conversation Log")]  # type: ignore
        )
        @has_permissions(PermissionConstants.APPLICATION_CHAT_LOG.get_workspace_application_permission(),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        def get(self, request: Request, workspace_id: str, application_id: str, chat_id: str, current_page: int,
                page_size: int):
            return result.success(ApplicationChatRecordQuerySerializers(
                data={**query_params_to_single_dict(request.query_params), 'application_id': application_id,
                      'chat_id': chat_id}).page(
                current_page=current_page,
                page_size=page_size))


class ApplicationChatRecordAddKnowledge(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_("Add to Knowledge Base"),
        summary=_("Add to Knowledge Base"),
        operation_id=_("Add to Knowledge Base"),  # type: ignore
        request=ApplicationChatRecordAddKnowledgeAPI.get_request(),
        parameters=ApplicationChatRecordAddKnowledgeAPI.get_parameters(),
        responses=ApplicationChatRecordAddKnowledgeAPI.get_response(),
        tags=[_("Application/Conversation Log")]  # type: ignore
    )
    @has_permissions(PermissionConstants.APPLICATION_CHAT_LOG.get_workspace_application_permission(),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def post(self, request: Request, workspace_id: str, application_id: str):
        return result.success(ApplicationChatRecordAddKnowledgeSerializer().post_improve(request.data))


class ApplicationChatRecordImprove(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_("Get the list of marked paragraphs"),
        summary=_("Get the list of marked paragraphs"),
        operation_id=_("Get the list of marked paragraphs"),  # type: ignore
        request=ApplicationChatRecordQueryAPI.get_request(),
        parameters=ApplicationChatRecordQueryAPI.get_parameters(),
        responses=ApplicationChatRecordQueryAPI.get_response(),
        tags=[_("Application/Conversation Log")]  # type: ignore
    )
    @has_permissions(PermissionConstants.APPLICATION_CHAT_LOG.get_workspace_application_permission(),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def get(self, request: Request, workspace_id: str, application_id: str, chat_id: str, chat_record_id: str):
        return result.success(ChatRecordImproveSerializer(
            data={'chat_id': chat_id, 'chat_record_id': chat_record_id}).get())


class ApplicationChatRecordImproveParagraph(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['PUT'],
        description=_("Annotation"),
        summary=_("Annotation"),
        operation_id=_("Annotation"),  # type: ignore
        request=ApplicationChatRecordImproveParagraphAPI.get_request(),
        parameters=ApplicationChatRecordImproveParagraphAPI.get_parameters(),
        responses=ApplicationChatRecordImproveParagraphAPI.get_response(),
        tags=[_("Application/Conversation Log")]  # type: ignore
    )
    @has_permissions(PermissionConstants.APPLICATION_CHAT_LOG_ANNOTATION.get_workspace_application_permission(),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def put(self, request: Request,
            workspace_id: str,
            application_id: str,
            chat_id: str,
            chat_record_id: str,
            knowledge_id: str,
            document_id: str):
        return result.success(ApplicationChatRecordImproveSerializer(
            data={'chat_id': chat_id, 'chat_record_id': chat_record_id,
                  'knowledge_id': knowledge_id, 'document_id': document_id}).improve(request.data))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['DELETE'],
            description=_("Delete a Annotation"),
            summary=_("Delete a Annotation"),
            operation_id=_("Delete a Annotation"),  # type: ignore
            request=ApplicationChatRecordImproveParagraphAPI.Operate.get_request(),
            parameters=ApplicationChatRecordImproveParagraphAPI.Operate.get_parameters(),
            responses=ApplicationChatRecordImproveParagraphAPI.Operate.get_response(),
            tags=[_("Application/Conversation Log")]  # type: ignore
        )
        @has_permissions(PermissionConstants.APPLICATION_CHAT_LOG_ANNOTATION.get_workspace_application_permission(),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        def delete(self, request: Request, workspace_id: str, application_id: str, chat_id: str, chat_record_id: str,
                   knowledge_id: str,
                   document_id: str, paragraph_id: str):
            return result.success(ApplicationChatRecordImproveSerializer.Operate(
                data={'chat_id': chat_id, 'chat_record_id': chat_record_id, 'workspace_id': workspace_id,
                      'knowledge_id': knowledge_id, 'document_id': document_id,
                      'paragraph_id': paragraph_id}).delete())
