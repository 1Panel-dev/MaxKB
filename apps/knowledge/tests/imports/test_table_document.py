import io
import zipfile

import openpyxl
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

from common.exception.app_exception import AppApiException
from django.core.files.base import ContentFile
from django.test import SimpleTestCase
from knowledge.models import FileSourceType
from knowledge.serializers.document import DocumentInstanceFileIdsSerializer, DocumentSerializers
from rest_framework import serializers


class UploadedDocumentFileTestsMixin:
    def setUp(self):
        self.knowledge_id = uuid4()
        self.user_id = uuid4()
        self.creator = DocumentSerializers.Create(
            data={"knowledge_id": self.knowledge_id, "workspace_id": "default", "user_id": self.user_id}
        )

        serializers.Serializer.is_valid(self.creator, raise_exception=True)

    def source(self, name="table.csv"):
        source = MagicMock()
        source.id = uuid4()
        source.file_name = name
        source.file_size = 10
        source.size = None
        source.meta = {}
        source.get_bytes.return_value = self.csv_bytes
        return source

    def save(self, payload):
        return getattr(self.creator, self.save_method)(payload)

    def test_invalid_id_lists(self):
        file_id = str(uuid4())
        for payload in ({}, {"file_id_list": []}, {"file_id_list": ["invalid"]}, {"file_id_list": [file_id, file_id]}):
            with self.subTest(payload=payload):
                self.assertFalse(DocumentInstanceFileIdsSerializer(data=payload).is_valid())

    def test_reuses_uploaded_sources_in_request_order(self):
        first, second = self.source("first.csv"), self.source("second.csv")
        knowledge = SimpleNamespace(file_size_limit=10)
        with (
            patch.object(self.creator, "is_valid"),
            patch("knowledge.serializers.document.QuerySet") as queryset,
            patch("knowledge.serializers.document.DocumentSerializers.Batch") as batch,
            patch.object(
                self.creator, self.parse_method, side_effect=[[{"name": "first"}], [{"name": "second"}]]
            ) as parse,
        ):
            queryset.return_value.filter.return_value.first.return_value = knowledge
            queryset.return_value.filter.return_value.__iter__.return_value = [second, first]
            batch.return_value.batch_save.return_value = [{"id": "created"}]
            self.assertEqual(self.save({"file_id_list": [str(first.id), str(second.id)]}), [{"id": "created"}])
            self.assertEqual([call.args[0].name for call in parse.call_args_list], ["first.csv", "second.csv"])
            self.assertEqual([call.kwargs["source_file_id"] for call in parse.call_args_list], [first.id, second.id])
            batch.return_value.batch_save.assert_called_once_with([{"name": "first"}, {"name": "second"}])
            queryset.return_value.filter.return_value.update.assert_called_once_with(
                source_type=FileSourceType.KNOWLEDGE, source_id=str(self.knowledge_id)
            )
            condition = queryset.return_value.filter.call_args_list[1].args[0]
            self.assertIn(str(self.user_id), str(condition))
            self.assertIn(str(self.knowledge_id), str(condition))

    def test_missing_or_inaccessible_file_fails_before_reading(self):
        source = self.source()
        with patch.object(self.creator, "is_valid"), patch("knowledge.serializers.document.QuerySet") as queryset:
            queryset.return_value.filter.return_value.first.return_value = SimpleNamespace(file_size_limit=10)
            queryset.return_value.filter.return_value.__iter__.return_value = [source]
            with self.assertRaises(AppApiException):
                self.save({"file_id_list": [str(source.id), str(uuid4())]})
            source.get_bytes.assert_not_called()
            queryset.return_value.filter.return_value.update.assert_not_called()

    def test_wrong_workspace_fails_before_loading_files(self):
        with patch.object(self.creator, "is_valid"), patch("knowledge.serializers.document.QuerySet") as queryset:
            queryset.return_value.filter.return_value.first.return_value = None
            with self.assertRaises(AppApiException):
                self.save({"file_id_list": [str(uuid4())]})
            self.assertEqual(queryset.return_value.filter.call_count, 1)

    def test_size_limit_checks_actual_uncompressed_bytes(self):
        source = self.source()
        source.get_bytes.return_value = b"x" * (1024 * 1024 + 1)
        with patch.object(self.creator, "is_valid"), patch("knowledge.serializers.document.QuerySet") as queryset:
            queryset.return_value.filter.return_value.first.return_value = SimpleNamespace(file_size_limit=1)
            queryset.return_value.filter.return_value.__iter__.return_value = [source]
            with self.assertRaises(AppApiException):
                self.save({"file_id_list": [str(source.id)]})
            queryset.return_value.filter.return_value.update.assert_not_called()

    def test_csv_parser_reuses_id_without_saving_another_source(self):
        source_id = uuid4()
        with patch("knowledge.serializers.document.File") as file_model:
            documents = getattr(self.creator, self.parse_method)(
                ContentFile(self.csv_bytes, name="table.csv"), source_file_id=source_id
            )
            file_model.assert_not_called()
        self.assertEqual(documents[0]["source_file_id"], source_id)
        self.assertEqual(documents[0]["paragraphs"][0], self.expected_paragraph)

    def test_original_upload_still_saves_source(self):
        with patch("knowledge.serializers.document.File") as file_model:
            documents = getattr(self.creator, self.parse_method)(ContentFile(self.csv_bytes, name="table.csv"))
            file_model.return_value.save.assert_called_once_with(self.csv_bytes)
            self.assertEqual(documents[0]["source_file_id"], file_model.call_args.kwargs["id"])

    def test_unsupported_format_is_rejected(self):
        with self.assertRaises(AppApiException):
            getattr(self.creator, self.parse_method)(ContentFile(b"text", name="table.txt"), source_file_id=uuid4())


class TableDocumentFileTests(UploadedDocumentFileTestsMixin, SimpleTestCase):
    save_method = "save_table_by_file_ids"
    parse_method = "parse_table_file"
    csv_bytes = b"name,value\na,1\n"
    expected_paragraph = {"title": "", "content": "name:a; value:1"}


class QaDocumentFileTests(UploadedDocumentFileTestsMixin, SimpleTestCase):
    save_method = "save_qa_by_file_ids"
    parse_method = "parse_qa_file"
    csv_bytes = b'title,content,questions\nFAQ,Answer,"Question one\nQuestion two"\n'
    expected_paragraph = {
        "title": "FAQ",
        "content": "Answer",
        "problem_list": [{"content": "Question one"}, {"content": "Question two"}],
    }

    def test_uploaded_csv_creates_qa_with_questions(self):
        source = self.source()
        with (
            patch.object(self.creator, "is_valid"),
            patch("knowledge.serializers.document.QuerySet") as queryset,
            patch("knowledge.serializers.document.DocumentSerializers.Batch") as batch,
            patch("knowledge.serializers.document.File") as file_model,
        ):
            queryset.return_value.filter.return_value.first.return_value = SimpleNamespace(file_size_limit=10)
            queryset.return_value.filter.return_value.__iter__.return_value = [source]
            batch.return_value.batch_save.return_value = [{"id": "created"}]
            self.assertEqual(self.save({"file_id_list": [str(source.id)]}), [{"id": "created"}])
            batch.return_value.batch_save.assert_called_once_with(
                [{"name": source.file_name, "paragraphs": [self.expected_paragraph], "source_file_id": source.id}]
            )
            file_model.assert_not_called()

    def test_zip_documents_share_uploaded_source_id(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("first.csv", self.csv_bytes)
            archive.writestr("second.csv", self.csv_bytes)
        source_id = uuid4()
        with patch("knowledge.serializers.document.File") as file_model:
            documents = self.creator.parse_qa_file(
                ContentFile(buffer.getvalue(), name="qa.zip"), source_file_id=source_id
            )
            file_model.assert_not_called()
        self.assertEqual([doc["name"] for doc in documents], ["first.csv", "second.csv"])
        for document in documents:
            self.assertEqual(document["source_file_id"], source_id)
            self.assertEqual(document["paragraphs"], [self.expected_paragraph])

    def test_xlsx_sheets_share_uploaded_source_id(self):
        workbook = openpyxl.Workbook()
        workbook.active.title = "first"
        workbook.create_sheet("second")
        for sheet in workbook:
            sheet.append(["title", "content", "questions"])
            sheet.append(["FAQ", "Answer", "Question one\nQuestion two"])
        buffer = io.BytesIO()
        workbook.save(buffer)
        source_id = uuid4()
        with patch("knowledge.serializers.document.File") as file_model:
            documents = self.creator.parse_qa_file(
                ContentFile(buffer.getvalue(), name="qa.xlsx"), source_file_id=source_id
            )
            file_model.assert_not_called()
        self.assertEqual([doc["name"] for doc in documents], ["first", "second"])
        for document in documents:
            self.assertEqual(document["source_file_id"], source_id)
            self.assertEqual(document["paragraphs"], [self.expected_paragraph])
