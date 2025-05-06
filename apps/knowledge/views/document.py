from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants
from common.result import result
from knowledge.api.document import DocumentSplitAPI, DocumentBatchAPI, DocumentBatchCreateAPI, DocumentCreateAPI, \
    DocumentReadAPI, DocumentEditAPI, DocumentDeleteAPI, TableDocumentCreateAPI, QaDocumentCreateAPI, \
    WebDocumentCreateAPI, CancelTaskAPI, BatchCancelTaskAPI, SyncWebAPI, RefreshAPI, BatchEditHitHandlingAPI, \
    DocumentTreeReadAPI, DocumentSplitPatternAPI
from knowledge.serializers.document import DocumentSerializers


class DocumentView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Create document'),
        summary=_('Create document'),
        operation_id=_('Create document'),
        request=DocumentCreateAPI.get_request(),
        parameters=DocumentCreateAPI.get_parameters(),
        responses=DocumentCreateAPI.get_response(),
        tags=[_('Knowledge Base/Documentation')]
    )
    @has_permissions(PermissionConstants.DOCUMENT_CREATE.get_workspace_permission())
    def post(self, request: Request, workspace_id: str, knowledge_id: str):
        return result.success(
            DocumentSerializers.Create(
                data={'workspace_id': workspace_id, 'knowledge_id': knowledge_id},
            ).save(request.data))

    @extend_schema(
        methods=['GET'],
        description=_('Get document'),
        summary=_('Get document'),
        operation_id=_('Get document'),
        parameters=DocumentTreeReadAPI.get_parameters(),
        responses=DocumentTreeReadAPI.get_response(),
        tags=[_('Knowledge Base/Documentation')]
    )
    @has_permissions(PermissionConstants.DOCUMENT_READ.get_workspace_permission())
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
            operation_id=_('Get document details'),
            parameters=DocumentReadAPI.get_parameters(),
            responses=DocumentReadAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]
        )
        @has_permissions(PermissionConstants.DOCUMENT_READ.get_workspace_permission())
        def get(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
            operate = DocumentSerializers.Operate(data={
                'document_id': document_id, 'knowledge_id': knowledge_id, 'workspace_id': workspace_id
            })
            operate.is_valid(raise_exception=True)
            return result.success(operate.one())

        @extend_schema(
            description=_('Modify document'),
            summary=_('Modify document'),
            operation_id=_('Modify document'),
            parameters=DocumentEditAPI.get_parameters(),
            request=DocumentEditAPI.get_request(),
            responses=DocumentEditAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]
        )
        @has_permissions(PermissionConstants.DOCUMENT_EDIT.get_workspace_permission())
        def put(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
            return result.success(DocumentSerializers.Operate(data={
                'document_id': document_id, 'knowledge_id': knowledge_id, 'workspace_id': workspace_id
            }).edit(request.data, with_valid=True))

        @extend_schema(
            description=_('Delete document'),
            summary=_('Delete document'),
            operation_id=_('Delete document'),
            parameters=DocumentDeleteAPI.get_parameters(),
            responses=DocumentDeleteAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]
        )
        @has_permissions(PermissionConstants.DOCUMENT_DELETE.get_workspace_permission())
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
            operation_id=_('Segmented document'),
            parameters=DocumentSplitAPI.get_parameters(),
            request=DocumentSplitAPI.get_request(),
            responses=DocumentSplitAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]
        )
        @has_permissions([
            PermissionConstants.DOCUMENT_CREATE.get_workspace_permission(),
            PermissionConstants.DOCUMENT_EDIT.get_workspace_permission(),
        ])
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
            operation_id=_('Get a list of segment IDs'),
            parameters=DocumentSplitPatternAPI.get_parameters(),
            responses=DocumentSplitPatternAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]
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
            operation_id=_('Modify document hit processing methods in batches'),
            request=BatchEditHitHandlingAPI.get_request(),
            parameters=BatchEditHitHandlingAPI.get_parameters(),
            responses=BatchEditHitHandlingAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]
        )
        @has_permissions(PermissionConstants.DOCUMENT_EDIT.get_workspace_permission())
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(DocumentSerializers.Batch(
                data={'knowledge_id': knowledge_id, 'workspace_id': workspace_id}
            ).batch_edit_hit_handling(request.data))

    class SyncWeb(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Synchronize web site types'),
            summary=_('Synchronize web site types'),
            operation_id=_('Synchronize web site types'),
            parameters=SyncWebAPI.get_parameters(),
            request=SyncWebAPI.get_request(),
            responses=SyncWebAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]
        )
        @has_permissions(PermissionConstants.DOCUMENT_EDIT.get_workspace_permission())
        def get(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
            return result.success(DocumentSerializers.Sync(
                data={'document_id': document_id, 'knowledge_id': knowledge_id, 'workspace_id': workspace_id}
            ).sync())

    class Refresh(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            summary=_('Refresh document vector library'),
            description=_('Refresh document vector library'),
            operation_id=_('Refresh document vector library'),
            parameters=RefreshAPI.get_parameters(),
            request=RefreshAPI.get_request(),
            responses=RefreshAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]
        )
        @has_permissions(PermissionConstants.DOCUMENT_EDIT.get_workspace_permission())
        def put(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
            return result.success(DocumentSerializers.Operate(
                data={'document_id': document_id, 'knowledge_id': knowledge_id, 'workspace_id': workspace_id}
            ).refresh(request.data.get('state_list')))

    class CancelTask(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_('Cancel task'),
            description=_('Cancel task'),
            operation_id=_('Cancel task'),
            parameters=CancelTaskAPI.get_parameters(),
            request=CancelTaskAPI.get_request(),
            responses=CancelTaskAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]
        )
        @has_permissions(PermissionConstants.DOCUMENT_EDIT.get_workspace_permission())
        def put(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
            return result.success(DocumentSerializers.Operate(
                data={'document_id': document_id, 'knowledge_id': knowledge_id, 'workspace_id': workspace_id}
            ).cancel(request.data))

    class BatchCancelTask(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_('Cancel tasks in batches'),
            description=_('Cancel tasks in batches'),
            operation_id=_('Cancel tasks in batches'),
            parameters=BatchCancelTaskAPI.get_parameters(),
            request=BatchCancelTaskAPI.get_request(),
            responses=BatchCancelTaskAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(DocumentSerializers.Batch(data={
                'knowledge_id': knowledge_id, 'workspace_id': workspace_id}
            ).batch_cancel(request.data))

    class Batch(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['POST'],
            description=_('Create documents in batches'),
            summary=_('Create documents in batches'),
            operation_id=_('Create documents in batches'),
            request=DocumentBatchCreateAPI.get_request(),
            parameters=DocumentBatchCreateAPI.get_parameters(),
            responses=DocumentBatchCreateAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]
        )
        @has_permissions([
            PermissionConstants.DOCUMENT_CREATE.get_workspace_permission(),
            PermissionConstants.DOCUMENT_EDIT.get_workspace_permission(),
        ])
        def post(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(DocumentSerializers.Batch(
                data={'knowledge_id': knowledge_id, 'workspace_id': workspace_id}
            ).batch_save(request.data))

        @extend_schema(
            methods=['PUT'],
            description=_('Batch sync documents'),
            summary=_('Batch sync documents'),
            operation_id=_('Batch sync documents'),
            request=DocumentBatchAPI.get_request(),
            parameters=DocumentBatchAPI.get_parameters(),
            responses=DocumentBatchAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]
        )
        @has_permissions([
            PermissionConstants.DOCUMENT_CREATE.get_workspace_permission(),
            PermissionConstants.DOCUMENT_EDIT.get_workspace_permission(),
        ])
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(DocumentSerializers.Batch(
                data={'knowledge_id': knowledge_id, 'workspace_id': workspace_id}
            ).batch_sync(request.data))

        @extend_schema(
            methods=['DELETE'],
            description=_('Delete documents in batches'),
            summary=_('Delete documents in batches'),
            operation_id=_('Delete documents in batches'),
            request=DocumentBatchAPI.get_request(),
            parameters=DocumentBatchAPI.get_parameters(),
            responses=DocumentBatchAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]
        )
        @has_permissions([
            PermissionConstants.DOCUMENT_CREATE.get_workspace_permission(),
            PermissionConstants.DOCUMENT_EDIT.get_workspace_permission(),
        ])
        def delete(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(DocumentSerializers.Batch(
                data={'workspace_id': workspace_id, 'knowledge_id': knowledge_id}
            ).batch_delete(request.data))

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Get document by pagination'),
            summary=_('Get document by pagination'),
            operation_id=_('Get document by pagination'),
            parameters=DocumentTreeReadAPI.get_parameters(),
            responses=DocumentTreeReadAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')]
        )
        @has_permissions(PermissionConstants.DOCUMENT_READ.get_workspace_permission())
        def get(self, request: Request, workspace_id: str, knowledge_id: str, current_page: int, page_size: int):
            return result.success(DocumentSerializers.Query(
                data={
                    'workspace_id': workspace_id,
                    'knowledge_id': knowledge_id,
                    'folder_id': request.query_params.get('folder_id'),
                    'name': request.query_params.get('name'),
                    'desc': request.query_params.get("desc"),
                    'user_id': request.query_params.get('user_id')
                }
            ).page(current_page, page_size))


class WebDocumentView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Create Web site documents'),
        summary=_('Create Web site documents'),
        operation_id=_('Create Web site documents'),
        request=WebDocumentCreateAPI.get_request(),
        parameters=WebDocumentCreateAPI.get_parameters(),
        responses=WebDocumentCreateAPI.get_response(),
        tags=[_('Knowledge Base/Documentation')]
    )
    @has_permissions(PermissionConstants.DOCUMENT_CREATE.get_workspace_permission())
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
        operation_id=_('Import QA and create documentation'),
        request=QaDocumentCreateAPI.get_request(),
        parameters=QaDocumentCreateAPI.get_parameters(),
        responses=QaDocumentCreateAPI.get_response(),
        tags=[_('Knowledge Base/Documentation')]
    )
    @has_permissions(PermissionConstants.DOCUMENT_CREATE.get_workspace_permission())
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
        operation_id=_('Import tables and create documents'),
        request=TableDocumentCreateAPI.get_request(),
        parameters=TableDocumentCreateAPI.get_parameters(),
        responses=TableDocumentCreateAPI.get_response(),
        tags=[_('Knowledge Base/Documentation')]
    )
    @has_permissions(PermissionConstants.DOCUMENT_CREATE.get_workspace_permission())
    def post(self, request: Request, workspace_id: str, knowledge_id: str):
        return result.success(DocumentSerializers.Create(
            data={'knowledge_id': knowledge_id, 'workspace_id': workspace_id}
        ).save_table({'file_list': request.FILES.getlist('file')}, with_valid=True))
