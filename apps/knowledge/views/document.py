from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants, ViewPermission, CompareConstants
from common.log.log import log
from common.result import result
from knowledge.api.document import DocumentSplitAPI, DocumentBatchAPI, DocumentBatchCreateAPI, DocumentCreateAPI, \
    DocumentReadAPI, DocumentEditAPI, DocumentDeleteAPI, TableDocumentCreateAPI, QaDocumentCreateAPI, \
    WebDocumentCreateAPI, CancelTaskAPI, BatchCancelTaskAPI, SyncWebAPI, RefreshAPI, BatchEditHitHandlingAPI, \
    DocumentTreeReadAPI, DocumentSplitPatternAPI, BatchRefreshAPI, BatchGenerateRelatedAPI, TemplateExportAPI, \
    DocumentExportAPI, DocumentMigrateAPI, DocumentDownloadSourceAPI, DocumentTagsAPI
from knowledge.serializers.common import get_knowledge_operation_object
from knowledge.serializers.document import DocumentSerializers
from knowledge.views.common import get_knowledge_document_operation_object, get_document_operation_object_batch, \
    get_document_operation_object


class DocumentView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Create document'),
        summary=_('Create document'),
        operation_id=_('Create document'),  # type: ignore
        request=DocumentCreateAPI.get_request(),
        parameters=DocumentCreateAPI.get_parameters(),
        responses=DocumentCreateAPI.get_response(),
        tags=[_('Knowledge Base/Documentation')]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_DOCUMENT_CREATE.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_DOCUMENT_CREATE.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission([RoleConstants.USER.get_workspace_role()],
                       [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
    )
    @log(menu='document', operate="Create document",
         get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
             get_knowledge_operation_object(keywords.get('knowledge_id')),
             {'name': r.data.get('name')}), )
    def post(self, request: Request, workspace_id: str, knowledge_id: str):
        return result.success(
            DocumentSerializers.Create(
                data={'workspace_id': workspace_id, 'knowledge_id': knowledge_id},
            ).save(request.data))

    @extend_schema(
        methods=['GET'],
        description=_('Get document'),
        summary=_('Get document'),
        operation_id=_('Get document'),  # type: ignore
        parameters=DocumentTreeReadAPI.get_parameters(),
        responses=DocumentTreeReadAPI.get_response(),
        tags=[_('Knowledge Base/Documentation')]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_DOCUMENT_READ.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_DOCUMENT_READ.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission([RoleConstants.USER.get_workspace_role()],
                       [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
    )
    def get(self, request: Request, workspace_id: str, knowledge_id: str):
        return result.success(DocumentSerializers.Query(
            data={
                'workspace_id': workspace_id,
                'knowledge_id': knowledge_id,
                'folder_id': request.query_params.get('folder_id'),
                'name': request.query_params.get('name'),
                'desc': request.query_params.get("desc"),
                'user_id': request.query_params.get('user_id')
            }
        ).list())

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            description=_('Get document details'),
            summary=_('Get document details'),
            operation_id=_('Get document details'),  # type: ignore
            parameters=DocumentReadAPI.get_parameters(),
            responses=DocumentReadAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_READ.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_READ.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        def get(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
            operate = DocumentSerializers.Operate(data={
                'document_id': document_id, 'knowledge_id': knowledge_id, 'workspace_id': workspace_id
            })
            operate.is_valid(raise_exception=True)
            return result.success(operate.one())

        @extend_schema(
            description=_('Modify document'),
            summary=_('Modify document'),
            operation_id=_('Modify document'),  # type: ignore
            parameters=DocumentEditAPI.get_parameters(),
            request=DocumentEditAPI.get_request(),
            responses=DocumentEditAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='document', operate="Modify document",
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object(keywords.get('document_id'))
            ),
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
            return result.success(DocumentSerializers.Operate(data={
                'document_id': document_id, 'knowledge_id': knowledge_id, 'workspace_id': workspace_id
            }).edit(request.data, with_valid=True))

        @extend_schema(
            description=_('Delete document'),
            summary=_('Delete document'),
            operation_id=_('Delete document'),  # type: ignore
            parameters=DocumentDeleteAPI.get_parameters(),
            responses=DocumentDeleteAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_DELETE.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_DELETE.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='document', operate="Delete document",
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object(keywords.get('document_id'))
            ),
        )
        def delete(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
            operate = DocumentSerializers.Operate(data={
                'document_id': document_id, 'knowledge_id': knowledge_id, 'workspace_id': workspace_id
            })
            operate.is_valid(raise_exception=True)
            return result.success(operate.delete())

    class Split(APIView):
        authentication_classes = [TokenAuth]
        parser_classes = [MultiPartParser]

        @extend_schema(
            methods=['POST'],
            description=_('Segmented document'),
            summary=_('Segmented document'),
            operation_id=_('Segmented document'),  # type: ignore
            parameters=DocumentSplitAPI.get_parameters(),
            request=DocumentSplitAPI.get_request(),
            responses=DocumentSplitAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_READ.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_READ.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        def post(self, request: Request, workspace_id: str, knowledge_id: str):
            split_data = {'file': request.FILES.getlist('file')}
            request_data = request.data
            if 'patterns' in request.data and request.data.get('patterns') is not None and len(
                    request.data.get('patterns')) > 0:
                split_data.__setitem__('patterns', request_data.getlist('patterns'))
            if 'limit' in request.data:
                split_data.__setitem__('limit', request_data.get('limit'))
            if 'with_filter' in request.data:
                split_data.__setitem__('with_filter', request_data.get('with_filter'))
            return result.success(DocumentSerializers.Split(data={
                'workspace_id': workspace_id,
                'knowledge_id': knowledge_id,
            }).parse(split_data))

    class SplitPattern(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_('Get a list of segment IDs'),
            description=_('Get a list of segment IDs'),
            operation_id=_('Get a list of segment IDs'),  # type: ignore
            parameters=DocumentSplitPatternAPI.get_parameters(),
            responses=DocumentSplitPatternAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        def get(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(DocumentSerializers.SplitPattern(
                data={'knowledge_id': knowledge_id, 'workspace_id': workspace_id}
            ).list())

    class BatchEditHitHandling(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            summary=_('Modify document hit processing methods in batches'),
            description=_('Modify document hit processing methods in batches'),
            operation_id=_('Modify document hit processing methods in batches'),  # type: ignore
            request=BatchEditHitHandlingAPI.get_request(),
            parameters=BatchEditHitHandlingAPI.get_parameters(),
            responses=BatchEditHitHandlingAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='document', operate="Modify document hit processing methods in batches",
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object_batch(r.data.get('id_list'))),

        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(DocumentSerializers.Batch(
                data={'knowledge_id': knowledge_id, 'workspace_id': workspace_id}
            ).batch_edit_hit_handling(request.data))

    class SyncWeb(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_('Synchronize web site types'),
            summary=_('Synchronize web site types'),
            operation_id=_('Synchronize web site types'),  # type: ignore
            parameters=SyncWebAPI.get_parameters(),
            request=SyncWebAPI.get_request(),
            responses=SyncWebAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_SYNC.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_SYNC.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='document', operate="Synchronize web site types",
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object(keywords.get('document_id'))
            ),
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
            return result.success(DocumentSerializers.Sync(
                data={'document_id': document_id, 'knowledge_id': knowledge_id, 'workspace_id': workspace_id}
            ).sync())

    class Refresh(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            summary=_('Refresh document vector library'),
            description=_('Refresh document vector library'),
            operation_id=_('Refresh document vector library'),  # type: ignore
            parameters=RefreshAPI.get_parameters(),
            request=RefreshAPI.get_request(),
            responses=RefreshAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_VECTOR.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_VECTOR.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='document', operate="Refresh document vector library",
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object(keywords.get('document_id'))
            ),
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
            return result.success(DocumentSerializers.Operate(
                data={'document_id': document_id, 'knowledge_id': knowledge_id, 'workspace_id': workspace_id}
            ).refresh(request.data.get('state_list')))

    class CancelTask(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_('Cancel task'),
            description=_('Cancel task'),
            operation_id=_('Cancel task'),  # type: ignore
            parameters=CancelTaskAPI.get_parameters(),
            request=CancelTaskAPI.get_request(),
            responses=CancelTaskAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='document', operate="Cancel task",
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object(keywords.get('document_id'))
            ),
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
            return result.success(DocumentSerializers.Operate(
                data={'document_id': document_id, 'knowledge_id': knowledge_id, 'workspace_id': workspace_id}
            ).cancel(request.data))

    class BatchCancelTask(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_('Cancel tasks in batches'),
            description=_('Cancel tasks in batches'),
            operation_id=_('Cancel tasks in batches'),  # type: ignore
            parameters=BatchCancelTaskAPI.get_parameters(),
            request=BatchCancelTaskAPI.get_request(),
            responses=BatchCancelTaskAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='document', operate="Cancel tasks in batches",
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object_batch(r.data.get('id_list'))
            ),
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(DocumentSerializers.Batch(data={
                'knowledge_id': knowledge_id, 'workspace_id': workspace_id}
            ).batch_cancel(request.data))

    class BatchCreate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_('Create documents in batches'),
            summary=_('Create documents in batches'),
            operation_id=_('Create documents in batches'),  # type: ignore
            request=DocumentBatchCreateAPI.get_request(),
            parameters=DocumentBatchCreateAPI.get_parameters(),
            responses=DocumentBatchCreateAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_CREATE.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_CREATE.get_workspace_permission_workspace_manage_role(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='document', operate="Create documents in batches",
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                {'name': f'[{",".join([document.get("name") for document in r.data])}]',
                 'document_list': r.data}),
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(DocumentSerializers.Batch(
                data={'knowledge_id': knowledge_id, 'workspace_id': workspace_id}
            ).batch_save(request.data))

    class BatchSync(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_('Batch sync documents'),
            summary=_('Batch sync documents'),
            operation_id=_('Batch sync documents'),  # type: ignore
            request=DocumentBatchAPI.get_request(),
            parameters=DocumentBatchAPI.get_parameters(),
            responses=DocumentBatchAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_SYNC.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_SYNC.get_workspace_permission_workspace_manage_role(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='document', operate="Batch sync documents",
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object_batch(r.data.get('id_list'))),

        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(DocumentSerializers.Batch(
                data={'knowledge_id': knowledge_id, 'workspace_id': workspace_id}
            ).batch_sync(request.data))

    class BatchDelete(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_('Delete documents in batches'),
            summary=_('Delete documents in batches'),
            operation_id=_('Delete documents in batches'),  # type: ignore
            request=DocumentBatchAPI.get_request(),
            parameters=DocumentBatchAPI.get_parameters(),
            responses=DocumentBatchAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_DELETE.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_DELETE.get_workspace_permission_workspace_manage_role(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='document', operate="Delete documents in batches",
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object_batch(r.data.get('id_list'))),

        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(DocumentSerializers.Batch(
                data={'workspace_id': workspace_id, 'knowledge_id': knowledge_id}
            ).batch_delete(request.data))

    class BatchRefresh(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            summary=_('Batch refresh document vector library'),
            operation_id=_('Batch refresh document vector library'),  # type: ignore
            request=BatchRefreshAPI.get_request(),
            parameters=BatchRefreshAPI.get_parameters(),
            responses=BatchRefreshAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_VECTOR.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_VECTOR.get_workspace_permission_workspace_manage_role(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='document', operate="Batch refresh document vector library",
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object_batch(r.data.get('id_list'))
            ),
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(
                DocumentSerializers.Batch(
                    data={'workspace_id': workspace_id, 'knowledge_id': knowledge_id}
                ).batch_refresh(request.data))

    class BatchAddTag(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['POST'],
            summary=_('Batch add tags to documents'),
            operation_id=_('Batch add tags to documents'),  # type: ignore
            request=DocumentTagsAPI.get_request(),
            parameters=DocumentTagsAPI.get_parameters(),
            responses=DocumentTagsAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_TAG.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_TAG.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='document', operate="Batch add tags to documents",
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object_batch(r.data.get('document_ids'))
            ),
        )
        def post(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(DocumentSerializers.Batch(
                data={'workspace_id': workspace_id, 'knowledge_id': knowledge_id}
            ).batch_add_tag(request.data))

    class BatchGenerateRelated(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            summary=_('Batch generate related documents'),
            description=_('Batch generate related documents'),
            operation_id=_('Batch generate related documents'),  # type: ignore
            request=BatchGenerateRelatedAPI.get_request(),
            parameters=BatchGenerateRelatedAPI.get_parameters(),
            responses=BatchGenerateRelatedAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_GENERATE.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_GENERATE.get_workspace_permission_workspace_manage_role(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='document', operate="Batch generate related documents",
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object_batch(r.data.get('document_id_list'))
            ),
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(DocumentSerializers.BatchGenerateRelated(
                data={'workspace_id': workspace_id, 'knowledge_id': knowledge_id}
            ).batch_generate_related(request.data))

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Get document by pagination'),
            summary=_('Get document by pagination'),
            operation_id=_('Get document by pagination'),  # type: ignore
            parameters=DocumentTreeReadAPI.get_parameters(),
            responses=DocumentTreeReadAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_READ.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_READ.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        def get(self, request: Request, workspace_id: str, knowledge_id: str, current_page: int, page_size: int):
            return result.success(DocumentSerializers.Query(
                data={
                    'workspace_id': workspace_id,
                    'knowledge_id': knowledge_id,
                    'folder_id': request.query_params.get('folder_id'),
                    'name': request.query_params.get('name'),
                    'tag': request.query_params.get('tag'),
                    'desc': request.query_params.get("desc"),
                    'user_id': request.query_params.get('user_id'),
                    'status': request.query_params.get('status'),
                    'is_active': request.query_params.get('is_active'),
                    'hit_handling_method': request.query_params.get('hit_handling_method'),
                    'order_by': request.query_params.get('order_by'),
                }
            ).page(current_page, page_size))

    class Export(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_('Export document'),
            operation_id=_('Export document'),  # type: ignore
            parameters=DocumentExportAPI.get_parameters(),
            responses=DocumentExportAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_EXPORT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_EXPORT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='document', operate="Export document",
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object(keywords.get('document_id'))
            ),
        )
        def get(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
            return DocumentSerializers.Operate(data={
                'workspace_id': workspace_id, 'document_id': document_id, 'knowledge_id': knowledge_id
            }).export()

    class ExportZip(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_('Export Zip document'),
            operation_id=_('Export Zip document'),  # type: ignore
            parameters=DocumentExportAPI.get_parameters(),
            responses=DocumentExportAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_EXPORT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_EXPORT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='document', operate="Export Zip document",
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object(keywords.get('document_id'))
            ),
        )
        def get(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
            return DocumentSerializers.Operate(data={
                'workspace_id': workspace_id, 'document_id': document_id, 'knowledge_id': knowledge_id
            }).export_zip()

    class DownloadSourceFile(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_('Download source file'),
            operation_id=_('Download source file'),  # type: ignore
            parameters=DocumentDownloadSourceAPI.get_parameters(),
            responses=DocumentDownloadSourceAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_DOWNLOAD_SOURCE_FILE.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_DOWNLOAD_SOURCE_FILE.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        def get(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
            return DocumentSerializers.Operate(data={
                'workspace_id': workspace_id, 'document_id': document_id, 'knowledge_id': knowledge_id
            }).download_source_file()

    class ReplaceSourceFile(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_('Replace source file'),
            operation_id=_('Replace source file'),  # type: ignore
            parameters=DocumentDownloadSourceAPI.get_parameters(),
            responses=DocumentDownloadSourceAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_REPLACE.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_REPLACE.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        def post(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
            return result.success(DocumentSerializers.ReplaceSourceFile(data={
                'workspace_id': workspace_id,
                'document_id': document_id,
                'knowledge_id': knowledge_id,
                'file': request.FILES.get('file')
            }).replace())

    class Tags(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_('Get document tags'),
            description=_('Get document tags'),
            operation_id=_('Get document tags'),  # type: ignore
            parameters=DocumentTagsAPI.get_parameters(),
            responses=DocumentTagsAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_TAG.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_TAG.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        def get(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
            return result.success(DocumentSerializers.Tags(data={
                'workspace_id': workspace_id, 'knowledge_id': knowledge_id, 'document_id': document_id,
                'name': request.query_params.get('name')
            }).list())

        @extend_schema(
            summary=_('Add document tags'),
            description=_('Add document tags'),
            operation_id=_('Add document tags'),  # type: ignore
            parameters=DocumentTagsAPI.get_parameters(),
            responses=DocumentTagsAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_TAG.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_TAG.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        def post(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
            return result.success(DocumentSerializers.AddTags(data={
                'workspace_id': workspace_id, 'knowledge_id': knowledge_id, 'document_id': document_id,
                'tag_ids': request.data
            }).add_tags())

        class BatchDelete(APIView):
            authentication_classes = [TokenAuth]

            @extend_schema(
                summary=_('Delete document tags'),
                description=_('Delete document tags'),
                operation_id=_('Delete document tags'),  # type: ignore
                parameters=DocumentTagsAPI.get_parameters(),
                request=DocumentTagsAPI.get_request(),
                responses=DocumentTagsAPI.get_response(),
                tags=[_('Knowledge Base/Documentation')]  # type: ignore
            )
            @has_permissions(
                PermissionConstants.KNOWLEDGE_DOCUMENT_TAG.get_workspace_knowledge_permission(),
                PermissionConstants.KNOWLEDGE_DOCUMENT_TAG.get_workspace_permission_workspace_manage_role(),
                RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
                ViewPermission([RoleConstants.USER.get_workspace_role()],
                               [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                               CompareConstants.AND),
            )
            @log(
                menu='document', operate="Delete document tags",
                get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                    get_knowledge_operation_object(keywords.get('knowledge_id')),
                    get_document_operation_object(keywords.get('document_id'))
                ),
            )
            def put(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
                return result.success(DocumentSerializers.DeleteTags(data={
                    'workspace_id': workspace_id,
                    'knowledge_id': knowledge_id,
                    'document_id': document_id,
                    'tag_ids': request.data
                }).delete_tags())

    class Migrate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_('Migrate documents in batches'),
            operation_id=_('Migrate documents in batches'),  # type: ignore
            parameters=DocumentMigrateAPI.get_parameters(),
            request=DocumentMigrateAPI.get_request(),
            responses=DocumentMigrateAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_MIGRATE.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_MIGRATE.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='document', operate="Migrate documents in batches",
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object_batch(r.data)
            ),
        )
        def put(self, request: Request, workspace_id, knowledge_id: str, target_knowledge_id: str):
            return result.success(DocumentSerializers.Migrate(
                data={
                    'workspace_id': workspace_id,
                    'knowledge_id': knowledge_id,
                    'target_knowledge_id': target_knowledge_id,
                    'document_id_list': request.data}
            ).migrate())


class WebDocumentView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Create Web site documents'),
        summary=_('Create Web site documents'),
        operation_id=_('Create Web site documents'),  # type: ignore
        request=WebDocumentCreateAPI.get_request(),
        parameters=WebDocumentCreateAPI.get_parameters(),
        responses=WebDocumentCreateAPI.get_response(),
        tags=[_('Knowledge Base/Documentation')]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_DOCUMENT_CREATE.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_DOCUMENT_CREATE.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission([RoleConstants.USER.get_workspace_role()],
                       [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
    )
    @log(
        menu='document', operate="Create Web site documents",
        get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
            get_knowledge_operation_object(keywords.get('knowledge_id')),
            {'name': f'[{",".join([url for url in r.data.get("source_url_list", [])])}]',
             'document_list': [{'name': url} for url in r.data.get("source_url_list", [])]}),

    )
    def post(self, request: Request, workspace_id: str, knowledge_id: str):
        return result.success(DocumentSerializers.Create(data={
            'knowledge_id': knowledge_id, 'workspace_id': workspace_id
        }).save_web(request.data, with_valid=True))


class QaDocumentView(APIView):
    authentication_classes = [TokenAuth]
    parser_classes = [MultiPartParser]

    @extend_schema(
        summary=_('Import QA and create documentation'),
        description=_('Import QA and create documentation'),
        operation_id=_('Import QA and create documentation'),  # type: ignore
        request=QaDocumentCreateAPI.get_request(),
        parameters=QaDocumentCreateAPI.get_parameters(),
        responses=QaDocumentCreateAPI.get_response(),
        tags=[_('Knowledge Base/Documentation')]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_DOCUMENT_CREATE.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_DOCUMENT_CREATE.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission([RoleConstants.USER.get_workspace_role()],
                       [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
    )
    @log(
        menu='document', operate="Import QA and create documentation",
        get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
            get_knowledge_operation_object(keywords.get('knowledge_id')),
            {'name': f'[{",".join([file.name for file in r.FILES.getlist("file")])}]',
             'document_list': [{'name': file.name} for file in r.FILES.getlist("file")]}),

    )
    def post(self, request: Request, workspace_id: str, knowledge_id: str):
        return result.success(DocumentSerializers.Create(data={
            'knowledge_id': knowledge_id, 'workspace_id': workspace_id
        }).save_qa({'file_list': request.FILES.getlist('file')}, with_valid=True))


class TableDocumentView(APIView):
    authentication_classes = [TokenAuth]
    parser_classes = [MultiPartParser]

    @extend_schema(
        summary=_('Import tables and create documents'),
        description=_('Import tables and create documents'),
        operation_id=_('Import tables and create documents'),  # type: ignore
        request=TableDocumentCreateAPI.get_request(),
        parameters=TableDocumentCreateAPI.get_parameters(),
        responses=TableDocumentCreateAPI.get_response(),
        tags=[_('Knowledge Base/Documentation')]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_DOCUMENT_CREATE.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_DOCUMENT_CREATE.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission([RoleConstants.USER.get_workspace_role()],
                       [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
    )
    @log(
        menu='document', operate="Import tables and create documents",
        get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
            get_knowledge_operation_object(keywords.get('knowledge_id')),
            {'name': f'[{",".join([file.name for file in r.FILES.getlist("file")])}]',
             'document_list': [{'name': file.name} for file in r.FILES.getlist("file")]}),

    )
    def post(self, request: Request, workspace_id: str, knowledge_id: str):
        return result.success(DocumentSerializers.Create(
            data={'knowledge_id': knowledge_id, 'workspace_id': workspace_id}
        ).save_table({'file_list': request.FILES.getlist('file')}, with_valid=True))


class Template(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        summary=_('Get QA template'),
        operation_id=_('Get QA template'),  # type: ignore
        parameters=TemplateExportAPI.get_parameters(),
        responses=TemplateExportAPI.get_response(),
        tags=[_('Knowledge Base/Documentation')]  # type: ignore
    )
    def get(self, request: Request):
        return DocumentSerializers.Export(data={'type': request.query_params.get('type')}).export(with_valid=True)


class TableTemplate(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        summary=_('Get form template'),
        operation_id=_('Get form template'),  # type: ignore
        parameters=TemplateExportAPI.get_parameters(),
        responses=TemplateExportAPI.get_response(),
        tags=[_('Knowledge Base/Documentation')])  # type: ignore
    def get(self, request: Request):
        return DocumentSerializers.Export(data={'type': request.query_params.get('type')}).table_export(with_valid=True)
