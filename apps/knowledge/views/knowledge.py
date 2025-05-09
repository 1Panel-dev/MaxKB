from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants
from common.result import result
from knowledge.api.knowledge import KnowledgeBaseCreateAPI, KnowledgeWebCreateAPI, KnowledgeTreeReadAPI, \
    KnowledgeEditAPI, KnowledgeReadAPI, KnowledgePageAPI, SyncWebAPI, GenerateRelatedAPI, HitTestAPI, EmbeddingAPI
from knowledge.serializers.knowledge import KnowledgeSerializer


class KnowledgeView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_('Get knowledge by folder'),
        summary=_('Get knowledge by folder'),
        operation_id=_('Get knowledge by folder'),
        parameters=KnowledgeTreeReadAPI.get_parameters(),
        responses=KnowledgeTreeReadAPI.get_response(),
        tags=[_('Knowledge Base')]
    )
    @has_permissions(PermissionConstants.KNOWLEDGE_READ.get_workspace_permission())
    def get(self, request: Request, workspace_id: str):
        return result.success(KnowledgeSerializer.Query(
            data={
                'workspace_id': workspace_id,
                'folder_id': request.query_params.get('folder_id'),
                'name': request.query_params.get('name'),
                'desc': request.query_params.get("desc"),
                'user_id': request.query_params.get('user_id')
            }
        ).list())

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_('Edit knowledge'),
            summary=_('Edit knowledge'),
            operation_id=_('Edit knowledge'),
            parameters=KnowledgeEditAPI.get_parameters(),
            request=KnowledgeEditAPI.get_request(),
            responses=KnowledgeEditAPI.get_response(),
            tags=[_('Knowledge Base')]
        )
        @has_permissions(PermissionConstants.KNOWLEDGE_EDIT.get_workspace_permission())
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(KnowledgeSerializer.Operate(
                data={'user_id': request.user.id, 'workspace_id': workspace_id, 'knowledge_id': knowledge_id}
            ).edit(request.data))

        @extend_schema(
            methods=['DELETE'],
            description=_('Delete knowledge'),
            summary=_('Delete knowledge'),
            operation_id=_('Delete knowledge'),
            parameters=KnowledgeBaseCreateAPI.get_parameters(),
            request=KnowledgeBaseCreateAPI.get_request(),
            responses=KnowledgeBaseCreateAPI.get_response(),
            tags=[_('Knowledge Base')]
        )
        @has_permissions(PermissionConstants.KNOWLEDGE_DELETE.get_workspace_permission())
        def delete(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(KnowledgeSerializer.Operate(
                data={'user_id': request.user.id, 'workspace_id': workspace_id, 'knowledge_id': knowledge_id}
            ).delete())

        @extend_schema(
            methods=['GET'],
            description=_('Get knowledge'),
            summary=_('Get knowledge'),
            operation_id=_('Get knowledge'),
            parameters=KnowledgeReadAPI.get_parameters(),
            responses=KnowledgeReadAPI.get_response(),
            tags=[_('Knowledge Base')]
        )
        @has_permissions(PermissionConstants.KNOWLEDGE_DELETE.get_workspace_permission())
        def get(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(KnowledgeSerializer.Operate(
                data={'user_id': request.user.id, 'workspace_id': workspace_id, 'knowledge_id': knowledge_id}
            ).one())

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Get the knowledge base paginated list'),
            summary=_('Get the knowledge base paginated list'),
            operation_id=_('Get the knowledge base paginated list'),
            parameters=KnowledgePageAPI.get_parameters(),
            responses=KnowledgePageAPI.get_response(),
            tags=[_('Knowledge Base')]
        )
        @has_permissions(PermissionConstants.KNOWLEDGE_READ.get_workspace_permission())
        def get(self, request: Request, workspace_id: str, current_page: int, page_size: int):
            return result.success(KnowledgeSerializer.Query(
                data={
                    'workspace_id': workspace_id,
                    'folder_id': request.query_params.get('folder_id'),
                    'name': request.query_params.get('name'),
                    'desc': request.query_params.get("desc"),
                    'user_id': request.query_params.get('user_id')
                }
            ).page(current_page, page_size))

    class SyncWeb(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            summary=_("Synchronize the knowledge base of the website"),
            description=_("Synchronize the knowledge base of the website"),
            operation_id=_("Synchronize the knowledge base of the website"),
            parameters=SyncWebAPI.get_parameters(),
            request=SyncWebAPI.get_request(),
            responses=SyncWebAPI.get_response(),
            tags=[_('Knowledge Base')]
        )
        @has_permissions(PermissionConstants.KNOWLEDGE_EDIT.get_workspace_permission())
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(KnowledgeSerializer.SyncWeb(
                data={
                    'workspace_id': workspace_id,
                    'sync_type': request.query_params.get('sync_type'),
                    'knowledge_id': knowledge_id,
                    'user_id': str(request.user.id)
                }
            ).sync())

    class HitTest(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            summary=_('Hit test list'),
            description=_('Hit test list'),
            operation_id=_('Hit test list'),
            parameters=HitTestAPI.get_parameters(),
            request=HitTestAPI.get_request(),
            responses=HitTestAPI.get_response(),
            tags=[_('Knowledge Base')]
        )
        @has_permissions(PermissionConstants.KNOWLEDGE_EDIT.get_workspace_permission())
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(KnowledgeSerializer.HitTest(
                data={
                    'workspace_id': workspace_id,
                    'knowledge_id': knowledge_id,
                    'user_id': request.user.id,
                    "query_text": request.query_params.get("query_text"),
                    "top_number": request.query_params.get("top_number"),
                    'similarity': request.query_params.get('similarity'),
                    'search_mode': request.query_params.get('search_mode')
                }
            ).hit_test())

    class Embedding(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            summary=_('Re-vectorize'),
            description=_('Re-vectorize'),
            operation_id=_('Re-vectorize'),
            parameters=EmbeddingAPI.get_parameters(),
            request=EmbeddingAPI.get_request(),
            responses=EmbeddingAPI.get_response(),
            tags=[_('Knowledge Base')]
        )
        @has_permissions(PermissionConstants.KNOWLEDGE_EDIT.get_workspace_permission())
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(KnowledgeSerializer.Operate(
                data={'knowledge_id': knowledge_id, 'workspace_id': workspace_id, 'user_id': request.user.id}
            ).embedding())

    class GenerateRelated(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            summary=_('Generate related'),
            description=_('Generate related'),
            operation_id=_('Generate related'),
            parameters=GenerateRelatedAPI.get_parameters(),
            request=GenerateRelatedAPI.get_request(),
            responses=GenerateRelatedAPI.get_response(),
            tags=[_('Knowledge Base')]
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(KnowledgeSerializer.Operate(
                data={'knowledge_id': knowledge_id, 'workspace_id': workspace_id, 'user_id': request.user.id}
            ).generate_related(request.data))


class KnowledgeBaseView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Create base knowledge'),
        summary=_('Create base knowledge'),
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
        ).save_base(request.data))


class KnowledgeWebView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Create web knowledge'),
        summary=_('Create web knowledge'),
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
        ).save_web(request.data))
