"""Web image ownership follows paragraphs without changing stable file references."""

from unittest.mock import patch

from django.db import transaction
from django.test import TestCase

from common.utils.fork import Fork
from knowledge.models import ContentOrigin, Document, File, FileSourceType, Knowledge, KnowledgeType, Paragraph
from knowledge.models import ParagraphAsset
from knowledge.serializers.document import DocumentSerializers
from knowledge.services.document_strategy import document_source_hash, normalize_document_strategy, strategy_hashes
from knowledge.services.incremental_sync import prepare_remote_paragraphs
from knowledge.services.paragraph_assets import sync_paragraph_assets
from knowledge.services.paragraph_files import bind_paragraph_image_files, migrate_paragraph_files
from knowledge.web_assets import _cached_web_image


class WebImageOwnershipTests(TestCase):
    def setUp(self):
        self.knowledge = Knowledge.objects.create(name="Web image ownership", desc="", type=KnowledgeType.WEB)
        self.strategy = normalize_document_strategy(None)
        self.document = Document.objects.create(
            knowledge=self.knowledge,
            name="Web page",
            char_length=0,
            type=KnowledgeType.WEB,
            meta={"source_url": "https://example.com/docs"},
            doc_strategy=self.strategy,
            **strategy_hashes(self.strategy),
        )
        self.image = File(
            file_name="chart.png",
            source_type=FileSourceType.KNOWLEDGE,
            source_id=str(self.knowledge.id),
            storage_type="seaweedfs",
            sha256_hash="image-hash",
            file_size=10,
            meta={"source_url": "https://example.com/chart.png", "seaweedfs_key": "files/shared-image"},
        )
        # No external storage is needed to test ownership and reference integrity.
        File.objects.bulk_create([self.image])
        self.content = f"before ![chart](./oss/file/{self.image.id}) after"

    def paragraph(self, document=None):
        return Paragraph.objects.create(
            knowledge=self.knowledge,
            document=document or self.document,
            content=self.content,
            chunks=[self.content],
            source_snapshot={"title": "", "content": self.content},
            origin=ContentOrigin.SYNCED,
        )

    def test_asset_sync_binds_shared_image_without_changing_file_or_content(self):
        first, second = self.paragraph(), self.paragraph()

        assets = sync_paragraph_assets([first, second])
        self.image.refresh_from_db()

        self.assertEqual(self.image.source_type, FileSourceType.PARAGRAPH)
        self.assertEqual(self.image.source_id, str(first.id))
        self.assertEqual({asset.file_id for asset in assets}, {self.image.id})
        self.assertEqual({asset.paragraph_id for asset in assets}, {first.id, second.id})
        for paragraph in (first, second):
            paragraph.refresh_from_db()
            self.assertEqual(paragraph.content, self.content)
            self.assertEqual(paragraph.source_snapshot["content"], self.content)
            self.assertEqual(paragraph.chunks, [self.content])
        self.assertEqual(bind_paragraph_image_files(assets), 0)
        self.assertEqual(File.objects.count(), 1)

    def test_paragraph_owned_image_is_reused_only_in_its_knowledge(self):
        paragraph = self.paragraph()
        sync_paragraph_assets([paragraph])
        other_knowledge = Knowledge.objects.create(name="Other knowledge", desc="")
        args = (self.image.meta["source_url"], self.knowledge.id, self.image.sha256_hash)

        self.assertEqual(_cached_web_image(*args).id, self.image.id)
        self.assertIsNone(_cached_web_image(args[0], other_knowledge.id, args[2]))
        self.assertIsNone(_cached_web_image(args[0], self.knowledge.id, "changed-image-hash"))
        self.assertIsNone(_cached_web_image("https://example.com/other.png", self.knowledge.id, args[2]))

    def test_image_moving_between_synced_paragraphs_transfers_ownership(self):
        first, second = self.paragraph(), self.paragraph()
        assets = sync_paragraph_assets([first])
        first.content = "image moved to the next paragraph"
        first.save(update_fields=["content"])

        moved = sync_paragraph_assets([first, second])

        self.assertEqual([asset.id for asset in moved], [assets[0].id])
        self.image.refresh_from_db()
        self.assertEqual(self.image.source_id, str(second.id))
        self.assertEqual(moved[0].paragraph_id, second.id)
        first.delete()
        self.assertTrue(File.objects.filter(id=self.image.id).exists())

    def test_deleting_owner_transfers_shared_file_then_last_delete_removes_it(self):
        first = self.paragraph()
        other_document = Document.objects.create(knowledge=self.knowledge, name="Other page", char_length=0)
        second = self.paragraph(other_document)
        sync_paragraph_assets([first, second])

        first.delete()

        self.image.refresh_from_db()
        self.assertEqual(self.image.source_id, str(second.id))
        self.assertTrue(ParagraphAsset.objects.filter(paragraph=second, file=self.image).exists())
        self.assertEqual(
            _cached_web_image(self.image.meta["source_url"], self.knowledge.id, self.image.sha256_hash).id,
            self.image.id,
        )

        with self.captureOnCommitCallbacks(execute=False) as callbacks:
            second.delete()
        self.assertFalse(File.objects.filter(id=self.image.id).exists())
        self.assertFalse(ParagraphAsset.objects.filter(file_id=self.image.id).exists())
        self.assertEqual(len(callbacks), 1)

    def test_deleting_shared_paragraphs_in_one_batch_does_not_leave_an_owner(self):
        first, second = self.paragraph(), self.paragraph()
        sync_paragraph_assets([first, second])

        Paragraph.objects.filter(id__in=[first.id, second.id]).delete()

        self.assertFalse(File.objects.filter(id=self.image.id).exists())

    def test_ownership_transfer_is_rolled_back_with_import(self):
        paragraph = self.paragraph()
        with self.assertRaises(RuntimeError), transaction.atomic():
            sync_paragraph_assets([paragraph])
            raise RuntimeError("import failed")

        self.image.refresh_from_db()
        self.assertEqual(self.image.source_type, FileSourceType.KNOWLEDGE)
        self.assertEqual(self.image.source_id, str(self.knowledge.id))
        self.assertFalse(ParagraphAsset.objects.exists())

    def test_foreign_knowledge_file_is_not_rebound(self):
        paragraph = self.paragraph()
        other_knowledge = Knowledge.objects.create(name="Other knowledge", desc="")
        File.objects.filter(id=self.image.id).update(
            meta={"source_url": "https://example.com/chart.png"}, source_id=str(other_knowledge.id)
        )
        assets = sync_paragraph_assets([paragraph])
        self.assertEqual(bind_paragraph_image_files(assets), 0)
        self.image.refresh_from_db()
        self.assertEqual(self.image.source_id, str(other_knowledge.id))

    def test_unchanged_web_sync_backfills_legacy_ownership(self):
        paragraph = self.paragraph()
        asset = ParagraphAsset.objects.create(
            knowledge=self.knowledge, document=self.document, paragraph=paragraph, file=self.image
        )
        paragraphs = [{"title": "", "content": self.content}]
        self.document.source_hash = document_source_hash(prepare_remote_paragraphs(paragraphs))
        self.document.save(update_fields=["source_hash"])
        serializer = DocumentSerializers.Sync(
            data={"knowledge_id": str(self.knowledge.id), "document_id": str(self.document.id)}
        )
        with (
            patch("knowledge.serializers.document.parse_web_content", return_value=paragraphs),
            patch("knowledge.serializers.document.ListenerManagement"),
            patch("knowledge.serializers.document.IncrementalDocumentSync") as merge,
        ):
            serializer.sync(
                with_valid=False,
                with_embedding=False,
                response=Fork.Response.success(self.content, []),
            )
        merge.assert_not_called()
        self.image.refresh_from_db()
        asset.refresh_from_db()
        self.assertEqual(self.image.source_type, FileSourceType.PARAGRAPH)
        self.assertEqual(self.image.source_id, str(paragraph.id))
        self.assertEqual(asset.file_id, self.image.id)

    def test_shared_non_owner_can_move_between_documents_in_same_knowledge(self):
        owner, moved = self.paragraph(), self.paragraph()
        sync_paragraph_assets([owner, moved])
        target = Document.objects.create(knowledge=self.knowledge, name="Target", char_length=0)

        migrate_paragraph_files([moved], target.id, self.knowledge)
        Paragraph.objects.filter(id=moved.id).update(document=target)

        self.assertEqual(File.objects.count(), 1)
        self.assertEqual(ParagraphAsset.objects.get(paragraph=moved).file_id, self.image.id)
        owner.delete()
        self.image.refresh_from_db()
        self.assertEqual(self.image.source_id, str(moved.id))

    def test_document_migration_splits_shared_ownership_without_copying_bytes(self):
        owner = self.paragraph()
        retained_document = Document.objects.create(knowledge=self.knowledge, name="Retained", char_length=0)
        retained = self.paragraph(retained_document)
        sync_paragraph_assets([owner, retained])
        target = Knowledge.objects.create(name="Target knowledge", desc="")
        serializer = DocumentSerializers.Migrate(
            data={
                "workspace_id": "default",
                "knowledge_id": str(self.knowledge.id),
                "target_knowledge_id": str(target.id),
                "document_id_list": [str(self.document.id)],
            }
        )

        with patch("knowledge.serializers.document.update_embedding_knowledge_id"):
            serializer.migrate()

        owner.refresh_from_db()
        self.image.refresh_from_db()
        copied = ParagraphAsset.objects.get(paragraph=owner).file
        self.assertNotEqual(copied.id, self.image.id)
        self.assertEqual(copied.source_id, str(owner.id))
        self.assertEqual(copied.meta["seaweedfs_key"], self.image.meta["seaweedfs_key"])
        self.assertEqual(self.image.source_id, str(retained.id))
        self.assertIn(str(copied.id), owner.content)
        self.assertIn(str(copied.id), owner.source_snapshot["content"])
        self.assertEqual(
            _cached_web_image(self.image.meta["source_url"], target.id, self.image.sha256_hash).id, copied.id
        )

        owner.delete()
        self.assertTrue(File.objects.filter(id=self.image.id).exists())
        self.assertTrue(ParagraphAsset.objects.filter(paragraph=retained, file=self.image).exists())
