from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants
from common.result import result
from knowledge.api.knowledge import KnowledgeBaseCreateAPI, KnowledgeLarkCreateAPI, \
    KnowledgeWebCreateAPI, KnowledgeTreeReadAPI
from knowledge.serializers.knowledge import KnowledgeSerializer, KnowledgeTreeSerializer


class KnowledgeView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_('Get knowledge by module'),
        operation_id=_('Get knowledge by module'),
        parameters=KnowledgeTreeReadAPI.get_parameters(),
        responses=KnowledgeTreeReadAPI.get_response(),
        tags=[_('Knowledge Base')]
    )
    @has_permissions(PermissionConstants.KNOWLEDGE_READ.get_workspace_permission())
    def get(self, request: Request, workspace_id: str):
        return result.success(KnowledgeTreeSerializer(
            data={'workspace_id': workspace_id}
        ).get_knowledge_list(request.query_params.get('module_id')))


class KnowledgeBaseView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Create base knowledge'),
        operation_id=_('Create base knowledge'),
        parameters=KnowledgeBaseCreateAPI.get_parameters(),
        request=KnowledgeBaseCreateAPI.get_request(),
        responses=KnowledgeBaseCreateAPI.get_response(),
        tags=[_('Knowledge Base')]
    )
    @has_permissions(PermissionConstants.KNOWLEDGE_CREATE.get_workspace_permission())
    def post(self, request: Request, workspace_id: str):
        return result.success(KnowledgeSerializer.Create(
            data={'user_id': request.user.id, 'workspace_id': workspace_id}
        ).insert(request.data))


class KnowledgeWebView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Create web knowledge'),
        operation_id=_('Create web knowledge'),
        parameters=KnowledgeWebCreateAPI.get_parameters(),
        request=KnowledgeWebCreateAPI.get_request(),
        responses=KnowledgeWebCreateAPI.get_response(),
        tags=[_('Knowledge Base')]
    )
    @has_permissions(PermissionConstants.KNOWLEDGE_CREATE.get_workspace_permission())
    def post(self, request: Request, workspace_id: str):
        return result.success(KnowledgeSerializer.Create(
            data={'user_id': request.user.id, 'workspace_id': workspace_id}
        ).insert(request.data))

