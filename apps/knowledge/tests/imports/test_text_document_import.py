"""Direct text import applies the strategy and creates documents in one request."""

import io
import json
from contextlib import ExitStack, nullcontext
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

from common.auth.constants.permission_constants import PermissionConstants
from common.exception.app_exception import AppApiException, AppUnauthorizedFailed
from django.core.files.base import ContentFile
from django.test import SimpleTestCase
from django.urls import resolve
from knowledge.api.document import DocumentImportAPI
from knowledge.models import File, FileSourceType
from knowledge.serializers.document import DocumentImportRequest, DocumentSerializers
from knowledge.services.document_strategy import normalize_document_strategy
from knowledge.views.document import DocumentView
from openpyxl import Workbook
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory, force_authenticate


class TextDocumentImportTests(SimpleTestCase):
    def setUp(self):
        self.scope = {"workspace_id": "default", "knowledge_id": str(uuid4()), "user_id": str(uuid4())}
        self.creator = DocumentSerializers.Create(data=self.scope)
        serializers.Serializer.is_valid(self.creator, raise_exception=True)
        self.sources = [self.source("first.txt", b"a" * 80), self.source("second.txt", b"answer")]
        self.strategy = {
            "split": {"mode": "advanced", "max_length": 50, "child_length": 50, "auto_clean": True},
            "visual": {"enabled": True, "strategy": "model", "model_id": str(uuid4())},
            "index": {"title_as_question": True},
        }
        self.payload = {
            "file_id_list": [str(source.id) for source in self.sources],
            "doc_strategy": self.strategy,
        }
        stack = ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(patch("knowledge.serializers.document.transaction.atomic", return_value=nullcontext()))
        stack.enter_context(patch.object(self.creator, "is_valid"))
        self.query = stack.enter_context(patch("knowledge.serializers.document.QuerySet"))
        self.knowledge = SimpleNamespace(file_size_limit=1)
        self.query.return_value.filter.return_value.first.return_value = self.knowledge
        self.query.return_value.filter.return_value.filter.return_value.first.return_value = self.knowledge
        self.query.return_value.filter.return_value.__iter__.return_value = self.sources[::-1]
        self.batch = stack.enter_context(patch("knowledge.serializers.document.DocumentSerializers.Batch"))
        self.batch.return_value.batch_save.return_value = [{"id": "created"}]

    def source(self, name, content):
        source = MagicMock()
        source.id = uuid4()
        source.file_name = name
        source.file_size = len(content)
        source.size = None
        source.meta = {"user_id": self.scope["user_id"]}
        source.get_bytes.return_value = content
        return source

    def test_import_parses_all_files_without_overwriting_document_file_ownership(self):
        # Use the actual text parser; importing sources must not save another source file.
        with patch("knowledge.serializers.document.File.save") as save_file:
            self.assertEqual(self.creator.save_text(self.payload), [{"id": "created"}])
            save_file.assert_not_called()

        self.batch.assert_called_once_with(data=self.scope)
        documents = self.batch.return_value.batch_save.call_args.args[0]
        self.assertEqual([document["name"] for document in documents], ["first.txt", "second.txt"])
        self.assertEqual([document["source_file_id"] for document in documents], [source.id for source in self.sources])
        self.assertEqual([len(p["content"]) for p in documents[0]["paragraphs"]], [50, 30])
        for document in documents:
            self.assertNotIn("content", document)
            self.assertEqual(document["doc_strategy"], normalize_document_strategy(self.strategy))
        self.query.return_value.filter.return_value.update.assert_not_called()
        condition = self.query.return_value.filter.call_args_list[1].args[0]
        self.assertIn(self.scope["user_id"], str(condition))
        self.assertIn(self.scope["knowledge_id"], str(condition))

    def test_existing_minimum_length_does_not_merge_the_file_tail(self):
        self.strategy["split"]["min_length"] = 40

        self.creator.save_text(self.payload)

        documents = self.batch.return_value.batch_save.call_args.args[0]
        self.assertEqual([len(p["content"]) for p in documents[0]["paragraphs"]], [50, 30])
        self.assertEqual(documents[0]["doc_strategy"]["split"]["min_length"], 0)
        self.assertEqual(documents[0]["doc_strategy"]["split"]["child_length"], 50)
        self.assertEqual(documents[0]["doc_strategy"]["visual"], normalize_document_strategy(self.strategy)["visual"])
        self.assertEqual(documents[0]["doc_strategy"]["index"], self.strategy["index"])

    def test_import_uses_nested_limit_and_preserves_it_in_the_saved_strategy(self):
        self.payload["doc_strategy"] = {
            "split": {"mode": "advanced", "patterns": None, "limit": 49523, "child_length": 256, "auto_clean": True},
            "visual": {"enabled": False, "strategy": "model", "model_id": None, "tool_id": None},
            "index": {"title_as_question": False},
        }
        self.sources[0].get_bytes.return_value = b"a" * 49623

        self.creator.save_text(self.payload)

        document = self.batch.return_value.batch_save.call_args.args[0][0]
        self.assertEqual([len(p["content"]) for p in document["paragraphs"]], [49523, 100])
        self.assertEqual(document["doc_strategy"]["split"]["limit"], 49523)
        self.assertEqual(document["doc_strategy"]["split"]["child_length"], 256)

    def test_empty_identifiers_keep_default_heading_splitting(self):
        self.strategy["split"]["patterns"] = []
        self.sources[0].file_name = "headings.md"
        self.sources[0].get_bytes.return_value = b"# First\nfirst paragraph\n# Second\nsecond paragraph"

        self.creator.save_text(self.payload)

        document = self.batch.return_value.batch_save.call_args.args[0][0]
        self.assertEqual([p["title"] for p in document["paragraphs"]], [" First", " Second"])
        self.assertEqual(
            [p["content"].strip() for p in document["paragraphs"]], ["first paragraph", "second paragraph"]
        )
        self.assertIsNone(document["doc_strategy"]["split"]["patterns"])

    def test_text_import_preserves_table_rows_exceeding_the_length_limit(self):
        workbook = Workbook()
        workbook.active.append(["column"])
        cell_content = "x" * 80
        workbook.active.append([cell_content])
        buffer = io.BytesIO()
        workbook.save(buffer)
        self.sources[0].file_name = "rows.xlsx"
        self.sources[0].get_bytes.return_value = buffer.getvalue()

        self.creator.save_text(self.payload)

        document = self.batch.return_value.batch_save.call_args.args[0][0]
        self.assertEqual(len(document["paragraphs"]), 1)
        self.assertIn(f"| {cell_content} |", document["paragraphs"][0]["content"])
        self.assertGreater(len(document["paragraphs"][0]["content"]), 50)

    def test_preview_accepts_v2_split_parameters(self):
        splitter = DocumentSerializers.Split(data=self.scope)
        serializers.Serializer.is_valid(splitter, raise_exception=True)
        with patch("knowledge.serializers.document.File.save"):
            document = splitter.parse(
                {"file": [ContentFile(b"a" * 80, name="legacy.txt")], "limit": 50, "with_filter": True}
            )[0]

        self.assertEqual([len(p["content"]) for p in document["content"]], [50, 30])
        self.assertEqual(document["doc_strategy"]["split"]["max_length"], 50)
        self.assertEqual(document["doc_strategy"]["split"]["min_length"], 0)
        self.assertTrue(document["doc_strategy"]["split"]["auto_clean"])

    def test_invalid_input_fails_before_parsing_or_saving(self):
        payloads = [
            {},
            {"file_id_list": []},
            {"file_id_list": ["invalid"]},
            {"file_id_list": [str(self.sources[0].id)] * 2},
            {"file": [ContentFile(b"text", name="text.txt")]},
            {**self.payload, "doc_strategy": {"split": {"max_length": 10}}},
            {**self.payload, "doc_strategy": {"split": {"limit": 10}}},
            {**self.payload, "doc_strategy": {"split": {"patterns": ["["]}}},
            {**self.payload, "doc_strategy": {"visual": {"enabled": True}}},
        ]
        with patch.object(DocumentSerializers.Split, "parse") as parse:
            for payload in payloads:
                with self.subTest(payload=payload), self.assertRaises(ValidationError):
                    self.creator.save_text(payload)
            parse.assert_not_called()
        self.batch.assert_not_called()
        self.query.assert_not_called()

    def test_missing_knowledge_or_wrong_workspace_fails_before_reading_files(self):
        self.query.return_value.filter.return_value.first.return_value = None
        with self.assertRaises(AppApiException):
            self.creator.save_text(self.payload)
        self.query.return_value.filter.assert_called_once_with(id=self.scope["knowledge_id"], workspace_id="default")
        for source in self.sources:
            source.get_bytes.assert_not_called()
        self.batch.assert_not_called()

    def test_missing_or_inaccessible_files_fail_before_reading(self):
        self.query.return_value.filter.return_value.__iter__.return_value = self.sources[:1]
        with self.assertRaises(AppApiException):
            self.creator.save_text(self.payload)
        for source in self.sources:
            source.get_bytes.assert_not_called()
        self.batch.assert_not_called()
        self.query.return_value.filter.return_value.update.assert_not_called()

    def test_knowledge_size_limit_fails_before_file_storage(self):
        self.knowledge.file_size_limit = 0
        with self.assertRaises(AppApiException):
            self.creator.save_text(self.payload)
        for source in self.sources:
            source.get_bytes.assert_not_called()
        self.batch.assert_not_called()

    def test_actual_uncompressed_bytes_are_checked_before_parsing(self):
        self.sources[0].get_bytes.return_value = b"x" * (1024 * 1024 + 1)
        with patch.object(DocumentSerializers.Split, "file_to_paragraph") as parse:
            with self.assertRaises(AppApiException):
                self.creator.save_text(self.payload)
            parse.assert_not_called()
        self.batch.assert_not_called()
        self.query.return_value.filter.return_value.update.assert_not_called()

    def test_no_importable_paragraphs_fails_without_creating_empty_documents(self):
        for documents in ([], [{"name": "blank.txt", "content": []}]):
            with (
                self.subTest(documents=documents),
                patch.object(DocumentSerializers.Split, "parse", return_value=documents),
            ):
                with self.assertRaises(AppApiException):
                    self.creator.save_text(self.payload)
        self.batch.assert_not_called()
        self.query.return_value.filter.return_value.update.assert_not_called()

    def test_parse_failure_does_not_create_documents(self):
        with patch.object(DocumentSerializers.Split, "parse", side_effect=AppApiException(500, "parse failed")):
            with self.assertRaises(AppApiException):
                self.creator.save_text(self.payload)
        self.batch.assert_not_called()
        self.query.return_value.filter.return_value.update.assert_not_called()

    def test_save_failure_does_not_promote_temporary_files(self):
        self.batch.return_value.batch_save.side_effect = AppApiException(500, "save failed")
        with patch("knowledge.serializers.document.File.save"):
            with self.assertRaises(AppApiException):
                self.creator.save_text(self.payload)
        self.query.return_value.filter.return_value.update.assert_not_called()

    def test_preview_upload_still_saves_a_source_file(self):
        splitter = DocumentSerializers.Split(data=self.scope)
        serializers.Serializer.is_valid(splitter, raise_exception=True)
        with patch("knowledge.serializers.document.File") as file_model:
            documents = splitter.file_to_paragraph(ContentFile(b"preview text", name="preview.txt"), None, False, 4096)
            file_model.return_value.save.assert_called_once_with(b"preview text")
            self.assertEqual(documents[0]["source_file_id"], file_model.call_args.kwargs["id"])
            self.assertEqual(file_model.call_args.kwargs["source_type"], FileSourceType.TEMPORARY_120_MINUTE)
            self.assertEqual(file_model.call_args.kwargs["source_id"], FileSourceType.TEMPORARY_120_MINUTE)
            self.assertEqual(file_model.call_args.kwargs["meta"], {"user_id": self.scope["user_id"]})

    def test_extracted_preview_images_remain_temporary_with_uploader_context(self):
        splitter = DocumentSerializers.Split(data=self.scope)
        serializers.Serializer.is_valid(splitter, raise_exception=True)
        image = File(file_name="inline.png", meta={"content": b"image", "debug": False})
        image.save = MagicMock()
        self.query.return_value.filter.return_value.values.return_value = []

        splitter.save_image([image])

        image.save.assert_called_once_with(b"image")
        self.assertEqual(image.source_type, FileSourceType.TEMPORARY_120_MINUTE)
        self.assertEqual(image.source_id, FileSourceType.TEMPORARY_120_MINUTE)
        self.assertEqual(image.meta["preview_knowledge_id"], self.scope["knowledge_id"])
        self.assertEqual(image.meta["user_id"], self.scope["user_id"])
        self.assertNotIn("knowledge_id", image.meta)


class TextDocumentImportViewTests(SimpleTestCase):
    def setUp(self):
        self.knowledge_id = str(uuid4())
        self.user_id = str(uuid4())
        self.url = f"/workspace/default/knowledge/{self.knowledge_id}/document/import"

    def test_json_import_passes_file_ids_and_strategy_and_uses_create_permission(self):
        strategy = {"index": {"title_as_question": True}}
        file_ids = [str(uuid4()), str(uuid4())]
        request = APIRequestFactory().post(
            self.url,
            {"file_id_list": file_ids, "doc_strategy": strategy},
            format="json",
        )
        force_authenticate(request, user=SimpleNamespace(id=self.user_id, type="TEST"))
        with (
            patch("common.auth.authentication._build") as permissions,
            patch("common.log.log.Log"),
            patch("knowledge.views.document.get_knowledge_operation_object", return_value={}),
            patch("knowledge.views.document.DocumentSerializers.Create") as creator,
        ):
            permissions.return_value.hasPermission.return_value = True
            creator.return_value.save_text.return_value = [{"id": "created"}]
            view = resolve(self.url, urlconf="knowledge.urls").func
            self.assertIs(view.view_class, DocumentView.Import)
            response = view(request, workspace_id="default", knowledge_id=self.knowledge_id)

        result = json.loads(response.content)
        self.assertEqual(result["code"], 200)
        self.assertEqual(result["data"], [{"id": "created"}])
        creator.assert_called_once_with(
            data={"workspace_id": "default", "knowledge_id": self.knowledge_id, "user_id": self.user_id}
        )
        payload = creator.return_value.save_text.call_args.args[0]
        self.assertEqual(payload["file_id_list"], file_ids)
        self.assertNotIn("file", payload)
        self.assertEqual(payload["doc_strategy"], strategy)
        scope = {"workspace_id": "default", "knowledge_id": self.knowledge_id}
        self.assertEqual(
            permissions.call_args.args[0][0](request, scope),
            PermissionConstants.KNOWLEDGE_DOCUMENT_CREATE.get_workspace_knowledge_permission()(request, scope),
        )

    def test_import_permission_denied_before_serializer(self):
        with (
            patch("common.auth.authentication._build") as permissions,
            patch("knowledge.views.document.DocumentSerializers.Create") as creator,
        ):
            permissions.return_value.hasPermission.return_value = False
            with self.assertRaises(AppUnauthorizedFailed):
                DocumentView.Import().post(SimpleNamespace(), workspace_id="default", knowledge_id=self.knowledge_id)
            creator.assert_not_called()

    def test_request_schema_exposes_file_ids_and_object_strategy(self):
        self.assertIs(DocumentImportAPI.get_request(), DocumentImportRequest)
        fields = DocumentImportAPI.get_request()().fields
        self.assertIn("file_id_list", fields)
        self.assertIn("doc_strategy", fields)
        self.assertNotIn("file", fields)
