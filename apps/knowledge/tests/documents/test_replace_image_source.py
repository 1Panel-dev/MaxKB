from io import BytesIO
from unittest.mock import MagicMock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from PIL import Image

from common.exception.app_exception import AppApiException
from knowledge.models import Document, DocumentResourceType, Knowledge
from knowledge.serializers.document import DocumentSerializers


class ReplaceImageSourceTests(SimpleTestCase):
    def validate(self, file, resource_type=DocumentResourceType.IMAGE):
        knowledge_query = MagicMock()
        knowledge_query.filter.return_value.filter.return_value.first.return_value = Knowledge(file_size_limit=10)
        document_query = MagicMock()
        document_query.filter.return_value.first.return_value = Document(resource_type=resource_type)
        with patch(
            "knowledge.serializers.document.QuerySet",
            side_effect=lambda model: knowledge_query if model is Knowledge else document_query,
        ):
            DocumentSerializers.ReplaceSourceFile(
                data={
                    "workspace_id": "workspace",
                    "knowledge_id": "00000000-0000-0000-0000-000000000001",
                    "document_id": "00000000-0000-0000-0000-000000000002",
                    "file": file,
                }
            ).is_valid(raise_exception=True)

    def test_nonimage_and_disguised_image_are_rejected(self):
        for name in ("document.pdf", "image.png", "image.gif"):
            with self.subTest(name=name), self.assertRaises(AppApiException):
                self.validate(SimpleUploadedFile(name, b"not an image"))

    def test_supported_images_preserve_file_contents_and_position(self):
        for extension, image_format in (
            ("JPG", "JPEG"),
            ("jpeg", "JPEG"),
            ("png", "PNG"),
            ("webp", "WEBP"),
            ("bmp", "BMP"),
        ):
            with self.subTest(extension=extension):
                buffer = BytesIO()
                Image.new("RGB", (2, 2)).save(buffer, format=image_format)
                file = SimpleUploadedFile(f"image.{extension}", buffer.getvalue())
                self.validate(file)
                self.assertEqual(file.tell(), 0)
                self.assertEqual(file.read(), buffer.getvalue())

    def test_regular_document_replacement_keeps_original_file_types(self):
        self.validate(SimpleUploadedFile("document.pdf", b"pdf"), DocumentResourceType.DOCUMENT)
