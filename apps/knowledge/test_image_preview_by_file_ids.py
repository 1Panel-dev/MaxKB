"""Image previews reuse authorized uploaded files without saving another copy."""

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

from knowledge.api.document import ImagePreviewAPI
from knowledge.models import AssetProcessStatus, FileSourceType, Knowledge, KnowledgeType
from knowledge.serializers.image_document import ImageDocumentSerializers, ImagePreviewUploadRequest
from knowledge.services.image_documents import ImageDocumentService


class ImagePreviewByFileIdsTests(SimpleTestCase):
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
            MagicMock(
                id=uuid4(),
                file_name=name,
                file_size=len(self.content),
                meta={"user_id": self.user_id, "original_size": len(self.content)},
            )
            for name in ("first.png", "second.png")
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
        self.on_commit = self.enterContext(patch("knowledge.services.image_documents.transaction.on_commit"))

    def test_reuses_original_ids_preserves_order_and_promotes_sources_without_saving_bytes(self):
        previews = self.service.create_previews_by_file_ids(self.ids)
        self.assertEqual([preview["preview_id"] for preview in previews], self.ids)
        self.assertEqual([preview["name"] for preview in previews], ["first.png", "second.png"])
        self.assertEqual([preview["source_file_id"] for preview in previews], self.ids)
        self.assertEqual(previews[0]["content"], [{"title": "first", "content": "first"}])
        self.assertIn("doc_strategy", previews[0])
        self.assertEqual(previews[0]["process_status"], AssetProcessStatus.SKIPPED)
        for file in self.files:
            file.save.assert_not_called()
        self.on_commit.assert_not_called()
        updates = [call.kwargs for call in self.query.return_value.filter.return_value.update.call_args_list]
        self.assertEqual(updates[0]["source_type"], FileSourceType.KNOWLEDGE)
        self.assertEqual(updates[0]["source_id"], self.service.knowledge_id)
        condition = self.query.return_value.filter.call_args_list[0].args[0]
        self.assertIn(("meta__user_id", self.user_id), condition.children[1].children)
        self.assertIn(("source_id", self.service.knowledge_id), condition.children[0].children)

    def test_visual_processing_is_queued_after_commit_without_calling_model(self):
        strategy = {"visual": {"enabled": True, "strategy": "model", "model_id": str(uuid4())}}
        with patch.object(self.service, "_run_visual_processor") as process:
            previews = self.service.create_previews_by_file_ids(self.ids, strategy)
        self.assertTrue(all(preview["process_status"] == AssetProcessStatus.PENDING for preview in previews))
        process.assert_not_called()
        self.assertEqual(self.on_commit.call_count, 2)
        self.assertEqual(self.on_commit.call_args_list[0].args[0].args, (self.ids[0],))

    def test_missing_or_inaccessible_file_fails_before_reading_or_promoting_any_file(self):
        self.query.return_value.filter.return_value.select_for_update.return_value.__iter__.return_value = self.files[
            :1
        ]
        with self.assertRaises(AppApiException):
            self.service.create_previews_by_file_ids(self.ids)
        for file in self.files:
            file.get_bytes.assert_not_called()
        self.query.return_value.filter.return_value.update.assert_not_called()

    def test_invalid_image_rejects_entire_batch_without_promoting_sources(self):
        self.files[1].get_bytes.return_value = b"not an image"
        with self.assertRaises(AppApiException):
            self.service.create_previews_by_file_ids(self.ids)
        self.query.return_value.filter.return_value.update.assert_not_called()
        self.on_commit.assert_not_called()

    def test_actual_bytes_obey_size_limit(self):
        self.files[0].get_bytes.return_value = self.content + b"a" * (1024 * 1024)
        with self.assertRaises(AppApiException):
            self.service.create_previews_by_file_ids(self.ids)
        self.query.return_value.filter.return_value.update.assert_not_called()

    def test_imported_preview_cannot_be_reused(self):
        self.files[0].meta["image_preview"] = {"imported": True}
        with self.assertRaises(AppApiException):
            self.service.create_previews_by_file_ids(self.ids)
        self.query.return_value.filter.return_value.update.assert_not_called()

    def test_knowledge_count_limit_is_enforced_before_file_lookup(self):
        self.knowledge.file_count_limit = 1
        with self.assertRaises(AppApiException):
            self.service.create_previews_by_file_ids(self.ids)
        self.query.assert_not_called()

    def test_wrong_workspace_fails_before_file_lookup(self):
        self.service.get_knowledge = ImageDocumentService.get_knowledge.__get__(self.service)
        self.query.return_value.filter.return_value.first.return_value = None
        with self.assertRaises(AppApiException):
            self.service.create_previews_by_file_ids(self.ids)
        self.query.return_value.filter.assert_called_once_with(id=self.service.knowledge_id, workspace_id="default")

    def test_schema_rejects_empty_invalid_duplicate_and_excessive_ids(self):
        self.assertIs(ImagePreviewAPI.get_request(), ImagePreviewUploadRequest)
        for ids in ([], ["invalid"], [self.ids[0]] * 2, [str(uuid4()) for _ in range(51)]):
            with self.subTest(ids=ids):
                serializer = ImagePreviewUploadRequest(data={"file_id_list": ids})
                self.assertFalse(serializer.is_valid())

    def test_serializer_forwards_validated_ids_and_strategy(self):
        payload = {"file_id_list": self.ids, "doc_strategy": {"visual": {"enabled": False}}}
        serializer = ImageDocumentSerializers.Preview(
            data={
                "workspace_id": "default",
                "knowledge_id": self.service.knowledge_id,
                "user_id": self.user_id,
            }
        )
        with (
            patch.object(serializer, "_service", return_value=self.service),
            patch.object(self.service, "create_previews_by_file_ids", return_value=[]) as create,
        ):
            self.assertEqual(serializer.upload(payload), [])
        self.assertEqual([str(file_id) for file_id in create.call_args.args[0]], self.ids)
        self.assertFalse(create.call_args.args[1]["visual"]["enabled"])

    def test_workspace_route_accepts_json_file_ids_and_preserves_identity(self):
        path = f"/workspace/default/knowledge/{self.service.knowledge_id}/document/image/preview"
        payload = {"file_id_list": self.ids, "doc_strategy": {"visual": {"enabled": False}}}
        request = APIRequestFactory().post(path, payload, format="json")
        force_authenticate(request, user=SimpleNamespace(id=self.user_id, type="TEST"))
        with (
            patch("common.auth.authentication._build") as permissions,
            patch("knowledge.views.image_document.ImageDocumentSerializers.Preview") as serializer,
        ):
            permissions.return_value.hasPermission.return_value = True
            serializer.return_value.upload.return_value = []
            response = resolve(path, urlconf="knowledge.urls").func(
                request, workspace_id="default", knowledge_id=self.service.knowledge_id
            )
        self.assertEqual(json.loads(response.content)["data"], [])
        serializer.assert_called_once_with(
            data={
                "workspace_id": "default",
                "knowledge_id": self.service.knowledge_id,
                "user_id": self.user_id,
            }
        )
        serializer.return_value.upload.assert_called_once_with(payload)

    def test_preview_endpoints_return_document_paragraphs_and_source_identity(self):
        path = f"/workspace/default/knowledge/{self.service.knowledge_id}/document/image/preview"
        requests = APIRequestFactory()
        cases = [
            (requests.post(path, {"file_id_list": self.ids}, format="json"), path, "first", "first"),
            (requests.get(f"{path}/{self.ids[0]}"), f"{path}/{self.ids[0]}", "first", "first"),
            (
                requests.put(
                    f"{path}/{self.ids[0]}",
                    {"name": "renamed.png", "caption": "chart", "ocr_text": "100", "description": "trend"},
                    format="json",
                ),
                f"{path}/{self.ids[0]}",
                "renamed",
                "chart\n100\ntrend",
            ),
        ]
        with (
            patch("common.auth.authentication._build") as permissions,
            patch.object(ImageDocumentSerializers.Preview, "_service", return_value=self.service),
            patch.object(self.service, "_get_preview_file", return_value=self.files[0]),
        ):
            permissions.return_value.hasPermission.return_value = True
            for request, url, title, content in cases:
                with self.subTest(method=request.method):
                    force_authenticate(request, user=SimpleNamespace(id=self.user_id, type="TEST"))
                    route = resolve(url, urlconf="knowledge.urls")
                    response = route.func(request, **route.kwargs)
                    self.assertEqual(response.status_code, 200)
                    data = json.loads(response.content)["data"]
                    preview = data[0] if request.method == "POST" else data
                    self.assertEqual(preview["name"], f"{title}.png")
                    self.assertEqual(preview["source_file_id"], self.ids[0])
                    self.assertEqual(preview["preview_id"], self.ids[0])
                    self.assertEqual(preview["content"], [{"title": title, "content": content}])
                    self.assertEqual(preview["char_length"], len(content))
                    self.assertFalse(preview["doc_strategy"]["visual"]["enabled"])
