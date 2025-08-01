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
from knowledge.api.paragraph import ParagraphReadAPI, ParagraphCreateAPI, ParagraphBatchDeleteAPI, ParagraphEditAPI, \
    ParagraphGetAPI, ProblemCreateAPI, UnAssociationAPI, AssociationAPI, ParagraphPageAPI, \
    ParagraphBatchGenerateRelatedAPI, ParagraphMigrateAPI, ParagraphAdjustOrderAPI
from knowledge.serializers.common import get_knowledge_operation_object
from knowledge.serializers.paragraph import ParagraphSerializers
from knowledge.views import get_knowledge_document_operation_object, get_document_operation_object


class ParagraphView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        summary=_('Paragraph list'),
        description=_('Paragraph list'),
        operation_id=_('Paragraph list'),  # type: ignore
        parameters=ParagraphReadAPI.get_parameters(),
        responses=ParagraphReadAPI.get_response(),
        tags=[_('Knowledge Base/Documentation/Paragraph')]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_DOCUMENT_READ.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_DOCUMENT_READ.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission([RoleConstants.USER.get_workspace_role()],
                       [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
    )
    def get(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
        q = ParagraphSerializers.Query(
            data={
                **query_params_to_single_dict(request.query_params),
                'workspace_id': workspace_id,
                'knowledge_id': knowledge_id,
                'document_id': document_id
            }
        )
        return result.success(q.list())

    @extend_schema(
        summary=_('Create Paragraph'),
        operation_id=_('Create Paragraph'),  # type: ignore
        parameters=ParagraphCreateAPI.get_parameters(),
        request=ParagraphCreateAPI.get_request(),
        responses=ParagraphCreateAPI.get_response(),
        tags=[_('Knowledge Base/Documentation/Paragraph')]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission([RoleConstants.USER.get_workspace_role()],
                       [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
    )
    @log(
        menu='Paragraph', operate='Create Paragraph',
        get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
            get_knowledge_operation_object(keywords.get('knowledge_id')),
            get_knowledge_operation_object(keywords.get('knowledge_id')),
            get_document_operation_object(keywords.get('document_id'))
        ),
    )
    def post(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
        return result.success(ParagraphSerializers.Create(
            data={'workspace_id': workspace_id, 'knowledge_id': knowledge_id, 'document_id': document_id}
        ).save(request.data))

    class BatchDelete(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            summary=_('Batch Paragraph'),
            description=_('Batch Paragraph'),
            operation_id=_('Batch Paragraph'),  # type: ignore
            parameters=ParagraphBatchDeleteAPI.get_parameters(),
            request=ParagraphBatchDeleteAPI.get_request(),
            responses=ParagraphBatchDeleteAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
            return result.success(ParagraphSerializers.Batch(
                data={'workspace_id': workspace_id, 'knowledge_id': knowledge_id, 'document_id': document_id}
            ).batch_delete(request.data))

    class BatchMigrate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_('Migrate paragraphs in batches'),
            operation_id=_('Migrate paragraphs in batches'),  # type: ignore
            parameters=ParagraphMigrateAPI.get_parameters(),
            request=ParagraphMigrateAPI.get_request(),
            responses=ParagraphMigrateAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='Paragraph', operate='Migrate paragraphs in batches',
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object(keywords.get('document_id'))
            ),
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str,
                target_knowledge_id: str, target_document_id):
            return result.success(
                ParagraphSerializers.Migrate(data={
                    'workspace_id': workspace_id,
                    'knowledge_id': knowledge_id,
                    'target_knowledge_id': target_knowledge_id,
                    'document_id': document_id,
                    'target_document_id': target_document_id,
                    'paragraph_id_list': request.data.get('id_list')
                }).migrate())

    class BatchGenerateRelated(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            summary=_('Batch Generate Related'),
            description=_('Batch Generate Related'),
            operation_id=_('Batch Generate Related'),  # type: ignore
            parameters=ParagraphBatchGenerateRelatedAPI.get_parameters(),
            request=ParagraphBatchGenerateRelatedAPI.get_request(),
            responses=ParagraphBatchGenerateRelatedAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_GENERATE.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_GENERATE.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='Paragraph', operate='Batch generate related',
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object(keywords.get('document_id'))
            ),
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
            return result.success(ParagraphSerializers.Batch(
                data={'workspace_id': workspace_id, 'knowledge_id': knowledge_id, 'document_id': document_id}
            ).batch_generate_related(request.data))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            summary=_('Modify paragraph data'),
            description=_('Modify paragraph data'),
            operation_id=_('Modify paragraph data'),  # type: ignore
            parameters=ParagraphEditAPI.get_parameters(),
            request=ParagraphEditAPI.get_request(),
            responses=ParagraphEditAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='Paragraph', operate='Modify paragraph data',
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object(keywords.get('document_id'))
            ),
        )
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
            operation_id=_('Get paragraph details'),  # type: ignore
            parameters=ParagraphGetAPI.get_parameters(),
            responses=ParagraphGetAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
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
            operation_id=_('Delete paragraph'),  # type: ignore
            parameters=ParagraphGetAPI.get_parameters(),
            responses=ParagraphGetAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph')])  # type: ignore
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='Paragraph', operate='Delete paragraph',
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object(keywords.get('document_id'))
            ),
        )
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
            operation_id=_('Add associated questions'),  # type: ignore
            parameters=ProblemCreateAPI.get_parameters(),
            request=ProblemCreateAPI.get_request(),
            responses=ProblemCreateAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='Paragraph', operate='Add associated questions',
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object(keywords.get('document_id'))
            ),
        )
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
            operation_id=_('Get a list of paragraph questions'),  # type: ignore
            parameters=ParagraphGetAPI.get_parameters(),
            responses=ParagraphGetAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_PROBLEM_READ.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_PROBLEM_READ.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
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
            methods=['PUT'],
            summary=_('Disassociation issue'),
            description=_('Disassociation issue'),
            operation_id=_('Disassociation issue'),  # type: ignore
            parameters=UnAssociationAPI.get_parameters(),
            request=UnAssociationAPI.get_request(),
            responses=UnAssociationAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_PROBLEM_RELATE.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_PROBLEM_RELATE.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='Paragraph', operate='Disassociation issue',
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object(keywords.get('document_id'))
            )
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
            return result.success(ParagraphSerializers.Association(
                data={
                    'workspace_id': workspace_id,
                    'knowledge_id': knowledge_id,
                    'document_id': document_id,
                    'paragraph_id': request.query_params.get('paragraph_id'),
                    'problem_id': request.query_params.get('problem_id')
                }
            ).un_association())

    class Association(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            summary=_('Related questions'),
            description=_('Related questions'),
            operation_id=_('Related questions'),  # type: ignore
            parameters=AssociationAPI.get_parameters(),
            request=AssociationAPI.get_request(),
            responses=AssociationAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_PROBLEM_RELATE.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_PROBLEM_RELATE.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='Paragraph', operate='Related questions',
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object(keywords.get('document_id'))
            ),
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
            return result.success(ParagraphSerializers.Association(
                data={
                    'workspace_id': workspace_id,
                    'knowledge_id': knowledge_id,
                    'document_id': document_id,
                    'paragraph_id': request.query_params.get('paragraph_id'),
                    'problem_id': request.query_params.get('problem_id')
                }
            ).association())

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            summary=_('Get paragraph list by pagination'),
            description=_('Get paragraph list by pagination'),
            operation_id=_('Get paragraph list by pagination'),  # type: ignore
            parameters=ParagraphPageAPI.get_parameters(),
            responses=ParagraphPageAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_READ.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_READ.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        def get(self, request: Request,
                workspace_id: str, knowledge_id: str, document_id: str, current_page: int, page_size: int):
            d = ParagraphSerializers.Query(
                data={
                    **query_params_to_single_dict(request.query_params),
                    'workspace_id': workspace_id,
                    'knowledge_id': knowledge_id,
                    'document_id': document_id
                }
            )
            return result.success(d.page(current_page, page_size))

    class AdjustPosition(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            summary=_('Adjust paragraph position'),
            description=_('Adjust paragraph position'),
            operation_id=_('Adjust paragraph position'),  # type: ignore
            parameters=ParagraphAdjustOrderAPI.get_parameters(),
            request=ParagraphAdjustOrderAPI.get_request(),
            responses=ParagraphAdjustOrderAPI.get_response(),
            tags=[_('Knowledge Base/Documentation/Paragraph')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str, document_id: str):
            return result.success(ParagraphSerializers.AdjustPosition(
                data={
                    'workspace_id': workspace_id,
                    'knowledge_id': knowledge_id,
                    'document_id': document_id,
                    'paragraph_id': request.query_params.get('paragraph_id'),
                }
            ).adjust_position(request.query_params.get('new_position')))
