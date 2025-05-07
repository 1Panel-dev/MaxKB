from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants
from common.result import result
from common.utils.common import query_params_to_single_dict
from knowledge.api.problem import ProblemReadAPI, ProblemBatchCreateAPI, BatchAssociationAPI, BatchDeleteAPI
from knowledge.serializers.problem import ProblemSerializers


class ProblemView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        summary=_('Question list'),
        description=_('Question list'),
        operation_id=_('Question list'),
        parameters=ProblemReadAPI.get_parameters(),
        responses=ProblemReadAPI.get_response(),
        tags=[_('Knowledge Base/Documentation/Paragraph/Question')]
    )
    @has_permissions(PermissionConstants.DOCUMENT_EDIT.get_workspace_permission())
    def get(self, request: Request, workspace_id: str, knowledge_id: str):
        q = ProblemSerializers.Query(
            data={
                **query_params_to_single_dict(request.query_params),
                'workspace_id': workspace_id,
                'knowledge_id': knowledge_id
            }
        )
        q.is_valid(raise_exception=True)
        return result.success(q.list())

    @extend_schema(
        methods=['POST'],
        summary=_('Create question'),
        description=_('Create question'),
        operation_id=_('Create question'),
        parameters=ProblemBatchCreateAPI.get_parameters(),
        responses=ProblemBatchCreateAPI.get_response(),
        request=ProblemBatchCreateAPI.get_request(),
        tags=[_('Knowledge Base/Documentation/Paragraph/Question')]
    )
    @has_permissions(PermissionConstants.DOCUMENT_EDIT.get_workspace_permission())
    def post(self, request: Request, workspace_id: str, knowledge_id: str):
        return result.success(ProblemSerializers.Create(
            data={'workspace_id': workspace_id, 'knowledge_id': knowledge_id, 'problem_list': request.data}
        ).batch())

    class BatchAssociation(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_('Batch associated paragraphs'),
            description=_('Batch associated paragraphs'),
            operation_id=_('Batch associated paragraphs'),
            request=BatchAssociationAPI.get_request(),
            parameters=BatchAssociationAPI.get_parameters(),
            responses=BatchAssociationAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph/Question')]
        )
        @has_permissions(PermissionConstants.DOCUMENT_EDIT.get_workspace_permission())
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(ProblemSerializers.BatchOperate(
                data={'knowledge_id': knowledge_id, 'workspace_id': workspace_id}
            ).association(request.data))

    class BatchDelete(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            summary=_('Batch deletion issues'),
            description=_('Batch deletion issues'),
            operation_id=_('Batch deletion issues'),
            request=BatchDeleteAPI.get_request(),
            parameters=BatchDeleteAPI.get_parameters(),
            responses=BatchDeleteAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph/Question')]
        )
        @has_permissions(PermissionConstants.DOCUMENT_EDIT.get_workspace_permission())
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(ProblemSerializers.BatchOperate(
                data={'knowledge_id': knowledge_id, 'workspace_id': workspace_id}
            ).delete(request.data))
