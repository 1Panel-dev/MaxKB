from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants, ViewPermission, CompareConstants
from common.log.log import log
from common.result import result
from knowledge.api.knowledge import KnowledgeBaseCreateAPI, KnowledgeWebCreateAPI, KnowledgeTreeReadAPI, \
    KnowledgeEditAPI, KnowledgeReadAPI, KnowledgePageAPI, SyncWebAPI, GenerateRelatedAPI, HitTestAPI, EmbeddingAPI, \
    GetModelAPI, KnowledgeExportAPI
from knowledge.models import KnowledgeScope
from knowledge.serializers.common import get_knowledge_operation_object
from knowledge.serializers.knowledge import KnowledgeSerializer
from models_provider.serializers.model_serializer import ModelSerializer


class KnowledgeView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_('Get knowledge by folder'),
        summary=_('Get knowledge by folder'),
        operation_id=_('Get knowledge by folder'),  # type: ignore
        parameters=KnowledgeTreeReadAPI.get_parameters(),
        responses=KnowledgeTreeReadAPI.get_response(),
        tags=[_('Knowledge Base')]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_READ.get_workspace_permission(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(), RoleConstants.USER.get_workspace_role()
    )
    def get(self, request: Request, workspace_id: str):
        return result.success(KnowledgeSerializer.Query(
            data={
                'workspace_id': workspace_id,
                'folder_id': request.query_params.get('folder_id'),
                'name': request.query_params.get('name'),
                'desc': request.query_params.get("desc"),
                'scope': KnowledgeScope.WORKSPACE,
                'user_id': request.user.id
            }
        ).list())

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_('Edit knowledge'),
            summary=_('Edit knowledge'),
            operation_id=_('Edit knowledge'),  # type: ignore
            parameters=KnowledgeEditAPI.get_parameters(),
            request=KnowledgeEditAPI.get_request(),
            responses=KnowledgeEditAPI.get_response(),
            tags=[_('Knowledge Base')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='Knowledge Base', operate="Modify knowledge base information",
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get('knowledge_id')),

        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(KnowledgeSerializer.Operate(
                data={'user_id': request.user.id, 'workspace_id': workspace_id, 'knowledge_id': knowledge_id}
            ).edit(request.data))

        @extend_schema(
            methods=['DELETE'],
            description=_('Delete knowledge'),
            summary=_('Delete knowledge'),
            operation_id=_('Delete knowledge'),  # type: ignore
            parameters=KnowledgeBaseCreateAPI.get_parameters(),
            request=KnowledgeBaseCreateAPI.get_request(),
            responses=KnowledgeBaseCreateAPI.get_response(),
            tags=[_('Knowledge Base')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DELETE.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DELETE.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='Knowledge Base', operate="Delete knowledge base",
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get('knowledge_id')),

        )
        def delete(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(KnowledgeSerializer.Operate(
                data={'user_id': request.user.id, 'workspace_id': workspace_id, 'knowledge_id': knowledge_id}
            ).delete())

        @extend_schema(
            methods=['GET'],
            description=_('Get knowledge'),
            summary=_('Get knowledge'),
            operation_id=_('Get knowledge'),  # type: ignore
            parameters=KnowledgeReadAPI.get_parameters(),
            responses=KnowledgeReadAPI.get_response(),
            tags=[_('Knowledge Base')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_READ.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_READ.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
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
            operation_id=_('Get the knowledge base paginated list'),  # type: ignore
            parameters=KnowledgePageAPI.get_parameters(),
            responses=KnowledgePageAPI.get_response(),
            tags=[_('Knowledge Base')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_READ.get_workspace_permission(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(), RoleConstants.USER.get_workspace_role()
        )
        def get(self, request: Request, workspace_id: str, current_page: int, page_size: int):
            return result.success(KnowledgeSerializer.Query(
                data={
                    'workspace_id': workspace_id,
                    'folder_id': request.query_params.get('folder_id'),
                    'name': request.query_params.get('name'),
                    'desc': request.query_params.get("desc"),
                    'scope': KnowledgeScope.WORKSPACE,
                    'user_id': request.user.id,
                    'create_user': request.query_params.get('create_user'),
                }
            ).page(current_page, page_size))

    class SyncWeb(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            summary=_("Synchronize the knowledge base of the website"),
            description=_("Synchronize the knowledge base of the website"),
            operation_id=_("Synchronize the knowledge base of the website"),  # type: ignore
            parameters=SyncWebAPI.get_parameters(),
            request=SyncWebAPI.get_request(),
            responses=SyncWebAPI.get_response(),
            tags=[_('Knowledge Base')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_SYNC.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_SYNC.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='Knowledge Base', operate="Synchronize the knowledge base of the website",
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get('knowledge_id')),

        )
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
            operation_id=_('Hit test list'),  # type: ignore
            parameters=HitTestAPI.get_parameters(),
            request=HitTestAPI.get_request(),
            responses=HitTestAPI.get_response(),
            tags=[_('Knowledge Base')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_HIT_TEST.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_HIT_TEST.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(KnowledgeSerializer.HitTest(
                data={
                    'workspace_id': workspace_id,
                    'knowledge_id': knowledge_id,
                    'user_id': request.user.id,
                    "query_text": request.data.get("query_text"),
                    "top_number": request.data.get("top_number"),
                    'similarity': request.data.get('similarity'),
                    'search_mode': request.data.get('search_mode')
                }
            ).hit_test())

    class Embedding(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            summary=_('Re-vectorize'),
            description=_('Re-vectorize'),
            operation_id=_('Re-vectorize'),  # type: ignore
            parameters=EmbeddingAPI.get_parameters(),
            request=EmbeddingAPI.get_request(),
            responses=EmbeddingAPI.get_response(),
            tags=[_('Knowledge Base')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_VECTOR.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_VECTOR.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='Knowledge Base', operate='Re-vectorize',
            get_operation_object=lambda r, k: get_knowledge_operation_object(k.get('knowledge_id')),

        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(KnowledgeSerializer.Operate(
                data={'knowledge_id': knowledge_id, 'workspace_id': workspace_id, 'user_id': request.user.id}
            ).embedding())

    class Export(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_('Export knowledge base'),
            operation_id=_('Export knowledge base'),  # type: ignore
            parameters=KnowledgeExportAPI.get_parameters(),
            responses=KnowledgeExportAPI.get_response(),
            tags=[_('Knowledge Base')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_EXPORT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_EXPORT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='Knowledge Base', operate="Export knowledge base",
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get('knowledge_id')),

        )
        def get(self, request: Request, workspace_id: str, knowledge_id: str):
            return KnowledgeSerializer.Operate(data={
                'workspace_id': workspace_id, 'knowledge_id': knowledge_id, 'user_id': request.user.id
            }).export_excel()

    class ExportZip(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_('Export knowledge base containing images'),
            operation_id=_('Export knowledge base containing images'),  # type: ignore
            parameters=KnowledgeExportAPI.get_parameters(),
            responses=KnowledgeExportAPI.get_response(),
            tags=[_('Knowledge Base')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_EXPORT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_EXPORT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='Knowledge Base', operate="Export knowledge base containing images",
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get('knowledge_id')),

        )
        def get(self, request: Request, workspace_id: str, knowledge_id: str):
            return KnowledgeSerializer.Operate(data={
                'workspace_id': workspace_id, 'knowledge_id': knowledge_id, 'user_id': request.user.id
            }).export_zip()

    class GenerateRelated(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            summary=_('Generate related'),
            description=_('Generate related'),
            operation_id=_('Generate related'),  # type: ignore
            parameters=GenerateRelatedAPI.get_parameters(),
            request=GenerateRelatedAPI.get_request(),
            responses=GenerateRelatedAPI.get_response(),
            tags=[_('Knowledge Base')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_GENERATE.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_GENERATE.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='document', operate='Generate related documents',
            get_operation_object=lambda r, k: get_knowledge_operation_object(k.get('knowledge_id')),

        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(KnowledgeSerializer.Operate(
                data={'knowledge_id': knowledge_id, 'workspace_id': workspace_id, 'user_id': request.user.id}
            ).generate_related(request.data))

    class Model(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            summary=_('Get model for knowledge base'),
            description=_('Get model for knowledge base'),
            operation_id=_('Get model for knowledge base'),  # type: ignore
            parameters=GetModelAPI.get_parameters(),
            responses=GetModelAPI.get_response(),
            tags=[_('Knowledge Base')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_EDIT.get_workspace_permission(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(), RoleConstants.USER.get_workspace_role()
        )
        def get(self, request: Request, workspace_id: str):
            return result.success(ModelSerializer.Query(
                data={
                    'workspace_id': workspace_id,
                    'model_type': 'LLM'
                }
            ).list(workspace_id, True))

    class EmbeddingModel(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            summary=_('Get embedding model for knowledge base'),
            description=_('Get embedding model for knowledge base'),
            operation_id=_('Get embedding model for knowledge base'),  # type: ignore
            parameters=GetModelAPI.get_parameters(),
            responses=GetModelAPI.get_response(),
            tags=[_('Knowledge Base')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_EDIT.get_workspace_permission(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(), RoleConstants.USER.get_workspace_role()
        )
        def get(self, request: Request, workspace_id: str):
            return result.success(ModelSerializer.Query(
                data={
                    'workspace_id': workspace_id,
                    'model_type': 'EMBEDDING'
                }
            ).list(workspace_id, True))

    class Tags(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Get all tags of knowledge base'),
            summary=_('Get all tags of knowledge base'),
            operation_id=_('Get all tags of knowledge base'),  # type: ignore
            parameters=KnowledgeReadAPI.get_parameters(),
            responses=KnowledgeReadAPI.get_response(),
            tags=[_('Knowledge Base')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_READ.get_workspace_permission(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(), RoleConstants.USER.get_workspace_role()
        )
        def get(self, request: Request, workspace_id: str):
            return result.success(KnowledgeSerializer.Tags(data={
                'user_id': request.user.id,
                'workspace_id': workspace_id,
                'knowledge_ids': request.query_params.getlist('knowledge_ids[]')
            }).list())


class KnowledgeBaseView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Create base knowledge'),
        summary=_('Create base knowledge'),
        operation_id=_('Create base knowledge'),  # type: ignore
        parameters=KnowledgeBaseCreateAPI.get_parameters(),
        request=KnowledgeBaseCreateAPI.get_request(),
        responses=KnowledgeBaseCreateAPI.get_response(),
        tags=[_('Knowledge Base')]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_CREATE.get_workspace_permission(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(), RoleConstants.USER.get_workspace_role()
    )
    @log(
        menu='knowledge Base', operate='Create base knowledge',
        get_operation_object=lambda r, k: {'name': r.data.get('name'), 'desc': r.data.get('desc')},

    )
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
        operation_id=_('Create web knowledge'),  # type: ignore
        parameters=KnowledgeWebCreateAPI.get_parameters(),
        request=KnowledgeWebCreateAPI.get_request(),
        responses=KnowledgeWebCreateAPI.get_response(),
        tags=[_('Knowledge Base')]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_CREATE.get_workspace_permission(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(), RoleConstants.USER.get_workspace_role()
    )
    @log(
        menu='Knowledge Base', operate="Create a web site knowledge base",
        get_operation_object=lambda r, k: {'name': r.data.get('name'), 'desc': r.data.get('desc'),
                                           'first_list': r.FILES.getlist('file'),
                                           'meta': {'source_url': r.data.get('source_url'),
                                                    'selector': r.data.get('selector'),
                                                    'embedding_model_id': r.data.get('embedding_model_id')}}
        ,
    )
    def post(self, request: Request, workspace_id: str):
        return result.success(KnowledgeSerializer.Create(
            data={'user_id': request.user.id, 'workspace_id': workspace_id}
        ).save_web(request.data))
