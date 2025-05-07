from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants
from common.result import result
from common.utils.common import query_params_to_single_dict
from knowledge.api.paragraph import ParagraphReadAPI, ParagraphCreateAPI, ParagraphBatchDeleteAPI, ParagraphEditAPI, \
    ParagraphGetAPI, ProblemCreateAPI, UnAssociationAPI, AssociationAPI
from knowledge.serializers.paragraph import ParagraphSerializers


class ParagraphView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        summary=_('Paragraph list'),
        description=_('Paragraph list'),
        operation_id=_('Paragraph list'),
        parameters=ParagraphReadAPI.get_parameters(),
        responses=ParagraphReadAPI.get_response(),
        tags=[_('Knowledge Base/Documentation/Paragraph')]
    )
    @has_permissions(PermissionConstants.DOCUMENT_READ.get_workspace_permission())
    def get(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
        q = ParagraphSerializers.Query(
            data={
                **query_params_to_single_dict(request.query_params),
                'workspace_id': workspace_id,
                'knowledge_id': knowledge_id,
                'document_id': document_id
            }
        )
        q.is_valid(raise_exception=True)
        return result.success(q.list())

    @extend_schema(
        summary=_('Create Paragraph'),
        operation_id=_('Create Paragraph'),
        parameters=ParagraphCreateAPI.get_parameters(),
        request=ParagraphCreateAPI.get_request(),
        responses=ParagraphCreateAPI.get_response(),
        tags=[_('Knowledge Base/Documentation/Paragraph')]
    )
    @has_permissions(PermissionConstants.DOCUMENT_CREATE.get_workspace_permission())
    def post(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
        return result.success(ParagraphSerializers.Create(
            data={'workspace_id': workspace_id, 'knowledge_id': knowledge_id, 'document_id': document_id}
        ).save(request.data))

    class Batch(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['DELETE'],
            summary=_('Batch Paragraph'),
            description=_('Batch Paragraph'),
            operation_id=_('Batch Paragraph'),
            parameters=ParagraphBatchDeleteAPI.get_parameters(),
            request=ParagraphBatchDeleteAPI.get_request(),
            responses=ParagraphBatchDeleteAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph')]
        )
        @has_permissions(PermissionConstants.DOCUMENT_EDIT.get_workspace_permission())
        def delete(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
            return result.success(ParagraphSerializers.Batch(
                data={'workspace_id': workspace_id, 'knowledge_id': knowledge_id, 'document_id': document_id}
            ).batch_delete(request.data))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            summary=_('Modify paragraph data'),
            description=_('Modify paragraph data'),
            operation_id=_('Modify paragraph data'),
            parameters=ParagraphEditAPI.get_parameters(),
            request=ParagraphEditAPI.get_request(),
            responses=ParagraphEditAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph')]
        )
        @has_permissions(PermissionConstants.DOCUMENT_EDIT.get_workspace_permission())
        def put(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str, paragraph_id: str):
            o = ParagraphSerializers.Operate(
                data={
                    'workspace_id': workspace_id,
                    "paragraph_id": paragraph_id,
                    'knowledge_id': knowledge_id,
                    'document_id': document_id
                }
            )
            o.is_valid(raise_exception=True)
            return result.success(o.edit(request.data))

        @extend_schema(
            methods=['GET'],
            summary=_('Get paragraph details'),
            description=_('Get paragraph details'),
            operation_id=_('Get paragraph details'),
            parameters=ParagraphGetAPI.get_parameters(),
            responses=ParagraphGetAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph')]
        )
        @has_permissions(PermissionConstants.DOCUMENT_EDIT.get_workspace_permission())
        def get(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str, paragraph_id: str):
            o = ParagraphSerializers.Operate(
                data={
                    'workspace_id': workspace_id,
                    "paragraph_id": paragraph_id,
                    'knowledge_id': knowledge_id,
                    'document_id': document_id
                }
            )
            o.is_valid(raise_exception=True)
            return result.success(o.one())

        @extend_schema(
            methods=['DELETE'],
            summary=_('Delete paragraph'),
            description=_('Delete paragraph'),
            operation_id=_('Delete paragraph'),
            parameters=ParagraphGetAPI.get_parameters(),
            responses=ParagraphGetAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph')])
        @has_permissions(PermissionConstants.DOCUMENT_EDIT.get_workspace_permission())
        def delete(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str, paragraph_id: str):
            o = ParagraphSerializers.Operate(
                data={
                    'workspace_id': workspace_id,
                    "paragraph_id": paragraph_id,
                    'knowledge_id': knowledge_id,
                    'document_id': document_id
                }
            )
            o.is_valid(raise_exception=True)
            return result.success(o.delete())

    class Problem(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['POST'],
            summary=_('Add associated questions'),
            description=_('Add associated questions'),
            operation_id=_('Add associated questions'),
            parameters=ProblemCreateAPI.get_parameters(),
            request=ProblemCreateAPI.get_request(),
            responses=ProblemCreateAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph')]
        )
        @has_permissions(PermissionConstants.DOCUMENT_EDIT.get_workspace_permission())
        def post(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str, paragraph_id: str):
            return result.success(ParagraphSerializers.Problem(
                data={
                    'workspace_id': workspace_id,
                    "knowledge_id": knowledge_id,
                    'document_id': document_id,
                    'paragraph_id': paragraph_id
                }
            ).save(request.data, with_valid=True))

        @extend_schema(
            methods=['GET'],
            summary=_('Get a list of paragraph questions'),
            description=_('Get a list of paragraph questions'),
            operation_id=_('Get a list of paragraph questions'),
            parameters=ParagraphGetAPI.get_parameters(),
            responses=ParagraphGetAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph')]
        )
        @has_permissions(PermissionConstants.DOCUMENT_EDIT.get_workspace_permission())
        def get(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str, paragraph_id: str):
            return result.success(ParagraphSerializers.Problem(
                data={
                    'workspace_id': workspace_id,
                    "knowledge_id": knowledge_id,
                    'document_id': document_id,
                    'paragraph_id': paragraph_id
                }
            ).list(with_valid=True))

    class UnAssociation(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            summary=_('Disassociation issue'),
            description=_('Disassociation issue'),
            operation_id=_('Disassociation issue'),
            parameters=UnAssociationAPI.get_parameters(),
            responses=UnAssociationAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph')]
        )
        @has_permissions(PermissionConstants.DOCUMENT_EDIT.get_workspace_permission())
        def get(self, request: Request,
                workspace_id: str, knowledge_id: str, document_id: str, paragraph_id: str, problem_id: str):
            return result.success(ParagraphSerializers.Association(
                data={
                    'workspace_id': workspace_id,
                    'knowledge_id': knowledge_id,
                    'document_id': document_id,
                    'paragraph_id': paragraph_id,
                    'problem_id': problem_id
                }
            ).un_association())

    class Association(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            summary=_('Related questions'),
            description=_('Related questions'),
            operation_id=_('Related questions'),
            parameters=AssociationAPI.get_parameters(),
            responses=AssociationAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph')]
        )
        @has_permissions(PermissionConstants.DOCUMENT_EDIT.get_workspace_permission())
        def get(self, request: Request,
                workspace_id: str, knowledge_id: str, document_id: str, paragraph_id: str, problem_id: str):
            return result.success(ParagraphSerializers.Association(
                data={
                    'workspace_id': workspace_id,
                    'knowledge_id': knowledge_id,
                    'document_id': document_id,
                    'paragraph_id': paragraph_id,
                    'problem_id': problem_id
                }
            ).association())
