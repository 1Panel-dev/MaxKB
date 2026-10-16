"""Uploaded-file previews preserve split behavior, source identity, and access checks."""

import json
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

from common.exception.app_exception import AppApiException, AppUnauthorizedFailed
from django.test import SimpleTestCase
from django.urls import resolve
from knowledge.api.document import DocumentSplitByFileAPI
from knowledge.models import FileSourceType
from knowledge.serializers.document import DocumentSerializers, DocumentSplitByFileRequest
from knowledge.views.document import DocumentView
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory, force_authenticate


class SplitByFileIdsTests(SimpleTestCase):
    def setUp(self):
        self.scope = {"workspace_id": "default", "knowledge_id": str(uuid4()), "user_id": str(uuid4())}
        self.splitter = DocumentSerializers.Split(data=self.scope)
        self.sources = []
        for name, content in (("first.txt", b"a" * 80), ("second.txt", b"answer")):
            source = MagicMock(id=uuid4(), file_name=name, file_size=len(content), size=None, meta={})
            source.get_bytes.return_value = content
            self.sources.append(source)
        self.payload = {"file_id_list": [str(source.id) for source in self.sources], "limit": 50}
        stack = ExitStack()
        self.addCleanup(stack.close)
        self.query = stack.enter_context(patch("knowledge.serializers.document.QuerySet"))
        self.knowledge = SimpleNamespace(file_size_limit=1)
        self.query.return_value.filter.return_value.first.return_value = self.knowledge
        self.query.return_value.filter.return_value.filter.return_value.first.return_value = self.knowledge
        self.query.return_value.filter.return_value.__iter__.return_value = self.sources[::-1]
        self.batch = stack.enter_context(patch("knowledge.serializers.document.DocumentSerializers.Batch"))

    def test_preview_preserves_file_order_ids_and_legacy_split_options(self):
        with patch("knowledge.serializers.document.File.save") as save:
            documents = self.splitter.parse_by_file_ids(self.payload)
            save.assert_not_called()
        self.assertEqual([d["name"] for d in documents], ["first.txt", "second.txt"])
        self.assertEqual([d["source_file_id"] for d in documents], [s.id for s in self.sources])
        self.assertEqual([len(p["content"]) for p in documents[0]["content"]], [50, 30])
        self.batch.assert_not_called()
        self.query.return_value.filter.return_value.update.assert_called_once_with(
            source_type=FileSourceType.KNOWLEDGE, source_id=self.scope["knowledge_id"]
        )
        condition = next(call.args[0] for call in self.query.return_value.filter.call_args_list if call.args)
        self.assertIn(self.scope["user_id"], str(condition))
        self.assertIn(self.scope["knowledge_id"], str(condition))

    def test_nested_strategy_overrides_legacy_options(self):
        self.payload["limit"] = 100
        self.payload["doc_strategy"] = {"split": {"limit": 60}, "index": {"title_as_question": True}}
        documents = self.splitter.parse_by_file_ids(self.payload)
        self.assertEqual([len(p["content"]) for p in documents[0]["content"]], [60, 20])
        self.assertTrue(documents[0]["doc_strategy"]["index"]["title_as_question"])

    def test_invalid_ids_fail_before_storage_access(self):
        for ids in ([], ["invalid"], [str(self.sources[0].id)] * 2):
            with self.subTest(ids=ids), self.assertRaises(ValidationError):
                self.splitter.parse_by_file_ids({"file_id_list": ids})
        self.query.assert_not_called()

    def test_missing_or_inaccessible_files_fail_before_reading(self):
        self.query.return_value.filter.return_value.__iter__.return_value = self.sources[:1]
        with self.assertRaises(AppApiException):
            self.splitter.parse_by_file_ids(self.payload)
        for source in self.sources:
            source.get_bytes.assert_not_called()
        self.query.return_value.filter.return_value.update.assert_not_called()

    def test_actual_bytes_obey_size_limit(self):
        self.sources[0].get_bytes.return_value = b"a" * (1024 * 1024 + 1)
        with patch.object(DocumentSerializers.Split, "file_to_paragraph") as parse:
            with self.assertRaises(AppApiException):
                self.splitter.parse_by_file_ids(self.payload)
            parse.assert_not_called()
        self.query.return_value.filter.return_value.update.assert_not_called()

    def test_parse_failure_does_not_promote_sources(self):
        with patch.object(DocumentSerializers.Split, "parse", side_effect=AppApiException(500, "parse failed")):
            with self.assertRaises(AppApiException):
                self.splitter.parse_by_file_ids(self.payload)
        self.query.return_value.filter.return_value.update.assert_not_called()

    def test_wrong_workspace_fails_before_reading(self):
        self.query.return_value.filter.return_value.first.return_value = None
        with self.assertRaises(AppApiException):
            self.splitter.parse_by_file_ids(self.payload)
        for source in self.sources:
            source.get_bytes.assert_not_called()


class SplitByFileIdsViewTests(SimpleTestCase):
    def test_json_route_passes_identity_and_split_payload(self):
        knowledge_id, user_id = str(uuid4()), str(uuid4())
        url = f"/workspace/default/knowledge/{knowledge_id}/document/split_by_file_ids"
        payload = {"file_id_list": [str(uuid4())], "limit": 100, "with_filter": True, "patterns": ["#"]}
        request = APIRequestFactory().post(url, payload, format="json")
        force_authenticate(request, user=SimpleNamespace(id=user_id, type="TEST"))
        with (
            patch("common.auth.authentication._build") as permissions,
            patch("knowledge.views.document.DocumentSerializers.Split") as splitter,
        ):
            permissions.return_value.hasPermission.return_value = True
            splitter.return_value.parse_by_file_ids.return_value = [{"name": "preview.txt", "content": []}]
            view = resolve(url, urlconf="knowledge.urls").func
            self.assertIs(view.view_class, DocumentView.SplitByFile)
            response = view(request, workspace_id="default", knowledge_id=knowledge_id)
        self.assertEqual(json.loads(response.content)["data"], [{"name": "preview.txt", "content": []}])
        splitter.assert_called_once_with(
            data={"workspace_id": "default", "knowledge_id": knowledge_id, "user_id": user_id}
        )
        splitter.return_value.parse_by_file_ids.assert_called_once_with(payload)

    def test_permission_denied_before_parsing(self):
        with (
            patch("common.auth.authentication._build") as permissions,
            patch("knowledge.views.document.DocumentSerializers.Split") as splitter,
        ):
            permissions.return_value.hasPermission.return_value = False
            with self.assertRaises(AppUnauthorizedFailed):
                DocumentView.SplitByFile().post(SimpleNamespace(), workspace_id="default", knowledge_id=str(uuid4()))
            splitter.assert_not_called()

    def test_schema_exposes_ids_and_all_split_options(self):
        self.assertIs(DocumentSplitByFileAPI.get_request(), DocumentSplitByFileRequest)
        self.assertEqual(
            set(DocumentSplitByFileRequest().fields),
            {"file_id_list", "limit", "patterns", "with_filter", "doc_strategy"},
        )
