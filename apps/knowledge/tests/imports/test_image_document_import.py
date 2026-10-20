"""Image batch import accepts uploaded files and preserves existing previews."""

import json
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

from common.exception.app_exception import AppApiException
from django.test import SimpleTestCase
from django.urls import resolve
from PIL import Image
from rest_framework.test import APIRequestFactory, force_authenticate

from knowledge.api.document import ImageBatchCreateAPI
from knowledge.models import AssetProcessStatus, DocumentResourceType, FileSourceType, Knowledge, KnowledgeType
from knowledge.serializers.image_document import ImagePreviewBatchCreateRequest
from knowledge.services.document_strategy import normalize_document_strategy
from knowledge.services.image_documents import ImageDocumentService


class ImageDocumentImportTests(SimpleTestCase):
    def setUp(self):
        self.user_id = str(uuid4())
        self.service = ImageDocumentService("default", str(uuid4()), self.user_id)
        self.knowledge = Knowledge(
            id=self.service.knowledge_id,
            workspace_id="default",
            type=KnowledgeType.BASE,
            file_size_limit=1,
            file_count_limit=2,
        )
        self.service.get_knowledge = MagicMock(return_value=self.knowledge)
        image = BytesIO()
        Image.new("RGB", (1, 1)).save(image, format="PNG")
        self.content = image.getvalue()
        self.files = [
            MagicMock(id=uuid4(), file_name=f"{name}.png", meta={"user_id": self.user_id})
            for name in ("first", "second")
        ]
        for file in self.files:
            file.get_bytes.return_value = self.content
        self.ids = [str(file.id) for file in self.files]
        self.enterContext(patch("django.db.transaction.Atomic.__enter__"))
        self.enterContext(patch("django.db.transaction.Atomic.__exit__", return_value=False))
        self.query = self.enterContext(patch("knowledge.services.image_documents.QuerySet"))
        self.query.return_value.filter.return_value.select_for_update.return_value.__iter__.return_value = self.files[
            ::-1
        ]
        self.documents = self.enterContext(patch("knowledge.services.image_documents.Document"))
        self.documents.side_effect = lambda **values: MagicMock(**values)
        self.paragraphs = self.enterContext(patch("knowledge.services.image_documents.Paragraph"))
        self.assets = self.enterContext(patch("knowledge.services.image_documents.ParagraphAsset.objects.create"))
        self.enterContext(patch("knowledge.services.image_documents.IncrementalDocumentSync"))
        self.on_commit = self.enterContext(patch("knowledge.services.image_documents.transaction.on_commit"))

    def test_direct_import_reuses_uploaded_images_and_preserves_file_order(self):
        result = self.service.import_previews(self.ids)

        self.assertEqual(len(result), 2)
        values = [call.kwargs for call in self.documents.call_args_list]
        self.assertEqual([document["name"] for document in values], ["first.png", "second.png"])
        self.assertEqual([document["meta"]["source_file_id"] for document in values], self.ids)
        self.assertTrue(all(document["resource_type"] == DocumentResourceType.IMAGE for document in values))
        self.assertEqual([call.kwargs["content"] for call in self.paragraphs.call_args_list], ["first", "second"])
        self.assertTrue(
            all(call.kwargs["process_status"] == AssetProcessStatus.SKIPPED for call in self.assets.call_args_list)
        )
        moves = [
            call.kwargs
            for call in self.query.return_value.filter.return_value.update.call_args_list
            if "source_type" in call.kwargs
        ]
        self.assertEqual([move["source_id"] for move in moves], result)
        self.assertTrue(all(move["source_type"] == FileSourceType.DOCUMENT for move in moves))
        for file in self.files:
            file.save.assert_not_called()
        condition = self.query.return_value.filter.call_args_list[0].args[0]
        self.assertIn(("meta__user_id", self.user_id), condition.children[1].children)
        self.assertIn(("source_id", self.service.knowledge_id), condition.children[0].children)
        self.on_commit.assert_not_called()

    def test_direct_import_preserves_strategy_and_defers_vision_to_embedding_worker(self):
        strategy = normalize_document_strategy(
            {"visual": {"enabled": True, "strategy": "model", "model_id": str(uuid4())}}
        )
        with patch.object(self.service, "_run_visual_processor") as process:
            self.service.import_previews(self.ids, strategy)
        process.assert_not_called()
        self.on_commit.assert_not_called()
        for call in self.documents.call_args_list:
            self.assertEqual(call.kwargs["doc_strategy"], strategy)
        for call in self.assets.call_args_list:
            self.assertEqual(call.kwargs["process_status"], AssetProcessStatus.PENDING)

    def test_direct_import_normalizes_mislabeled_image_without_rewriting_bytes(self):
        self.files[0].file_name = "神奇图片.jpg"

        self.service.import_previews(self.ids)

        document = self.documents.call_args_list[0].kwargs
        self.assertEqual(document["name"], "神奇图片.png")
        self.assertEqual(document["meta"]["source_file_id"], self.ids[0])
        moves = [
            call.kwargs
            for call in self.query.return_value.filter.return_value.update.call_args_list
            if "source_type" in call.kwargs
        ]
        self.assertEqual(moves[0]["file_name"], "神奇图片.png")
        self.files[0].save.assert_not_called()

    def test_mixed_import_preserves_existing_preview_text_edits_and_strategy(self):
        strategy = normalize_document_strategy({"index": {"title_as_question": True}})
        self.files[0].meta["image_preview"] = {
            "caption": "manual caption",
            "description": "edited description",
            "edited_fields": ["description"],
            "doc_strategy": strategy,
            "process_status": AssetProcessStatus.SUCCESS,
        }
        self.service.import_previews(self.ids, {"index": {"title_as_question": False}})

        self.files[0].get_bytes.assert_not_called()
        self.assertEqual(self.documents.call_args_list[0].kwargs["doc_strategy"], strategy)
        self.assertEqual(self.paragraphs.call_args_list[0].kwargs["content"], "manual caption\nedited description")
        self.assertEqual(self.assets.call_args_list[0].kwargs["meta"]["visual_edited_fields"], ["description"])
        self.assertFalse(self.documents.call_args_list[1].kwargs["doc_strategy"]["index"]["title_as_question"])

    def test_invalid_image_rejects_entire_batch_before_creating_documents(self):
        self.files[1].get_bytes.return_value = b"not an image"
        with self.assertRaises(AppApiException):
            self.service.import_previews(self.ids)
        self.documents.assert_not_called()
        self.query.return_value.filter.return_value.update.assert_not_called()

    def test_missing_or_inaccessible_file_fails_before_reading_any_file(self):
        self.query.return_value.filter.return_value.select_for_update.return_value.__iter__.return_value = self.files[
            :1
        ]
        with self.assertRaises(AppApiException):
            self.service.import_previews(self.ids)
        for file in self.files:
            file.get_bytes.assert_not_called()
        self.documents.assert_not_called()

    def test_imported_preview_rejects_entire_batch_before_creating_documents(self):
        self.files[1].meta["image_preview"] = {"imported": True}
        with self.assertRaises(AppApiException):
            self.service.import_previews(self.ids)
        self.documents.assert_not_called()
        self.query.return_value.filter.return_value.update.assert_not_called()

    def test_count_and_actual_size_limits_apply_to_direct_import(self):
        self.knowledge.file_count_limit = 1
        with self.assertRaises(AppApiException):
            self.service.import_previews(self.ids)
        self.query.assert_not_called()
        self.knowledge.file_count_limit = 2
        self.files[0].get_bytes.return_value = self.content + b"a" * (1024 * 1024)
        with self.assertRaises(AppApiException):
            self.service.import_previews(self.ids)
        self.documents.assert_not_called()

    def test_batch_create_route_imports_uploaded_files_with_strategy_and_returns_document_list(self):
        path = f"/workspace/default/knowledge/{self.service.knowledge_id}/document/image/batch_create"
        strategy = {"visual": {"enabled": False}, "index": {"title_as_question": True}}
        request = APIRequestFactory().put(path, {"file_id_list": self.ids, "doc_strategy": strategy}, format="json")
        force_authenticate(request, user=SimpleNamespace(id=self.user_id, type="TEST"))
        response_document = {"id": str(uuid4()), "resource_type": DocumentResourceType.IMAGE}
        with (
            patch("common.auth.authentication._build") as permissions,
            patch("knowledge.serializers.image_document.ImageDocumentService", return_value=self.service),
            patch("knowledge.serializers.image_document.DocumentSerializers.Operate") as operate,
        ):
            permissions.return_value.hasPermission.return_value = True
            operate.return_value.one.return_value = response_document
            route = resolve(path, urlconf="knowledge.urls")
            response = route.func(request, **route.kwargs)
        self.assertEqual(json.loads(response.content)["data"], [response_document, response_document])
        self.assertEqual(operate.return_value.refresh.call_count, 2)
        for call in self.documents.call_args_list:
            self.assertTrue(call.kwargs["doc_strategy"]["index"]["title_as_question"])

    def test_schema_requires_file_id_list_and_validates_optional_strategy(self):
        self.assertIs(ImageBatchCreateAPI.get_request(), ImagePreviewBatchCreateRequest)
        self.assertEqual(set(ImagePreviewBatchCreateRequest().fields), {"file_id_list", "doc_strategy"})
        serializer = ImagePreviewBatchCreateRequest(data={"file_id_list": self.ids})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer = ImagePreviewBatchCreateRequest(
            data={"file_id_list": self.ids, "doc_strategy": {"visual": {"enabled": True}}}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("doc_strategy", serializer.errors)

    def test_schema_rejects_missing_empty_invalid_or_excessive_file_id_list(self):
        for payload in (
            {},
            {"preview_ids": self.ids},
            {"file_ids": self.ids},
            {"file_id_list": []},
            {"file_id_list": ["invalid"]},
            {"file_id_list": [str(uuid4()) for _ in range(51)]},
        ):
            with self.subTest(payload=payload):
                serializer = ImagePreviewBatchCreateRequest(data=payload)
                self.assertFalse(serializer.is_valid())
                self.assertIn("file_id_list", serializer.errors)
