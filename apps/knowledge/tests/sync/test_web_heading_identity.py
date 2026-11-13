"""A Web heading rename updates its source paragraph instead of leaving a disabled copy."""

from unittest.mock import patch

from django.test import TestCase

from common.utils.fork import Fork
from knowledge.models import (
    ContentOrigin,
    Document,
    Knowledge,
    KnowledgeType,
    LocalState,
    Paragraph,
    Problem,
    ProblemParagraphMapping,
    SyncState,
)
from knowledge.serializers.document import DocumentSerializers
from knowledge.services.document_strategy import parse_web_content
from knowledge.services.incremental_sync import IncrementalDocumentSync


class WebHeadingIdentityTests(TestCase):
    def setUp(self):
        self.knowledge = Knowledge.objects.create(name="Web heading test", desc="", type=KnowledgeType.WEB)
        self.document = Document.objects.create(
            knowledge=self.knowledge,
            name="Inspection",
            type=KnowledgeType.WEB,
            char_length=0,
            meta={"source_url": "https://example.test/inspection", "selector": "body"},
        )

    def merge(self, paragraphs):
        return IncrementalDocumentSync(self.document).merge(paragraphs)

    def test_document_sync_renames_heading_in_place_and_preserves_question_links(self):
        markdown = "# 巡检规范\n文档介绍\n\n## 巡检准备\n[L101] 核对设备台账。\n\n## 巡检项目\n[L104] 检查油位。"
        self.merge(parse_web_content(markdown, None))
        paragraph = Paragraph.objects.get(document=self.document, title__contains="巡检准备")
        ids = set(Paragraph.objects.filter(document=self.document).values_list("id", flat=True))
        question = Problem.objects.create(knowledge=self.knowledge, content="如何巡检？")
        mapping = ProblemParagraphMapping.objects.create(
            knowledge=self.knowledge,
            document=self.document,
            paragraph=paragraph,
            problem=question,
        )
        changed = markdown.replace("## 巡检准备", "## 巡检准备 | 增量同步测试")
        response = Fork.Response.success(changed, [])
        with patch("knowledge.serializers.document.ListenerManagement"):
            DocumentSerializers.Sync(
                data={"knowledge_id": str(self.knowledge.id), "document_id": str(self.document.id)}
            ).sync(with_valid=False, with_embedding=False, response=response)

        paragraph.refresh_from_db()
        self.assertEqual(set(Paragraph.objects.filter(document=self.document).values_list("id", flat=True)), ids)
        self.assertIn("增量同步测试", paragraph.title)
        self.assertEqual(paragraph.sync_state, SyncState.ACTIVE)
        self.assertTrue(paragraph.is_active)
        self.assertTrue(ProblemParagraphMapping.objects.filter(id=mapping.id, paragraph=paragraph).exists())
        self.assertFalse(Paragraph.objects.filter(document=self.document, is_active=False).exists())

    def test_unchanged_duplicate_body_is_reserved_before_matching_renamed_heading(self):
        self.merge([{"title": "Before", "content": "Same body"}, {"title": "Unchanged", "content": "Same body"}])
        old = Paragraph.objects.get(document=self.document, title="Before")
        unchanged = Paragraph.objects.get(document=self.document, title="Unchanged")

        result = self.merge(
            [
                {"title": "After", "content": "Same body"},
                {"title": "Unchanged", "content": "Same body"},
            ]
        )

        old.refresh_from_db()
        unchanged.refresh_from_db()
        self.assertEqual(old.title, "After")
        self.assertEqual(unchanged.title, "Unchanged")
        self.assertEqual(result.updated_ids, [str(old.id)])
        self.assertEqual(result.unchanged_ids, [str(unchanged.id)])
        self.assertFalse(result.created_ids or result.disabled_ids)

    def test_swapped_headings_retain_body_identity_without_source_key_collision(self):
        self.merge([{"title": "First", "content": "Body A"}, {"title": "Second", "content": "Body B"}])
        old_ids = dict(Paragraph.objects.filter(document=self.document).values_list("content", "id"))

        result = self.merge([{"title": "Second", "content": "Body A"}, {"title": "First", "content": "Body B"}])

        self.assertEqual(dict(Paragraph.objects.filter(document=self.document).values_list("content", "id")), old_ids)
        self.assertEqual(Paragraph.objects.get(id=old_ids["Body A"]).title, "Second")
        self.assertFalse(result.created_ids or result.disabled_ids)

    def test_removed_duplicate_heading_releases_key_for_the_remaining_source(self):
        self.merge([{"title": "Repeated", "content": "Removed"}, {"title": "Repeated", "content": "Kept"}])
        removed = Paragraph.objects.get(document=self.document, content="Removed")
        kept = Paragraph.objects.get(document=self.document, content="Kept")

        result = self.merge([{"title": "Repeated", "content": "Kept"}])

        kept.refresh_from_db()
        removed.refresh_from_db()
        self.assertTrue(kept.is_active)
        self.assertEqual(kept.source_key, "heading:repeated:1")
        self.assertFalse(removed.is_active)
        self.assertFalse(result.created_ids)
        self.assertEqual(result.disabled_ids, [str(removed.id)])

    def test_renamed_source_matches_snapshot_and_preserves_manual_edits(self):
        self.merge([{"title": "Before", "content": "Source body"}])
        paragraph = Paragraph.objects.get(document=self.document)
        paragraph.content = "Locally edited body"
        paragraph.local_state = LocalState.MODIFIED
        paragraph.save(update_fields=["content", "local_state"])

        result = self.merge([{"title": "After", "content": "Source body"}])

        paragraph.refresh_from_db()
        self.assertEqual(paragraph.content, "Locally edited body")
        self.assertEqual(paragraph.sync_state, SyncState.CONFLICT)
        self.assertEqual(result.conflict_ids, [str(paragraph.id)])
        self.assertFalse(result.created_ids or result.disabled_ids)

    def test_renamed_source_does_not_restore_a_locally_deleted_paragraph(self):
        self.merge([{"title": "Before", "content": "Source body"}])
        paragraph = Paragraph.objects.get(document=self.document)
        paragraph.local_state = LocalState.DELETED
        paragraph.is_active = False
        paragraph.save(update_fields=["local_state", "is_active"])

        result = self.merge([{"title": "After", "content": "Source body"}])

        paragraph.refresh_from_db()
        self.assertEqual(paragraph.local_state, LocalState.DELETED)
        self.assertFalse(paragraph.is_active)
        self.assertEqual(result.conflict_ids, [str(paragraph.id)])
        self.assertFalse(result.created_ids)

    def test_manual_paragraph_with_matching_body_is_never_consumed(self):
        manual = Paragraph.objects.create(
            knowledge=self.knowledge,
            document=self.document,
            origin=ContentOrigin.MANUAL,
            title="Manual",
            content="Shared body",
            position=1,
        )

        result = self.merge([{"title": "Remote", "content": "Shared body"}])

        manual.refresh_from_db()
        self.assertEqual(manual.title, "Manual")
        self.assertEqual(manual.origin, ContentOrigin.MANUAL)
        self.assertEqual(len(result.created_ids), 1)

    def test_ambiguous_identical_bodies_are_not_matched_by_position(self):
        self.merge([{"title": "A", "content": "Repeated"}, {"title": "B", "content": "Repeated"}])

        result = self.merge([{"title": "C", "content": "Repeated"}, {"title": "D", "content": "Repeated"}])

        self.assertEqual(len(result.created_ids), 2)
        self.assertFalse(result.updated_ids)
