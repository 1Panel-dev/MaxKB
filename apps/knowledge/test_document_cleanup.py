"""Batch deletion must remove attachments, including compatible V2 PG objects."""

from io import BytesIO
from unittest.mock import MagicMock, patch
from uuid import uuid4
from zipfile import ZIP_DEFLATED, ZipFile

from django.db import connection
from django.test import SimpleTestCase, TestCase

from common.exception.app_exception import AppApiException
from common.utils.common import get_sha256_hash
from knowledge.models import Document, File, FileSourceType, Knowledge, Paragraph, ParagraphAsset
from knowledge.serializers.document import DocumentSerializers


class BatchDocumentCleanupTests(SimpleTestCase):
    @patch("knowledge.serializers.document.delete_document_data")
    @patch("knowledge.serializers.document.BatchSerializer")
    def test_deletes_only_validated_documents_using_the_complete_cleanup(self, batch_serializer, cleanup):
        document_id = str(uuid4())
        serializer = MagicMock()
        serializer.validate_document_ids.return_value = [document_id]
        request = {"id_list": [document_id]}

        result = DocumentSerializers.Batch.batch_delete.__wrapped__(serializer, request)

        self.assertTrue(result)
        serializer.is_valid.assert_called_once_with(raise_exception=True)
        serializer.validate_document_ids.assert_called_once_with(request)
        cleanup.assert_called_once_with([document_id])

    @patch("knowledge.serializers.document.delete_document_data")
    @patch("knowledge.serializers.document.BatchSerializer")
    def test_invalid_document_scope_does_not_delete_files(self, batch_serializer, cleanup):
        serializer = MagicMock()
        serializer.validate_document_ids.side_effect = AppApiException(500, "document belongs to another knowledge")

        with self.assertRaises(AppApiException):
            DocumentSerializers.Batch.batch_delete.__wrapped__(serializer, {"id_list": [str(uuid4())]})

        cleanup.assert_not_called()


class BatchDocumentCleanupDatabaseTests(TestCase):
    def create_file(self, document, name, content):
        # Construct a V2 fixture directly; V3 File.save no longer writes PG objects.
        archive = BytesIO()
        with ZipFile(archive, "w", ZIP_DEFLATED) as zipped:
            zipped.writestr(name, content)
        compressed = archive.getvalue()
        file_hash = get_sha256_hash(content)
        shared = File.objects.filter(storage_type="pg", sha256_hash=file_hash).first()
        if shared:
            loid = shared.loid
        else:
            with connection.cursor() as cursor:
                cursor.execute("SELECT lo_from_bytea(0, %s)", [compressed])
                loid = cursor.fetchone()[0]
        file = File(
            file_name=name,
            source_type=FileSourceType.DOCUMENT,
            source_id=str(document.id),
            storage_type="pg",
            loid=loid,
            sha256_hash=file_hash,
            file_size=len(compressed),
            meta={"original_size": len(content)},
        )
        File.objects.bulk_create([file])
        return file

    def large_object_exists(self, loid):
        with connection.cursor() as cursor:
            cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_largeobject_metadata WHERE oid=%s)", [loid])
            return cursor.fetchone()[0]

    def test_batch_deletion_cleans_images_and_preserves_shared_pg_bytes(self):
        knowledge = Knowledge.objects.create(name="cleanup test", desc="")
        selected = Document.objects.create(knowledge=knowledge, name="selected", char_length=0)
        retained = Document.objects.create(knowledge=knowledge, name="retained", char_length=0)
        unique_bytes = uuid4().bytes
        source = self.create_file(selected, "guide.txt", b"source" + unique_bytes)
        image = self.create_file(selected, "image.png", b"shared image" + unique_bytes)
        retained_image = self.create_file(retained, "image.png", b"shared image" + unique_bytes)
        private_image = self.create_file(selected, "private.png", b"private image" + unique_bytes)
        selected.meta = {"source_file_id": str(source.id)}
        selected.save(update_fields=["meta"])
        paragraph = Paragraph.objects.create(
            knowledge=knowledge,
            document=selected,
            content=f"![image](/admin/oss/file/{image.id})",
        )
        ParagraphAsset.objects.create(knowledge=knowledge, document=selected, paragraph=paragraph, file=image)
        self.assertEqual(image.loid, retained_image.loid)
        serializer = DocumentSerializers.Batch(data={"knowledge_id": str(knowledge.id)})

        with patch("knowledge.services.document_cleanup.delete_embedding_by_document_list"):
            DocumentSerializers.Batch.batch_delete.__wrapped__(
                serializer, {"id_list": [str(selected.id)]}, with_valid=False
            )

        self.assertFalse(Document.objects.filter(id=selected.id).exists())
        self.assertFalse(File.objects.filter(source_type=FileSourceType.DOCUMENT, source_id=str(selected.id)).exists())
        self.assertFalse(Paragraph.objects.filter(document_id=selected.id).exists())
        self.assertFalse(ParagraphAsset.objects.filter(document_id=selected.id).exists())
        self.assertTrue(Document.objects.filter(id=retained.id).exists())
        self.assertTrue(File.objects.filter(id=retained_image.id).exists())
        self.assertFalse(self.large_object_exists(source.loid))
        self.assertFalse(self.large_object_exists(private_image.loid))
        self.assertTrue(self.large_object_exists(retained_image.loid))
        self.assertEqual(retained_image.get_bytes(), b"shared image" + unique_bytes)
