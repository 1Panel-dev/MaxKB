from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import CompareConstants, PermissionConstants, RoleConstants, ViewPermission
from common.log.log import log
from common.result import result
from common.utils.common import query_params_to_single_dict
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView, Request

from knowledge.api.termbase import (
    BatchDeleteAPI,
    TermbaseBatchCreateAPI,
    TermbaseDeleteAPI,
    TermbaseEditAPI,
    TermbasePageAPI,
    TermbaseReadAPI,
)
from knowledge.serializers.common import get_knowledge_operation_object
from knowledge.serializers.termbase import TermbaseSerializers


class TermbaseView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Termbase list"),
        description=_("Termbase list"),
        operation_id=_("Termbase list"),  # type: ignore
        parameters=TermbaseReadAPI.get_parameters(),
        responses=TermbaseReadAPI.get_response(),
        tags=[_("Knowledge Base/Documentation/Termbase")],  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_TERMBASE_READ.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_TERMBASE_READ.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
            CompareConstants.AND,
        ),
    )
    def get(self, request: Request, workspace_id: str, knowledge_id: str):
        q = TermbaseSerializers.Query(
            data={
                **query_params_to_single_dict(request.query_params),
                "workspace_id": workspace_id,
                "knowledge_id": knowledge_id,
            }
        )
        q.is_valid(raise_exception=True)
        return result.success(q.list())

    @extend_schema(
        methods=["POST"],
        summary=_("Create termbase"),
        description=_("Create termbase"),
        operation_id=_("Create termbase"),  # type: ignore
        parameters=TermbaseBatchCreateAPI.get_parameters(),
        responses=TermbaseBatchCreateAPI.get_response(),
        request=TermbaseBatchCreateAPI.get_request(),
        tags=[_("Knowledge Base/Documentation/Termbase")],  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_TERMBASE_CREATE.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_TERMBASE_CREATE.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
            CompareConstants.AND,
        ),
    )
    @log(
        menu="termbase",
        operate="Create termbase",
        get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get("knowledge_id")),
    )
    def post(self, request: Request, workspace_id: str, knowledge_id: str):
        return result.success(
            TermbaseSerializers.Create(data={"workspace_id": workspace_id, "knowledge_id": knowledge_id}).batch(
                request.data
            )
        )

    class BatchDelete(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["PUT"],
            summary=_("Batch deletion issues"),
            description=_("Batch deletion issues"),
            operation_id=_("Batch deletion issues"),  # type: ignore
            request=BatchDeleteAPI.get_request(),
            parameters=BatchDeleteAPI.get_parameters(),
            responses=BatchDeleteAPI.get_response(),
            tags=[_("Knowledge Base/Documentation/Termbase")],  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_TERMBASE_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_TERMBASE_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission(
                [RoleConstants.USER.get_workspace_role()],
                [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                CompareConstants.AND,
            ),
        )
        @log(
            menu="termbase",
            operate="Batch deletion issues",
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get("knowledge_id")),
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(
                TermbaseSerializers.BatchOperate(
                    data={"knowledge_id": knowledge_id, "workspace_id": workspace_id}
                ).delete(request.data)
            )

    class BatchExport(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["POST"],
            summary=_("Batch export termbase"),
            description=_("Batch export termbase"),
            operation_id=_("Batch export termbase"),  # type: ignore
            request=BatchDeleteAPI.get_request(),
            parameters=BatchDeleteAPI.get_parameters(),
            responses=BatchDeleteAPI.get_response(),
            tags=[_("Knowledge Base/Documentation/Termbase")],  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_TERMBASE_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_TERMBASE_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission(
                [RoleConstants.USER.get_workspace_role()],
                [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                CompareConstants.AND,
            ),
        )
        @log(
            menu="termbase",
            operate="Batch export termbase",
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get("knowledge_id")),
        )
        def post(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(
                TermbaseSerializers.BatchOperate(
                    data={"knowledge_id": knowledge_id, "workspace_id": workspace_id}
                ).export(request.data)
            )

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["DELETE"],
            summary=_("Delete termbase"),
            description=_("Delete termbase"),
            operation_id=_("Delete termbase"),  # type: ignore
            parameters=TermbaseDeleteAPI.get_parameters(),
            responses=TermbaseDeleteAPI.get_response(),
            tags=[_("Knowledge Base/Documentation/Termbase")],  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_TERMBASE_DELETE.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_TERMBASE_DELETE.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission(
                [RoleConstants.USER.get_workspace_role()],
                [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                CompareConstants.AND,
            ),
        )
        @log(
            menu="termbase",
            operate="Delete termbase",
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get("knowledge_id")),
        )
        def delete(self, request: Request, workspace_id: str, knowledge_id: str, termbase_id: str):
            return result.success(
                TermbaseSerializers.Operate(
                    data={
                        **query_params_to_single_dict(request.query_params),
                        "workspace_id": workspace_id,
                        "knowledge_id": knowledge_id,
                        "termbase_id": termbase_id,
                    }
                ).delete()
            )

        @extend_schema(
            methods=["PUT"],
            summary=_("Modify termbase"),
            description=_("Modify termbase"),
            operation_id=_("Modify termbase"),  # type: ignore
            parameters=TermbaseEditAPI.get_parameters(),
            request=TermbaseEditAPI.get_request(),
            responses=TermbaseEditAPI.get_response(),
            tags=[_("Knowledge Base/Documentation/Termbase")],  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_TERMBASE_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_TERMBASE_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission(
                [RoleConstants.USER.get_workspace_role()],
                [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                CompareConstants.AND,
            ),
        )
        @log(
            menu="termbase",
            operate="Modify termbase",
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get("knowledge_id")),
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str, termbase_id: str):
            return result.success(
                TermbaseSerializers.Operate(
                    data={
                        **query_params_to_single_dict(request.query_params),
                        "workspace_id": workspace_id,
                        "knowledge_id": knowledge_id,
                        "termbase_id": termbase_id,
                    }
                ).edit(request.data)
            )

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_("Get the list of termbase by page"),
            description=_("Get the list of termbase by page"),
            operation_id=_("Get the list of termbase by page"),  # type: ignore
            parameters=TermbasePageAPI.get_parameters(),
            responses=TermbasePageAPI.get_response(),
            tags=[_("Knowledge Base/Documentation/Termbase")],  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_TERMBASE_READ.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_TERMBASE_READ.get_workspace_permission_workspace_manage_role(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_READ.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DOCUMENT_READ.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission(
                [RoleConstants.USER.get_workspace_role()],
                [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                CompareConstants.AND,
            ),
        )
        def get(self, request: Request, workspace_id: str, knowledge_id: str, current_page, page_size):
            d = TermbaseSerializers.Query(
                data={
                    **query_params_to_single_dict(request.query_params),
                    "knowledge_id": knowledge_id,
                    "workspace_id": workspace_id,
                }
            )
            d.is_valid(raise_exception=True)
            return result.success(d.page(current_page, page_size))
