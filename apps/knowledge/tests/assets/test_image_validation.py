"""Validate image bytes and normalize mislabeled, supported image formats."""

from io import BytesIO

from common.exception.app_exception import AppApiException
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from PIL import Image

from knowledge.models import Knowledge
from knowledge.services.image_documents import ImageDocumentService


class ImageValidationTests(SimpleTestCase):
    def setUp(self):
        self.knowledge = Knowledge(file_size_limit=1)

    @staticmethod
    def image_bytes(image_format):
        buffer = BytesIO()
        Image.new("RGB", (2, 2), "white").save(buffer, format=image_format)
        return buffer.getvalue()

    def test_supported_content_normalizes_mismatched_extension_without_changing_bytes(self):
        for image_format, name, expected in (
            ("PNG", "神奇图片.jpg", "神奇图片.png"),
            ("JPEG", "photo.png", "photo.jpg"),
            ("WEBP", "photo.jpeg", "photo.webp"),
            ("BMP", "photo.webp", "photo.bmp"),
        ):
            with self.subTest(image_format=image_format):
                content = self.image_bytes(image_format)
                upload = SimpleUploadedFile(name, content)
                upload.seek(5)

                self.assertEqual(ImageDocumentService._validate_image(upload, self.knowledge), expected)
                self.assertEqual(upload.tell(), 5)
                upload.seek(0)
                self.assertEqual(upload.read(), content)
                self.assertEqual(upload.name, name)

    def test_matching_extensions_preserve_names_including_jpeg_alias_and_case(self):
        for image_format, name in (
            ("JPEG", "photo.jpg"),
            ("JPEG", "photo.JPEG"),
            ("PNG", "photo.PNG"),
            ("WEBP", "photo.webp"),
            ("BMP", "photo.bmp"),
        ):
            with self.subTest(name=name):
                upload = SimpleUploadedFile(name, self.image_bytes(image_format))
                self.assertEqual(ImageDocumentService._validate_image(upload, self.knowledge), name)

    def test_unsupported_content_is_rejected_even_with_supported_extension(self):
        for image_format in ("GIF", "TIFF"):
            with self.subTest(image_format=image_format):
                upload = SimpleUploadedFile("photo.jpg", self.image_bytes(image_format))
                with self.assertRaises(AppApiException):
                    ImageDocumentService._validate_image(upload, self.knowledge)
                self.assertEqual(upload.tell(), 0)

    def test_unsupported_extension_is_still_rejected(self):
        upload = SimpleUploadedFile("photo.txt", self.image_bytes("PNG"))
        with self.assertRaises(AppApiException):
            ImageDocumentService._validate_image(upload, self.knowledge)

    def test_invalid_and_corrupt_images_are_rejected_and_stream_position_is_restored(self):
        corrupt_png = bytearray(self.image_bytes("PNG"))
        corrupt_png[corrupt_png.index(b"IDAT") + 4] ^= 0xFF
        for content in (b"not an image", bytes(corrupt_png)):
            with self.subTest(content=content):
                upload = SimpleUploadedFile("photo.jpg", content)
                upload.seek(5)
                with self.assertRaises(AppApiException):
                    ImageDocumentService._validate_image(upload, self.knowledge)
                self.assertEqual(upload.tell(), 5)
