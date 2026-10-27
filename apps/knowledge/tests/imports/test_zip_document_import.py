"""PDF archives use the real parsers for preview and direct document import."""

import io
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4
from zipfile import ZIP_DEFLATED, ZipFile

from common.handle.impl.text.pdf_split_handle import PdfSplitHandle
from common.handle.impl.text.zip_split_handle import FileBufferHandle
from django.core.files.base import ContentFile
from django.test import SimpleTestCase
from knowledge.serializers.document import DocumentSerializers
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject


def pdf_bytes(text, *, padding_size=0):
    writer = PdfWriter()
    if padding_size:
        writer.add_metadata({"/TestPadding": "x" * padding_size})
    page = writer.add_blank_page(width=612, height=792)
    page[NameObject("/Resources")] = DictionaryObject(
        {
            NameObject("/Font"): DictionaryObject(
                {
                    NameObject("/F1"): DictionaryObject(
                        {
                            NameObject("/Type"): NameObject("/Font"),
                            NameObject("/Subtype"): NameObject("/Type1"),
                            NameObject("/BaseFont"): NameObject("/Helvetica"),
                        }
                    )
                }
            )
        }
    )
    stream = DecodedStreamObject()
    stream.set_data(f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("ascii"))
    page[NameObject("/Contents")] = stream
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


class PdfFileStreamTests(SimpleTestCase):
    def test_standalone_upload_still_extracts_text(self):
        with ContentFile(pdf_bytes("Standalone PDF text"), name="standalone.pdf") as file:
            document = PdfSplitHandle().handle(file, None, False, 4096, FileBufferHandle().get_buffer, MagicMock())

        self.assertEqual(document["name"], "standalone.pdf")
        self.assertIn("Standalone PDF text", "".join(p["content"] for p in document["content"]))

    def test_pdf_rewinds_previously_read_input_without_populating_the_buffer(self):
        get_buffer = MagicMock(side_effect=AssertionError("PDF parsing must not buffer the entire input"))
        with ContentFile(pdf_bytes("Previously read PDF text"), name="read.pdf") as file:
            file.read()
            document = PdfSplitHandle().handle(file, None, False, 4096, get_buffer, MagicMock())

        self.assertIn("Previously read PDF text", "".join(p["content"] for p in document["content"]))
        get_buffer.assert_not_called()

    def test_large_pdf_zip_member_is_read_in_bounded_chunks(self):
        payload = pdf_bytes("PDF text across chunk boundaries", padding_size=192 * 1024)
        archive_buffer = io.BytesIO()
        with ZipFile(archive_buffer, "w", compression=ZIP_DEFLATED) as archive:
            archive.writestr("large.pdf", payload)
        get_buffer = MagicMock(side_effect=AssertionError("PDF parsing must not buffer the entire input"))

        with ZipFile(archive_buffer) as archive, archive.open("large.pdf") as file:
            original_read = file.read
            read_sizes = []

            def read_chunk(size=-1):
                self.assertGreater(size, 0)
                self.assertLessEqual(size, 64 * 1024)
                chunk = original_read(size)
                read_sizes.append(len(chunk))
                return chunk

            with patch.object(file, "read", side_effect=read_chunk):
                document = PdfSplitHandle().handle(file, None, False, 4096, get_buffer, MagicMock())

        self.assertEqual(sum(read_sizes), len(payload))
        self.assertGreater(len([size for size in read_sizes if size]), 1)
        self.assertIn("PDF text across chunk boundaries", "".join(p["content"] for p in document["content"]))
        get_buffer.assert_not_called()


class ZipDocumentImportTests(SimpleTestCase):
    def setUp(self):
        self.scope = {"workspace_id": "default", "knowledge_id": str(uuid4()), "user_id": str(uuid4())}
        self.pdf_name = "英语句型转换练习.pdf"
        self.text = "PDF archive text " * 8
        self.source = MagicMock(id=uuid4(), file_name="documents.zip", size=None, meta={})
        self.knowledge = SimpleNamespace(file_size_limit=1)
        query = self.enterContext(patch("knowledge.serializers.document.QuerySet"))
        query.return_value.filter.return_value.first.return_value = self.knowledge
        query.return_value.filter.return_value.filter.return_value.first.return_value = self.knowledge
        query.return_value.filter.return_value.__iter__.return_value = [self.source]
        self.save_file = self.enterContext(patch("knowledge.serializers.document.File.save"))
        self.payload = {"file_id_list": [str(self.source.id)]}

    def set_archive(self, members):
        buffer = io.BytesIO()
        with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as archive:
            for name, content in members:
                archive.writestr(name, content)
        self.source.get_bytes.return_value = buffer.getvalue()
        self.source.file_size = len(buffer.getvalue())

    def test_preview_pdf_only_archive_preserves_source_and_split_options(self):
        self.set_archive([(self.pdf_name, pdf_bytes(self.text))])
        self.payload["doc_strategy"] = {"split": {"limit": 50, "auto_clean": True}}

        documents = DocumentSerializers.Split(data=self.scope).parse_by_file_ids(self.payload)

        self.assertEqual(len(documents), 1)
        document = documents[0]
        self.assertEqual(document["name"], self.pdf_name)
        self.assertEqual(document["source_file_id"], self.source.id)
        self.assertEqual("".join(p["content"] for p in document["content"]).strip(), self.text.strip())
        self.assertGreater(len(document["content"]), 1)
        self.assertTrue(all(len(p["content"]) <= 50 for p in document["content"]))
        self.assertEqual(document["doc_strategy"]["split"]["limit"], 50)
        self.assertTrue(document["doc_strategy"]["split"]["auto_clean"])
        self.save_file.assert_not_called()

    def test_preview_keeps_all_pdfs_and_text_in_a_mixed_nested_archive(self):
        names = [f"练习/{self.pdf_name}", "answers.PDF", "notes.txt"]
        texts = ["First PDF text", "Second PDF text", "Text document"]
        self.set_archive(
            [
                ("练习/", b""),
                (names[0], pdf_bytes(texts[0])),
                (names[1], pdf_bytes(texts[1])),
                (names[2], texts[2].encode()),
                ("__MACOSX/._answers.PDF", b"ignored metadata"),
            ]
        )

        documents = DocumentSerializers.Split(data=self.scope).parse_by_file_ids(self.payload)

        self.assertEqual([document["name"] for document in documents], names)
        for document, text in zip(documents, texts):
            self.assertEqual(document["source_file_id"], self.source.id)
            self.assertIn(text, "".join(p["content"] for p in document["content"]))
        self.save_file.assert_not_called()

    def test_direct_import_passes_pdf_paragraphs_to_document_creation(self):
        self.set_archive([(self.pdf_name, pdf_bytes(self.text))])
        with (
            patch("knowledge.serializers.document.transaction.atomic", return_value=nullcontext()),
            patch("knowledge.serializers.document.DocumentSerializers.Batch") as batch,
        ):
            batch.return_value.batch_save.return_value = [{"id": "created"}]

            result = DocumentSerializers.Create(data=self.scope).save_text(self.payload)

        self.assertEqual(result, [{"id": "created"}])
        batch.assert_called_once_with(data=self.scope)
        documents = batch.return_value.batch_save.call_args.args[0]
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0]["name"], self.pdf_name)
        self.assertEqual(documents[0]["source_file_id"], self.source.id)
        self.assertIn(self.text.strip(), "".join(p["content"] for p in documents[0]["paragraphs"]))
        self.assertNotIn("content", documents[0])
        self.save_file.assert_not_called()
