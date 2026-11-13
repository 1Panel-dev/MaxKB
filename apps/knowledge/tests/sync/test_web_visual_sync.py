"""Generated image descriptions must not conflict with subsequent Web source updates."""

from uuid import uuid4

from django.test import TestCase

from knowledge.models import File, FileSourceType, Knowledge, KnowledgeType, Document, LocalState, Paragraph, SyncState
from knowledge.services.document_strategy import normalize_document_strategy
from knowledge.services.incremental_sync import IncrementalDocumentSync
from knowledge.services.paragraph_assets import process_visual_assets, sync_paragraph_assets


class WebVisualSyncTests(TestCase):
    def setUp(self):
        self.strategy = normalize_document_strategy(
            {"visual": {"enabled": True, "strategy": "model", "model_id": str(uuid4())}}
        )
        self.knowledge = Knowledge.objects.create(name="Web visual sync test", desc="", type=KnowledgeType.WEB)
        self.document = Document.objects.create(
            name="Web document",
            knowledge=self.knowledge,
            type=KnowledgeType.WEB,
            doc_strategy=self.strategy,
            char_length=0,
        )
        self.file = File(
            file_name="image.png",
            source_type=FileSourceType.KNOWLEDGE,
            source_id=str(self.knowledge.id),
            storage_type="seaweedfs",
            meta={"seaweedfs_key": "test-web-image"},
        )
        File.objects.bulk_create([self.file])
        self.url = f"./oss/file/{self.file.id}"
        self.source = {"title": "Images", "content": f"原始正文 ![原始说明]({self.url})"}
        IncrementalDocumentSync(self.document).merge([self.source])
        self.paragraph = Paragraph.objects.get(document=self.document)
        self.recognize()

    def recognize(self):
        self.paragraph.refresh_from_db()
        assets = sync_paragraph_assets([self.paragraph], self.document.visual_strategy_hash)
        process_visual_assets(
            assets, self.strategy, processor=lambda *_: {"description": "识别出的 [图表]\\说明\n第二行"}
        )
        self.paragraph.refresh_from_db()
        self.document.refresh_from_db()

    def test_unchanged_source_retains_description_and_clean_state(self):
        enhanced = self.paragraph.content
        self.assertIn("识别出的", enhanced)

        result = IncrementalDocumentSync(self.document).merge([self.source])

        self.paragraph.refresh_from_db()
        self.document.refresh_from_db()
        self.assertEqual(self.paragraph.content, enhanced)
        self.assertEqual(self.paragraph.local_state, LocalState.CLEAN)
        self.assertEqual(result.unchanged_ids, [str(self.paragraph.id)])
        self.assertFalse(result.reembed_ids)
        self.assertFalse(result.conflict_ids)
        self.assertEqual(self.paragraph.source_snapshot, self.source)
        self.assertEqual(self.document.char_length, len(enhanced))

    def test_changed_source_updates_same_paragraph_without_false_conflict(self):
        changed = {**self.source, "content": self.source["content"].replace("原始正文", "更新后的正文")}

        result = IncrementalDocumentSync(self.document).merge([changed])

        self.paragraph.refresh_from_db()
        self.assertEqual(self.paragraph.content, changed["content"])
        self.assertEqual(self.paragraph.local_state, LocalState.CLEAN)
        self.assertFalse(result.conflict_ids)
        self.assertEqual(result.updated_ids, [str(self.paragraph.id)])
        self.recognize()
        self.assertIn("更新后的正文", self.paragraph.content)
        self.assertIn("识别出的", self.paragraph.content)
        self.assertEqual(self.paragraph.source_snapshot, changed)
        self.assertEqual(self.document.char_length, len(self.paragraph.content))

    def test_actual_local_edits_still_conflict_with_source_changes(self):
        for state in (LocalState.CLEAN, LocalState.MODIFIED):
            with self.subTest(state=state):
                edited = self.paragraph.content + " 人工编辑"
                self.paragraph.content = edited
                self.paragraph.local_state = state
                self.paragraph.source_snapshot = self.source
                self.paragraph.save(update_fields=["content", "local_state", "source_snapshot"])
                changed = {**self.source, "content": self.source["content"] + " 来源更新"}

                result = IncrementalDocumentSync(self.document).merge([changed])

                self.paragraph.refresh_from_db()
                self.assertEqual(self.paragraph.content, edited)
                self.assertEqual(self.paragraph.sync_state, SyncState.CONFLICT)
                self.assertEqual(self.paragraph.local_state, LocalState.MODIFIED)
                self.assertEqual(result.conflict_ids, [str(self.paragraph.id)])

    def test_manual_image_caption_is_not_treated_as_generated_text(self):
        edited = f"原始正文 ![人工修改图片说明]({self.url})"
        self.paragraph.content = edited
        self.paragraph.save(update_fields=["content"])
        changed = {**self.source, "content": self.source["content"] + " 来源更新"}

        result = IncrementalDocumentSync(self.document).merge([changed])

        self.paragraph.refresh_from_db()
        self.assertEqual(self.paragraph.content, edited)
        self.assertEqual(result.conflict_ids, [str(self.paragraph.id)])

    def test_manual_deletion_is_preserved_when_source_changes(self):
        self.paragraph.local_state = LocalState.DELETED
        self.paragraph.is_active = False
        self.paragraph.save(update_fields=["local_state", "is_active"])
        changed = {**self.source, "content": self.source["content"] + " 来源更新"}

        result = IncrementalDocumentSync(self.document).merge([changed])

        self.paragraph.refresh_from_db()
        self.assertFalse(self.paragraph.is_active)
        self.assertEqual(self.paragraph.local_state, LocalState.DELETED)
        self.assertEqual(result.conflict_ids, [str(self.paragraph.id)])
