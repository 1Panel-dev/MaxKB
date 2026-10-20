from unittest.mock import MagicMock, patch
from uuid import uuid4

from django.test import TestCase
from django.utils import timezone

from application.workflow.nodes.knowledge_write_node.knowledge_write_node import KnowledgeWriteNode
from knowledge.models import Document, File, FileSourceType, Knowledge, KnowledgeType, Paragraph, ParagraphAsset
from knowledge.services.paragraph_assets import sync_paragraph_assets
from knowledge.services.workflow_sync import WorkflowDocumentSyncRun, merge_workflow_incremental_snapshot


class WorkflowDocumentImageTests(TestCase):
    def setUp(self):
        self.knowledge = Knowledge.objects.create(name="workflow images", desc="")
        self.node = KnowledgeWriteNode.__new__(KnowledgeWriteNode)
        self.node.get_workflow_parameters = MagicMock(
            return_value={"knowledge_id": str(self.knowledge.id), "knowledge_action_id": str(uuid4())}
        )

    def image(self, source_type=FileSourceType.KNOWLEDGE, source_id=None):
        image = File(
            file_name="image.png",
            source_type=source_type,
            source_id=str(source_id or self.knowledge.id),
            storage_type="seaweedfs",
            meta={"seaweedfs_key": f"files/{uuid4()}", "mime_type": "image/png"},
        )
        File.objects.bulk_create([image])
        return image

    def document(self, name, images):
        return {
            "name": name,
            "paragraphs": [{"content": f"![image](/admin/oss/file/{image.id})"} for image in images],
        }

    def test_import_binds_each_documents_images_before_returning_and_preserves_urls(self):
        first, second, unused = self.image(), self.image(), self.image()
        original_meta = dict(first.meta)
        documents, _, _ = self.node.save(
            [self.document("first", [first, first]), self.document("second", [second])], None
        )

        for image, document in zip((first, second), documents):
            image.refresh_from_db()
            self.assertEqual(image.source_type, FileSourceType.PARAGRAPH)
            self.assertTrue(
                ParagraphAsset.objects.filter(document=document, paragraph_id=image.source_id, file=image).exists()
            )
            self.assertTrue(
                Paragraph.objects.filter(document=document, content__contains=f"/oss/file/{image.id}").exists()
            )
        self.assertEqual(first.meta, original_meta)
        unused.refresh_from_db()
        self.assertEqual(unused.source_type, FileSourceType.KNOWLEDGE)
        self.assertEqual(unused.source_id, str(self.knowledge.id))

    def test_import_preserves_files_owned_by_another_knowledge_or_document(self):
        other_knowledge = self.image(source_id=uuid4())
        other_document = self.image(FileSourceType.DOCUMENT, uuid4())
        images = (other_knowledge, other_document)
        owners = [(image.source_type, image.source_id) for image in images]

        self.node.save([self.document("references", images)], None)

        for image, owner in zip(images, owners):
            image.refresh_from_db()
            self.assertEqual((image.source_type, image.source_id), owner)

    def test_plain_text_import_does_not_bind_unreferenced_images(self):
        image = self.image()

        self.node.save([{"name": "text", "paragraphs": [{"content": "plain text"}]}], None)

        image.refresh_from_db()
        self.assertEqual(image.source_type, FileSourceType.KNOWLEDGE)
        self.assertEqual(image.source_id, str(self.knowledge.id))

    def test_incremental_sync_transfers_images_to_the_retained_paragraph(self):
        source_meta = {"source_scope": "lark", "token": "remote-document"}
        retained = Document.objects.create(
            knowledge=self.knowledge, name="old", char_length=0, type=KnowledgeType.WORKFLOW, meta=source_meta
        )
        parameters = self.node.get_workflow_parameters.return_value
        parameters["workflow_source"] = {"source_scope": "lark"}
        run = WorkflowDocumentSyncRun(
            id=parameters["knowledge_action_id"], knowledge_id=self.knowledge.id, create_time=timezone.now()
        )
        image = self.image()
        incoming = {**self.document("new", [image]), "meta": source_meta}
        documents, _, _ = self.node.save([incoming], None)

        result = merge_workflow_incremental_snapshot(run, {"source_scope": "lark"}, retained.id)

        image.refresh_from_db()
        self.assertEqual(result["synced_count"], 1)
        self.assertEqual(image.source_type, FileSourceType.PARAGRAPH)
        self.assertTrue(
            ParagraphAsset.objects.filter(document=retained, paragraph_id=image.source_id, file=image).exists()
        )
        self.assertFalse(Document.objects.filter(id=documents[0].id).exists())
        self.assertTrue(Paragraph.objects.filter(document=retained, content__contains=f"/oss/file/{image.id}").exists())

    def test_image_binding_failure_rolls_back_documents_and_prior_bindings(self):
        first, second = self.image(), self.image()

        def bind_then_fail(paragraphs, visual_strategy_hash):
            assets = sync_paragraph_assets(paragraphs, visual_strategy_hash)
            if paragraphs[0].document.name == "second":
                raise RuntimeError("binding failed")
            return assets

        with (
            patch(
                "application.workflow.nodes.knowledge_write_node.knowledge_write_node.sync_paragraph_assets",
                side_effect=bind_then_fail,
            ),
            self.assertRaisesRegex(RuntimeError, "binding failed"),
        ):
            self.node.save([self.document("first", [first]), self.document("second", [second])], None)

        self.assertFalse(Document.objects.filter(knowledge=self.knowledge).exists())
        self.assertFalse(Paragraph.objects.filter(knowledge=self.knowledge).exists())
        self.assertFalse(ParagraphAsset.objects.filter(knowledge=self.knowledge).exists())
        for image in (first, second):
            image.refresh_from_db()
            self.assertEqual(image.source_type, FileSourceType.KNOWLEDGE)
            self.assertEqual(image.source_id, str(self.knowledge.id))
