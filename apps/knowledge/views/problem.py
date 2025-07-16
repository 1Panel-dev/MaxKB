from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants, ViewPermission, CompareConstants
from common.log.log import log
from common.result import result
from common.utils.common import query_params_to_single_dict
from knowledge.api.problem import ProblemReadAPI, ProblemBatchCreateAPI, BatchAssociationAPI, BatchDeleteAPI, \
    ProblemPageAPI, ProblemDeleteAPI, ProblemEditAPI, ProblemParagraphAPI
from knowledge.serializers.common import get_knowledge_operation_object
from knowledge.serializers.problem import ProblemSerializers


class ProblemView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        summary=_('Question list'),
        description=_('Question list'),
        operation_id=_('Question list'),  # type: ignore
        parameters=ProblemReadAPI.get_parameters(),
        responses=ProblemReadAPI.get_response(),
        tags=[_('Knowledge Base/Documentation/Paragraph/Question')]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_PROBLEM_READ.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_PROBLEM_READ.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission([RoleConstants.USER.get_workspace_role()],
                       [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
    )
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
        operation_id=_('Create question'),  # type: ignore
        parameters=ProblemBatchCreateAPI.get_parameters(),
        responses=ProblemBatchCreateAPI.get_response(),
        request=ProblemBatchCreateAPI.get_request(),
        tags=[_('Knowledge Base/Documentation/Paragraph/Question')]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_PROBLEM_EDIT.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_PROBLEM_EDIT.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission([RoleConstants.USER.get_workspace_role()],
                       [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
    )
    @log(
        menu='problem', operate='Create question',
        get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get('knowledge_id'))
        ,
    )
    def post(self, request: Request, workspace_id: str, knowledge_id: str):
        return result.success(ProblemSerializers.Create(
            data={'workspace_id': workspace_id, 'knowledge_id': knowledge_id}
        ).batch(request.data))

    class Paragraph(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_('Get a list of associated paragraphs'),
            description=_('Get a list of associated paragraphs'),
            operation_id=_('Get a list of associated paragraphs'),  # type: ignore
            parameters=ProblemParagraphAPI.get_parameters(),
            responses=ProblemParagraphAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph/Question')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_PROBLEM_READ.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_PROBLEM_READ.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        def get(self, request: Request, workspace_id: str, knowledge_id: str, problem_id: str):
            return result.success(ProblemSerializers.Operate(
                data={
                    **query_params_to_single_dict(request.query_params),
                    'workspace_id': workspace_id,
                    'knowledge_id': knowledge_id,
                    'problem_id': problem_id
                }
            ).list_paragraph())

    class BatchAssociation(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_('Batch associated paragraphs'),
            description=_('Batch associated paragraphs'),
            operation_id=_('Batch associated paragraphs'),  # type: ignore
            request=BatchAssociationAPI.get_request(),
            parameters=BatchAssociationAPI.get_parameters(),
            responses=BatchAssociationAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph/Question')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_PROBLEM_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_PROBLEM_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='problem', operate='Batch associated paragraphs',
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get('knowledge_id')),

        )
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
            operation_id=_('Batch deletion issues'),  # type: ignore
            request=BatchDeleteAPI.get_request(),
            parameters=BatchDeleteAPI.get_parameters(),
            responses=BatchDeleteAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph/Question')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_PROBLEM_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_PROBLEM_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='problem', operate='Batch deletion issues',
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get('knowledge_id')),

        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(ProblemSerializers.BatchOperate(
                data={'knowledge_id': knowledge_id, 'workspace_id': workspace_id}
            ).delete(request.data))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['DELETE'],
            summary=_('Delete question'),
            description=_('Delete question'),
            operation_id=_('Delete question'),  # type: ignore
            parameters=ProblemDeleteAPI.get_parameters(),
            responses=ProblemDeleteAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph/Question')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_PROBLEM_DELETE.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_PROBLEM_DELETE.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='problem', operate='Delete question',
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get('knowledge_id')),

        )
        def delete(self, request: Request, workspace_id: str, knowledge_id: str, problem_id: str):
            return result.success(ProblemSerializers.Operate(
                data={
                    **query_params_to_single_dict(request.query_params),
                    'workspace_id': workspace_id,
                    'knowledge_id': knowledge_id,
                    'problem_id': problem_id
                }
            ).delete())

        @extend_schema(
            methods=['PUT'],
            summary=_('Modify question'),
            description=_('Modify question'),
            operation_id=_('Modify question'),  # type: ignore
            parameters=ProblemEditAPI.get_parameters(),
            request=ProblemEditAPI.get_request(),
            responses=ProblemEditAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph/Question')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_PROBLEM_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_PROBLEM_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='problem', operate='Modify question',
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get('knowledge_id')),

        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str, problem_id: str):
            return result.success(ProblemSerializers.Operate(
                data={
                    **query_params_to_single_dict(request.query_params),
                    'workspace_id': workspace_id,
                    'knowledge_id': knowledge_id,
                    'problem_id': problem_id
                }
            ).edit(request.data))

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_('Get the list of questions by page'),
            description=_('Get the list of questions by page'),
            operation_id=_('Get the list of questions by page'),  # type: ignore
            parameters=ProblemPageAPI.get_parameters(),
            responses=ProblemPageAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph/Question')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_PROBLEM_READ.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_PROBLEM_READ.get_workspace_permission_workspace_manage_role(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_READ.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_READ.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        def get(self, request: Request, workspace_id: str, knowledge_id: str, current_page, page_size):
            d = ProblemSerializers.Query(
                data={
                    **query_params_to_single_dict(request.query_params),
                    'knowledge_id': knowledge_id,
                    'workspace_id': workspace_id
                }
            )
            d.is_valid(raise_exception=True)
            return result.success(d.page(current_page, page_size))
