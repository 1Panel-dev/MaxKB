"""Missing embedding models fail vectorization without rejecting document imports."""

from unittest.mock import patch
from uuid import uuid4

from common.exception.app_exception import AppApiException
from django.test import TestCase
from knowledge.models import Document, File, FileSourceType, Knowledge, Paragraph, State, Status, TaskType
from knowledge.serializers.document import DocumentSerializers
from knowledge.task.embedding import embedding_by_document
from models_provider.models import Model


class MissingEmbeddingModelImportTests(TestCase):
    def setUp(self):
        self.knowledge = Knowledge.objects.create(name="Missing embedding model", desc="")
        self.scope = {"workspace_id": "default", "knowledge_id": str(self.knowledge.id)}
        self.delay = self.enterContext(patch("knowledge.serializers.document.embedding_by_document.delay"))

    def assert_imported(self, result, content):
        document = Document.objects.get(id=result["id"])
        self.assertEqual(document.knowledge_id, self.knowledge.id)
        self.assertEqual(document.paragraph_set.get().content, content)
        self.assertEqual(Status(document.status)[TaskType.EMBEDDING], State.PENDING)
        return document

    def test_single_document_is_saved_without_an_embedding_model(self):
        with self.captureOnCommitCallbacks(execute=True):
            result = DocumentSerializers.Create(data=self.scope).save(
                {"name": "Manual document", "paragraphs": [{"content": "Saved paragraph"}]}
            )
            self.delay.assert_not_called()

        document = self.assert_imported(result, "Saved paragraph")
        self.assertEqual(self.delay.call_args.args[:2], (str(document.id), None))

    def test_batch_import_saves_all_documents_with_a_deleted_model_reference(self):
        missing_model_id = uuid4()
        Knowledge.objects.filter(id=self.knowledge.id).update(embedding_model_id=missing_model_id)
        inputs = [{"name": name, "paragraphs": [{"content": name}]} for name in ("First document", "Second document")]

        with self.captureOnCommitCallbacks(execute=True):
            results = DocumentSerializers.Batch(data=self.scope).batch_save(inputs)
            self.delay.assert_not_called()

        self.assertEqual(len(results), 2)
        for result in results:
            self.assert_imported(result, result["name"])
        self.assertEqual(self.delay.call_count, 2)
        self.assertEqual(
            {call.args[0] for call in self.delay.call_args_list}, {str(result["id"]) for result in results}
        )
        self.assertTrue(all(call.args[1] == missing_model_id for call in self.delay.call_args_list))

    def test_text_import_after_model_deletion_preserves_document_and_source(self):
        model = Model.objects.create(
            name="Deleted model", model_type="EMBEDDING", model_name="test", provider="test", credential=""
        )
        Knowledge.objects.filter(id=self.knowledge.id).update(embedding_model=model)
        model.delete()
        self.knowledge.refresh_from_db()
        self.assertIsNone(self.knowledge.embedding_model_id)
        source = File(
            file_name="guide.txt",
            file_size=15,
            source_type=FileSourceType.KNOWLEDGE,
            source_id=str(self.knowledge.id),
            storage_type="pg",
        )
        File.objects.bulk_create([source])

        with (
            patch.object(File, "get_bytes", return_value=b"Import survives"),
            self.captureOnCommitCallbacks(execute=True),
        ):
            results = DocumentSerializers.Create(data=self.scope).save_text({"file_id_list": [str(source.id)]})
            self.delay.assert_not_called()

        self.assertEqual(len(results), 1)
        document = self.assert_imported(results[0], "Import survives")
        source.refresh_from_db()
        self.assertEqual((source.source_type, source.source_id), (FileSourceType.DOCUMENT, str(document.id)))
        self.assertEqual(document.meta["source_file_id"], str(source.id))
        self.assertEqual(self.delay.call_args.args[:2], (str(document.id), None))

    def test_worker_marks_document_failed_when_model_is_missing(self):
        with (
            patch("knowledge.task.embedding.maxkb_logger.error"),
            patch("knowledge.task.embedding.ListenerManagement.embedding_by_document") as embed,
        ):
            for model_id in (None, uuid4()):
                with self.subTest(model_id=model_id):
                    document = Document.objects.create(
                        knowledge=self.knowledge, name="Imported", char_length=16, status="2nn0"
                    )
                    paragraph = Paragraph.objects.create(
                        knowledge=self.knowledge, document=document, content="Retained content"
                    )

                    with self.assertRaises(AppApiException):
                        embedding_by_document.run(str(document.id), model_id)

                    document.refresh_from_db()
                    paragraph.refresh_from_db()
                    self.assertEqual(document.status, "2nn3")
                    self.assertEqual(paragraph.content, "Retained content")
            embed.assert_not_called()

    def test_existing_model_still_reaches_embedding_processing(self):
        model = Model.objects.create(
            name="Existing model", model_type="EMBEDDING", model_name="test", provider="test", credential=""
        )
        Knowledge.objects.filter(id=self.knowledge.id).update(embedding_model=model)
        with self.captureOnCommitCallbacks(execute=True):
            result = DocumentSerializers.Create(data=self.scope).save(
                {"name": "Normal document", "paragraphs": [{"content": "Normal content"}]}
            )
        document = self.assert_imported(result, "Normal content")
        self.assertEqual(self.delay.call_args.args[:2], (str(document.id), model.id))

        with (
            patch("knowledge.task.embedding.ModelManage.get_model") as get_model,
            patch("knowledge.task.embedding.ListenerManagement.embedding_by_document") as embed,
        ):
            embedding_by_document.run(*self.delay.call_args.args)
        embed.assert_called_once_with(str(document.id), get_model.return_value, self.delay.call_args.args[2])
