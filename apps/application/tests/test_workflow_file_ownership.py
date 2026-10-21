"""Workflow imports transfer source uploads to their persisted documents."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

from django.test import TestCase
from django.utils import timezone

from application.workflow.nodes.knowledge_write_node.knowledge_write_node import KnowledgeWriteNode
from knowledge.models import Document, File, FileSourceType, Knowledge, KnowledgeType
from knowledge.services.workflow_sync import (
    WorkflowDocumentSyncRun,
    finalize_workflow_complete_snapshot,
    merge_workflow_incremental_snapshot,
)


class WorkflowFileOwnershipTests(TestCase):
    def setUp(self):
        self.knowledge = Knowledge.objects.create(name="Workflow sources", desc="", type=KnowledgeType.WORKFLOW)
        self.parameters = {
            "knowledge_id": str(self.knowledge.id),
            "knowledge_action_id": str(uuid4()),
            "workflow_source": {"source_scope": "lark", "source_type": "tool"},
        }
        self.node = KnowledgeWriteNode.__new__(KnowledgeWriteNode)
        self.node.get_workflow_parameters = MagicMock(return_value=self.parameters)

    def source(self, source_type=FileSourceType.KNOWLEDGE):
        file = File(
            file_name="lark.docx",
            source_type=source_type,
            source_id=str(self.knowledge.id),
            storage_type="seaweedfs",
            sha256_hash=str(uuid4()),
        )
        File.objects.bulk_create([file])
        return file

    def document_input(self, file, name="Lark document"):
        return {
            "name": name,
            "source_file_id": str(file.id),
            "meta": {"token": "remote-document"},
            "paragraphs": [{"content": "Imported content"}],
        }

    def assert_owned_by(self, file, document):
        file.refresh_from_db()
        document.refresh_from_db()
        self.assertEqual((file.source_type, file.source_id), (FileSourceType.DOCUMENT, str(document.id)))
        self.assertEqual(document.meta["source_file_id"], str(file.id))

    def test_import_transfers_knowledge_and_temporary_sources_without_copying_bytes(self):
        for source_type in (
            FileSourceType.KNOWLEDGE,
            FileSourceType.TEMPORARY_30_MINUTE,
            FileSourceType.TEMPORARY_120_MINUTE,
            FileSourceType.TEMPORARY_1_DAY,
        ):
            with self.subTest(source_type=source_type):
                file = self.source(source_type)
                with patch.object(File, "get_bytes") as read, patch.object(File, "save") as upload:
                    documents, _, _ = self.node.save([self.document_input(file)], None)
                self.assert_owned_by(file, documents[0])
                self.assertEqual(File.objects.filter(sha256_hash=file.sha256_hash).count(), 1)
                read.assert_not_called()
                upload.assert_not_called()

    def test_one_source_split_into_two_documents_has_independent_file_references(self):
        file = self.source()

        documents, _, _ = self.node.save(
            [self.document_input(file, "first"), self.document_input(file, "second")], None
        )

        self.assert_owned_by(file, documents[0])
        second_file = File.objects.get(id=documents[1].meta["source_file_id"])
        self.assert_owned_by(second_file, documents[1])
        self.assertNotEqual(file.id, second_file.id)
        self.assertEqual(second_file.meta["seaweedfs_key"], f"files/{file.id}")
        self.assertFalse(File.objects.filter(source_type=FileSourceType.KNOWLEDGE).exists())

    def test_failed_save_restores_upload_ownership(self):
        file = self.source()
        with (
            patch(
                "application.workflow.nodes.knowledge_write_node.knowledge_write_node.sync_paragraph_assets",
                side_effect=RuntimeError("save failed"),
            ),
            self.assertRaisesRegex(RuntimeError, "save failed"),
        ):
            self.node.save([self.document_input(file, "first"), self.document_input(file, "second")], None)

        file.refresh_from_db()
        self.assertEqual((file.source_type, file.source_id), (FileSourceType.KNOWLEDGE, str(self.knowledge.id)))
        self.assertEqual(File.objects.filter(sha256_hash=file.sha256_hash).count(), 1)
        self.assertFalse(Document.objects.filter(knowledge=self.knowledge).exists())

    def test_incremental_merge_keeps_source_on_the_stable_document(self):
        retained = Document.objects.create(
            knowledge=self.knowledge,
            name="old",
            char_length=0,
            type=KnowledgeType.WORKFLOW,
            meta={"source_scope": "lark", "token": "remote-document"},
        )
        run = WorkflowDocumentSyncRun(
            id=self.parameters["knowledge_action_id"], knowledge_id=self.knowledge.id, create_time=timezone.now()
        )
        file = self.source()
        documents, _, _ = self.node.save([self.document_input(file)], None)

        result = merge_workflow_incremental_snapshot(run, {"source_scope": "lark"}, retained.id)

        self.assertEqual(result["failed_count"], 0)
        self.assert_owned_by(file, retained)
        self.assertFalse(Document.objects.filter(id=documents[0].id).exists())
        self.assertEqual(File.objects.filter(sha256_hash=file.sha256_hash).count(), 1)

    def test_failed_workflow_only_removes_its_output_and_preserves_other_document_file(self):
        file = self.source()
        retained, _, _ = self.node.save([self.document_input(file)], None)
        self.parameters["knowledge_action_id"] = str(uuid4())
        run = WorkflowDocumentSyncRun(
            id=self.parameters["knowledge_action_id"], knowledge_id=self.knowledge.id, create_time=timezone.now()
        )
        output, _, _ = self.node.save([self.document_input(file)], None)
        output_file_id = output[0].meta["source_file_id"]

        result = finalize_workflow_complete_snapshot(run, False, {"source_scope": "lark"})

        self.assertEqual(result["failed_count"], 1)
        self.assert_owned_by(file, retained[0])
        self.assertFalse(File.objects.filter(id=output_file_id).exists())
        self.assertFalse(Document.objects.filter(id=output[0].id).exists())

    def test_unrelated_knowledge_files_are_preserved(self):
        file, unused = self.source(), self.source()

        self.node.save([self.document_input(file)], None)

        unused.refresh_from_db()
        self.assertEqual((unused.source_type, unused.source_id), (FileSourceType.KNOWLEDGE, str(self.knowledge.id)))
