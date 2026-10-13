"""Standalone image uploads recognize previews asynchronously without losing user edits."""

from io import BytesIO
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from PIL import Image

from common.event.listener_manage import ListenerManagement
from knowledge.models import (
    AssetProcessStatus,
    DocumentResourceType,
    Knowledge,
    KnowledgeType,
    LocalState,
    Paragraph,
)
from knowledge.services.document_strategy import normalize_document_strategy
from knowledge.services.image_documents import ImageDocumentService
from knowledge.services.paragraph_assets import _write_asset_description, process_visual_assets


class AsyncImagePreviewTests(SimpleTestCase):
    def setUp(self):
        self.service = ImageDocumentService("default", str(uuid4()))
        self.knowledge = Knowledge(
            id=self.service.knowledge_id,
            workspace_id="default",
            type=KnowledgeType.BASE,
            file_size_limit=100,
            file_count_limit=50,
        )
        self.service.get_knowledge = MagicMock(return_value=self.knowledge)
        self.strategy = normalize_document_strategy(
            {"visual": {"enabled": True, "strategy": "model", "model_id": str(uuid4())}}
        )
        self.file = MagicMock(
            id=uuid4(),
            file_name="chart.png",
            file_size=5,
            sha256_hash="image-hash",
            meta={
                "upload_size": 5,
                "image_preview": {
                    "caption": "",
                    "ocr_text": "",
                    "description": "",
                    "process_status": AssetProcessStatus.PENDING,
                    "process_error": "",
                    "doc_strategy": self.strategy,
                    "imported": False,
                    "document_id": None,
                },
            },
        )
        self.enterContext(patch("django.db.transaction.Atomic.__enter__"))
        self.enterContext(patch("django.db.transaction.Atomic.__exit__", return_value=False))
        self.query = self.enterContext(patch("knowledge.services.image_documents.QuerySet"))
        self.files = self.query.return_value.filter.return_value
        self.files.first.return_value = self.file
        self.files.select_for_update.return_value.first.return_value = self.file
        self.files.select_for_update.return_value.__iter__.return_value = [self.file]
        self.files.update.side_effect = self.persist
        self.run_visual = self.enterContext(patch.object(self.service, "_run_visual_processor"))
        self.processed = {
            "caption": "chart",
            "ocr_text": "revenue 100",
            "description": "upward trend",
            "process_status": AssetProcessStatus.SUCCESS,
            "process_error": "",
            "meta": {},
        }
        self.run_visual.return_value = self.processed

    def persist(self, **values):
        for field, value in values.items():
            setattr(self.file, field, value)
        return 1

    def upload(self):
        buffer = BytesIO()
        Image.new("RGB", (1, 1)).save(buffer, format="PNG")
        return SimpleUploadedFile("chart.png", buffer.getvalue(), content_type="image/png")

    def test_upload_returns_pending_without_vision_call_and_queues_only_after_commit(self):
        with (
            patch("knowledge.services.image_documents.File", return_value=self.file),
            patch("knowledge.services.image_documents.transaction.on_commit") as on_commit,
            patch("knowledge.tasks.process_image_preview.delay") as delay,
        ):
            previews = self.service.create_previews([self.upload()], self.strategy)

            self.assertEqual(previews[0]["process_status"], AssetProcessStatus.PENDING)
            self.assertEqual(previews[0]["content"], "chart")
            self.file.save.assert_called_once()
            self.run_visual.assert_not_called()
            delay.assert_not_called()
            on_commit.assert_called_once()
            on_commit.call_args.args[0]()
            delay.assert_called_once_with("default", self.service.knowledge_id, str(self.file.id))

    def test_disabled_enhancement_never_queues_a_task(self):
        self.run_visual.return_value = {**self.processed, "process_status": AssetProcessStatus.SKIPPED}
        with (
            patch("knowledge.services.image_documents.File", return_value=self.file),
            patch("knowledge.services.image_documents.transaction.on_commit") as on_commit,
        ):
            previews = self.service.create_previews([self.upload()])

        self.assertEqual(previews[0]["process_status"], AssetProcessStatus.SKIPPED)
        on_commit.assert_not_called()

    def test_worker_saves_result_and_existing_get_endpoint_returns_completed_preview(self):
        self.service.process_preview(self.file.id)

        preview = self.service.get_preview(self.file.id)
        self.assertEqual(preview["process_status"], AssetProcessStatus.SUCCESS)
        self.assertEqual(preview["content"], "chart\nrevenue 100\nupward trend")
        self.assertEqual(self.file.meta["upload_size"], 5)
        self.run_visual.assert_called_once_with(self.file, self.strategy, "default")

    def test_user_edits_and_renames_while_running_are_preserved_including_empty_text(self):
        def recognize(*args):
            self.service.update_preview(self.file.id, {"name": "renamed.png", "description": "", "caption": "mine"})
            return self.processed

        self.run_visual.side_effect = recognize

        self.service.process_preview(self.file.id)

        preview = self.service.get_preview(self.file.id)
        self.assertEqual(preview["name"], "renamed.png")
        self.assertEqual(preview["caption"], "mine")
        self.assertEqual(preview["description"], "")
        self.assertEqual(preview["ocr_text"], "revenue 100")
        self.assertEqual(preview["process_status"], AssetProcessStatus.SUCCESS)

    def test_import_during_recognition_discards_late_preview_result(self):
        def recognize(*args):
            self.file.meta["image_preview"]["imported"] = True
            return self.processed

        self.run_visual.side_effect = recognize

        self.service.process_preview(self.file.id)

        self.files.update.assert_not_called()

    def test_deleted_preview_is_not_recreated_after_recognition(self):
        def recognize(*args):
            self.files.select_for_update.return_value.first.return_value = None
            return self.processed

        self.run_visual.side_effect = recognize

        self.service.process_preview(self.file.id)

        self.files.update.assert_not_called()

    def test_completed_preview_does_not_call_vision_again(self):
        self.file.meta["image_preview"]["process_status"] = AssetProcessStatus.SUCCESS

        self.service.process_preview(self.file.id)

        self.run_visual.assert_not_called()

    def test_enqueue_failure_is_visible_in_preview_status(self):
        with patch("knowledge.tasks.process_image_preview.delay", side_effect=RuntimeError("broker unavailable")):
            self.service._enqueue_preview(str(self.file.id))

        preview = self.service.get_preview(self.file.id)
        self.assertEqual(preview["process_status"], AssetProcessStatus.FAILURE)
        self.assertEqual(preview["process_error"], "broker unavailable")

    def test_pending_preview_can_be_imported_with_its_edited_fields(self):
        self.file.meta["image_preview"].update(description="manual description", edited_fields=["description"])
        with (
            patch("knowledge.services.image_documents.Document") as document,
            patch("knowledge.services.image_documents.Paragraph"),
            patch("knowledge.services.image_documents.ParagraphAsset.objects.create") as create_asset,
            patch("knowledge.services.image_documents.IncrementalDocumentSync"),
        ):
            result = self.service.import_previews([self.file.id])

        self.assertEqual(result, [str(document.return_value.id)])
        self.assertEqual(create_asset.call_args.kwargs["process_status"], AssetProcessStatus.PENDING)
        self.assertEqual(create_asset.call_args.kwargs["description"], "manual description")
        self.assertEqual(create_asset.call_args.kwargs["meta"]["visual_edited_fields"], ["description"])


class DeferredImageContentTests(SimpleTestCase):
    def setUp(self):
        self.enterContext(patch("django.db.transaction.Atomic.__enter__"))
        self.enterContext(patch("django.db.transaction.Atomic.__exit__", return_value=False))
        self.paragraph = Paragraph(
            id=uuid4(),
            title="chart",
            content="chart",
            content_schema=[{"type": "image", "file_id": str(uuid4())}],
            local_state=LocalState.CLEAN,
        )
        self.paragraph.save = MagicMock()
        self.asset = MagicMock(
            paragraph_id=self.paragraph.id,
            document_id=uuid4(),
            position=1,
            caption="recognized chart",
            ocr_text="revenue 100",
            description="upward trend",
            meta={},
            document=SimpleNamespace(resource_type=DocumentResourceType.IMAGE, doc_strategy=None),
        )
        paragraphs = self.enterContext(patch("knowledge.services.paragraph_assets.Paragraph.objects.select_for_update"))
        paragraphs.return_value.filter.return_value.first.return_value = self.paragraph
        self.documents = self.enterContext(patch("knowledge.services.paragraph_assets.Document.objects.filter"))

    def test_standalone_image_updates_text_chunks_schema_and_document_length(self):
        _write_asset_description(self.asset)

        content = "recognized chart\nrevenue 100\nupward trend"
        self.assertEqual(self.paragraph.content, content)
        self.assertIn("revenue 100", "\n".join(self.paragraph.chunks))
        self.assertNotEqual(self.paragraph.chunks, ["chart"])
        self.assertEqual(self.paragraph.content_schema[0]["description"], "upward trend")
        self.assertEqual(self.documents.return_value.update.call_args.kwargs["char_length"], len(content))

    def test_inline_image_never_replaces_paragraph_text(self):
        self.asset.document.resource_type = DocumentResourceType.DOCUMENT

        _write_asset_description(self.asset)

        self.assertEqual(self.paragraph.content, "chart")
        self.documents.assert_not_called()

    def test_manual_paragraph_edit_is_not_replaced(self):
        self.paragraph.local_state = LocalState.MODIFIED
        self.paragraph.content = "my paragraph"

        _write_asset_description(self.asset)

        self.assertEqual(self.paragraph.content, "my paragraph")
        self.documents.assert_not_called()

    def test_imported_preview_edits_are_preserved_by_asset_processor(self):
        self.asset.caption = "my caption"
        self.asset.description = ""
        self.asset.meta = {"visual_edited_fields": ["caption", "description"]}
        strategy = {"visual": {"enabled": True, "strategy": "model", "model_id": str(uuid4())}}

        process_visual_assets(
            [self.asset],
            strategy,
            processor=lambda *args: {"caption": "model caption", "description": "model text", "ocr_text": "new OCR"},
        )

        self.assertEqual(self.asset.caption, "my caption")
        self.assertEqual(self.asset.description, "")
        self.assertEqual(self.asset.ocr_text, "new OCR")
        self.assertEqual(self.paragraph.content, "my caption\nnew OCR")


class DeferredImageEmbeddingOrderTests(SimpleTestCase):
    def test_image_recognition_precedes_reading_the_text_for_single_and_batch_embedding(self):
        for batch in (False, True):
            with (
                self.subTest(batch=batch),
                patch("common.event.listener_manage.QuerySet"),
                patch.object(ListenerManagement, "update_status"),
                patch("common.event.listener_manage.VectorStore"),
                patch("common.event.listener_manage.embed_paragraph_assets"),
                patch("common.event.listener_manage.process_pending_visual_assets") as recognize,
                patch("common.event.listener_manage.native_search") as query,
            ):
                events = []
                recognize.side_effect = lambda *args: events.append("recognize")
                query.side_effect = lambda *args, **kwargs: events.append("read text") or []

                if batch:
                    ListenerManagement.embedding_by_paragraph_list([str(uuid4())], MagicMock())
                else:
                    ListenerManagement.embedding_by_paragraph(str(uuid4()), MagicMock())

                self.assertEqual(events, ["recognize", "read text"])
