"""Regression coverage for safe snapshots and abandoned scheduled runs."""

from contextlib import nullcontext
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from knowledge.models import Document, Knowledge, KnowledgeSyncLog, KnowledgeSyncStatus
from knowledge.models.knowledge_action import State
from knowledge.serializers.knowledge_workflow import finalize_knowledge_action
from knowledge.services.sync_status import recover_stale_sync_logs, start_sync_heartbeat
from knowledge.task.sync import scheduled_sync_web_knowledge, sync_replace_web_knowledge


class WebSnapshotFailureTests(SimpleTestCase):
    def setUp(self):
        self.knowledge_query = MagicMock()
        self.knowledge_query.filter.return_value.first.return_value = SimpleNamespace(id="knowledge", workspace_id="ws")
        self.document_query = MagicMock()
        self.old_documents = MagicMock()
        self.old_documents.count.return_value = 1
        self.old_documents.values_list.return_value = ["old"]
        self.old_documents.__iter__.return_value = [
            SimpleNamespace(id="old", meta={"source_url": "https://example.com/section/child"})
        ]
        self.new_documents = MagicMock()
        self.new_documents.values_list.return_value = ["staged"]
        self.document_query.filter.side_effect = lambda **filters: (
            self.new_documents if "meta__web_sync_run_id" in filters else self.old_documents
        )
        query_patch = patch(
            "knowledge.task.sync.QuerySet",
            side_effect=lambda model: {
                Knowledge: self.knowledge_query,
                Document: self.document_query,
            }[model],
        )
        query_patch.start()
        self.addCleanup(query_patch.stop)
        atomic_patch = patch("knowledge.task.sync.transaction.atomic", return_value=nullcontext())
        atomic_patch.start()
        self.addCleanup(atomic_patch.stop)

    @patch("knowledge.task.sync.delete_document_data")
    @patch("knowledge.task.sync.get_sync_handler")
    @patch("knowledge.task.sync.ForkManage")
    def test_failed_subtree_never_deletes_missing_descendants(self, crawler, handler, cleanup):
        def collect(_knowledge, _user, _strategy, _mode, successful_urls, stats):
            successful_urls.add("https://example.com")
            stats["failed_count"] = 1
            return MagicMock()

        handler.side_effect = collect
        crawler.return_value.fork.side_effect = lambda _level, visited, _handler: visited.update(
            {"https://example.com", "https://example.com/section"}
        )
        result = sync_replace_web_knowledge.run("knowledge", "user", "https://example.com", "body")
        self.assertEqual(result["status"], KnowledgeSyncStatus.FAILURE)
        self.assertEqual(result["deleted_count"], 0)
        cleanup.assert_not_called()

    @patch("knowledge.task.sync.delete_document_data")
    @patch("knowledge.task.sync.get_save_handler")
    @patch("knowledge.task.sync.ForkManage")
    def test_partial_complete_run_discards_only_its_staged_documents(self, crawler, handler, cleanup):
        def collect(_knowledge, _user, _selector, _strategy, stats, _source_meta):
            stats.update(synced_count=1, failed_count=1)
            return MagicMock()

        handler.side_effect = collect
        result = sync_replace_web_knowledge.run(
            "knowledge", "user", "https://example.com", "body", sync_type="complete"
        )
        self.assertEqual(result["synced_count"], 0)
        self.assertEqual(result["deleted_count"], 0)
        self.assertEqual(result["status"], KnowledgeSyncStatus.FAILURE)
        cleanup.assert_called_once_with(["staged"])
        snapshot_id = handler.call_args.args[-1]["web_sync_run_id"]
        self.document_query.filter.assert_any_call(knowledge_id="knowledge", meta__web_sync_run_id=snapshot_id)

    @patch("knowledge.task.sync.delete_document_data")
    @patch("knowledge.task.sync.get_save_handler")
    @patch("knowledge.task.sync.ForkManage")
    def test_crawl_exception_preserves_old_documents(self, crawler, _handler, cleanup):
        crawler.return_value.fork.side_effect = RuntimeError("crawl interrupted")
        result = sync_replace_web_knowledge.run(
            "knowledge", "user", "https://example.com", "body", sync_type="complete"
        )
        self.assertEqual(result["status"], KnowledgeSyncStatus.FAILURE)
        self.assertEqual(result["message"], "crawl interrupted")
        cleanup.assert_called_once_with(["staged"])


class SyncHeartbeatTests(SimpleTestCase):
    @patch("knowledge.services.sync_status.Thread")
    @patch("knowledge.services.sync_status.QuerySet")
    def test_expired_execution_cannot_acquire_a_new_heartbeat(self, query_set, thread):
        query_set.return_value.filter.return_value.update.return_value = 0
        with self.assertRaisesRegex(ValueError, "no longer running"):
            start_sync_heartbeat("expired")
        thread.assert_not_called()

    @patch("knowledge.services.sync_status.close_old_connections")
    @patch("knowledge.services.sync_status.Event")
    @patch("knowledge.services.sync_status.Thread")
    @patch("knowledge.services.sync_status.QuerySet")
    def test_healthy_run_refreshes_lease_and_can_stop(self, query_set, thread, event, _connections):
        event.return_value.wait.side_effect = [False, False, True]
        stop = start_sync_heartbeat("log")
        thread.call_args.kwargs["target"]()
        self.assertEqual(query_set.return_value.filter.return_value.update.call_count, 3)
        query_set.return_value.filter.assert_called_with(id="log", status=KnowledgeSyncStatus.RUNNING)
        stop()
        event.return_value.set.assert_called_once()

    @patch("knowledge.services.sync_status.Thread")
    @patch("knowledge.services.sync_status.QuerySet")
    def test_manual_workflow_does_not_create_heartbeat(self, query_set, thread):
        start_sync_heartbeat(None)()
        query_set.assert_not_called()
        thread.assert_not_called()

    @patch("knowledge.services.sync_status._delete_workflow_documents")
    @patch("knowledge.services.sync_status.timezone.now")
    @patch("knowledge.services.sync_status.QuerySet")
    def test_recovery_discards_expired_run_output_and_releases_running_status(self, query_set, now, cleanup):
        current_time = datetime.now(UTC)
        now.return_value = current_time
        expired = SimpleNamespace(id="expired", failed_count=0, create_time=current_time - timedelta(hours=2))
        logs = MagicMock()
        logs.select_for_update.return_value.filter.return_value = [expired]
        documents = MagicMock()
        documents.filter.return_value.filter.return_value.values_list.return_value = ["incomplete-output"]
        knowledge = MagicMock()
        query_set.side_effect = lambda model: {Knowledge: knowledge, KnowledgeSyncLog: logs, Document: documents}[model]
        self.assertEqual(recover_stale_sync_logs.__wrapped__("knowledge"), 1)
        logs.select_for_update.return_value.filter.assert_called_once_with(
            knowledge_id="knowledge",
            status=KnowledgeSyncStatus.RUNNING,
            update_time__lt=current_time - timedelta(hours=1),
        )
        cleanup.assert_called_once_with(["incomplete-output"])
        update = logs.filter.return_value.update.call_args.kwargs
        self.assertEqual(update["status"], KnowledgeSyncStatus.FAILURE)
        self.assertEqual(update["duration_ms"], 7200000)

    @patch("knowledge.services.sync_status._delete_workflow_documents")
    @patch("knowledge.services.sync_status.QuerySet")
    def test_no_expired_lease_does_not_touch_documents(self, query_set, cleanup):
        query_set.return_value.select_for_update.return_value.filter.return_value = []
        self.assertEqual(recover_stale_sync_logs.__wrapped__("knowledge"), 0)
        cleanup.assert_not_called()


class ExpiredRunCompletionTests(SimpleTestCase):
    @patch("knowledge.serializers.knowledge_workflow.merge_workflow_incremental_snapshot")
    @patch("knowledge.serializers.knowledge_workflow.finalize_workflow_complete_snapshot")
    @patch("knowledge.serializers.knowledge_workflow.QuerySet")
    def test_repeated_success_callback_keeps_published_documents(self, query_set, discard, merge):
        log = SimpleNamespace(id="published", knowledge_id="knowledge", status=KnowledgeSyncStatus.SUCCESS)
        query_set.return_value.filter.return_value.first.return_value = log
        query_set.return_value.select_for_update.return_value.get.return_value = log
        finalize_knowledge_action.__wrapped__("action", State.SUCCESS, 1.0, "published", MagicMock())
        discard.assert_not_called()
        merge.assert_not_called()

    @patch("knowledge.task.sync.sync_replace_web_knowledge.delay")
    @patch("knowledge.task.sync.QuerySet")
    def test_recovered_queued_web_run_cannot_start(self, query_set, submit):
        knowledge = SimpleNamespace(id="knowledge", meta={"sync_setting": {"enabled": True}}, user_id="user")
        query_set.return_value.filter.return_value.first.return_value = knowledge
        query_set.return_value.get.return_value = SimpleNamespace(
            sync_type="incremental", status=KnowledgeSyncStatus.FAILURE
        )
        self.assertFalse(scheduled_sync_web_knowledge.run("knowledge", sync_log_id="expired"))
        submit.assert_not_called()

    @patch("knowledge.serializers.knowledge_workflow.merge_workflow_incremental_snapshot")
    @patch("knowledge.serializers.knowledge_workflow.finalize_workflow_complete_snapshot")
    @patch("knowledge.serializers.knowledge_workflow.QuerySet")
    def test_late_workflow_completion_cannot_publish_expired_output(self, query_set, discard, merge):
        log = SimpleNamespace(id="expired", knowledge_id="knowledge", status=KnowledgeSyncStatus.FAILURE)
        log_query = MagicMock()
        log_query.filter.return_value.first.return_value = log
        log_query.select_for_update.return_value.get.return_value = log
        action_query = MagicMock()
        query_set.side_effect = lambda model: log_query if model is KnowledgeSyncLog else action_query
        finalize_knowledge_action.__wrapped__(
            "action", State.SUCCESS, 1.0, "expired", MagicMock(), {"source_scope": "scope"}
        )
        discard.assert_called_once_with(log, False, {"source_scope": "scope"})
        merge.assert_not_called()
        log_query.filter.return_value.update.assert_not_called()
        action_query.filter.return_value.update.assert_called_with(state=State.FAILURE)
