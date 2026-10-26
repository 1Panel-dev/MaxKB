"""HTTP endpoints for standalone image documents."""

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.auth.constants.permission_constants import PermissionConstants
from common.result import result
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.views import APIView

from knowledge.permissions import knowledge_permission
from knowledge.api.document import ImageBatchCreateAPI, ImagePreviewAPI, ImagePreviewOperateAPI
from knowledge.serializers.image_document import ImageDocumentSerializers


class ImageDocumentView:
    class Preview(APIView):
        authentication_classes = [TokenAuth]
        parser_classes = [JSONParser]

        @extend_schema(
            methods=["POST"],
            description=_("Generate editable previews from uploaded image file IDs"),
            summary=_("Generate image previews"),
            operation_id=_("Generate image previews"),  # type: ignore
            parameters=ImagePreviewAPI.get_parameters(),
            request=ImagePreviewAPI.get_request(),
            responses=ImagePreviewAPI.get_response(),
            tags=[_("Knowledge Base/Images")],  # type: ignore
        )
        @has_permissions(knowledge_permission(PermissionConstants.KNOWLEDGE_IMAGE_CREATE))
        def post(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(
                ImageDocumentSerializers.Preview(
                    data={
                        "workspace_id": workspace_id,
                        "knowledge_id": knowledge_id,
                        "user_id": request.user.id,
                    }
                ).upload(request.data)
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
        @has_permissions(knowledge_permission(PermissionConstants.KNOWLEDGE_IMAGE_READ))
        def get(self, request: Request, workspace_id: str, knowledge_id: str, preview_id: str):
            return result.success(
                ImageDocumentSerializers.Preview(
                    data={"workspace_id": workspace_id, "knowledge_id": knowledge_id, "user_id": request.user.id}
                ).one(preview_id)
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
        @has_permissions(knowledge_permission(PermissionConstants.KNOWLEDGE_IMAGE_EDIT))
        def put(self, request: Request, workspace_id: str, knowledge_id: str, preview_id: str):
            return result.success(
                ImageDocumentSerializers.Preview(
                    data={"workspace_id": workspace_id, "knowledge_id": knowledge_id, "user_id": request.user.id}
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
        @has_permissions(knowledge_permission(PermissionConstants.KNOWLEDGE_IMAGE_EDIT))
        def delete(self, request: Request, workspace_id: str, knowledge_id: str, preview_id: str):
            return result.success(
                ImageDocumentSerializers.Preview(
                    data={"workspace_id": workspace_id, "knowledge_id": knowledge_id, "user_id": request.user.id}
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
        @has_permissions(knowledge_permission(PermissionConstants.KNOWLEDGE_IMAGE_CREATE))
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
