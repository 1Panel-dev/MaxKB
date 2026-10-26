"""Restart recovery releases orphaned locks without replaying an old embedding job."""

from unittest.mock import patch

from celery_once import AlreadyQueued, QueueOnce
from common.event import update_document_status_sql
from common.event.listener_manage import ListenerManagement
from common.exception.app_exception import AppApiException
from django.db import connection
from django.test import SimpleTestCase, TestCase
from knowledge.models import Document, Knowledge, Paragraph, State
from knowledge.serializers.document import DocumentSerializers
from knowledge.services.embedding_recovery import (
    EMBEDDING_GENERATION,
    _clear_embedding_locks,
    recover_interrupted_embeddings,
)
from knowledge.task.embedding import embedding_by_document
from knowledge.tasks import recover_interrupted_document_embeddings
from models_provider.models import Model


class EmbeddingRestartSignalTests(SimpleTestCase):
    @patch("knowledge.services.embedding_recovery.recover_interrupted_embeddings")
    @patch("knowledge.tasks.celery_app.control.inspect")
    def test_only_first_worker_recovers_embeddings(self, inspect, recover):
        for queues, expected in ((None, 1), ({"peer": [{"name": "celery"}]}, 0)):
            with self.subTest(queues=queues):
                recover.reset_mock()
                recover.return_value = 0
                inspect.return_value.active_queues.return_value = queues
                recover_interrupted_document_embeddings()
                self.assertEqual(recover.call_count, expected)

    @patch("knowledge.services.embedding_recovery.get_redis_connection")
    @patch("knowledge.services.embedding_recovery.import_backend")
    def test_clears_only_the_two_locks_for_the_document(self, backend, redis):
        _clear_embedding_locks("document")
        backend.return_value.clear_lock.assert_called_once_with("qo_celery:embedding_by_document_document_id-document")
        redis.return_value.delete.assert_called_once_with("embedding:document")


class EmbeddingRestartTests(TestCase):
    def setUp(self):
        model = Model.objects.create(
            name="Restart test model", model_type="EMBEDDING", model_name="test", provider="test", credential=""
        )
        self.knowledge = Knowledge.objects.create(name="Restart test", desc="", embedding_model=model)
        self.clear_locks = self.enterContext(patch("knowledge.services.embedding_recovery._clear_embedding_locks"))
        self.delay = self.enterContext(patch("knowledge.serializers.document.embedding_by_document.delay"))

    def create_document(self, state, paragraph_states=()):
        document = Document.objects.create(
            knowledge=self.knowledge,
            name="Test document",
            char_length=3,
            status="2nn" + state.value,
            meta={"source_url": "https://example.com"},
        )
        for paragraph_state in paragraph_states:
            Paragraph.objects.create(
                knowledge=self.knowledge, document=document, content="content", status="2nn" + paragraph_state.value
            )
        ListenerManagement.get_aggregation_document_status(document.id)()
        return document

    def refresh(self, document, **kwargs):
        return DocumentSerializers.Operate(
            data={"knowledge_id": str(self.knowledge.id), "document_id": str(document.id)}
        ).refresh(**kwargs)

    def test_restart_fails_unfinished_paragraphs_and_preserves_success_and_other_tasks(self):
        unfinished = (State.PENDING, State.STARTED, State.REVOKE)
        document = self.create_document(State.STARTED, (*unfinished, State.SUCCESS, State.FAILURE))
        untouched = self.create_document(State.SUCCESS, (State.SUCCESS,))
        with self.captureOnCommitCallbacks(execute=True):
            self.assertEqual(recover_interrupted_embeddings(), 1)
            self.clear_locks.assert_not_called()
        document.refresh_from_db()
        untouched.refresh_from_db()
        self.assertEqual(document.status, "2nn3")
        self.assertEqual(document.meta["source_url"], "https://example.com")
        self.assertTrue(document.meta[EMBEDDING_GENERATION])
        self.assertEqual(
            list(document.paragraph_set.order_by("id").values_list("status", flat=True)),
            ["2nn3", "2nn3", "2nn3", "2nn2", "2nn3"],
        )
        counts = {item["status"]: item["count"] for item in document.status_meta["aggs"]}
        self.assertEqual(counts, {"2nn3": 4, "2nn2": 1})
        self.assertEqual(untouched.status, "2nn2")
        self.assertNotIn(EMBEDDING_GENERATION, untouched.meta)
        self.clear_locks.assert_called_once_with(document.id)
        self.assertEqual(recover_interrupted_embeddings(), 0)

    def test_recovers_documents_already_reset_by_an_older_web_process(self):
        document = self.create_document(State.FAILURE, (State.PENDING,))
        with self.captureOnCommitCallbacks(execute=True):
            self.assertEqual(recover_interrupted_embeddings(), 1)
        self.clear_locks.assert_called_once_with(document.id)
        self.assertEqual(document.paragraph_set.get().status, "2nn3")

    def test_web_restart_preserves_running_embedding(self):
        document = self.create_document(State.STARTED)
        Document.objects.filter(id=document.id).update(status="1011")
        with connection.cursor() as cursor:
            cursor.execute(update_document_status_sql)
        document.refresh_from_db()
        self.assertEqual(document.status, "3331")

    @patch("knowledge.task.embedding.get_embedding_model")
    @patch("knowledge.task.embedding.ListenerManagement.embedding_by_document")
    def test_old_delivery_is_ignored_without_loading_model_or_releasing_new_lock(self, embed, model):
        document = self.create_document(State.STARTED, (State.PENDING,))
        with self.captureOnCommitCallbacks(execute=True):
            recover_interrupted_embeddings()
        document.refresh_from_db()
        with patch.object(embedding_by_document, "after_return") as after_return:
            # Celery's eager tracer exercises Ignore and the QueueOnce lifecycle together.
            result = embedding_by_document.apply(args=[str(document.id), str(self.knowledge.embedding_model_id)])
        self.assertEqual(result.state, "IGNORED")
        after_return.assert_not_called()
        model.assert_not_called()
        embed.assert_not_called()
        # Run the accepted delivery with its headers without touching the real QueueOnce backend.
        embedding_by_document.push_request(headers={EMBEDDING_GENERATION: document.meta[EMBEDDING_GENERATION]})
        try:
            with patch("knowledge.task.embedding.current_task", embedding_by_document):
                embedding_by_document.run(str(document.id), str(self.knowledge.embedding_model_id))
        finally:
            embedding_by_document.pop_request()
        model.assert_called_once()
        embed.assert_called_once()

    @patch.object(QueueOnce, "apply_async")
    def test_new_submission_carries_recovery_generation(self, apply_async):
        document = self.create_document(State.FAILURE, (State.PENDING,))
        recover_interrupted_embeddings()
        document.refresh_from_db()
        embedding_by_document.apply_async(
            kwargs={"document_id": str(document.id), "model_id": str(self.knowledge.embedding_model_id)},
            headers={"trace": "retained"},
        )
        self.assertEqual(
            apply_async.call_args.kwargs["headers"],
            {"trace": "retained", EMBEDDING_GENERATION: document.meta[EMBEDDING_GENERATION]},
        )

    def test_duplicate_submission_does_not_reset_document_or_paragraph_states(self):
        document = self.create_document(State.STARTED, (State.SUCCESS, State.STARTED))
        old_meta = Document.objects.get(id=document.id).status_meta
        self.delay.side_effect = AlreadyQueued(60)
        with self.assertRaises(AppApiException), self.captureOnCommitCallbacks(execute=True):
            self.refresh(document)
        document.refresh_from_db()
        self.assertEqual(document.status, "2nn1")
        self.assertEqual(document.status_meta, old_meta)
        self.assertEqual(list(document.paragraph_set.order_by("id").values_list("status", flat=True)), ["2nn2", "2nn1"])

    def test_batch_skips_active_document_and_submits_remaining_documents(self):
        active = self.create_document(State.STARTED, (State.STARTED,))
        failed = self.create_document(State.FAILURE, (State.FAILURE, State.SUCCESS))
        self.delay.side_effect = [AlreadyQueued(60), None]
        with self.captureOnCommitCallbacks(execute=True):
            DocumentSerializers.Batch(
                data={"knowledge_id": str(self.knowledge.id), "workspace_id": "default"}
            ).batch_refresh(
                {"id_list": [str(active.id), str(failed.id)], "state_list": [State.PENDING.value, State.FAILURE.value]}
            )
            self.delay.assert_not_called()
        self.assertEqual(self.delay.call_count, 2)
        active.refresh_from_db()
        failed.refresh_from_db()
        self.assertEqual(active.status, "2nn1")
        self.assertEqual(failed.status, "2nn0")
        self.assertEqual(list(failed.paragraph_set.order_by("id").values_list("status", flat=True)), ["2nn0", "2nn2"])

    def test_broker_failure_does_not_leave_manual_retry_pending(self):
        document = self.create_document(State.FAILURE, (State.FAILURE,))
        self.delay.side_effect = RuntimeError("broker unavailable")
        with self.assertRaisesRegex(RuntimeError, "broker unavailable"), self.captureOnCommitCallbacks(execute=True):
            self.refresh(document)
        document.refresh_from_db()
        self.assertEqual(document.status, "2nn3")
        self.assertEqual(document.paragraph_set.get().status, "2nn3")
