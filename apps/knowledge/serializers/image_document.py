"""API serializers for standalone image documents."""

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from knowledge.serializers.document import DocumentSerializers
from knowledge.serializers.document_strategy import DocumentStrategySerializer
from knowledge.services.image_documents import ImageDocumentService


class ImagePreviewUploadRequest(serializers.Serializer):
    file = serializers.ListField(child=serializers.FileField(), allow_empty=False, max_length=50)
    doc_strategy = DocumentStrategySerializer(required=False, allow_null=True)


class ImagePreviewUpdateRequest(serializers.Serializer):
    name = serializers.CharField(required=False, min_length=1, max_length=150)
    caption = serializers.CharField(required=False, allow_blank=True, max_length=1024)
    ocr_text = serializers.CharField(required=False, allow_blank=True, max_length=102400)
    description = serializers.CharField(required=False, allow_blank=True, max_length=102400)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError(_("At least one field must be provided"))
        return attrs


class ImagePreviewBatchCreateRequest(serializers.Serializer):
    preview_ids = serializers.ListField(
        child=serializers.UUIDField(), allow_empty=False, max_length=50, label=_("image preview ids")
    )


class ImageDocumentSerializers:
    class Preview(serializers.Serializer):
        workspace_id = serializers.CharField(required=True)
        knowledge_id = serializers.UUIDField(required=True)
        user_id = serializers.UUIDField(required=False, allow_null=True)

        def _service(self) -> ImageDocumentService:
            self.is_valid(raise_exception=True)
            return ImageDocumentService(
                self.validated_data["workspace_id"],
                self.validated_data["knowledge_id"],
                self.validated_data.get("user_id"),
            )

        def upload(self, instance):
            request_serializer = ImagePreviewUploadRequest(data=instance)
            request_serializer.is_valid(raise_exception=True)
            return self._service().create_previews(
                request_serializer.validated_data["file"],
                request_serializer.validated_data.get("doc_strategy"),
            )

        def one(self, preview_id):
            return self._service().get_preview(preview_id)

        def edit(self, preview_id, instance):
            request_serializer = ImagePreviewUpdateRequest(data=instance)
            request_serializer.is_valid(raise_exception=True)
            return self._service().update_preview(preview_id, request_serializer.validated_data)

        def delete(self, preview_id):
            return self._service().delete_preview(preview_id)

        def batch_create(self, instance):
            request_serializer = ImagePreviewBatchCreateRequest(data=instance)
            request_serializer.is_valid(raise_exception=True)
            service = self._service()
            document_ids = service.import_previews(request_serializer.validated_data["preview_ids"])
            result = []
            for document_id in document_ids:
                operate = DocumentSerializers.Operate(
                    data={
                        "workspace_id": self.validated_data["workspace_id"],
                        "knowledge_id": self.validated_data["knowledge_id"],
                        "document_id": document_id,
                    }
                )
                result.append(operate.one(with_valid=True))
                operate.refresh(with_valid=False)
            return result
