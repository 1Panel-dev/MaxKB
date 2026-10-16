"""Keep knowledge schedule changes out of the Web process's scheduler."""

from contextlib import ExitStack, nullcontext
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from knowledge.models import KnowledgeType
from knowledge.serializers.knowledge import KnowledgeSerializer
from knowledge.serializers.knowledge_sync import KnowledgeSyncSettingOperationSerializer
from knowledge.services import knowledge_sync_schedule as schedule
from knowledge.tasks import deploy_knowledge_sync_job


KNOWLEDGE_ID = "00000000-0000-0000-0000-000000000001"
USER_ID = "00000000-0000-0000-0000-000000000002"
SETTING = {"enabled": True, "schedule_type": "daily", "time": ["01:00"], "sync_type": "incremental"}


class KnowledgeScheduleDispatchTests(SimpleTestCase):
    def prepare_setting_update(self, stack, knowledge_type=KnowledgeType.WEB):
        knowledge = SimpleNamespace(
            id=KNOWLEDGE_ID, type=knowledge_type, meta={"source_url": "https://example.com"}, save=MagicMock()
        )
        query = stack.enter_context(patch("knowledge.serializers.knowledge_sync.QuerySet"))
        query.return_value.filter.return_value.first.return_value = knowledge
        query.return_value.select_for_update.return_value.get.return_value = knowledge
        stack.enter_context(
            patch("knowledge.serializers.knowledge_sync.transaction.atomic", return_value=nullcontext())
        )
        on_commit = stack.enter_context(patch("knowledge.serializers.knowledge_sync.transaction.on_commit"))
        delay = stack.enter_context(patch("knowledge.tasks.deploy_knowledge_sync_job.delay"))
        scheduler = stack.enter_context(patch.object(schedule, "_get_scheduler"))
        stack.enter_context(patch("knowledge.serializers.knowledge_sync.validate_workflow_sync_source"))
        serializer = KnowledgeSyncSettingOperationSerializer(
            data={"workspace_id": "default", "knowledge_id": KNOWLEDGE_ID}
        )
        return serializer, knowledge, on_commit, delay, scheduler

    def test_setting_changes_only_dispatch_after_commit_and_never_start_a_web_scheduler(self):
        for knowledge_type in (KnowledgeType.WEB, KnowledgeType.LARK, KnowledgeType.WORKFLOW):
            for enabled in (True, False):
                with self.subTest(knowledge_type=knowledge_type, enabled=enabled), ExitStack() as stack:
                    serializer, knowledge, on_commit, delay, scheduler = self.prepare_setting_update(
                        stack, knowledge_type
                    )
                    result = serializer.update_setting({**SETTING, "enabled": enabled})

                    self.assertEqual(knowledge.meta["sync_setting"], result)
                    self.assertEqual(knowledge.meta["source_url"], "https://example.com")
                    delay.assert_not_called()
                    scheduler.assert_not_called()
                    on_commit.assert_called_once()
                    on_commit.call_args.args[0]()
                    delay.assert_called_once_with(KNOWLEDGE_ID)
                    scheduler.assert_not_called()

    def test_failed_save_does_not_register_a_schedule_or_dispatch_a_task(self):
        with ExitStack() as stack:
            serializer, knowledge, on_commit, delay, scheduler = self.prepare_setting_update(stack)
            knowledge.save.side_effect = RuntimeError("save failed")

            with self.assertRaisesRegex(RuntimeError, "save failed"):
                serializer.update_setting(SETTING)

            on_commit.assert_not_called()
            delay.assert_not_called()
            scheduler.assert_not_called()

    def test_delete_only_dispatches_schedule_removal_after_commit(self):
        with ExitStack() as stack:
            query = stack.enter_context(patch("knowledge.serializers.knowledge.QuerySet"))
            query.return_value.get.return_value = SimpleNamespace(id=KNOWLEDGE_ID, delete=MagicMock())
            stack.enter_context(patch("knowledge.serializers.knowledge.drop_knowledge_index"))
            stack.enter_context(patch("knowledge.serializers.knowledge.delete_embedding_by_knowledge"))
            on_commit = stack.enter_context(patch("knowledge.serializers.knowledge.transaction.on_commit"))
            delay = stack.enter_context(patch("knowledge.tasks.remove_knowledge_sync_job.delay"))
            scheduler = stack.enter_context(patch.object(schedule, "_get_scheduler"))
            serializer = KnowledgeSerializer.Operate(
                data={"knowledge_id": KNOWLEDGE_ID, "user_id": USER_ID, "workspace_id": "default"}
            )

            self.assertTrue(KnowledgeSerializer.Operate.delete.__wrapped__(serializer))

            delay.assert_not_called()
            scheduler.assert_not_called()
            on_commit.assert_called_once()
            on_commit.call_args.args[0]()
            delay.assert_called_once_with(KNOWLEDGE_ID)
            scheduler.assert_not_called()

    @patch("knowledge.services.knowledge_sync_schedule.QuerySet")
    @patch("knowledge.services.knowledge_sync_schedule._get_scheduler")
    def test_worker_removes_jobs_when_latest_setting_is_disabled_or_knowledge_is_deleted(self, scheduler, query):
        for knowledge in (SimpleNamespace(meta={"sync_setting": {**SETTING, "enabled": False}}), None):
            with self.subTest(knowledge=knowledge):
                job = MagicMock(id=schedule.knowledge_sync_job_id(KNOWLEDGE_ID))
                scheduler.return_value.get_jobs.return_value = [job]
                query.return_value.filter.return_value.first.return_value = knowledge

                self.assertFalse(deploy_knowledge_sync_job.run(KNOWLEDGE_ID))

                job.remove.assert_called_once()
                scheduler.return_value.add_job.assert_not_called()

    @patch("knowledge.tasks.deploy_knowledge_sync_job.delay")
    @patch("knowledge.services.knowledge_sync_schedule.recover_stale_sync_logs")
    @patch("knowledge.services.knowledge_sync_schedule.deploy_knowledge_sync_job")
    @patch("knowledge.services.knowledge_sync_schedule.QuerySet")
    @patch("knowledge.services.knowledge_sync_schedule._get_scheduler")
    def test_worker_startup_restores_schedules_directly(self, scheduler, query, deploy, recover, delay):
        scheduler.return_value.get_jobs.return_value = []
        query.return_value.filter.return_value.values_list.return_value = [KNOWLEDGE_ID]

        schedule.restore_knowledge_sync_jobs()

        recover.assert_called_once_with(KNOWLEDGE_ID)
        deploy.assert_called_once_with(KNOWLEDGE_ID)
        delay.assert_not_called()
