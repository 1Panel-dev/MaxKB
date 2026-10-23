"""Generating an image preview returns completed model or tool recognition."""

import base64
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

from knowledge.models import AssetProcessStatus, File, FileSourceType, Knowledge, KnowledgeType
from knowledge.services.image_documents import ImageDocumentService


class ImageVisualPreviewTests(SimpleTestCase):
    def setUp(self):
        self.user_id = str(uuid4())
        self.service = ImageDocumentService("default", str(uuid4()), self.user_id)
        self.service.get_knowledge = MagicMock(
            return_value=Knowledge(
                id=self.service.knowledge_id,
                workspace_id="default",
                type=KnowledgeType.BASE,
                file_size_limit=1,
                file_count_limit=50,
            )
        )
        image = BytesIO()
        Image.new("RGB", (1, 1)).save(image, format="PNG")
        self.image_bytes = image.getvalue()
        self.files = [
            File(
                id=uuid4(),
                file_name=f"{name}.png",
                file_size=len(self.image_bytes),
                source_type=FileSourceType.TEMPORARY_120_MINUTE,
                source_id=FileSourceType.TEMPORARY_120_MINUTE,
                meta={"user_id": self.user_id},
            )
            for name in ("first", "second")
        ]
        for file in self.files:
            file.get_bytes = MagicMock(return_value=self.image_bytes)
        self.ids = [str(file.id) for file in self.files]
        self.strategy = {"visual": {"enabled": True, "strategy": "model", "model_id": str(uuid4())}}
        self.output = {"caption": "订单", "ocr_text": "Total: 128.50", "description": "订单截图"}
        self.transaction_depth = 0
        self.enterContext(patch("django.db.transaction.Atomic.__enter__", side_effect=self.enter_transaction))
        self.enterContext(patch("django.db.transaction.Atomic.__exit__", side_effect=self.exit_transaction))
        query = self.enterContext(patch("knowledge.services.image_documents.QuerySet"))
        query.return_value.filter.side_effect = self.filter_files
        self.on_commit = self.enterContext(patch("knowledge.services.image_documents.transaction.on_commit"))
        self.model_loader = self.enterContext(patch("knowledge.services.paragraph_assets._get_llm_model"))
        self.model = self.model_loader.return_value
        self.model.invoke.side_effect = self.recognize

    def enter_transaction(self, *args):
        self.transaction_depth += 1

    def exit_transaction(self, *args):
        self.transaction_depth -= 1
        return False

    def filter_files(self, *conditions, **filters):
        files = [
            file
            for file in self.files[::-1]
            if all(
                str(file.id) in {str(value) for value in expected}
                if field == "id__in"
                else str(getattr(file, field)) == str(expected)
                for field, expected in filters.items()
            )
        ]
        query = MagicMock()
        query.__iter__.return_value = files
        query.first.return_value = files[0] if files else None
        query.select_for_update.return_value = query

        def update(**values):
            for file in files:
                for field, value in values.items():
                    setattr(file, field, value)
            return len(files)

        query.update.side_effect = update
        return query

    def recognize(self, messages):
        self.assertEqual(self.transaction_depth, 0, "Vision calls must run after releasing database locks")
        data_url = messages[0].content[1]["image_url"]["url"]
        self.assertTrue(data_url.startswith("data:image/png;base64,"))
        self.assertEqual(base64.b64decode(data_url.split(",", 1)[1]), self.image_bytes)
        return SimpleNamespace(content=f"```json\n{json.dumps(self.output)}\n```")

    def test_generate_waits_for_model_results_without_enqueuing_a_background_preview(self):
        previews = self.service.generate_previews_by_file_ids(self.ids, self.strategy)

        self.assertEqual([preview["file_id"] for preview in previews], self.ids)
        self.assertEqual([preview["name"] for preview in previews], ["first.png", "second.png"])
        for preview in previews:
            self.assertEqual(preview["process_status"], AssetProcessStatus.SUCCESS)
            self.assertEqual(preview["content"][0]["content"], "订单\nTotal: 128.50\n订单截图")
            self.assertEqual(preview["description"], self.output["description"])
        self.model_loader.assert_called_with(self.strategy["visual"]["model_id"], "default")
        self.assertEqual(self.model.invoke.call_count, 2)
        self.on_commit.assert_not_called()

    def test_generate_runs_the_selected_tool_and_returns_its_recognition(self):
        tool_id = str(uuid4())
        tool = SimpleNamespace(
            code="def enhance_image(image_base64): return {}",
            input_field_list=[{"name": "image_base64"}],
            init_field_list=[],
            init_params={},
        )
        with (
            patch("knowledge.services.paragraph_assets.filter_authorized_ids", return_value=[tool_id]) as authorize,
            patch("knowledge.services.paragraph_assets.Tool.objects.filter") as tools,
            patch("knowledge.services.paragraph_assets.ToolExecutor") as executor,
        ):
            tools.return_value.first.return_value = tool
            executor.return_value.exec_code.return_value = self.output
            preview = self.service.generate_previews_by_file_ids(
                self.ids[:1], {"visual": {"enabled": True, "strategy": "tool", "tool_id": tool_id}}
            )[0]
        self.assertEqual(preview["process_status"], AssetProcessStatus.SUCCESS)
        self.assertEqual(preview["ocr_text"], self.output["ocr_text"])
        authorize.assert_called_once_with("tool", [tool_id], "default")
        executor.return_value.exec_code.assert_called_once_with(
            tool.code, {"image_base64": base64.b64encode(self.image_bytes).decode("ascii")}
        )
        self.model_loader.assert_not_called()
        self.on_commit.assert_not_called()

    def test_one_model_failure_does_not_discard_other_image_results(self):
        self.model.invoke.side_effect = [RuntimeError("model timeout"), SimpleNamespace(content="recognized image")]
        previews = self.service.generate_previews_by_file_ids(self.ids, self.strategy)

        self.assertEqual(previews[0]["process_status"], AssetProcessStatus.FAILURE)
        self.assertEqual(previews[0]["process_error"], "model timeout")
        self.assertEqual(previews[0]["content"], [{"title": "first", "content": "first"}])
        self.assertEqual(previews[1]["process_status"], AssetProcessStatus.SUCCESS)
        self.assertEqual(previews[1]["description"], "recognized image")

    def test_disabled_enhancement_returns_skipped_without_calling_a_model(self):
        previews = self.service.generate_previews_by_file_ids(self.ids)

        self.assertTrue(all(preview["process_status"] == AssetProcessStatus.SKIPPED for preview in previews))
        self.model_loader.assert_not_called()
        self.on_commit.assert_not_called()

    def test_invalid_image_rejects_the_batch_before_any_visual_processing(self):
        self.files[1].get_bytes.return_value = b"invalid image"
        with self.assertRaises(AppApiException):
            self.service.generate_previews_by_file_ids(self.ids, self.strategy)
        self.assertTrue(all(file.source_type == FileSourceType.TEMPORARY_120_MINUTE for file in self.files))
        self.model_loader.assert_not_called()

    def test_preview_api_returns_completed_paragraphs_in_the_initial_response(self):
        path = f"/workspace/default/knowledge/{self.service.knowledge_id}/document/image/preview"
        request = APIRequestFactory().post(
            path, {"file_id_list": self.ids, "doc_strategy": self.strategy}, format="json"
        )
        force_authenticate(request, user=SimpleNamespace(id=self.user_id, type="TEST"))
        with (
            patch("common.auth.authentication._build") as permissions,
            patch("knowledge.serializers.image_document.ImageDocumentService", return_value=self.service),
        ):
            permissions.return_value.hasPermission.return_value = True
            route = resolve(path, urlconf="knowledge.urls")
            response = route.func(request, **route.kwargs)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 200)
        self.assertTrue(all(preview["resource_type"] == "image" for preview in payload["data"]))
        self.assertEqual(payload["data"][0]["process_status"], AssetProcessStatus.SUCCESS)
        self.assertEqual(payload["data"][0]["content"][0]["content"], "订单\nTotal: 128.50\n订单截图")

    def test_import_reuses_completed_preview_results_without_recognizing_them_again(self):
        self.service.generate_previews_by_file_ids(self.ids, self.strategy)
        with (
            patch("knowledge.services.image_documents.Document"),
            patch("knowledge.services.image_documents.Paragraph"),
            patch("knowledge.services.image_documents.ParagraphAsset.objects.create") as assets,
            patch("knowledge.services.image_documents.IncrementalDocumentSync"),
        ):
            self.service.import_previews(self.ids)
        self.assertEqual(self.model.invoke.call_count, 2)
        self.assertTrue(
            all(call.kwargs["process_status"] == AssetProcessStatus.SUCCESS for call in assets.call_args_list)
        )
        self.assertEqual(assets.call_args_list[0].kwargs["description"], self.output["description"])
