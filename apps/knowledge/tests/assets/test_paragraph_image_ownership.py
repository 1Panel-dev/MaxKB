"""All importers share paragraph image ownership and safe source replacement."""

from unittest.mock import patch

import uuid_utils.compat as uuid
from django.db import transaction
from django.test import TestCase
from django.utils import timezone
from users.models import User

from knowledge.models import (
    ContentOrigin,
    Document,
    DocumentResourceType,
    File,
    FileSourceType,
    Knowledge,
    KnowledgeType,
    Paragraph,
    ParagraphAsset,
)
from knowledge.services.document_cleanup import reset_document_content
from knowledge.services.document_strategy import normalize_document_strategy
from knowledge.services.incremental_sync import IncrementalDocumentSync
from knowledge.services.paragraph_assets import sync_paragraph_assets
from knowledge.services.paragraph_files import bind_paragraph_image_files, preserve_incoming_image_files
from knowledge.services.workflow_sync import WorkflowDocumentSyncRun, merge_workflow_incremental_snapshot


class ParagraphImageOwnershipTests(TestCase):
    def setUp(self):
        self.knowledge = Knowledge.objects.create(name="Images", desc="")
        self.document = Document.objects.create(
            knowledge=self.knowledge, name="Document", char_length=0, doc_strategy=normalize_document_strategy(None)
        )
        self.file = File(
            source_type=FileSourceType.KNOWLEDGE,
            source_id=str(self.knowledge.id),
            storage_type="seaweedfs",
            file_name="inline.png",
            sha256_hash="same-image",
            meta={"seaweedfs_key": "files/shared"},
        )
        File.objects.bulk_create([self.file])
        self.content = f"![inline](./oss/file/{self.file.id})"

    def create_paragraph(self):
        return Paragraph.objects.create(
            knowledge=self.knowledge,
            document=self.document,
            content=self.content,
            origin=ContentOrigin.SYNCED,
        )

    def test_every_knowledge_type_binds_parser_images_without_web_metadata(self):
        for knowledge_type in KnowledgeType.values:
            with self.subTest(knowledge_type=knowledge_type):
                self.knowledge.type = knowledge_type
                self.knowledge.save(update_fields=["type"])
                self.document.type = knowledge_type
                self.document.save(update_fields=["type"])
                paragraph = self.create_paragraph()
                File.objects.filter(id=self.file.id).update(
                    source_type=FileSourceType.KNOWLEDGE, source_id=str(self.knowledge.id)
                )

                first = sync_paragraph_assets([paragraph])
                second = sync_paragraph_assets([paragraph])

                self.file.refresh_from_db()
                self.assertEqual(self.file.source_type, FileSourceType.PARAGRAPH)
                self.assertEqual(self.file.source_id, str(paragraph.id))
                self.assertEqual([asset.id for asset in first], [asset.id for asset in second])
                self.assertEqual(first[0].file_id, self.file.id)
                self.assertEqual(self.file.meta, {"seaweedfs_key": "files/shared"})

    def test_legacy_document_image_is_rebound_but_source_file_is_not(self):
        paragraph = self.create_paragraph()
        File.objects.filter(id=self.file.id).update(
            source_type=FileSourceType.DOCUMENT, source_id=str(self.document.id)
        )
        self.document.meta = {"source_file_id": str(self.file.id)}
        self.document.save(update_fields=["meta"])

        assets = sync_paragraph_assets([paragraph])
        self.file.refresh_from_db()
        self.assertEqual(self.file.source_type, FileSourceType.DOCUMENT)

        self.document.meta = {}
        self.document.save(update_fields=["meta"])
        self.assertEqual(bind_paragraph_image_files(assets), 1)
        self.file.refresh_from_db()
        self.assertEqual(self.file.source_id, str(paragraph.id))
        self.assertEqual(self.file.source_type, FileSourceType.PARAGRAPH)

    def test_standalone_image_file_retains_document_lifecycle(self):
        self.document.resource_type = DocumentResourceType.IMAGE
        self.document.save(update_fields=["resource_type"])
        paragraph = self.create_paragraph()
        File.objects.filter(id=self.file.id).update(
            source_type=FileSourceType.DOCUMENT, source_id=str(self.document.id)
        )
        asset = ParagraphAsset.objects.create(
            knowledge=self.knowledge,
            document=self.document,
            paragraph=paragraph,
            file=self.file,
            source_asset_key="standalone:image",
        )

        self.assertEqual(bind_paragraph_image_files([asset]), 0)
        self.file.refresh_from_db()
        self.assertEqual(self.file.source_type, FileSourceType.DOCUMENT)

    def test_saved_paragraph_promotes_its_uploaders_preview_image(self):
        user = User.objects.create(username="preview-owner", password="unused")
        self.document.user = user
        self.document.save(update_fields=["user"])
        File.objects.filter(id=self.file.id).update(
            source_type=FileSourceType.TEMPORARY_120_MINUTE,
            source_id=FileSourceType.TEMPORARY_120_MINUTE,
            meta={"preview_knowledge_id": str(self.knowledge.id), "user_id": str(user.id)},
        )
        paragraph = self.create_paragraph()

        sync_paragraph_assets([paragraph])

        self.file.refresh_from_db()
        self.assertEqual(self.file.source_type, FileSourceType.PARAGRAPH)
        self.assertEqual(self.file.source_id, str(paragraph.id))

    def test_unrelated_temporary_images_are_not_promoted(self):
        user = User.objects.create(username="preview-owner", password="unused")
        self.document.user = user
        self.document.save(update_fields=["user"])
        for knowledge_id, user_id in (
            (str(uuid.uuid7()), str(user.id)),
            (str(self.knowledge.id), str(uuid.uuid7())),
            (None, str(user.id)),
        ):
            with self.subTest(knowledge_id=knowledge_id, user_id=user_id):
                File.objects.filter(id=self.file.id).update(
                    source_type=FileSourceType.TEMPORARY_120_MINUTE,
                    source_id=FileSourceType.TEMPORARY_120_MINUTE,
                    meta={"preview_knowledge_id": knowledge_id, "user_id": user_id},
                )

                sync_paragraph_assets([self.create_paragraph()])

                self.file.refresh_from_db()
                self.assertEqual(self.file.source_type, FileSourceType.TEMPORARY_120_MINUTE)

    def test_source_authoritative_rechunk_preserves_reused_image(self):
        service = IncrementalDocumentSync(self.document, source_authoritative=True)
        first = service.merge([{"title": "Old heading", "content": self.content}])
        sync_paragraph_assets(Paragraph.objects.filter(id__in=first.reembed_ids))

        result = service.merge([{"title": "New heading", "content": self.content}])

        self.assertEqual(result.deleted_ids, first.created_ids)
        self.assertTrue(File.objects.filter(id=self.file.id).exists())
        assets = sync_paragraph_assets(Paragraph.objects.filter(id__in=result.reembed_ids))
        self.file.refresh_from_db()
        self.assertEqual(self.file.source_type, FileSourceType.PARAGRAPH)
        self.assertEqual(self.file.source_id, result.created_ids[0])
        self.assertEqual(assets[0].file_id, self.file.id)

    def test_replace_content_stages_reused_image_until_new_paragraphs_exist(self):
        paragraph = self.create_paragraph()
        sync_paragraph_assets([paragraph])
        incoming = [{"title": "Replacement", "content": self.content}]

        with transaction.atomic(), patch("knowledge.services.document_cleanup.delete_embedding_by_document_list"):
            preserve_incoming_image_files([paragraph.id], self.knowledge.id, incoming)
            reset_document_content([self.document.id])
            self.assertTrue(File.objects.filter(id=self.file.id).exists())
            self.document.refresh_from_db()
            result = IncrementalDocumentSync(self.document, source_authoritative=True).merge(incoming)
            sync_paragraph_assets(Paragraph.objects.filter(id__in=result.reembed_ids))

        self.file.refresh_from_db()
        self.assertEqual(self.file.source_type, FileSourceType.PARAGRAPH)
        self.assertEqual(self.file.source_id, result.created_ids[0])

    def test_failed_replacement_restores_image_owner_and_assets(self):
        paragraph = self.create_paragraph()
        sync_paragraph_assets([paragraph])

        with self.assertRaises(RuntimeError), transaction.atomic():
            preserve_incoming_image_files([paragraph.id], self.knowledge.id, [{"content": self.content}])
            paragraph.delete()
            raise RuntimeError("replacement failed")

        self.file.refresh_from_db()
        self.assertEqual(self.file.source_type, FileSourceType.PARAGRAPH)
        self.assertTrue(ParagraphAsset.objects.filter(file=self.file, paragraph_id=self.file.source_id).exists())

    def test_staging_does_not_change_non_image_attachments(self):
        paragraph = self.create_paragraph()
        File.objects.filter(id=self.file.id).update(source_type=FileSourceType.PARAGRAPH, source_id=str(paragraph.id))

        preserve_incoming_image_files(
            [paragraph.id], self.knowledge.id, [{"content": f"[attachment](./oss/file/{self.file.id})"}]
        )

        self.file.refresh_from_db()
        self.assertEqual(self.file.source_type, FileSourceType.PARAGRAPH)
        self.assertEqual(self.file.source_id, str(paragraph.id))

    def workflow_snapshot(self):
        self.document.type = KnowledgeType.WORKFLOW
        self.document.meta = {"source_scope": "scope", "source_key": "remote-document"}
        self.document.save(update_fields=["type", "meta"])
        run = WorkflowDocumentSyncRun(id=uuid.uuid7(), knowledge_id=self.knowledge.id, create_time=timezone.now())
        temporary = Document.objects.create(
            knowledge=self.knowledge,
            name=self.document.name,
            char_length=0,
            type=KnowledgeType.WORKFLOW,
            doc_strategy=self.document.doc_strategy,
            meta={**self.document.meta, "workflow_action_id": str(run.id)},
        )
        paragraph = Paragraph.objects.create(
            knowledge=self.knowledge, document=temporary, content=self.content, origin=ContentOrigin.SYNCED
        )
        sync_paragraph_assets([paragraph])
        return run, temporary, paragraph

    def test_workflow_snapshot_deletion_transfers_temporary_image_owner(self):
        run, temporary, temporary_paragraph = self.workflow_snapshot()
        self.file.refresh_from_db()
        self.assertEqual(self.file.source_id, str(temporary_paragraph.id))

        result = merge_workflow_incremental_snapshot(run, {"source_scope": "scope"})

        self.assertEqual(result["failed_count"], 0)
        self.assertEqual(result["synced_count"], 1)
        self.assertFalse(Document.objects.filter(id=temporary.id).exists())
        asset = ParagraphAsset.objects.get(document=self.document)
        self.file.refresh_from_db()
        self.assertEqual(self.file.source_type, FileSourceType.PARAGRAPH)
        self.assertEqual(self.file.source_id, str(asset.paragraph_id))
        self.assertEqual(asset.file_id, self.file.id)

    def test_unchanged_workflow_repairs_legacy_document_image_owner(self):
        result = IncrementalDocumentSync(self.document).merge([{"content": self.content}])
        assets = sync_paragraph_assets(Paragraph.objects.filter(id__in=result.reembed_ids))
        run, temporary, _ = self.workflow_snapshot()
        File.objects.filter(id=self.file.id).update(
            source_type=FileSourceType.DOCUMENT, source_id=str(self.document.id)
        )

        result = merge_workflow_incremental_snapshot(run, {"source_scope": "scope"})

        self.assertEqual(result["failed_count"], 0)
        self.assertEqual(result["skipped_count"], 1)
        self.assertFalse(Document.objects.filter(id=temporary.id).exists())
        self.file.refresh_from_db()
        self.assertEqual(self.file.source_type, FileSourceType.PARAGRAPH)
        self.assertEqual(self.file.source_id, str(assets[0].paragraph_id))

    def test_unchanged_workflow_restores_missing_legacy_assets_before_temporary_cleanup(self):
        result = IncrementalDocumentSync(self.document).merge([{"content": self.content}])
        old_paragraph_id = result.created_ids[0]
        File.objects.filter(id=self.file.id).update(
            source_type=FileSourceType.DOCUMENT, source_id=str(self.document.id)
        )
        run, temporary, _ = self.workflow_snapshot()

        result = merge_workflow_incremental_snapshot(run, {"source_scope": "scope"})

        self.assertEqual(result["failed_count"], 0)
        self.assertEqual(result["skipped_count"], 1)
        self.assertFalse(Document.objects.filter(id=temporary.id).exists())
        self.file.refresh_from_db()
        self.assertEqual(self.file.source_type, FileSourceType.PARAGRAPH)
        self.assertEqual(self.file.source_id, old_paragraph_id)
        self.assertTrue(ParagraphAsset.objects.filter(paragraph_id=old_paragraph_id, file=self.file).exists())
