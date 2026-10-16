"""Web synchronization publishes complete content and preserves unrelated sources."""

from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import patch

from django.db import transaction
from django.test import SimpleTestCase, TestCase

from common.utils.fork import ChildLink, Fork
from knowledge.models import (
    ContentOrigin,
    Document,
    DocumentTag,
    Embedding,
    File,
    FileSourceType,
    Knowledge,
    KnowledgeSyncLog,
    KnowledgeSyncStatus,
    KnowledgeType,
    Paragraph,
    ParagraphAsset,
    Problem,
    ProblemParagraphMapping,
    SourceType,
    State,
    Status,
    Tag,
    TaskType,
)
from knowledge.serializers.document import DocumentSerializers
from knowledge.services.document_cleanup import delete_document_data
from knowledge.services.document_strategy import normalize_document_strategy
from knowledge.task.handler import (
    get_save_handler,
    get_sync_handler,
    get_sync_web_document_handler,
    is_web_sync_document,
)
from knowledge.task.sync import sync_replace_web_knowledge
from models_provider.models import Model


ROOT_URL = "https://example.com/docs"


class WebSyncSourceScopeTests(SimpleTestCase):
    def test_legacy_scope_uses_origin_and_path_boundaries(self):
        for url, expected in (
            (ROOT_URL, True),
            (ROOT_URL + "/child#heading", True),
            ("https://EXAMPLE.com/docs/", True),
            ("https://example.com/docs-other", False),
            ("https://example.com/independent", False),
            ("https://example.com.evil/docs/child", False),
            ("https://other.example/docs/child", False),
            ("http://example.com/docs/child", False),
        ):
            with self.subTest(url=url):
                self.assertEqual(is_web_sync_document(SimpleNamespace(meta={"source_url": url}), ROOT_URL), expected)

    def test_explicit_source_overrides_url_inference(self):
        for source, expected in ((None, False), (ROOT_URL + "/other", False), (ROOT_URL + "/#top", True)):
            with self.subTest(source=source):
                document = SimpleNamespace(meta={"source_url": ROOT_URL + "/child", "web_sync_source_url": source})
                self.assertEqual(is_web_sync_document(document, ROOT_URL), expected)
        self.assertFalse(is_web_sync_document(SimpleNamespace(meta={}), ROOT_URL))

    def test_legacy_html_entry_uses_the_crawled_parent_directory(self):
        document = SimpleNamespace(meta={"source_url": ROOT_URL + "/child.html"})
        self.assertTrue(is_web_sync_document(document, ROOT_URL + "/index.html"))


class WebSyncSafetyTests(TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        for module in ("knowledge.task.handler", "knowledge.serializers.document"):
            self.stack.enter_context(patch(module + ".internalize_web_images", side_effect=lambda content, _: content))
        self.stack.enter_context(
            patch(
                "common.event.listener_manage.ListenerManagement.get_aggregation_document_status",
                return_value=lambda: None,
            )
        )
        self.stack.enter_context(patch("knowledge.task.sync.start_sync_heartbeat", return_value=lambda: None))
        self.document_delay = self.stack.enter_context(
            patch("knowledge.serializers.document.embedding_by_document.delay")
        )
        self.paragraph_delay = self.stack.enter_context(
            patch("knowledge.serializers.document.embedding_by_paragraph_list.delay")
        )
        model = Model.objects.create(
            name="Web test model", model_type="EMBEDDING", model_name="test", provider="test", credential=""
        )
        self.knowledge = Knowledge.objects.create(
            name="Web safety test",
            desc="",
            type=KnowledgeType.WEB,
            embedding_model=model,
            meta={"source_url": ROOT_URL, "selector": "body"},
        )
        self.document = Document.objects.create(
            knowledge=self.knowledge,
            name="Old",
            char_length=3,
            type=KnowledgeType.WEB,
            meta={"source_url": ROOT_URL, "selector": "body", "web_sync_source_url": ROOT_URL},
            doc_strategy=normalize_document_strategy({"split": {"max_length": 777}}),
            source_hash="old-hash",
        )
        self.paragraph = Paragraph.objects.create(
            knowledge=self.knowledge,
            document=self.document,
            title="Title",
            content="old",
            hit_num=7,
            origin=ContentOrigin.SYNCED,
            source_snapshot={"title": "Title", "content": "old"},
        )
        self.file = File(source_type=FileSourceType.DOCUMENT, source_id=str(self.document.id), storage_type="pg")
        File.objects.bulk_create([self.file])
        self.document.meta["source_file_id"] = str(self.file.id)
        self.document.save(update_fields=["meta"])
        self.asset = ParagraphAsset.objects.create(
            knowledge=self.knowledge, document=self.document, paragraph=self.paragraph, file=self.file
        )
        self.tag = DocumentTag.objects.create(
            document=self.document, tag=Tag.objects.create(knowledge=self.knowledge, key="scope", value="old")
        )
        self.problem = Problem.objects.create(knowledge=self.knowledge, content="Old question")
        self.mapping = ProblemParagraphMapping.objects.create(
            knowledge=self.knowledge, document=self.document, paragraph=self.paragraph, problem=self.problem
        )
        self.embedding = Embedding.objects.create(
            id=str(self.paragraph.id),
            knowledge=self.knowledge,
            document=self.document,
            paragraph=self.paragraph,
            source_id=str(self.paragraph.id),
            source_type=SourceType.PARAGRAPH,
            embedding=[0.1, 0.2],
        )

    def assert_old_content_preserved(self):
        self.document.refresh_from_db()
        self.paragraph.refresh_from_db()
        self.assertEqual(
            (self.document.source_hash, self.document.char_length, self.document.sync_version), ("old-hash", 3, 0)
        )
        self.assertIsNone(self.document.last_sync_time)
        self.assertEqual((self.paragraph.content, self.paragraph.hit_num), ("old", 7))
        for model, instance in (
            (File, self.file),
            (ParagraphAsset, self.asset),
            (DocumentTag, self.tag),
            (Problem, self.problem),
            (ProblemParagraphMapping, self.mapping),
            (Embedding, self.embedding),
        ):
            self.assertTrue(model.objects.filter(pk=instance.pk).exists(), model.__name__)

    def sync_document(self):
        return DocumentSerializers.Sync(
            data={"knowledge_id": str(self.knowledge.id), "document_id": str(self.document.id)}
        ).sync(response=Fork.Response.success("updated", []))

    def run_crawl(self, mode, crawl, *, record_log=False):
        with patch("knowledge.task.sync.ForkManage") as crawler:
            crawler.return_value.fork.side_effect = crawl
            return sync_replace_web_knowledge.run(
                str(self.knowledge.id), None, ROOT_URL, "body", sync_type=mode, record_log=record_log
            )

    def successful_crawl(self, _level, visited, handler):
        visited.add(ROOT_URL)
        handler(ChildLink(ROOT_URL, None), Fork.Response.success("# Title\n\nnew", []))

    def add_independent_documents(self):
        docs = []
        for url, extra in (
            ("https://other.example/page", {}),
            ("https://example.com/docs-other", {}),
            (ROOT_URL + "/independent", {"web_sync_source_url": None}),
            (ROOT_URL + "/different-scope", {"web_sync_source_url": ROOT_URL + "/other"}),
        ):
            docs.append(
                Document.objects.create(
                    knowledge=self.knowledge,
                    name="Independent",
                    char_length=0,
                    type=KnowledgeType.WEB,
                    meta={"source_url": url, **extra},
                )
            )
        docs.append(
            Document.objects.create(knowledge=self.knowledge, name="Local", char_length=0, type=KnowledgeType.BASE)
        )
        return docs

    def assert_independent_documents_preserved(self, docs):
        self.assertEqual(Document.objects.filter(id__in=[doc.id for doc in docs]).count(), len(docs))

    def test_incremental_processing_failure_rolls_back_content_and_relations(self):
        with (
            patch(
                "knowledge.serializers.document.parse_web_content", return_value=[{"title": "Title", "content": "new"}]
            ),
            patch("knowledge.serializers.document.defer_visual_assets", side_effect=RuntimeError("asset failed")),
            self.captureOnCommitCallbacks(execute=True) as callbacks,
        ):
            self.sync_document()
        self.assert_old_content_preserved()
        self.assertEqual(Status.of(self.document.status)[TaskType.SYNC], State.FAILURE)
        self.assertEqual(callbacks, [])
        self.paragraph_delay.assert_not_called()

    def test_failed_incremental_can_retry_and_queue_embedding_after_commit(self):
        with patch(
            "knowledge.serializers.document.parse_web_content", return_value=[{"title": "Title", "content": "new"}]
        ):
            with patch("knowledge.serializers.document.defer_visual_assets", side_effect=RuntimeError("asset failed")):
                self.sync_document()
            with self.captureOnCommitCallbacks(execute=True):
                self.sync_document()
                self.paragraph_delay.assert_not_called()
        self.document.refresh_from_db()
        self.paragraph.refresh_from_db()
        self.assertEqual((self.document.sync_version, self.paragraph.content), (1, "new"))
        self.paragraph_delay.assert_called_once()

    def test_replace_post_save_failure_rolls_back_new_document(self):
        stats = {"failed_count": 0, "synced_count": 0, "deleted_count": 0}
        with patch.object(DocumentSerializers.Operate, "refresh", side_effect=RuntimeError("refresh failed")):
            handler = get_sync_handler(str(self.knowledge.id), None, sync_type="replace", stats=stats)
            self.successful_crawl(2, set(), handler)
        self.assert_old_content_preserved()
        self.assertEqual(Document.objects.filter(knowledge=self.knowledge).count(), 1)
        self.assertEqual(stats, {"failed_count": 1, "synced_count": 0, "deleted_count": 0})

    def fail_after_cleanup(self, document_ids):
        delete_document_data(document_ids)
        raise RuntimeError("publication failed")

    def test_replace_cleanup_failure_restores_old_relations_and_discards_jobs(self):
        with (
            patch("knowledge.task.handler.delete_document_data", side_effect=self.fail_after_cleanup),
            self.captureOnCommitCallbacks(execute=True) as callbacks,
        ):
            result = self.run_crawl("replace", self.successful_crawl, record_log=True)
        self.assert_old_content_preserved()
        self.assertEqual(Document.objects.filter(knowledge=self.knowledge).count(), 1)
        self.assertEqual((result["status"], result["synced_count"], result["deleted_count"]), ("failure", 0, 0))
        self.assertEqual(callbacks, [])
        self.document_delay.assert_not_called()

    def test_replace_success_replaces_match_and_preserves_unmatched_documents(self):
        independent = self.add_independent_documents()
        with self.captureOnCommitCallbacks(execute=True):
            result = self.run_crawl("replace", self.successful_crawl)
            self.document_delay.assert_not_called()
        self.assert_independent_documents_preserved(independent)
        self.assertFalse(Document.objects.filter(pk=self.document.pk).exists())
        new_document = Document.objects.get(knowledge=self.knowledge, meta__web_sync_source_url=ROOT_URL)
        self.assertEqual(new_document.doc_strategy, self.document.doc_strategy)
        self.assertEqual((result["synced_count"], result["deleted_count"]), (1, 1))
        self.document_delay.assert_called_once()

    def test_incremental_prunes_only_missing_documents_from_current_source(self):
        independent = self.add_independent_documents()
        stale = Document.objects.create(
            knowledge=self.knowledge,
            name="Removed",
            char_length=0,
            type=KnowledgeType.WEB,
            meta={"source_url": ROOT_URL + "/removed", "web_sync_source_url": ROOT_URL},
        )
        result = self.run_crawl("incremental", self.successful_crawl)
        self.assertEqual((result["status"], result["deleted_count"]), ("success", 1))
        self.assertFalse(Document.objects.filter(pk=stale.pk).exists())
        self.assertTrue(Document.objects.filter(pk=self.document.pk).exists())
        self.assert_independent_documents_preserved(independent)

    def test_partial_complete_crawl_never_exposes_prepared_documents(self):
        observed = []

        def crawl(level, visited, handler):
            self.successful_crawl(level, visited, handler)
            listing = DocumentSerializers.Query(
                data={"knowledge_id": str(self.knowledge.id), "workspace_id": "default"}
            )
            listing.is_valid(raise_exception=True)
            observed.append(listing.get_query_set()["document_custom_sql"].count())
            self.document_delay.assert_not_called()
            handler(ChildLink(ROOT_URL + "/failed", None), Fork.Response.error("unavailable"))

        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            result = self.run_crawl("complete", crawl)
        self.assertEqual(observed, [1])
        self.assert_old_content_preserved()
        self.assertEqual((result["status"], result["synced_count"], result["deleted_count"]), ("failure", 0, 0))
        self.assertEqual(callbacks, [])

    def test_interrupted_complete_crawl_keeps_old_documents(self):
        def crawl(level, visited, handler):
            self.successful_crawl(level, visited, handler)
            raise RuntimeError("crawl interrupted")

        result = self.run_crawl("complete", crawl)
        self.assert_old_content_preserved()
        self.assertEqual(Document.objects.filter(knowledge=self.knowledge).count(), 1)
        self.assertEqual(result["status"], "failure")

    def test_complete_success_publishes_current_source_and_log_together(self):
        independent = self.add_independent_documents()
        with self.captureOnCommitCallbacks(execute=True):
            result = self.run_crawl("complete", self.successful_crawl, record_log=True)
            self.document_delay.assert_not_called()
        self.assert_independent_documents_preserved(independent)
        self.assertFalse(Document.objects.filter(pk=self.document.pk).exists())
        new_document = Document.objects.get(knowledge=self.knowledge, meta__web_sync_source_url=ROOT_URL)
        self.assertEqual(new_document.doc_strategy, self.document.doc_strategy)
        sync_log = KnowledgeSyncLog.objects.get(knowledge=self.knowledge)
        self.assertEqual((sync_log.status, sync_log.synced_count, sync_log.deleted_count), ("success", 1, 1))
        self.assertEqual((result["synced_count"], result["deleted_count"]), (1, 1))
        self.document_delay.assert_called_once()

    def test_complete_publication_failure_rolls_back_cleanup_and_new_documents(self):
        with (
            patch("knowledge.task.sync.delete_document_data", side_effect=self.fail_after_cleanup),
            self.captureOnCommitCallbacks(execute=True) as callbacks,
        ):
            result = self.run_crawl("complete", self.successful_crawl, record_log=True)
        self.assert_old_content_preserved()
        self.assertEqual(Document.objects.filter(knowledge=self.knowledge).count(), 1)
        sync_log = KnowledgeSyncLog.objects.get(knowledge=self.knowledge)
        self.assertEqual((sync_log.status, sync_log.synced_count, sync_log.deleted_count), ("failure", 0, 0))
        self.assertEqual((result["synced_count"], result["deleted_count"]), (0, 0))
        self.assertEqual(callbacks, [])

    def test_complete_second_document_failure_rolls_back_first_document_and_jobs(self):
        original_refresh = DocumentSerializers.Operate.refresh
        refresh_count = 0

        def refresh(operation, **kwargs):
            nonlocal refresh_count
            refresh_count += 1
            if refresh_count == 2:
                raise RuntimeError("second document failed")
            return original_refresh(operation, **kwargs)

        def crawl(level, visited, handler):
            self.successful_crawl(level, visited, handler)
            handler(ChildLink(ROOT_URL + "/second", None), Fork.Response.success("second", []))

        with (
            patch.object(DocumentSerializers.Operate, "refresh", autospec=True, side_effect=refresh),
            self.captureOnCommitCallbacks(execute=True) as callbacks,
        ):
            result = self.run_crawl("complete", crawl, record_log=True)
        self.assert_old_content_preserved()
        self.assertEqual(Document.objects.filter(knowledge=self.knowledge).count(), 1)
        self.assertEqual((result["synced_count"], result["deleted_count"]), (0, 0))
        self.assertEqual(callbacks, [])
        self.document_delay.assert_not_called()

    def test_initial_crawl_records_its_source(self):
        handler = get_save_handler(str(self.knowledge.id), None, "body")
        handler(ChildLink(ROOT_URL + "/new", None), Fork.Response.success("new", []))
        document = Document.objects.get(knowledge=self.knowledge, meta__source_url=ROOT_URL + "/new")
        self.assertEqual(document.meta["web_sync_source_url"], ROOT_URL)

    def test_standalone_import_is_preserved_even_inside_current_site(self):
        handler = get_sync_web_document_handler(str(self.knowledge.id), None)
        url = ROOT_URL + "/independent"
        handler(url, "body", Fork.Response.success("independent", []))
        document = Document.objects.get(knowledge=self.knowledge, meta__source_url=url)
        self.assertIsNone(document.meta["web_sync_source_url"])
        result = self.run_crawl("complete", self.successful_crawl)
        self.assertEqual(result["status"], "success")
        self.assertTrue(Document.objects.filter(pk=document.pk).exists())

    def test_expired_complete_run_cannot_publish(self):
        def crawl(level, visited, handler):
            self.successful_crawl(level, visited, handler)
            KnowledgeSyncLog.objects.filter(knowledge=self.knowledge).update(status=KnowledgeSyncStatus.FAILURE)

        result = self.run_crawl("complete", crawl, record_log=True)
        self.assert_old_content_preserved()
        self.assertEqual(result["status"], "failure")
        self.assertEqual(Document.objects.filter(knowledge=self.knowledge).count(), 1)

    def test_empty_complete_snapshot_does_not_delete_old_content(self):
        result = self.run_crawl("complete", lambda *_: None)
        self.assert_old_content_preserved()
        self.assertEqual(result["status"], "failure")

    def test_broker_failure_marks_embedding_failed_without_duplicate_replace_documents(self):
        self.document_delay.side_effect = RuntimeError("broker unavailable")
        with self.captureOnCommitCallbacks(execute=True):
            result = self.run_crawl("replace", self.successful_crawl, record_log=True)
        self.assertEqual(result["status"], "success")
        self.assertEqual(Document.objects.filter(knowledge=self.knowledge).count(), 1)
        new_document = Document.objects.get(knowledge=self.knowledge)
        self.assertEqual(Status.of(new_document.status)[TaskType.EMBEDDING], State.FAILURE)
        for paragraph in Paragraph.objects.filter(document=new_document):
            self.assertEqual(Status.of(paragraph.status)[TaskType.EMBEDDING], State.FAILURE)
        self.assertEqual(KnowledgeSyncLog.objects.get(knowledge=self.knowledge).status, KnowledgeSyncStatus.SUCCESS)

    def test_incremental_broker_failure_keeps_new_content_and_reports_embedding_failure(self):
        self.paragraph_delay.side_effect = RuntimeError("broker unavailable")
        with (
            patch(
                "knowledge.serializers.document.parse_web_content", return_value=[{"title": "Title", "content": "new"}]
            ),
            self.captureOnCommitCallbacks(execute=True),
        ):
            self.sync_document()
        self.document.refresh_from_db()
        self.paragraph.refresh_from_db()
        self.assertEqual(Status.of(self.document.status)[TaskType.SYNC], State.SUCCESS)
        self.assertEqual(Status.of(self.document.status)[TaskType.EMBEDDING], State.FAILURE)
        self.assertEqual((self.document.sync_version, self.paragraph.content), (1, "new"))

    def test_failed_outer_transaction_never_dispatches_embedding(self):
        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            try:
                with transaction.atomic():
                    self.run_crawl("replace", self.successful_crawl)
                    raise RuntimeError("outer transaction failed")
            except RuntimeError:
                pass
        self.assert_old_content_preserved()
        self.assertEqual(callbacks, [])
        self.document_delay.assert_not_called()
