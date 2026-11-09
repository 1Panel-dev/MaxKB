"""Workflow libraries reuse standalone image management without joining source snapshots."""

from io import BytesIO
from unittest.mock import patch
from uuid import uuid4

from common.exception.app_exception import AppApiException
from django.test import SimpleTestCase, TestCase
from django.utils import timezone
from PIL import Image

from knowledge.models import (
    AssetProcessStatus,
    Document,
    DocumentResourceType,
    File,
    FileSourceType,
    Knowledge,
    KnowledgeType,
    Paragraph,
    ParagraphAsset,
)
from knowledge.serializers.document import DocumentSerializers
from knowledge.services.image_documents import ImageDocumentService
from knowledge.services.workflow_sync import (
    WorkflowDocumentSyncRun,
    finalize_workflow_complete_snapshot,
    merge_workflow_incremental_snapshot,
)


class WorkflowImageContractTests(SimpleTestCase):
    @patch("knowledge.services.image_documents.QuerySet")
    def test_image_service_accepts_base_and_workflow_but_rejects_external_libraries(self, query):
        service = ImageDocumentService("default", str(uuid4()))
        for kind in KnowledgeType:
            with self.subTest(kind=kind):
                knowledge = Knowledge(type=kind)
                query.return_value.filter.return_value.first.return_value = knowledge
                if kind in (KnowledgeType.BASE, KnowledgeType.WORKFLOW):
                    self.assertIs(service.get_knowledge(), knowledge)
                else:
                    with self.assertRaises(AppApiException):
                        service.get_knowledge()


class WorkflowImageManagementTests(TestCase):
    def setUp(self):
        self.knowledge = Knowledge.objects.create(name="Workflow images", desc="", type=KnowledgeType.WORKFLOW)
        self.service = ImageDocumentService(self.knowledge.workspace_id, self.knowledge.id)
        image = BytesIO()
        Image.new("RGB", (2, 2), "red").save(image, format="PNG")
        self.image_bytes = image.getvalue()
        self.enterContext(patch.object(File, "get_bytes", return_value=self.image_bytes))

    def create_file(self, knowledge=None):
        file = File(
            file_name="photo.png",
            file_size=len(self.image_bytes),
            sha256_hash="pixels",
            source_type=FileSourceType.KNOWLEDGE,
            source_id=str((knowledge or self.knowledge).id),
            storage_type="seaweedfs",
            meta={"seaweedfs_key": f"files/{uuid4()}"},
        )
        # Storage I/O is mocked; database ownership and image validation remain real.
        File.objects.bulk_create([file])
        return file

    def test_preview_edit_and_import_preserve_content_and_source(self):
        file = self.create_file()
        previews = self.service.generate_previews_by_file_ids([file.id])
        self.assertEqual(previews[0]["resource_type"], DocumentResourceType.IMAGE)
        self.assertEqual(previews[0]["content"], [{"title": "photo", "content": "photo"}])
        self.service.update_preview(file.id, {"name": "edited.png", "description": "Edited description"})
        document_id = self.service.import_previews([file.id])[0]
        document = Document.objects.get(id=document_id)
        paragraph = Paragraph.objects.get(document=document)
        self.assertEqual(document.type, KnowledgeType.BASE)
        self.assertEqual(document.resource_type, DocumentResourceType.IMAGE)
        self.assertEqual(document.name, "edited.png")
        self.assertEqual((paragraph.title, paragraph.content), ("edited", "Edited description"))
        self.assertTrue(ParagraphAsset.objects.filter(document=document, paragraph=paragraph, file=file).exists())
        file.refresh_from_db()
        self.assertEqual((file.source_type, file.source_id), (FileSourceType.DOCUMENT, document_id))

    def test_direct_import_retains_visual_processing_for_embedding_worker(self):
        for enabled in (False, True):
            with self.subTest(enabled=enabled):
                file = self.create_file()
                strategy = {"visual": {"enabled": enabled, "strategy": "model", "model_id": str(uuid4())}}
                with patch.object(self.service, "_enqueue_preview") as enqueue:
                    document_id = self.service.import_previews([file.id], strategy)[0]
                enqueue.assert_not_called()
                asset = ParagraphAsset.objects.get(document_id=document_id)
                self.assertEqual(
                    asset.process_status, AssetProcessStatus.PENDING if enabled else AssetProcessStatus.SKIPPED
                )
                self.assertEqual(asset.paragraph.content, "photo")
                self.assertEqual(asset.document.doc_strategy["visual"]["enabled"], enabled)

    def test_visual_preview_supports_model_and_tool_strategies(self):
        for strategy_type in ("model", "tool"):
            with self.subTest(strategy=strategy_type):
                file = self.create_file()
                strategy = {"visual": {"enabled": True, "strategy": strategy_type, f"{strategy_type}_id": str(uuid4())}}
                with patch("knowledge.services.image_documents.resolve_visual_processor") as resolve:
                    resolve.return_value.return_value = {"description": "Recognized image"}
                    preview = self.service.generate_previews_by_file_ids([file.id], strategy)[0]
                resolve.return_value.assert_called_once()
                self.assertEqual(preview["process_status"], AssetProcessStatus.SUCCESS)
                document_id = self.service.import_previews([file.id])[0]
                self.assertEqual(Paragraph.objects.get(document_id=document_id).content, "Recognized image")

    def migrate(self, source, target, document_id):
        operation = DocumentSerializers.Migrate(
            data={
                "workspace_id": source.workspace_id,
                "knowledge_id": str(source.id),
                "target_knowledge_id": str(target.id),
                "document_id_list": [str(document_id)],
            }
        )
        with patch("knowledge.serializers.document.update_embedding_knowledge_id"):
            operation.migrate()

    def test_image_migration_between_supported_libraries_keeps_source_and_asset(self):
        for source_type in (KnowledgeType.BASE, KnowledgeType.WORKFLOW):
            for target_type in (KnowledgeType.BASE, KnowledgeType.WORKFLOW):
                with self.subTest(source=source_type, target=target_type):
                    source = Knowledge.objects.create(name="Source", desc="", type=source_type)
                    target = Knowledge.objects.create(name="Target", desc="", type=target_type)
                    file = self.create_file(source)
                    service = ImageDocumentService(source.workspace_id, source.id)
                    document_id = service.import_previews([file.id])[0]
                    self.migrate(source, target, document_id)
                    document = Document.objects.get(id=document_id)
                    self.assertEqual(document.knowledge_id, target.id)
                    self.assertEqual(document.resource_type, DocumentResourceType.IMAGE)
                    self.assertEqual(document.type, KnowledgeType.BASE)
                    self.assertEqual(ParagraphAsset.objects.get(document=document).knowledge_id, target.id)
                    self.assertEqual(Paragraph.objects.get(document=document).knowledge_id, target.id)
                    self.assertEqual(document.meta["source_file_id"], str(file.id))
                    file.refresh_from_db()
                    self.assertEqual((file.source_type, file.source_id), (FileSourceType.DOCUMENT, document_id))

    def test_image_migration_rejects_unsupported_libraries_without_moving_data(self):
        file = self.create_file()
        document_id = self.service.import_previews([file.id])[0]
        for kind in (KnowledgeType.WEB, KnowledgeType.LARK):
            with self.subTest(kind=kind):
                target = Knowledge.objects.create(name="Unsupported", desc="", type=kind)
                with self.assertRaises(AppApiException):
                    self.migrate(self.knowledge, target, document_id)
                self.assertEqual(Document.objects.get(id=document_id).knowledge_id, self.knowledge.id)
                self.assertEqual(ParagraphAsset.objects.get(document_id=document_id).knowledge_id, self.knowledge.id)

    def test_workflow_snapshot_cleanup_preserves_manually_imported_images(self):
        file = self.create_file()
        document_id = self.service.import_previews([file.id])[0]
        run = WorkflowDocumentSyncRun(id=uuid4(), knowledge_id=self.knowledge.id, create_time=timezone.now())
        document = Document.objects.get(id=document_id)
        document.meta.update(source_scope="remote", workflow_action_id=str(run.id))
        document.save(update_fields=["meta"])
        for success in (True, False):
            finalize_workflow_complete_snapshot(run, success, {"source_scope": "remote"})
        merge_workflow_incremental_snapshot(run, {"source_scope": "remote"})
        self.assertTrue(Document.objects.filter(id=document_id).exists())
        self.assertTrue(ParagraphAsset.objects.filter(document_id=document_id, file=file).exists())
        self.assertTrue(File.objects.filter(id=file.id).exists())
