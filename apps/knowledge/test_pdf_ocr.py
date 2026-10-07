# coding=utf-8
"""Regression checks for local OCR integration; no database or OCR model is required."""
import io
import json
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject, NumberObject

from common.handle.impl.text.pdf_ocr import PdfOcrError, recognize_pdf_page
from common.handle.impl.text.pdf_split_handle import PdfSplitHandle

OCR_TEXT = "青年创业领军项目扶持办法\n首次资金资助为50万元。\n申报条件与选拔程序应以政策正文为准。"


def pdf_bytes(image=True, native=False, outline=False):
    writer = PdfWriter()
    page = writer.add_blank_page(width=595, height=842)
    resources = DictionaryObject()
    operators = b""
    if image:
        bitmap = DecodedStreamObject()
        bitmap.set_data(b"\xff" * 16 * 16 * 3)
        bitmap.update({NameObject("/Type"): NameObject("/XObject"), NameObject("/Subtype"): NameObject("/Image"),
                       NameObject("/Width"): NumberObject(16), NameObject("/Height"): NumberObject(16),
                       NameObject("/ColorSpace"): NameObject("/DeviceRGB"), NameObject("/BitsPerComponent"): NumberObject(8)})
        resources[NameObject("/XObject")] = DictionaryObject({NameObject("/Im0"): writer._add_object(bitmap)})
        operators += b"q 400 0 0 600 20 20 cm /Im0 Do Q\n"
    if native:
        font = DictionaryObject({NameObject("/Type"): NameObject("/Font"),
                                 NameObject("/Subtype"): NameObject("/Type1"),
                                 NameObject("/BaseFont"): NameObject("/Helvetica")})
        resources[NameObject("/Font")] = DictionaryObject({NameObject("/F1"): writer._add_object(font)})
        operators += b"BT /F1 12 Tf 72 700 Td (Existing native text must remain unchanged.) Tj ET\n"
    page[NameObject("/Resources")] = resources
    stream = DecodedStreamObject()
    stream.set_data(operators)
    page[NameObject("/Contents")] = writer._add_object(stream)
    if outline:
        writer.add_outline_item("Policy", 0)
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


class PdfOcrTests(SimpleTestCase):
    def setUp(self):
        self.enabled = patch("common.handle.impl.text.pdf_split_handle.ocr_enabled", return_value=True)
        self.enabled.start()
        self.addCleanup(self.enabled.stop)

    @patch("common.handle.impl.text.pdf_split_handle.recognize_pdf_page", return_value=OCR_TEXT)
    def test_scan_is_split_into_actual_text_even_with_bookmarks(self, recognize):
        file = SimpleUploadedFile("scan.pdf", pdf_bytes(outline=True))
        save_image = MagicMock()
        result = PdfSplitHandle().handle(file, None, False, 1500, lambda f: f.read(), save_image)
        text = "\n".join(p["content"] for p in result["content"])
        self.assertIn("首次资金资助为50万元", text)
        self.assertNotIn("![image]", text)
        self.assertNotIn("./oss/file/", text)
        save_image.assert_not_called()
        recognize.assert_called_once()

    @patch("common.handle.impl.text.pdf_split_handle.recognize_pdf_page", return_value=OCR_TEXT)
    def test_workflow_extraction_uses_same_ocr(self, recognize):
        file = SimpleUploadedFile("scan.pdf", pdf_bytes())
        save_image = MagicMock()
        text = PdfSplitHandle().get_content(file, save_image)
        self.assertIn("青年创业领军项目", text)
        self.assertNotIn("![image]", text)
        save_image.assert_not_called()
        recognize.assert_called_once()

    @patch("common.handle.impl.text.pdf_split_handle.recognize_pdf_page")
    def test_text_pdf_preserves_native_text_and_skips_ocr(self, recognize):
        file = SimpleUploadedFile("native.pdf", pdf_bytes(image=False, native=True))
        text = PdfSplitHandle().get_content(file, lambda images: None)
        self.assertIn("Existing native text must remain unchanged.", text)
        recognize.assert_not_called()

    @patch("common.handle.impl.text.pdf_split_handle.recognize_pdf_page")
    def test_native_pdf_illustration_is_still_preserved(self, recognize):
        file = SimpleUploadedFile("illustrated.pdf", pdf_bytes(native=True))
        save_image = MagicMock()
        text = PdfSplitHandle().get_content(file, save_image)
        self.assertIn("Existing native text", text)
        self.assertEqual(text.count("![image]"), 1)
        save_image.assert_called_once()
        self.assertEqual(len(save_image.call_args.args[0]), 1)
        recognize.assert_not_called()

    @patch("common.handle.impl.text.pdf_split_handle.recognize_pdf_page", return_value=OCR_TEXT)
    def test_mixed_pdf_only_recognizes_scan_page(self, recognize):
        writer = PdfWriter()
        writer.append(PdfReader(io.BytesIO(pdf_bytes(native=True))))
        writer.append(PdfReader(io.BytesIO(pdf_bytes())))
        buffer = io.BytesIO()
        writer.write(buffer)
        file = SimpleUploadedFile("mixed.pdf", buffer.getvalue())
        save_image = MagicMock()
        text = PdfSplitHandle().get_content(file, save_image)
        self.assertIn("Existing native text", text)
        self.assertIn("50万元", text)
        self.assertEqual(text.count("![image]"), 1)
        save_image.assert_called_once()
        self.assertEqual(len(save_image.call_args.args[0]), 1)
        self.assertEqual(recognize.call_args.args[1], 2)
        recognize.assert_called_once()

    @patch("common.handle.impl.text.pdf_split_handle.recognize_pdf_page", side_effect=PdfOcrError("OCR unavailable"))
    def test_failure_is_not_silently_returned_as_empty_paragraphs(self, recognize):
        file = SimpleUploadedFile("scan.pdf", pdf_bytes())
        with self.assertRaises(PdfOcrError):
            PdfSplitHandle().handle(file, None, False, 1500, lambda f: f.read(), lambda images: None)
        file.seek(0)
        with self.assertRaises(PdfOcrError):
            PdfSplitHandle().get_content(file, lambda images: None)

    @patch("common.handle.impl.text.pdf_split_handle.recognize_pdf_page")
    def test_disabled_ocr_retains_previous_behavior(self, recognize):
        with patch("common.handle.impl.text.pdf_split_handle.ocr_enabled", return_value=False):
            file = SimpleUploadedFile("scan.pdf", pdf_bytes())
            save_image = MagicMock()
            text = PdfSplitHandle().get_content(file, save_image)
            self.assertIn("![image]", text)
            save_image.assert_called_once()
        recognize.assert_not_called()

    @patch("common.handle.impl.text.pdf_ocr.CONFIG", {"OCR_TOKEN": "test-token"})
    @patch("common.handle.impl.text.pdf_ocr.urlopen")
    def test_client_only_sends_requested_page(self, urlopen):
        response = MagicMock()
        response.read.return_value = json.dumps({"text": OCR_TEXT}).encode()
        urlopen.return_value.__enter__.return_value = response
        writer = PdfWriter()
        writer.append(PdfReader(io.BytesIO(pdf_bytes())))
        writer.append(PdfReader(io.BytesIO(pdf_bytes(image=False, native=True))))
        output = io.BytesIO()
        writer.write(output)
        recognize_pdf_page(PdfReader(output), 2)
        request = urlopen.call_args.args[0]
        sent = PdfReader(io.BytesIO(request.data))
        self.assertEqual(len(sent.pages), 1)
        self.assertIn("Existing native text", sent.pages[0].extract_text())

    @patch("common.handle.impl.text.pdf_ocr.CONFIG", {"OCR_URL": "https://external.example", "OCR_TOKEN": "test"})
    @patch("common.handle.impl.text.pdf_ocr.urlopen")
    def test_external_ocr_address_is_rejected(self, urlopen):
        with self.assertRaises(PdfOcrError):
            recognize_pdf_page(PdfReader(io.BytesIO(pdf_bytes())), 1)
        urlopen.assert_not_called()

    @patch("common.handle.impl.text.pdf_ocr.CONFIG", {"OCR_TOKEN": "test"})
    @patch("common.handle.impl.text.pdf_ocr.urlopen", side_effect=URLError("connection refused"))
    def test_unavailable_service_has_actionable_error(self, urlopen):
        with self.assertRaises(PdfOcrError) as caught:
            recognize_pdf_page(PdfReader(io.BytesIO(pdf_bytes())), 1)
        self.assertIn("OCR 服务不可用", caught.exception.message)

    @patch("common.handle.impl.text.pdf_ocr.CONFIG", {"OCR_TOKEN": "test"})
    @patch("common.handle.impl.text.pdf_ocr.urlopen")
    def test_busy_timeout_and_authentication_failures_are_distinct(self, urlopen):
        for status, message in ((429, "排队超时"), (504, "识别超时"), (401, "认证失败")):
            urlopen.side_effect = HTTPError("http://127.0.0.1:11637", status, "error", {}, io.BytesIO())
            with self.assertRaises(PdfOcrError) as caught:
                recognize_pdf_page(PdfReader(io.BytesIO(pdf_bytes())), 1)
            self.assertIn(message, caught.exception.message)

    @patch("common.handle.impl.text.pdf_ocr.CONFIG", {"OCR_TOKEN": "test"})
    @patch("common.handle.impl.text.pdf_ocr.urlopen")
    def test_empty_and_invalid_service_results_cannot_be_imported(self, urlopen):
        response = MagicMock()
        urlopen.return_value.__enter__.return_value = response
        for payload in ([], {"text": ""}, {"text": None}):
            response.read.return_value = json.dumps(payload).encode()
            with self.assertRaises(PdfOcrError):
                recognize_pdf_page(PdfReader(io.BytesIO(pdf_bytes())), 1)
