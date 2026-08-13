"""HTTP endpoints for standalone image documents."""

import json

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.auth.constants.compare_constants import CompareConstants
from common.auth.constants.permission_constants import PermissionConstants
from common.auth.constants.role_constants import RoleConstants
from common.auth.struct.aggregate_permission import ViewPermission
from common.exception.app_exception import AppApiException
from common.result import result
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.views import APIView

from knowledge.api.document import ImageBatchCreateAPI, ImagePreviewAPI, ImagePreviewOperateAPI
from knowledge.serializers.image_document import ImageDocumentSerializers


def _document_permissions(permission):
    return has_permissions(
        permission.get_workspace_knowledge_permission(),
        permission.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
            compare=CompareConstants.AND,
        ),
    )


class ImageDocumentView:
    class Preview(APIView):
        authentication_classes = [TokenAuth]
        parser_classes = [MultiPartParser]

        @extend_schema(
            methods=["POST"],
            description=_("Upload images and generate editable previews"),
            summary=_("Generate image previews"),
            operation_id=_("Generate image previews"),  # type: ignore
            parameters=ImagePreviewAPI.get_parameters(),
            request=ImagePreviewAPI.get_request(),
            responses=ImagePreviewAPI.get_response(),
            tags=[_("Knowledge Base/Images")],  # type: ignore
        )
        @_document_permissions(PermissionConstants.KNOWLEDGE_DOCUMENT_CREATE)
        def post(self, request: Request, workspace_id: str, knowledge_id: str):
            payload = {"file": request.FILES.getlist("file")}
            raw_strategy = request.data.get("doc_strategy")
            if raw_strategy not in (None, ""):
                if isinstance(raw_strategy, str):
                    try:
                        raw_strategy = json.loads(raw_strategy)
                    except json.JSONDecodeError as exc:
                        raise AppApiException(500, _("Invalid document processing strategy")) from exc
                payload["doc_strategy"] = raw_strategy
            return result.success(
                ImageDocumentSerializers.Preview(
                    data={
                        "workspace_id": workspace_id,
                        "knowledge_id": knowledge_id,
                        "user_id": request.user.id,
                    }
                ).upload(payload)
            )

    class PreviewOperate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Get an image preview"),
            summary=_("Get an image preview"),
            operation_id=_("Get an image preview"),  # type: ignore
            parameters=ImagePreviewOperateAPI.get_parameters(),
            responses=ImagePreviewOperateAPI.get_response(),
            tags=[_("Knowledge Base/Images")],  # type: ignore
        )
        @_document_permissions(PermissionConstants.KNOWLEDGE_DOCUMENT_READ)
        def get(self, request: Request, workspace_id: str, knowledge_id: str, preview_id: str):
            return result.success(
                ImageDocumentSerializers.Preview(data={"workspace_id": workspace_id, "knowledge_id": knowledge_id}).one(
                    preview_id
                )
            )

        @extend_schema(
            methods=["PUT"],
            description=_("Edit an image preview"),
            summary=_("Edit an image preview"),
            operation_id=_("Edit an image preview"),  # type: ignore
            parameters=ImagePreviewOperateAPI.get_parameters(),
            request=ImagePreviewOperateAPI.get_request(),
            responses=ImagePreviewOperateAPI.get_response(),
            tags=[_("Knowledge Base/Images")],  # type: ignore
        )
        @_document_permissions(PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT)
        def put(self, request: Request, workspace_id: str, knowledge_id: str, preview_id: str):
            return result.success(
                ImageDocumentSerializers.Preview(
                    data={"workspace_id": workspace_id, "knowledge_id": knowledge_id}
                ).edit(preview_id, request.data)
            )

        @extend_schema(
            methods=["DELETE"],
            description=_("Delete an image preview"),
            summary=_("Delete an image preview"),
            operation_id=_("Delete an image preview"),  # type: ignore
            parameters=ImagePreviewOperateAPI.get_parameters(),
            responses=ImagePreviewOperateAPI.get_response(),
            tags=[_("Knowledge Base/Images")],  # type: ignore
        )
        @_document_permissions(PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT)
        def delete(self, request: Request, workspace_id: str, knowledge_id: str, preview_id: str):
            return result.success(
                ImageDocumentSerializers.Preview(
                    data={"workspace_id": workspace_id, "knowledge_id": knowledge_id}
                ).delete(preview_id)
            )

    class BatchCreate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["PUT"],
            description=_("Import image previews as standalone image documents"),
            summary=_("Import image documents"),
            operation_id=_("Import image documents"),  # type: ignore
            parameters=ImageBatchCreateAPI.get_parameters(),
            request=ImageBatchCreateAPI.get_request(),
            responses=ImageBatchCreateAPI.get_response(),
            tags=[_("Knowledge Base/Images")],  # type: ignore
        )
        @_document_permissions(PermissionConstants.KNOWLEDGE_DOCUMENT_CREATE)
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(
                ImageDocumentSerializers.Preview(
                    data={
                        "workspace_id": workspace_id,
                        "knowledge_id": knowledge_id,
                        "user_id": request.user.id,
                    }
                ).batch_create(request.data)
            )
