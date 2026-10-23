"""Imported source files belong to documents once the save transaction succeeds."""

from io import BytesIO
from unittest.mock import patch
from uuid import uuid4

from django.test import TestCase
from PIL import Image

from knowledge.models import Document, File, FileSourceType, Knowledge
from knowledge.serializers.document import DocumentSerializers
from knowledge.services.document_cleanup import delete_document_data
from knowledge.services.image_documents import ImageDocumentService


class DocumentSourceFileOwnershipTests(TestCase):
    def setUp(self):
        self.knowledge = Knowledge.objects.create(name="File ownership", desc="", workspace_id="default")
        self.scope = {"workspace_id": "default", "knowledge_id": str(self.knowledge.id), "user_id": str(uuid4())}
        self.batch = DocumentSerializers.Batch(data=self.scope)
        self.creator = DocumentSerializers.Create(data=self.scope)
        # These tests exercise persistence without scheduling embedding jobs.
        self.enterContext(patch.object(DocumentSerializers.Operate, "refresh"))

    def source(self, source_type=FileSourceType.KNOWLEDGE, **kwargs):
        file = File(
            file_name="guide.pdf",
            file_size=12,
            sha256_hash=str(uuid4()),
            source_type=source_type,
            source_id=str(self.knowledge.id) if source_type == FileSourceType.KNOWLEDGE else source_type,
            **{
                "storage_type": "seaweedfs",
                "meta": {"user_id": self.scope["user_id"], "seaweedfs_key": "files/original"},
                **kwargs,
            },
        )
        File.objects.bulk_create([file])
        return file

    @staticmethod
    def document_input(file, name="guide.pdf"):
        return {"name": name, "source_file_id": str(file.id), "paragraphs": [{"content": "PDF paragraph"}]}

    def assert_document_owns_file(self, document, file):
        file.refresh_from_db()
        self.assertEqual(file.source_type, FileSourceType.DOCUMENT)
        self.assertEqual(file.source_id, str(document.id))
        self.assertEqual(document.meta["source_file_id"], str(file.id))

    def test_preview_save_transfers_the_original_file_without_copying_stored_bytes(self):
        for storage_type, loid in (("seaweedfs", None), ("pg", 123)):
            with self.subTest(storage_type=storage_type):
                source = self.source(storage_type=storage_type, loid=loid)
                with patch.object(File, "get_bytes") as read, patch.object(File, "save") as upload:
                    result = self.batch.batch_save([self.document_input(source)])
                document = Document.objects.get(id=result[0]["id"])
                self.assert_document_owns_file(document, source)
                self.assertEqual(File.objects.filter(sha256_hash=source.sha256_hash).count(), 1)
                self.assertEqual((source.storage_type, source.loid), (storage_type, loid))
                self.assertEqual(source.meta["seaweedfs_key"], "files/original")
                read.assert_not_called()
                upload.assert_not_called()
                with patch("knowledge.serializers.document.FileSerializer.Operate") as download:
                    DocumentSerializers.Operate(
                        data={**self.scope, "document_id": str(document.id)}
                    ).download_source_file()
                download.assert_called_once_with(data={"id": source.id})

    def test_direct_text_import_does_not_restore_knowledge_or_temporary_ownership(self):
        for source_type in (
            FileSourceType.KNOWLEDGE,
            FileSourceType.TEMPORARY_30_MINUTE,
            FileSourceType.TEMPORARY_120_MINUTE,
            FileSourceType.TEMPORARY_1_DAY,
        ):
            with self.subTest(source_type=source_type):
                source = self.source(source_type)
                File.objects.filter(id=source.id).update(file_name="guide.txt")
                with patch.object(File, "get_bytes", return_value=b"text content"):
                    result = self.creator.save_text({"file_id_list": [str(source.id)]})
                document = Document.objects.get(id=result[0]["id"])
                self.assert_document_owns_file(document, source)
                self.assertEqual(File.objects.filter(sha256_hash=source.sha256_hash).count(), 1)

    def test_text_preview_remains_temporary_until_document_save(self):
        source = self.source(FileSourceType.TEMPORARY_120_MINUTE)
        File.objects.filter(id=source.id).update(file_name="guide.txt")
        splitter = DocumentSerializers.Split(data=self.scope)
        with patch.object(File, "get_bytes", return_value=b"preview text"):
            previews = splitter.parse_by_file_ids({"file_id_list": [str(source.id)]})

        source.refresh_from_db()
        self.assertEqual(source.source_type, FileSourceType.TEMPORARY_120_MINUTE)
        self.assertEqual(source.source_id, FileSourceType.TEMPORARY_120_MINUTE)
        self.assertFalse(Document.objects.filter(knowledge_id=self.knowledge.id).exists())

        preview = previews[0]
        result = self.batch.batch_save([{**preview, "paragraphs": preview["content"]}])
        self.assert_document_owns_file(Document.objects.get(id=result[0]["id"]), source)

    def test_table_and_qa_import_transfer_the_uploaded_file_to_the_document(self):
        for method, content in (
            ("save_table_by_file_ids", b"name,value\nexample,1\n"),
            ("save_qa_by_file_ids", b"title,content,questions\nFAQ,Answer,Question\n"),
        ):
            with self.subTest(method=method):
                source = self.source(FileSourceType.TEMPORARY_120_MINUTE)
                File.objects.filter(id=source.id).update(file_name="guide.csv")
                with patch.object(File, "get_bytes", return_value=content):
                    result = getattr(self.creator, method)({"file_id_list": [str(source.id)]})
                document = Document.objects.get(id=result[0]["id"])
                self.assert_document_owns_file(document, source)

    def test_image_preview_binds_only_after_successful_import(self):
        source = self.source(FileSourceType.TEMPORARY_120_MINUTE)
        File.objects.filter(id=source.id).update(file_name="preview.png")
        image = BytesIO()
        Image.new("RGB", (1, 1)).save(image, format="PNG")
        service = ImageDocumentService("default", str(self.knowledge.id), self.scope["user_id"])
        with patch.object(File, "get_bytes", return_value=image.getvalue()):
            previews = service.generate_previews_by_file_ids([source.id])

        source.refresh_from_db()
        self.assertEqual(source.source_type, FileSourceType.TEMPORARY_120_MINUTE)
        self.assertEqual(source.source_id, FileSourceType.TEMPORARY_120_MINUTE)
        self.assertNotIn("knowledge_id", source.meta)
        self.assertFalse(Document.objects.filter(knowledge_id=self.knowledge.id).exists())

        with (
            patch(
                "knowledge.services.image_documents.ParagraphAsset.objects.create",
                side_effect=RuntimeError("save failed"),
            ),
            self.assertRaisesRegex(RuntimeError, "save failed"),
        ):
            service.import_previews([previews[0]["source_file_id"]])

        source.refresh_from_db()
        self.assertEqual(source.source_type, FileSourceType.TEMPORARY_120_MINUTE)
        self.assertFalse(source.meta["image_preview"]["imported"])
        self.assertFalse(Document.objects.filter(knowledge_id=self.knowledge.id).exists())

        document_ids = service.import_previews([previews[0]["source_file_id"]])
        self.assert_document_owns_file(Document.objects.get(id=document_ids[0]), source)

    def test_shared_upload_gives_each_document_its_own_source_reference(self):
        source = self.source(meta={"user_id": self.scope["user_id"]})
        with patch.object(File, "get_bytes") as read, patch.object(File, "save") as upload:
            self.batch.batch_save([self.document_input(source, "first"), self.document_input(source, "second")])
        first = Document.objects.get(name="first")
        second = Document.objects.get(name="second")
        self.assert_document_owns_file(first, source)
        second_source = File.objects.get(id=second.meta["source_file_id"])
        self.assert_document_owns_file(second, second_source)
        self.assertNotEqual(source.id, second_source.id)
        self.assertEqual(second_source.meta["seaweedfs_key"], f"files/{source.id}")
        self.assertEqual(second_source.sha256_hash, source.sha256_hash)
        self.assertEqual(File.objects.filter(sha256_hash=source.sha256_hash).count(), 2)
        self.assertFalse(File.objects.filter(source_type=FileSourceType.KNOWLEDGE).exists())
        read.assert_not_called()
        upload.assert_not_called()

        with patch("knowledge.services.document_cleanup.delete_embedding_by_document_list"):
            delete_document_data([str(second.id)])
        self.assertTrue(File.objects.filter(id=source.id, source_id=str(first.id)).exists())
        self.assertFalse(File.objects.filter(id=second_source.id).exists())

    def test_failed_save_restores_the_previous_owner_and_removes_copied_records(self):
        for source_type in (FileSourceType.KNOWLEDGE, FileSourceType.TEMPORARY_120_MINUTE):
            with self.subTest(source_type=source_type):
                source = self.source(source_type)
                original_owner = source.source_id
                with (
                    patch(
                        "knowledge.serializers.document.sync_paragraph_assets", side_effect=RuntimeError("save failed")
                    ),
                    self.assertRaisesRegex(RuntimeError, "save failed"),
                ):
                    self.batch.batch_save([self.document_input(source, "first"), self.document_input(source, "second")])
                source.refresh_from_db()
                self.assertEqual((source.source_type, source.source_id), (source_type, original_owner))
                self.assertEqual(File.objects.filter(sha256_hash=source.sha256_hash).count(), 1)
                self.assertFalse(Document.objects.filter(knowledge_id=self.knowledge.id).exists())

    def test_saving_one_upload_leaves_other_knowledge_files_unchanged(self):
        source = self.source()
        unrelated = self.source()

        self.batch.batch_save([self.document_input(source)])

        unrelated.refresh_from_db()
        self.assertEqual(unrelated.source_type, FileSourceType.KNOWLEDGE)
        self.assertEqual(unrelated.source_id, str(self.knowledge.id))
