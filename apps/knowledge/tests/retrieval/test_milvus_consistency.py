"""PG scope and transaction regressions for PR #7445 (real PostgreSQL required)."""

import json
import os
import time
from unittest import skipUnless
from unittest.mock import patch
from uuid import uuid4

from django.db import transaction
from django.test import TestCase, TransactionTestCase

from common.exception.app_exception import AppApiException
from knowledge.models import Document, Embedding, Knowledge, KnowledgeFolder, LocalState, Paragraph, SourceType
from knowledge.vector.milvus_vector import MilvusVector
from maxkb.const import CONFIG


class MilvusConsistencyTests(TestCase):
    def setUp(self):
        self.source = Knowledge.objects.create(name="Source", workspace_id="default")
        self.target = Knowledge.objects.create(name="Target", workspace_id="default")
        self.document = Document.objects.create(knowledge=self.source, name="Document", char_length=0)
        self.paragraph = Paragraph.objects.create(knowledge=self.source, document=self.document, content="text")
        self.row = self.create_embedding(self.paragraph)
        self.store = MilvusVector()
        self.enterContext(patch.object(MilvusVector, "_existing", set()))
        self.enterContext(patch.object(MilvusVector, "_loaded", set()))
        self.enterContext(patch("knowledge.vector.milvus_vector.maxkb_logger"))
        self.query = self.enterContext(patch.object(self.store, "_query_records"))
        self.query.return_value = [{"id": self.row.id, "embedding": [1.0, 0.0]}]
        self.upsert = self.enterContext(patch.object(self.store, "_upsert_records"))
        self.delete = self.enterContext(patch.object(self.store, "_delete_ids"))

    def create_embedding(self, paragraph, **values):
        return Embedding.objects.create(
            id=str(uuid4()),
            knowledge=paragraph.knowledge,
            document=paragraph.document,
            paragraph=paragraph,
            source_id=str(paragraph.id),
            source_type=SourceType.PARAGRAPH,
            **values,
        )

    def move(self):
        self.store.update_by_paragraph_id(str(self.paragraph.id), {"knowledge_id": str(self.target.id)})

    def assert_source_intact(self):
        self.row.refresh_from_db()
        self.assertEqual(self.row.knowledge_id, self.source.id)
        self.delete.assert_not_called()

    def test_lookup_or_target_write_failure_preserves_pg_and_source(self):
        for failing_call in (self.query, self.upsert):
            with self.subTest(operation=failing_call):
                failing_call.side_effect = AppApiException(500, "injected failure")
                with self.captureOnCommitCallbacks(execute=True), self.assertRaises(AppApiException):
                    self.move()
                self.assert_source_intact()
                failing_call.side_effect = None

    def test_incomplete_lookup_aborts_milvus_only_move(self):
        self.query.return_value = []
        with self.captureOnCommitCallbacks(execute=True), self.assertRaises(AppApiException):
            self.move()
        self.assert_source_intact()
        self.upsert.assert_not_called()

    def test_pg_failure_after_copy_never_deletes_source(self):
        from django.db.models import QuerySet

        with patch.object(QuerySet, "update", side_effect=RuntimeError("PG update failed")):
            with self.captureOnCommitCallbacks(execute=True), self.assertRaises(RuntimeError):
                self.move()
        self.upsert.assert_called_once()
        self.assert_source_intact()

    def test_outer_transaction_rollback_never_deletes_source(self):
        with self.captureOnCommitCallbacks(execute=True):
            with self.assertRaises(RuntimeError), transaction.atomic():
                self.move()
                raise RuntimeError("later document migration failure")
        self.assert_source_intact()

    def test_success_deletes_only_copied_ids_after_pg_commit(self):
        historical = self.create_embedding(self.paragraph, embedding="[0, 1]")
        with self.captureOnCommitCallbacks(execute=True):
            self.move()
            self.delete.assert_not_called()
            self.row.refresh_from_db()
            self.assertEqual(self.row.knowledge_id, self.target.id)
        self.delete.assert_called_once_with(str(self.source.id), [self.row.id])
        historical.refresh_from_db()
        self.assertEqual(historical.knowledge_id, self.target.id)
        self.assertIsNotNone(historical.embedding)

    def test_failed_cleanup_keeps_target_vector_and_pg_target_scope(self):
        self.delete.side_effect = AppApiException(500, "cleanup failed")
        with self.assertRaises(AppApiException), self.captureOnCommitCallbacks(execute=True):
            self.move()
        self.row.refresh_from_db()
        self.assertEqual(self.row.knowledge_id, self.target.id)
        self.assertEqual(self.upsert.call_args.args[0], str(self.target.id))

    def test_delayed_cleanup_preserves_vectors_moved_back_to_source(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.move()
            # Model a later committed move back before the first cleanup callback runs.
            Embedding.objects.filter(id=self.row.id).update(knowledge=self.source)
        self.assert_source_intact()

    def test_replacement_clears_historical_pg_vector_only_after_success(self):
        Embedding.objects.filter(id=self.row.id).update(embedding="[1, 0]")
        self.upsert.side_effect = AppApiException(500, "write failed")
        with self.assertRaises(AppApiException):
            self.store.update_by_source_id(self.row.source_id, {"embedding": [0.0, 1.0]})
        self.row.refresh_from_db()
        self.assertIsNotNone(self.row.embedding)
        self.upsert.side_effect = None
        self.store.update_by_source_id(self.row.source_id, {"embedding": [0.0, 1.0]})
        self.row.refresh_from_db()
        self.assertIsNone(self.row.embedding)
        self.assertEqual(self.upsert.call_args.args[1][0]["embedding"], [0.0, 1.0])

    def test_search_rechecks_scope_state_and_refills_rejected_candidates(self):
        rows = [self.create_embedding(self.paragraph) for _ in range(7)]
        Embedding.objects.filter(id=rows[0].id).update(knowledge=self.target)
        Embedding.objects.filter(id=rows[1].id).update(is_active=False)
        Embedding.objects.filter(id=rows[2].id).update(document_id=uuid4())
        Embedding.objects.filter(id=rows[3].id).update(paragraph_id=uuid4())
        for row, values in zip(
            rows[4:], [{"local_state": LocalState.DELETED}, {"is_active": False}, {"knowledge": self.target}]
        ):
            paragraph = Paragraph.objects.create(knowledge=self.source, document=self.document, content="stale")
            Paragraph.objects.filter(id=paragraph.id).update(**values)
            Embedding.objects.filter(id=row.id).update(paragraph=paragraph)
        hits = [{"id": f"orphan-{i}", "distance": 1.0} for i in range(12)]
        hits += [{"id": row.id, "distance": 0.99} for row in rows]
        hits += [{"id": self.row.id, "distance": 0.8}]

        def search(_path, body):
            excluded = json.loads(body["filter"].split("id not in ")[-1]) if " and id not in " in body["filter"] else []
            return True, {"code": 0, "data": [hit for hit in hits if hit["id"] not in excluded][: body["limit"]]}

        with (
            patch.object(self.store, "_has_collection", return_value=True),
            patch.object(self.store, "_post", side_effect=search) as post,
        ):
            result = self.store._milvus_search(
                str(self.source.id), [1.0, 0.0], 1, True, [str(self.document.id)], [], []
            )
        self.assertEqual([hit["id"] for hit in result], [self.row.id])
        self.assertGreater(post.call_count, 1)

    def test_search_rechecks_document_and_paragraph_exclusions(self):
        for documents, excluded_documents, excluded_paragraphs in (
            ([str(uuid4())], [], []),
            (None, [str(self.document.id)], []),
            (None, [], [str(self.paragraph.id)]),
        ):
            with self.subTest(scope=(documents, excluded_documents, excluded_paragraphs)):
                with (
                    patch.object(self.store, "_has_collection", return_value=True),
                    patch.object(
                        self.store,
                        "_post",
                        return_value=(True, {"code": 0, "data": [{"id": self.row.id, "distance": 1.0}]}),
                    ),
                ):
                    self.assertEqual(
                        self.store._milvus_search(
                            str(self.source.id), [1.0, 0.0], 1, True, documents, excluded_documents, excluded_paragraphs
                        ),
                        [],
                    )


@skipUnless(os.environ.get("MILVUS_LIVE_TEST_URL"), "Requires a dedicated disposable Milvus instance")
class MilvusLiveConsistencyTests(TransactionTestCase):
    """Real PostgreSQL + Milvus; only synthetic UUID collections are created and dropped."""

    def setUp(self):
        KnowledgeFolder.objects.get_or_create(id="default", defaults={"name": "Default"})
        self.enterContext(patch.dict(CONFIG, MILVUS_URI=os.environ["MILVUS_LIVE_TEST_URL"], MILVUS_TOKEN=""))
        self.enterContext(patch.object(MilvusVector, "_session", None))
        self.enterContext(patch.object(MilvusVector, "_uri", ""))
        self.enterContext(patch.object(MilvusVector, "_existing", set()))
        self.enterContext(patch.object(MilvusVector, "_loaded", set()))
        self.store = MilvusVector()
        self.source = Knowledge.objects.create(name="Live source", workspace_id="default")
        self.target = Knowledge.objects.create(name="Live target", workspace_id="default")
        self.document = Document.objects.create(knowledge=self.source, name="Document", char_length=0)
        self.paragraph = Paragraph.objects.create(knowledge=self.source, document=self.document, content="text")
        self.row = Embedding.objects.create(
            id=str(uuid4()),
            knowledge=self.source,
            document=self.document,
            paragraph=self.paragraph,
            source_id=str(self.paragraph.id),
            source_type=SourceType.PARAGRAPH,
        )
        self.record = {
            "id": self.row.id,
            "embedding": [1.0, 0.0],
            "document_id": str(self.document.id),
            "paragraph_id": str(self.paragraph.id),
            "source_id": self.row.source_id,
            "source_type": int(self.row.source_type),
            "is_active": True,
        }
        self.addCleanup(self.cleanup_collections)
        self.store._upsert_records(str(self.source.id), [self.record])

    def cleanup_collections(self):
        try:
            for knowledge in (self.source, self.target):
                self.store.drop_knowledge_index(str(knowledge.id))
        finally:
            if MilvusVector._session is not None:
                MilvusVector._session.close()

    def test_move_copies_before_cleanup_and_stale_source_is_not_recalled(self):
        with transaction.atomic():
            Document.objects.filter(id=self.document.id).update(knowledge=self.target)
            Paragraph.objects.filter(id=self.paragraph.id).update(knowledge=self.target)
            self.store.update_by_paragraph_id(str(self.paragraph.id), {"knowledge_id": str(self.target.id)})
            for knowledge in (self.source, self.target):
                rows = self.store._query_records(str(knowledge.id), [self.row.id], ["embedding"])
                self.assertEqual(rows[0]["embedding"], [1.0, 0.0])
        self.assertEqual(self.store._query_records(str(self.source.id), [self.row.id], ["embedding"]), [])
        # Reintroduce the stale source copy that a failed cleanup could leave behind.
        self.store._upsert_records(str(self.source.id), [self.record])
        self.assertEqual(len(self.store._query_records(str(self.source.id), [self.row.id], ["embedding"])), 1)
        self.assertEqual(self.store._milvus_search(str(self.source.id), [1.0, 0.0], 1, True, None, [], []), [])
        result = []
        for _ in range(20):
            result = self.store._milvus_search(str(self.target.id), [1.0, 0.0], 1, True, None, [], [])
            if result:
                break
            time.sleep(0.2)
        self.assertEqual([row["id"] for row in result], [self.row.id])

    def test_outer_rollback_retains_source_and_retry_after_other_worker_drop(self):
        with self.assertRaises(RuntimeError), transaction.atomic():
            self.store.update_by_paragraph_id(str(self.paragraph.id), {"knowledge_id": str(self.target.id)})
            raise RuntimeError("rollback")
        self.row.refresh_from_db()
        self.assertEqual(self.row.knowledge_id, self.source.id)
        self.assertEqual(len(self.store._query_records(str(self.source.id), [self.row.id], ["embedding"])), 1)
        self.store._post_required(
            "/v2/vectordb/collections/drop", {"collectionName": self.store._collection_name(str(self.source.id))}
        )
        with self.assertRaises(AppApiException):
            self.store._upsert_records(str(self.source.id), [self.record])
        self.store._upsert_records(str(self.source.id), [self.record])
        self.assertEqual(len(self.store._query_records(str(self.source.id), [self.row.id], ["embedding"])), 1)
