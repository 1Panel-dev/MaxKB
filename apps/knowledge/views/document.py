from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, CompareConstants
from common.result import result
from knowledge.api.document import DocumentSplitAPI
from knowledge.api.knowledge import KnowledgeTreeReadAPI
from knowledge.serializers.document import DocumentSerializers
from knowledge.serializers.knowledge import KnowledgeSerializer


class DocumentView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_('Get document'),
        operation_id=_('Get document'),
        parameters=KnowledgeTreeReadAPI.get_parameters(),
        responses=KnowledgeTreeReadAPI.get_response(),
        tags=[_('Knowledge Base')]
    )
    @has_permissions(PermissionConstants.DOCUMENT_READ.get_workspace_permission())
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

    class Split(APIView):
        authentication_classes = [TokenAuth]
        parser_classes = [MultiPartParser]

        @extend_schema(
            methods=['POST'],
            description=_('Segmented document'),
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
