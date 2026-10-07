# coding=utf-8
"""
@project: maxkb
@file: test_pdf_split_mode.py
@desc: Regression checks for explicit PDF splitting modes; no database is required.
"""
import io
import json
import zipfile
from unittest.mock import MagicMock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from pypdf import PdfWriter
from pypdf.annotations import Link
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject
from rest_framework.serializers import Serializer
from rest_framework.test import APIRequestFactory, force_authenticate

from common.handle.impl.text.pdf_split_handle import PdfSplitHandle
from common.handle.impl.text.zip_split_handle import ZipSplitHandle, file_to_paragraph
from knowledge.serializers.document import DocumentSerializers, DocumentSplitRequest
from knowledge.views.document import DocumentView

SECTION_PATTERN = r"(?<=^)Section.*|(?<=\n)Section.*"
KNOWLEDGE_ID = "00000000-0000-0000-0000-000000000001"


def native_pdf(bookmarks=True, links=False):
    writer = PdfWriter()
    for section in ("One", "Two"):
        page = writer.add_blank_page(width=595, height=842)
        font = DictionaryObject({
            NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        })
        page[NameObject("/Resources")] = DictionaryObject({
            NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)}),
        })
        body = "Alpha   beta. " + "A complete sentence. " * 12
        operators = f"BT /F1 12 Tf 72 700 Td (Section {section}) Tj 0 -20 Td ({body}) Tj ET"
        stream = DecodedStreamObject()
        stream.set_data(operators.encode("ascii"))
        page[NameObject("/Contents")] = writer._add_object(stream)
    if bookmarks:
        writer.add_outline_item("Document bookmark", 0)
    if links:
        writer.add_annotation(0, Link(rect=(72, 680, 200, 710), target_page_index=1))
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


class PdfSplitModeTests(SimpleTestCase):
    def setUp(self):
        enabled = patch("common.handle.impl.text.pdf_split_handle.ocr_enabled", return_value=False)
        enabled.start()
        self.addCleanup(enabled.stop)

    def split(self, mode=None, patterns=None, clean=False, limit=4096, bookmarks=True, links=False):
        file = SimpleUploadedFile("policy.pdf", native_pdf(bookmarks, links))
        return PdfSplitHandle().handle(
            file, patterns, clean, limit, lambda f: f.read(), MagicMock(), split_mode=mode
        )["content"]

    def test_advanced_patterns_change_bookmarked_pdf_segments(self):
        sections = self.split("advanced", [SECTION_PATTERN])
        unsplit = self.split("advanced", [r"NEVER_MATCH"])
        self.assertEqual([p["title"] for p in sections], ["Section One", "Section Two"])
        self.assertEqual(len(unsplit), 1)
        self.assertIn("Section Two", unsplit[0]["content"])
        self.assertTrue(all("Alpha   beta." in p["content"] for p in sections))

    def test_advanced_without_patterns_honors_cleaning_and_length(self):
        raw = self.split("advanced", [], limit=100)
        cleaned = self.split("advanced", [], clean=True, limit=100)
        self.assertTrue(all(0 < len(p["content"]) <= 100 for p in raw + cleaned))
        self.assertIn("Alpha   beta.", "".join(p["content"] for p in raw))
        self.assertIn("Alpha beta.", "".join(p["content"] for p in cleaned))
        self.assertNotIn("   ", "".join(p["content"] for p in cleaned))

    def test_intelligent_and_omitted_mode_preserve_bookmark_behavior(self):
        legacy = self.split()
        intelligent = self.split("intelligent")
        self.assertEqual(intelligent, legacy)
        self.assertEqual(len(legacy), 1)
        self.assertEqual(legacy[0]["title"], "Document bookmark")

    def test_user_patterns_take_priority_without_advanced_mode(self):
        for mode in (None, "intelligent"):
            with self.subTest(mode=mode):
                paragraphs = self.split(mode, [SECTION_PATTERN])
                self.assertEqual([p["title"] for p in paragraphs], ["Section One", "Section Two"])
                self.assertTrue(all("Alpha   beta." in p["content"] for p in paragraphs))

    def test_unmatched_user_pattern_uses_length_splitting_without_directory_fallback(self):
        paragraphs = self.split(patterns=[r"NEVER_MATCH"], clean=True, limit=100)
        self.assertGreater(len(paragraphs), 1)
        self.assertTrue(all(p["title"] == "" and len(p["content"]) <= 100 for p in paragraphs))
        self.assertIn("Section One", "".join(p["content"] for p in paragraphs))
        self.assertIn("Section Two", "".join(p["content"] for p in paragraphs))

    @patch("common.handle.impl.text.pdf_split_handle.ocr_enabled", return_value=True)
    @patch.object(PdfSplitHandle, "page_needs_ocr", return_value=True)
    @patch("common.handle.impl.text.pdf_split_handle.recognize_pdf_page", return_value="Recognized policy text.")
    def test_advanced_keeps_ocr_in_full_text_extraction(self, recognize, needs_ocr, enabled):
        paragraphs = self.split("advanced", [r"NEVER_MATCH"], limit=100)
        self.assertEqual(recognize.call_count, 2)
        self.assertIn("Recognized policy text.", paragraphs[0]["content"])
        self.assertNotIn("![image]", paragraphs[0]["content"])

    def test_advanced_bypasses_internal_links_and_keeps_all_text(self):
        with patch.object(PdfSplitHandle, "handle_links", wraps=PdfSplitHandle.handle_links) as handle_links:
            for mode in (None, "advanced"):
                paragraphs = self.split(mode, [SECTION_PATTERN], bookmarks=False, links=True)
                self.assertEqual([p["title"] for p in paragraphs], ["Section One", "Section Two"])
            handle_links.assert_not_called()
            self.split("intelligent", bookmarks=False, links=True)
            handle_links.assert_called_once()

    def test_request_modes_are_optional_and_validated(self):
        for mode in (None, "intelligent", "advanced"):
            data = {"file": []}
            if mode is not None:
                data["split_mode"] = mode
            self.assertTrue(DocumentSplitRequest(data=data).is_valid())
        invalid = DocumentSplitRequest(data={"file": [], "split_mode": "invalid"})
        self.assertFalse(invalid.is_valid())
        self.assertIn("split_mode", invalid.errors)

    @patch("common.auth.authentication.exist", return_value=True)
    @patch.object(DocumentSerializers.Split, "is_valid", autospec=True)
    @patch("knowledge.serializers.document.File")
    def test_multipart_request_carries_mode_to_pdf_splitter(self, file_model, validate, permission):
        validate.side_effect = lambda serializer, **kwargs: Serializer.is_valid(serializer, raise_exception=True)
        for mode in (None, "advanced"):
            with self.subTest(mode=mode):
                data = {
                    "file": SimpleUploadedFile("policy.pdf", native_pdf()),
                    "patterns": [SECTION_PATTERN], "limit": "100", "with_filter": "true",
                }
                if mode is not None:
                    data["split_mode"] = mode
                request = APIRequestFactory().post("/split", data, format="multipart")
                force_authenticate(request, user=MagicMock(), token=MagicMock())
                response = DocumentView.Split.as_view()(request, workspace_id="default", knowledge_id=KNOWLEDGE_ID)
                self.assertEqual(response.status_code, 200)
                payload = json.loads(response.content)
                self.assertEqual(payload["code"], 200)
                paragraphs = payload["data"][0]["content"]
                self.assertEqual({p["title"] for p in paragraphs}, {"Section One", "Section Two"})
                self.assertTrue(all(len(p["content"]) <= 100 for p in paragraphs))
                self.assertNotIn("   ", "".join(p["content"] for p in paragraphs))

    def test_zip_dispatch_carries_mode_to_pdf_splitter(self):
        file = SimpleUploadedFile("policy.pdf", native_pdf())
        paragraphs = file_to_paragraph(file, [SECTION_PATTERN], False, 4096, MagicMock(), split_mode="advanced")
        self.assertEqual([p["title"] for p in paragraphs["content"]], ["Section One", "Section Two"])

    def test_zip_archive_forwards_mode_and_preserves_legacy_call(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("policy.pdf", native_pdf())
        for mode, patterns in ((None, []), (None, [SECTION_PATTERN]), ("advanced", [SECTION_PATTERN])):
            file = SimpleUploadedFile("policies.zip", buffer.getvalue())
            result = ZipSplitHandle().handle(
                file, patterns, False, 4096, lambda f: f.read(), MagicMock(), split_mode=mode
            )
            expected = ["Section One", "Section Two"] if patterns else ["Document bookmark"]
            self.assertEqual([p["title"] for p in result[0]["content"]], expected)
