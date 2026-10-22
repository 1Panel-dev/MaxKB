"""Deleted paragraphs stay available to synchronization but leave visible lists and totals."""

import json
from io import BytesIO
from unittest.mock import patch
from uuid import uuid4
from zipfile import ZipFile

import openpyxl
from common.exception.app_exception import AppApiException
from django.test import TestCase

from knowledge.models import (
    ContentOrigin,
    Document,
    Knowledge,
    LocalState,
    Paragraph,
    Problem,
    ProblemParagraphMapping,
    SyncState,
)
from knowledge.serializers.document import DocumentSerializers
from knowledge.serializers.knowledge import KnowledgeSerializer
from knowledge.serializers.paragraph import ParagraphSerializers
from knowledge.serializers.problem import ProblemSerializers
from knowledge.services.incremental_sync import IncrementalDocumentSync


class ParagraphDeletionTests(TestCase):
    def setUp(self):
        self.knowledge = Knowledge.objects.create(name="Paragraph deletion", desc="", workspace_id="default")
        self.document = Document.objects.create(knowledge=self.knowledge, name="Document", char_length=0)
        self.scope = {
            "workspace_id": "default",
            "knowledge_id": str(self.knowledge.id),
            "document_id": str(self.document.id),
        }
        self.delete_vector = self.enterContext(patch("knowledge.serializers.paragraph.delete_embedding_by_paragraph"))
        self.delete_vectors = self.enterContext(
            patch("knowledge.serializers.paragraph.delete_embedding_by_paragraph_ids")
        )

    def create_paragraph(self, **overrides):
        return Paragraph.objects.create(
            **{
                "knowledge": self.knowledge,
                "document": self.document,
                "title": "Visible paragraph",
                "content": "Paragraph content",
                **overrides,
            }
        )

    def delete_paragraph(self, paragraph):
        ParagraphSerializers.Operate(data={**self.scope, "paragraph_id": str(paragraph.id)}).delete(with_valid=True)

    def assert_visible_paragraphs(self, paragraphs):
        expected_ids = {str(paragraph.id) for paragraph in paragraphs}
        query = ParagraphSerializers.Query(data=self.scope)
        self.assertEqual({row["id"] for row in query.list()}, expected_ids)
        page = query.page(1, 20)
        self.assertEqual({row["id"] for row in page["records"]}, expected_ids)
        self.assertEqual(page["total"], len(expected_ids))
        documents = DocumentSerializers.Query(data=self.scope).list()
        document = next(row for row in documents if str(row["id"]) == str(self.document.id))
        self.assertEqual(document["paragraph_count"], len(expected_ids))

    def test_lists_and_pagination_exclude_deleted_but_keep_disabled_paragraphs(self):
        self.create_paragraph(title="Deleted only", local_state=LocalState.DELETED, is_active=False, position=1)
        enabled = self.create_paragraph(position=2)
        disabled = self.create_paragraph(is_active=False, position=3)

        self.assert_visible_paragraphs([enabled, disabled])
        query = ParagraphSerializers.Query(data=self.scope)
        for current_page, paragraph in enumerate([enabled, disabled], 1):
            page = query.page(current_page, 1)
            self.assertEqual(page["total"], 2)
            self.assertEqual([row["id"] for row in page["records"]], [str(paragraph.id)])
        filtered = ParagraphSerializers.Query(data={**self.scope, "title": "Deleted only"}).page(1, 20)
        self.assertEqual(filtered["total"], 0)
        self.assertEqual(filtered["records"], [])

    def test_single_synced_delete_retains_source_metadata_and_updates_totals(self):
        snapshot = {"title": "Source", "content": "Source content"}
        synced = self.create_paragraph(
            origin=ContentOrigin.SYNCED, source_key="block-1", source_snapshot=snapshot, **snapshot
        )
        disabled = self.create_paragraph(is_active=False)

        self.delete_paragraph(synced)

        synced.refresh_from_db()
        self.assertEqual(synced.local_state, LocalState.DELETED)
        self.assertFalse(synced.is_active)
        self.assertEqual(synced.source_key, "block-1")
        self.assertEqual(synced.source_snapshot, snapshot)
        self.assert_visible_paragraphs([disabled])
        self.document.refresh_from_db()
        self.assertEqual(self.document.char_length, len(disabled.content))
        self.delete_vector.assert_called_once_with(str(synced.id))

    def test_single_manual_delete_removes_the_row(self):
        manual = self.create_paragraph()

        self.delete_paragraph(manual)

        self.assertFalse(Paragraph.objects.filter(id=manual.id).exists())
        self.assert_visible_paragraphs([])
        self.document.refresh_from_db()
        self.assertEqual(self.document.char_length, 0)
        self.delete_vector.assert_called_once_with(str(manual.id))

    def test_problem_associations_hide_deleted_paragraphs_without_removing_sync_mappings(self):
        visible = self.create_paragraph(is_active=False)
        deleted = self.create_paragraph(origin=ContentOrigin.SYNCED)
        problem = Problem.objects.create(knowledge=self.knowledge, content="Shared question")
        for paragraph in (visible, deleted):
            ProblemParagraphMapping.objects.create(
                knowledge=self.knowledge, document=self.document, paragraph=paragraph, problem=problem
            )
        self.delete_paragraph(deleted)

        linked = ProblemSerializers.Operate(data={**self.scope, "problem_id": str(problem.id)}).list_paragraph()
        self.assertEqual([str(row["id"]) for row in linked], [str(visible.id)])
        query = ProblemSerializers.Query(data=self.scope)
        self.assertEqual(query.list()[0]["paragraph_count"], 1)
        self.assertEqual(query.page(1, 20)["records"][0]["paragraph_count"], 1)
        self.assertEqual(ProblemParagraphMapping.objects.filter(problem=problem).count(), 2)
        self.assertTrue(Paragraph.objects.filter(id=deleted.id, local_state=LocalState.DELETED).exists())
        self.delete_paragraph(visible)
        self.assertEqual(query.list()[0]["paragraph_count"], 0)
        self.assertEqual(
            ProblemSerializers.Operate(data={**self.scope, "problem_id": str(problem.id)}).list_paragraph(), []
        )
        self.assertTrue(ProblemParagraphMapping.objects.filter(problem=problem, paragraph=deleted).exists())

    def test_new_problem_associations_reject_deleted_paragraphs(self):
        deleted = self.create_paragraph(origin=ContentOrigin.SYNCED)
        self.delete_paragraph(deleted)
        problem = Problem.objects.create(knowledge=self.knowledge, content="Question")
        scope = {**self.scope, "paragraph_id": str(deleted.id), "problem_id": str(problem.id)}

        with self.assertRaises(AppApiException):
            ParagraphSerializers.Association(data=scope).association(with_embedding=False)
        with self.assertRaises(AppApiException):
            ParagraphSerializers.Problem(data=scope).save({"content": "New question"}, with_embedding=False)
        with (
            patch("knowledge.serializers.problem.get_embedding_model_id_by_knowledge_id"),
            patch("knowledge.serializers.problem.embedding_by_data_list") as embed,
            self.assertRaises(AppApiException),
        ):
            ProblemSerializers.BatchOperate(data=self.scope).association(
                {
                    "problem_id_list": [str(problem.id)],
                    "paragraph_list": [{"paragraph_id": str(deleted.id), "document_id": str(self.document.id)}],
                }
            )
        embed.assert_not_called()
        self.assertFalse(ProblemParagraphMapping.objects.exists())
        self.assertFalse(Problem.objects.filter(content="New question").exists())

    def test_all_content_exports_exclude_deleted_paragraphs_and_keep_disabled_ones(self):
        deleted = self.create_paragraph(origin=ContentOrigin.SYNCED, content="Deleted export content")
        disabled = self.create_paragraph(is_active=False, content="Disabled export content")
        self.delete_paragraph(deleted)
        document = DocumentSerializers.Operate(data=self.scope)
        batch = DocumentSerializers.Batch(data=self.scope)
        knowledge = KnowledgeSerializer.Operate(data={**self.scope, "user_id": str(uuid4())})
        exporters = {
            "document_excel": document.export,
            "document_zip": document.export_zip,
            "batch_excel": lambda: batch.batch_export({"id_list": [str(self.document.id)]}),
            "batch_zip": lambda: batch.batch_export_zip({"id_list": [str(self.document.id)]}),
            "knowledge_excel": knowledge.export_excel,
            "knowledge_zip": knowledge.export_zip,
            "knowledge_archive": knowledge.export_knowledge,
        }
        for name, export in exporters.items():
            with self.subTest(export=name):
                response = export()
                content = response.content
                if response["Content-Type"] == "application/zip":
                    with ZipFile(BytesIO(content)) as archive:
                        content = archive.read(next(path for path in archive.namelist() if path.endswith(".xlsx")))
                        if name == "knowledge_archive":
                            resources = json.loads(archive.read("knowledge.json"))["resources"]
                            retained = next(row for row in resources["paragraphs"] if row["id"] == str(deleted.id))
                            self.assertEqual(retained["local_state"], LocalState.DELETED)
                workbook = openpyxl.load_workbook(BytesIO(content))
                values = [cell for sheet in workbook for row in sheet.iter_rows(values_only=True) for cell in row]
                self.assertNotIn(deleted.content, values)
                self.assertIn(disabled.content, values)
                workbook.close()
        self.assertTrue(Paragraph.objects.filter(id=deleted.id).exists())

    def test_batch_string_ids_keep_synced_rows_and_delete_manual_rows(self):
        synced = self.create_paragraph(origin=ContentOrigin.SYNCED, source_key="block-1")
        manual = self.create_paragraph()
        disabled = self.create_paragraph(is_active=False)
        paragraph_ids = [str(synced.id), str(manual.id)]

        result = ParagraphSerializers.Batch(data=self.scope).batch_delete({"id_list": paragraph_ids})

        self.assertTrue(result)
        self.assertTrue(Paragraph.objects.filter(id=synced.id).exists())
        synced.refresh_from_db()
        self.assertEqual(synced.local_state, LocalState.DELETED)
        self.assertFalse(synced.is_active)
        self.assertEqual(synced.source_key, "block-1")
        self.assertFalse(Paragraph.objects.filter(id=manual.id).exists())
        self.assert_visible_paragraphs([disabled])
        self.document.refresh_from_db()
        self.assertEqual(self.document.char_length, len(disabled.content))
        self.delete_vectors.assert_called_once_with(paragraph_ids)

    def test_batch_deleting_all_synced_paragraphs_leaves_zero_visible_totals(self):
        synced = [self.create_paragraph(origin=ContentOrigin.SYNCED) for _ in range(2)]
        paragraph_ids = [str(paragraph.id) for paragraph in synced]

        ParagraphSerializers.Batch(data=self.scope).batch_delete({"id_list": paragraph_ids})

        self.assertEqual(Paragraph.objects.filter(id__in=paragraph_ids, local_state=LocalState.DELETED).count(), 2)
        self.assert_visible_paragraphs([])
        self.document.refresh_from_db()
        self.assertEqual(self.document.char_length, 0)

    def test_incremental_sync_preserves_the_deleted_row_and_detects_source_changes(self):
        remote = {"source_key": "block-1", "title": "Source", "content": "Source content"}
        service = IncrementalDocumentSync(self.document)
        result = service.merge([remote])
        synced = Paragraph.objects.get(id=result.created_ids[0])
        self.delete_paragraph(synced)

        unchanged = service.merge([remote])

        self.assertEqual(unchanged.created_ids, [])
        self.assertIn(str(synced.id), unchanged.unchanged_ids)
        self.assert_visible_paragraphs([])
        changed = service.merge([{**remote, "content": "Updated source content"}])
        synced.refresh_from_db()
        self.assertEqual(changed.created_ids, [])
        self.assertIn(str(synced.id), changed.conflict_ids)
        self.assertEqual(synced.local_state, LocalState.DELETED)
        self.assertEqual(synced.sync_state, SyncState.CONFLICT)
        self.assertFalse(synced.is_active)
        self.assert_visible_paragraphs([])
