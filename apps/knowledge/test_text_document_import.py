"""Direct text import applies the strategy and creates documents in one request."""

import json
from contextlib import ExitStack, nullcontext
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from common.auth.constants.permission_constants import PermissionConstants
from common.exception.app_exception import AppApiException, AppUnauthorizedFailed
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from django.urls import resolve
from knowledge.serializers.document import DocumentSerializers
from knowledge.services.document_strategy import normalize_document_strategy
from knowledge.views.document import DocumentView
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory, force_authenticate


class TextDocumentImportTests(SimpleTestCase):
    def setUp(self):
        self.scope = {"workspace_id": "default", "knowledge_id": str(uuid4()), "user_id": str(uuid4())}
        self.creator = DocumentSerializers.Create(data=self.scope)
        self.source_id = uuid4()
        self.strategy = {
            "split": {"mode": "advanced", "max_length": 50, "child_length": 50, "auto_clean": True},
            "visual": {"enabled": True, "strategy": "model", "model_id": str(uuid4())},
            "index": {"title_as_question": True},
        }
        self.payload = {
            "file": [SimpleUploadedFile("first.txt", b"first"), SimpleUploadedFile("second.txt", b"second")],
            "doc_strategy": self.strategy,
        }
        stack = ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(patch("knowledge.serializers.document.transaction.atomic", return_value=nullcontext()))
        self.batch = stack.enter_context(patch("knowledge.serializers.document.DocumentSerializers.Batch"))
        self.batch.return_value.batch_save.return_value = [{"id": "created"}]

    def test_import_parses_all_files_with_strategy_and_preserves_sources(self):
        with (
            patch.object(DocumentSerializers.Split, "is_valid"),
            patch.object(DocumentSerializers.Split, "file_to_paragraph") as parse,
        ):
            parse.side_effect = [
                [
                    {
                        "name": "first.txt",
                        "content": [{"title": "First", "content": "a" * 80}],
                        "source_file_id": self.source_id,
                    }
                ],
                [
                    {
                        "name": "second.txt",
                        "content": [{"title": "Second", "content": "answer"}],
                        "source_file_id": uuid4(),
                    }
                ],
            ]
            self.assertEqual(self.creator.save_text(self.payload), [{"id": "created"}])

        self.assertEqual([call.args[0].name for call in parse.call_args_list], ["first.txt", "second.txt"])
        self.assertTrue(all(call.args[1:] == (None, True, 50) for call in parse.call_args_list))
        self.batch.assert_called_once_with(data=self.scope)
        documents = self.batch.return_value.batch_save.call_args.args[0]
        self.assertEqual([document["name"] for document in documents], ["first.txt", "second.txt"])
        self.assertEqual(documents[0]["source_file_id"], self.source_id)
        self.assertEqual([len(p["content"]) for p in documents[0]["paragraphs"]], [50, 30])
        for document in documents:
            self.assertNotIn("content", document)
            self.assertEqual(document["doc_strategy"], normalize_document_strategy(self.strategy))

    def test_invalid_input_fails_before_parsing_or_saving(self):
        payloads = [
            {},
            {"file": []},
            {"file": [SimpleUploadedFile("empty.txt", b"")]},
            {**self.payload, "doc_strategy": {"split": {"max_length": 10}}},
            {**self.payload, "doc_strategy": {"split": {"patterns": ["["]}}},
            {**self.payload, "doc_strategy": {"visual": {"enabled": True}}},
        ]
        with patch.object(DocumentSerializers.Split, "parse") as parse:
            for payload in payloads:
                with self.subTest(payload=payload), self.assertRaises(ValidationError):
                    self.creator.save_text(payload)
            parse.assert_not_called()
        self.batch.assert_not_called()

    def test_missing_knowledge_or_wrong_workspace_fails_before_file_storage(self):
        with (
            patch("knowledge.serializers.document.QuerySet") as query,
            patch.object(DocumentSerializers.Split, "file_to_paragraph") as parse,
        ):
            query.return_value.filter.return_value.filter.return_value.first.return_value = None
            with self.assertRaises(AppApiException):
                self.creator.save_text(self.payload)
            query.return_value.filter.return_value.filter.assert_called_once_with(workspace_id="default")
            parse.assert_not_called()
        self.batch.assert_not_called()

    def test_knowledge_size_limit_fails_before_file_storage(self):
        with (
            patch("knowledge.serializers.document.QuerySet") as query,
            patch.object(DocumentSerializers.Split, "file_to_paragraph") as parse,
        ):
            query.return_value.filter.return_value.filter.return_value.first.return_value = SimpleNamespace(
                file_size_limit=0
            )
            with self.assertRaises(AppApiException):
                self.creator.save_text(self.payload)
            parse.assert_not_called()
        self.batch.assert_not_called()

    def test_no_importable_paragraphs_fails_without_creating_empty_documents(self):
        for documents in ([], [{"name": "blank.txt", "content": []}]):
            with (
                self.subTest(documents=documents),
                patch.object(DocumentSerializers.Split, "parse", return_value=documents),
            ):
                with self.assertRaises(AppApiException):
                    self.creator.save_text(self.payload)
        self.batch.assert_not_called()

    def test_parse_failure_does_not_create_documents(self):
        with patch.object(DocumentSerializers.Split, "parse", side_effect=AppApiException(500, "parse failed")):
            with self.assertRaises(AppApiException):
                self.creator.save_text(self.payload)
        self.batch.assert_not_called()


class TextDocumentImportViewTests(SimpleTestCase):
    def setUp(self):
        self.knowledge_id = str(uuid4())
        self.user_id = str(uuid4())
        self.url = f"/workspace/default/knowledge/{self.knowledge_id}/document/import"

    def test_multipart_import_returns_created_documents_and_uses_create_permission(self):
        strategy = {"index": {"title_as_question": True}}
        request = APIRequestFactory().post(
            self.url,
            {
                "file": [SimpleUploadedFile("first.txt", b"first"), SimpleUploadedFile("second.txt", b"second")],
                "doc_strategy": json.dumps(strategy),
            },
            format="multipart",
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
        self.assertEqual([file.name for file in payload["file"]], ["first.txt", "second.txt"])
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

    def test_malformed_strategy_fails_before_serializer(self):
        request = APIRequestFactory().post(
            self.url, {"file": SimpleUploadedFile("text.txt", b"text"), "doc_strategy": "{"}, format="multipart"
        )
        force_authenticate(request, user=SimpleNamespace(id=self.user_id, type="TEST"))
        with (
            patch("common.auth.authentication._build") as permissions,
            patch("common.log.log.Log"),
            patch("knowledge.views.document.get_knowledge_operation_object", return_value={}),
            patch("knowledge.views.document.DocumentSerializers.Create") as creator,
        ):
            permissions.return_value.hasPermission.return_value = True
            response = DocumentView.Import.as_view()(request, workspace_id="default", knowledge_id=self.knowledge_id)
            self.assertEqual(json.loads(response.content)["code"], 500)
            creator.return_value.save_text.assert_not_called()
