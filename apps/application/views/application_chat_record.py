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
    ApplicationChatRecordImproveSerializer, ChatRecordImproveSerializer, ApplicationChatRecordAddKnowledgeSerializer, \
    ChatRecordOperateSerializer
from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants, ViewPermission, CompareConstants
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
    @has_permissions(PermissionConstants.APPLICATION_CHAT_LOG_READ.get_workspace_application_permission(),
                     PermissionConstants.APPLICATION_CHAT_LOG_READ.get_workspace_permission_workspace_manage_role(),
                     ViewPermission([RoleConstants.USER.get_workspace_role()],
                                    [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                    CompareConstants.AND),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def get(self, request: Request, workspace_id: str, application_id: str, chat_id: str):
        return result.success(ApplicationChatRecordQuerySerializers(
            data={**query_params_to_single_dict(request.query_params), 'workspace_id': workspace_id,
                  'application_id': application_id,
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
        @has_permissions(PermissionConstants.APPLICATION_CHAT_LOG_READ.get_workspace_application_permission(),
                         PermissionConstants.APPLICATION_CHAT_LOG_READ.get_workspace_permission_workspace_manage_role(),
                         ViewPermission([RoleConstants.USER.get_workspace_role()],
                                        [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                        CompareConstants.AND),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        def get(self, request: Request, workspace_id: str, application_id: str, chat_id: str, current_page: int,
                page_size: int):
            return result.success(ApplicationChatRecordQuerySerializers(
                data={**query_params_to_single_dict(request.query_params), 'workspace_id': workspace_id,
                      'application_id': application_id,
                      'chat_id': chat_id}).page(
                current_page=current_page,
                page_size=page_size))


class ApplicationChatRecordOperateAPI(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_("Get conversation record details"),
        summary=_("Get conversation record details"),
        operation_id=_("Get conversation record details"),  # type: ignore
        request=ApplicationChatRecordQueryAPI.get_request(),
        parameters=ApplicationChatRecordQueryAPI.get_parameters(),
        responses=ApplicationChatRecordQueryAPI.get_response(),
        tags=[_("Application/Conversation Log")]  # type: ignore
    )
    @has_permissions(PermissionConstants.APPLICATION_CHAT_LOG_READ.get_workspace_application_permission(),
                     PermissionConstants.APPLICATION_CHAT_LOG_READ.get_workspace_permission_workspace_manage_role(),
                     PermissionConstants.APPLICATION_READ.get_workspace_application_permission(),
                     PermissionConstants.APPLICATION_READ.get_workspace_permission_workspace_manage_role(),
                     ViewPermission([RoleConstants.USER.get_workspace_role()],
                                    [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                    CompareConstants.AND),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def get(self, request: Request, workspace_id: str, application_id: str, chat_id: str, chat_record_id: str):
        return result.success(ChatRecordOperateSerializer(
            data={
                'workspace_id': workspace_id,
                'application_id': application_id,
                'chat_id': chat_id,
                'chat_record_id': chat_record_id}).one(True))


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
    @has_permissions(PermissionConstants.APPLICATION_CHAT_LOG_ADD_KNOWLEDGE.get_workspace_application_permission(),
                     PermissionConstants.APPLICATION_CHAT_LOG_ADD_KNOWLEDGE.get_workspace_permission_workspace_manage_role(),
                     ViewPermission([RoleConstants.USER.get_workspace_role()],
                                    [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                    CompareConstants.AND),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def post(self, request: Request, workspace_id: str, application_id: str):
        return result.success(ApplicationChatRecordAddKnowledgeSerializer(data = {'workspace_id': workspace_id, 'application_id': application_id, **request.data}).post_improve(
            {'workspace_id': workspace_id, 'application_id': application_id, **request.data}, request=request))


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
    @has_permissions(PermissionConstants.APPLICATION_CHAT_LOG_ANNOTATION.get_workspace_application_permission(),
                     PermissionConstants.APPLICATION_CHAT_LOG_ANNOTATION.get_workspace_permission_workspace_manage_role(),
                     ViewPermission([RoleConstants.USER.get_workspace_role()],
                                    [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                    CompareConstants.AND),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def get(self, request: Request, workspace_id: str, application_id: str, chat_id: str, chat_record_id: str):
        return result.success(ChatRecordImproveSerializer(
            data={'workspace_id': workspace_id, 'application_id': application_id, 'chat_id': chat_id,
                  'chat_record_id': chat_record_id}).get())


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
                     PermissionConstants.APPLICATION_CHAT_LOG_ANNOTATION.get_workspace_permission_workspace_manage_role(),
                     ViewPermission([RoleConstants.USER.get_workspace_role()],
                                    [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                    CompareConstants.AND),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def put(self, request: Request,
            workspace_id: str,
            application_id: str,
            chat_id: str,
            chat_record_id: str,
            knowledge_id: str,
            document_id: str):
        return result.success(ApplicationChatRecordImproveSerializer(
            data={'workspace_id': workspace_id, 'application_id': application_id, 'chat_id': chat_id,
                  'chat_record_id': chat_record_id,
                  'knowledge_id': knowledge_id, 'document_id': document_id}).improve(request.data, request=request))

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
                         PermissionConstants.APPLICATION_CHAT_LOG_ANNOTATION.get_workspace_permission_workspace_manage_role(),
                         ViewPermission([RoleConstants.USER.get_workspace_role()],
                                        [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                        CompareConstants.AND),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        def delete(self, request: Request, workspace_id: str, application_id: str, chat_id: str, chat_record_id: str,
                   knowledge_id: str,
                   document_id: str, paragraph_id: str):
            return result.success(ApplicationChatRecordImproveSerializer.Operate(
                data={'chat_id': chat_id, 'chat_record_id': chat_record_id, 'workspace_id': workspace_id,
                      'application_id': application_id,
                      'knowledge_id': knowledge_id, 'document_id': document_id,
                      'paragraph_id': paragraph_id}).delete(request=request))
