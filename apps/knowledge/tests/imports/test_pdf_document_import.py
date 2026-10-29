"""Compatibility checks through the real PDF import parser."""

import io
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.core.files.base import ContentFile
from django.test import SimpleTestCase
from PIL import Image

from common.handle.impl.text.pdf_split_handle import PdfSplitHandle
from knowledge.tests.imports.pdf_helpers import content_pdf


class PdfDocumentImportTests(SimpleTestCase):
    def parse(self, content, *, limit=4096):
        save_image = MagicMock()
        get_buffer = MagicMock(side_effect=AssertionError("PDF import should read the file stream"))
        with ContentFile(content, name="回归样例.pdf") as file:
            result = PdfSplitHandle().handle(file, None, False, limit, get_buffer, save_image)
        self.assertEqual(result["name"], "回归样例.pdf")
        get_buffer.assert_not_called()
        return result["content"], save_image

    def test_compressed_unicode_text_and_font_sizes_survive_import(self):
        content = content_pdf([[("中文标题", 720, 18), ("第一段正文。", 680, 12), ("Second paragraph.", 650, 12)]])
        paragraphs, save_image = self.parse(content)
        self.assertEqual(paragraphs[0]["title"].strip("# "), "中文标题")
        text = "".join(p["content"] for p in paragraphs)
        self.assertIn("第一段正文。", text)
        self.assertIn("Second paragraph.", text)
        self.assertNotIn("\x00", text)
        save_image.assert_not_called()

    def test_positioned_bookmarks_split_two_chapters_on_the_same_page(self):
        content = content_pdf(
            [[("第一章", 720, 18), ("甲正文。", 690, 12), ("第二章", 420, 18), ("乙正文。", 390, 12)]],
            bookmarks=[("第一章", 0, 730), ("第二章", 0, 430)],
        )
        paragraphs, save_image = self.parse(content)
        self.assertEqual([p["title"] for p in paragraphs], ["第一章", "第二章"])
        self.assertEqual([p["content"].strip() for p in paragraphs], ["甲正文。", "乙正文。"])
        save_image.assert_not_called()

    def test_internal_link_directory_resolves_destination_page(self):
        content = content_pdf(
            [[("目标章节", 720, 12)], [("目标章节", 720, 18), ("链接正文。", 680, 12)]],
            links=[(0, 1, (70, 718, 200, 735))],
        )
        paragraphs, _save_image = self.parse(content)
        self.assertEqual(paragraphs, [{"title": "目标章节", "content": "链接正文。"}])

    def test_embedded_image_keeps_pixels_and_saved_file_reference(self):
        paragraphs, save_image = self.parse(content_pdf([[("图片正文。", 720, 12)]], image=True))
        save_image.assert_called_once()
        files = save_image.call_args.args[0]
        self.assertEqual(len(files), 1)
        text = "".join(p["content"] for p in paragraphs)
        self.assertIn("图片正文。", text)
        self.assertIn(f"![image](./oss/file/{files[0].id})", text)
        with Image.open(io.BytesIO(files[0].meta["content"])) as bitmap:
            self.assertEqual(bitmap.size, (2, 2))
            self.assertEqual(bitmap.convert("RGB").getpixel((0, 0)), (255, 0, 0))
            self.assertEqual(bitmap.convert("RGB").getpixel((1, 1)), (255, 255, 255))

    def test_empty_password_encrypted_document_remains_readable(self):
        paragraphs, _save_image = self.parse(content_pdf([[("加密正文。", 720, 12)]], password=""))
        self.assertIn("加密正文。", "".join(p["content"] for p in paragraphs))

    def test_password_protected_document_preserves_empty_result_behavior(self):
        with self.assertLogs("max_kb", level="ERROR"):
            paragraphs, save_image = self.parse(content_pdf([[("保密正文。", 720, 12)]], password="fixture-password"))
        self.assertEqual(paragraphs, [])
        save_image.assert_not_called()

    def test_blank_page_returns_no_paragraphs(self):
        paragraphs, save_image = self.parse(content_pdf([[]]))
        self.assertEqual(paragraphs, [])
        save_image.assert_not_called()

    def test_malformed_document_returns_empty_result_and_removes_tempfile(self):
        create_tempfile = tempfile.NamedTemporaryFile
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch(
                    "common.handle.impl.text.pdf_split_handle.tempfile.NamedTemporaryFile",
                    side_effect=lambda **kwargs: create_tempfile(dir=directory, **kwargs),
                ),
                self.assertLogs("max_kb", level="ERROR"),
            ):
                paragraphs, save_image = self.parse(b"%PDF-1.7\n1 0 obj\n<< /Type /Catalog >>\nendobj\n")
            self.assertEqual(paragraphs, [])
            self.assertEqual(list(Path(directory).iterdir()), [])
            save_image.assert_not_called()
