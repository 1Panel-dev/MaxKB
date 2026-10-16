"""Interrupted sync states and QueueOnce locks must not block the next scheduled run."""

from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from knowledge.models import Document, Knowledge, KnowledgeSyncLog, KnowledgeSyncStatus, KnowledgeType
from knowledge.services.sync_status import _clear_sync_queue_lock, fail_running_sync_logs_on_startup
from knowledge.task.sync import (
    scheduled_sync_knowledge,
    scheduled_sync_web_knowledge,
    scheduled_sync_workflow_knowledge,
)
from knowledge.tasks import fail_interrupted_knowledge_synchronizations


class SyncRestartSignalTests(SimpleTestCase):
    @patch("knowledge.services.sync_status.fail_running_sync_logs_on_startup", return_value=1)
    def test_worker_initialization_marks_interrupted_runs_failed(self, fail_running):
        fail_interrupted_knowledge_synchronizations()
        fail_running.assert_called_once_with()

    @patch("knowledge.services.sync_status.import_backend")
    def test_only_the_relevant_knowledge_queue_lock_is_cleared(self, backend):
        tasks = {
            KnowledgeType.WEB: "celery:sync_replace_web_knowledge",
            KnowledgeType.LARK: "celery:scheduled_sync_lark_knowledge",
            KnowledgeType.WORKFLOW: "celery:scheduled_sync_workflow_knowledge",
        }
        for knowledge_type, task_name in tasks.items():
            with self.subTest(knowledge_type=knowledge_type):
                backend.reset_mock()
                _clear_sync_queue_lock(SimpleNamespace(id="knowledge", type=knowledge_type))
                backend.return_value.clear_lock.assert_called_once_with(f"qo_{task_name}_knowledge_id-knowledge")


class SyncRestartDatabaseTests(TestCase):
    def create_knowledge(self, knowledge_type):
        return Knowledge.objects.create(
            name="restart test",
            desc="",
            type=knowledge_type,
            meta={"sync_setting": {"enabled": True, "sync_type": "incremental"}},
        )

    def create_log(self, knowledge, status=KnowledgeSyncStatus.RUNNING):
        return KnowledgeSyncLog.objects.create(knowledge=knowledge, workspace_id="default", status=status)

    @patch("knowledge.services.sync_status._clear_sync_queue_lock")
    def test_recent_running_logs_fail_without_resuming_or_changing_documents(self, clear_lock):
        now = timezone.now()
        for knowledge_type in (KnowledgeType.WEB, KnowledgeType.LARK, KnowledgeType.WORKFLOW):
            knowledge = self.create_knowledge(knowledge_type)
            interrupted = self.create_log(knowledge)
            KnowledgeSyncLog.objects.filter(id=interrupted.id).update(create_time=now - timedelta(seconds=20))
            historical = [
                self.create_log(knowledge, status)
                for status in (KnowledgeSyncStatus.SUCCESS, KnowledgeSyncStatus.FAILURE, KnowledgeSyncStatus.SKIPPED)
            ]
            document = Document.objects.create(
                knowledge=knowledge,
                name="retained document",
                char_length=0,
                meta={"workflow_sync_log_id": str(interrupted.id)},
            )
            with patch("knowledge.services.sync_status.timezone.now", return_value=now):
                self.assertEqual(fail_running_sync_logs_on_startup(), 1)
            interrupted.refresh_from_db()
            self.assertEqual(interrupted.status, KnowledgeSyncStatus.FAILURE)
            self.assertEqual(interrupted.duration_ms, 20000)
            self.assertIn("restart", interrupted.message)
            self.assertTrue(Document.objects.filter(id=document.id).exists())
            for log in historical:
                old_status = log.status
                log.refresh_from_db()
                self.assertEqual(log.status, old_status)
            clear_lock.assert_called_with(knowledge)
        self.assertEqual(clear_lock.call_count, 3)
        clear_lock.reset_mock()
        self.assertEqual(fail_running_sync_logs_on_startup(), 0)
        clear_lock.assert_not_called()

    @patch("knowledge.task.sync.celery_app.send_task")
    @patch("knowledge.task.sync.scheduled_sync_workflow_knowledge.delay")
    @patch("knowledge.task.sync.scheduled_sync_web_knowledge.delay")
    @patch("knowledge.services.sync_status._clear_sync_queue_lock")
    def test_next_schedule_creates_a_new_running_log_and_dispatches(self, clear_lock, web, workflow, lark):
        for knowledge_type in (KnowledgeType.WEB, KnowledgeType.LARK, KnowledgeType.WORKFLOW):
            with self.subTest(knowledge_type=knowledge_type):
                knowledge = self.create_knowledge(knowledge_type)
                interrupted = self.create_log(knowledge)
                web.reset_mock()
                workflow.reset_mock()
                lark.reset_mock()

                self.assertEqual(fail_running_sync_logs_on_startup(), 1)
                web.assert_not_called()
                workflow.assert_not_called()
                lark.assert_not_called()
                self.assertTrue(scheduled_sync_knowledge.run(str(knowledge.id)))
                interrupted.refresh_from_db()
                self.assertEqual(interrupted.status, KnowledgeSyncStatus.FAILURE)
                new_log = KnowledgeSyncLog.objects.filter(knowledge=knowledge).exclude(id=interrupted.id).get()
                self.assertEqual(new_log.status, KnowledgeSyncStatus.RUNNING)
                if knowledge_type == KnowledgeType.WEB:
                    web.assert_called_once_with(str(knowledge.id), sync_log_id=str(new_log.id))
                elif knowledge_type == KnowledgeType.LARK:
                    lark.assert_called_once_with(
                        "celery:scheduled_sync_lark_knowledge", args=[str(knowledge.id), str(new_log.id)]
                    )
                else:
                    workflow.assert_called_once_with(str(knowledge.id), str(new_log.id))
                # Finish this new run before starting the next independent case.
                KnowledgeSyncLog.objects.filter(id=new_log.id).update(status=KnowledgeSyncStatus.SUCCESS)

    @patch("knowledge.task.sync.sync_replace_web_knowledge.delay")
    @patch("knowledge.services.sync_status._clear_sync_queue_lock")
    def test_queued_interrupted_tasks_do_not_restart(self, clear_lock, submit_web):
        for knowledge_type, task in (
            (KnowledgeType.WEB, scheduled_sync_web_knowledge),
            (KnowledgeType.WORKFLOW, scheduled_sync_workflow_knowledge),
        ):
            with self.subTest(knowledge_type=knowledge_type):
                knowledge = self.create_knowledge(knowledge_type)
                interrupted = self.create_log(knowledge)
                fail_running_sync_logs_on_startup()
                self.assertFalse(task.run(str(knowledge.id), sync_log_id=str(interrupted.id)))
                interrupted.refresh_from_db()
                self.assertIn("restart", interrupted.message)
                self.assertEqual(KnowledgeSyncLog.objects.filter(knowledge=knowledge).count(), 1)
        submit_web.assert_not_called()
