# coding=utf-8

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.api.application_api import SpeechToTextAPI
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants, ViewPermission, CompareConstants
from common.log.log import log
from common.result import result, DefaultResultSerializer
from knowledge.api.knowledge_workflow import KnowledgeWorkflowApi, KnowledgeWorkflowActionApi
from knowledge.serializers.common import get_knowledge_operation_object
from knowledge.serializers.knowledge_workflow import KnowledgeWorkflowSerializer, KnowledgeWorkflowActionSerializer, \
    KnowledgeWorkflowMcpSerializer


class KnowledgeDatasourceFormListView(APIView):
    authentication_classes = [TokenAuth]

    def post(self, request: Request, workspace_id: str, knowledge_id: str, type: str, id: str):
        return result.success(KnowledgeWorkflowSerializer.Datasource(
            data={'type': type, 'id': id, 'params': request.data, 'function_name': 'get_form_list'}).action())


class KnowledgeDatasourceView(APIView):
    def post(self, request: Request, workspace_id: str, knowledge_id: str, type: str, id: str, function_name: str):
        return result.success(KnowledgeWorkflowSerializer.Datasource(
            data={'type': type, 'id': id, 'params': request.data, 'function_name': function_name}).action())


class KnowledgeWorkflowUploadDocumentView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_('Knowledge workflow upload document'),
        summary=_('Knowledge workflow upload document'),
        operation_id=_('Knowledge workflow upload document'),  # type: ignore
        parameters=KnowledgeWorkflowActionApi.get_parameters(),
        request=KnowledgeWorkflowActionApi.get_request(),
        responses=KnowledgeWorkflowActionApi.get_response(),
        tags=[_('Knowledge Base')]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_READ.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_READ.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
            CompareConstants.AND
        ),
    )
    def post(self, request: Request, workspace_id: str, knowledge_id: str):
        return result.success(KnowledgeWorkflowActionSerializer(
            data={'workspace_id': workspace_id, 'knowledge_id': knowledge_id}).upload_document(request.data, True))


class KnowledgeWorkflowActionView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_('Knowledge workflow debug'),
        summary=_('Knowledge workflow debug'),
        operation_id=_('Knowledge workflow debug'),  # type: ignore
        parameters=KnowledgeWorkflowActionApi.get_parameters(),
        request=KnowledgeWorkflowActionApi.get_request(),
        responses=KnowledgeWorkflowActionApi.get_response(),
        tags=[_('Knowledge Base')]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_DOCUMENT_CREATE.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_DOCUMENT_CREATE.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
            CompareConstants.AND
        ),
    )
    def post(self, request: Request, workspace_id: str, knowledge_id: str):
        return result.success(KnowledgeWorkflowActionSerializer(
            data={'workspace_id': workspace_id, 'knowledge_id': knowledge_id}).action(request.data, True))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Get knowledge workflow action'),
            summary=_('Get knowledge workflow action'),
            operation_id=_('Get knowledge workflow action'),  # type: ignore
            parameters=KnowledgeWorkflowActionApi.get_parameters(),
            responses=KnowledgeWorkflowActionApi.get_response(),
            tags=[_('Knowledge Base')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_READ.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_READ.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission(
                [RoleConstants.USER.get_workspace_role()],
                [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                CompareConstants.AND
            ),
        )
        def get(self, request, workspace_id: str, knowledge_id: str, knowledge_action_id: str):
            return result.success(KnowledgeWorkflowActionSerializer.Operate(
                data={'workspace_id': workspace_id, 'knowledge_id': knowledge_id, 'id': knowledge_action_id})
                                  .one())


class KnowledgeWorkflowView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Create knowledge workflow'),
        summary=_('Create knowledge workflow'),
        operation_id=_('Create knowledge workflow'),  # type: ignore
        parameters=KnowledgeWorkflowApi.get_parameters(),
        responses=KnowledgeWorkflowApi.get_response(),
        tags=[_('Knowledge Base')]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_CREATE.get_workspace_permission(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(), RoleConstants.USER.get_workspace_role()
    )
    def post(self, request: Request, workspace_id: str):
        return result.success(KnowledgeWorkflowSerializer.Create(
            data={'user_id': request.user.id, 'workspace_id': workspace_id}
        ).save_workflow(request.data))

    class Publish(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_("Publishing an knowledge"),
            summary=_("Publishing an knowledge"),
            operation_id=_("Publishing an knowledge"),  # type: ignore
            parameters=KnowledgeWorkflowApi.get_parameters(),
            request=None,
            responses=DefaultResultSerializer,
            tags=[_('Knowledge')]  # type: ignore
        )
        @has_permissions(PermissionConstants.KNOWLEDGE_WORKFLOW_EDIT.get_workspace_knowledge_permission(),
                         PermissionConstants.KNOWLEDGE_WORKFLOW_EDIT.get_workspace_permission_workspace_manage_role(),
                         ViewPermission([RoleConstants.USER.get_workspace_role()],
                                        [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                                        CompareConstants.AND),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        @log(menu='Knowledge', operate='Publishing an knowledge',
             get_operation_object=lambda r, k: get_knowledge_operation_object(k.get('knowledge_id')))
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(
                KnowledgeWorkflowSerializer.Operate(
                    data={'knowledge_id': knowledge_id, 'user_id': request.user.id,
                          'workspace_id': workspace_id, }).publish())

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_('Edit knowledge workflow'),
            summary=_('Edit knowledge workflow'),
            operation_id=_('Edit knowledge workflow'),  # type: ignore
            parameters=KnowledgeWorkflowApi.get_parameters(),
            request=KnowledgeWorkflowApi.get_request(),
            responses=KnowledgeWorkflowApi.get_response(),
            tags=[_('Knowledge Base')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_WORKFLOW_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_WORKFLOW_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission(
                [RoleConstants.USER.get_workspace_role()],
                [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                CompareConstants.AND
            )
        )
        @log(
            menu='Knowledge Base', operate="Modify knowledge workflow",
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get('knowledge_id')),
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(KnowledgeWorkflowSerializer.Operate(
                data={'user_id': request.user.id, 'workspace_id': workspace_id, 'knowledge_id': knowledge_id}
            ).edit(request.data))

        @extend_schema(
            methods=['GET'],
            description=_('Get knowledge workflow'),
            summary=_('Get knowledge workflow'),
            operation_id=_('Get knowledge workflow'),  # type: ignore
            parameters=KnowledgeWorkflowApi.get_parameters(),
            responses=KnowledgeWorkflowApi.get_response(),
            tags=[_('Knowledge Base')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_READ.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_READ.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission(
                [RoleConstants.USER.get_workspace_role()],
                [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                CompareConstants.AND
            ),
        )
        def get(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(KnowledgeWorkflowSerializer.Operate(
                data={'user_id': request.user.id, 'workspace_id': workspace_id, 'knowledge_id': knowledge_id}
            ).one())


class KnowledgeWorkflowVersionView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_('Get knowledge workflow version list'),
        summary=_('Get knowledge workflow version list'),
        operation_id=_('Get knowledge workflow version list'),  # type: ignore
        parameters=KnowledgeWorkflowApi.get_parameters(),
        responses=KnowledgeWorkflowApi.get_response(),
        tags=[_('Knowledge Base')]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_READ.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_READ.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
            CompareConstants.AND
        ),
    )
    def get(self, request: Request, workspace_id: str, knowledge_id: str):
        return result.success(KnowledgeWorkflowSerializer.Operate(
            data={'user_id': request.user.id, 'workspace_id': workspace_id, 'knowledge_id': knowledge_id}
        ).one())


class McpServers(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_("speech to text"),
        summary=_("speech to text"),
        operation_id=_("speech to text"),  # type: ignore
        parameters=SpeechToTextAPI.get_parameters(),
        request=SpeechToTextAPI.get_request(),
        responses=SpeechToTextAPI.get_response(),
        tags=[_('Knowledge Base')]  # type: ignore
    )
    @has_permissions(PermissionConstants.KNOWLEDGE_READ.get_workspace_application_permission(),
                     PermissionConstants.KNOWLEDGE_READ.get_workspace_permission_workspace_manage_role(),
                     ViewPermission([RoleConstants.USER.get_workspace_role()],
                                    [PermissionConstants.KNOWLEDGE.get_workspace_application_permission()],
                                    CompareConstants.AND),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def post(self, request: Request, workspace_id, knowledge_id: str):
        return result.success(KnowledgeWorkflowMcpSerializer(
            data={'mcp_servers': request.query_params.get('mcp_servers'), 'workspace_id': workspace_id,
                  'user_id': request.user.id,
                  'knowledge_id': knowledge_id}).get_mcp_servers(request.data))
