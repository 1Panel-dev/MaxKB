from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from django.utils import timezone
from django.utils.translation import override
from knowledge.models import (
    Knowledge,
    KnowledgeSyncLog,
    KnowledgeSyncStatus,
    KnowledgeSyncTrigger,
    KnowledgeSyncType,
    KnowledgeType,
    KnowledgeWorkflow,
)
from knowledge.models.knowledge_action import State as KnowledgeActionState
from knowledge.serializers.knowledge_sync import (
    KnowledgeSyncSettingOperationSerializer,
    KnowledgeSyncSettingRequest,
)
from knowledge.serializers.knowledge_workflow import KnowledgeWorkflowActionSerializer, finalize_knowledge_action
from knowledge.services.document_strategy import (
    normalize_document_strategy,
)
from knowledge.services.knowledge_sync_schedule import (
    deploy_knowledge_sync_job,
    normalize_knowledge_sync_setting,
)
from knowledge.services.workflow_sync import (
    finalize_workflow_complete_snapshot,
)
from knowledge.services.workflow_sync_source import validate_workflow_sync_source
from knowledge.task.sync import (
    scheduled_sync_knowledge,
    scheduled_sync_web_knowledge,
    scheduled_sync_workflow_knowledge,
)


class KnowledgeScheduleTests(SimpleTestCase):
    def setUp(self):
        super().setUp()
        heartbeat_patch = patch("knowledge.task.sync.start_sync_heartbeat", return_value=lambda: None)
        heartbeat_patch.start()
        self.addCleanup(heartbeat_patch.stop)
        heartbeat_patch = patch("knowledge.task.sync.recover_stale_sync_logs", return_value=lambda: None)
        heartbeat_patch.start()
        self.addCleanup(heartbeat_patch.stop)
        heartbeat_patch = patch(
            "knowledge.serializers.knowledge_workflow.start_sync_heartbeat", return_value=lambda: None
        )
        heartbeat_patch.start()
        self.addCleanup(heartbeat_patch.stop)

    def test_daily_setting_uses_trigger_schedule_fields(self):
        serializer = KnowledgeSyncSettingRequest(
            data={
                "enabled": True,
                "schedule_type": "daily",
                "time": "01:30",
                "sync_type": "incremental",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data,
            {
                "enabled": True,
                "schedule_type": "daily",
                "time": ["01:30"],
                "sync_type": "incremental",
            },
        )

    def test_only_active_trigger_schedule_fields_are_returned(self):
        self.assertEqual(
            normalize_knowledge_sync_setting(
                {
                    "enabled": True,
                    "schedule_type": "interval",
                    "interval_unit": "minutes",
                    "interval_value": 5,
                    "time": ["01:00"],
                    "days": [1],
                    "cron_expression": "0 1 * * *",
                    "sync_type": "replace",
                }
            ),
            {
                "enabled": True,
                "schedule_type": "interval",
                "interval_unit": "minutes",
                "interval_value": 5,
                "sync_type": "replace",
            },
        )

    def test_custom_cron_is_validated(self):
        self.assertEqual(
            normalize_knowledge_sync_setting(
                {
                    "enabled": True,
                    "schedule_type": "cron",
                    "cron_expression": "*/15 * * * *",
                    "sync_type": "replace",
                }
            )["cron_expression"],
            "*/15 * * * *",
        )
        serializer = KnowledgeSyncSettingRequest(
            data={
                "enabled": True,
                "schedule_type": "cron",
                "cron_expression": "invalid",
                "sync_type": "replace",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_preset_periods_and_minimum_interval(self):
        for setting in [
            {"schedule_type": "weekly", "days": [1], "time": ["01:00"]},
            {"schedule_type": "monthly", "days": [31], "time": ["01:00"]},
            {"schedule_type": "interval", "interval_unit": "hours", "interval_value": 1},
            {"schedule_type": "interval", "interval_unit": "minutes", "interval_value": 5},
        ]:
            with self.subTest(setting=setting):
                serializer = KnowledgeSyncSettingRequest(data={"enabled": True, "sync_type": "incremental", **setting})
                self.assertTrue(serializer.is_valid(), serializer.errors)
        for setting in [
            {"schedule_type": "interval", "interval_unit": "minutes", "interval_value": 4},
            {"schedule_type": "cron", "cron_expression": "*/4 * * * *"},
            {"schedule_type": "daily", "time": ["01:00", "01:03"]},
        ]:
            with self.subTest(setting=setting):
                serializer = KnowledgeSyncSettingRequest(data={"enabled": True, "sync_type": "incremental", **setting})
                self.assertFalse(serializer.is_valid())

    @patch("knowledge.services.knowledge_sync_schedule._get_scheduler")
    @patch("knowledge.services.knowledge_sync_schedule.QuerySet")
    def test_enabled_setting_deploys_one_replaceable_job(self, query_set, get_scheduler):
        scheduler = get_scheduler.return_value
        scheduler.get_job.return_value = None
        knowledge = MagicMock(
            id="00000000-0000-0000-0000-000000000021",
            meta={
                "sync_setting": {
                    "enabled": True,
                    "schedule_type": "daily",
                    "time": "02:00",
                    "sync_type": "incremental",
                }
            },
        )
        query_set.return_value.filter.return_value.first.return_value = knowledge

        self.assertTrue(deploy_knowledge_sync_job(knowledge.id))

        self.assertEqual(scheduler.add_job.call_count, 1)
        self.assertTrue(scheduler.add_job.call_args.kwargs["replace_existing"])
        self.assertEqual(scheduler.add_job.call_args.kwargs["id"], f"knowledge:sync:{knowledge.id}")

    @patch("knowledge.task.sync.sync_replace_web_knowledge.delay")
    @patch("knowledge.task.sync.QuerySet")
    def test_scheduled_entry_uses_saved_strategy_and_sync_type_and_records_log(self, query_set, delay):
        strategy = normalize_document_strategy(
            {"visual": {"enabled": True, "strategy": "model", "model_id": "00000000-0000-0000-0000-000000000043"}}
        )
        knowledge = MagicMock(
            id="00000000-0000-0000-0000-000000000022",
            user_id="00000000-0000-0000-0000-000000000023",
            meta={
                "source_url": "https://example.com",
                "selector": "body",
                "doc_strategy": strategy,
                "sync_setting": {"enabled": True, "sync_type": "complete"},
            },
        )
        query_set.return_value.filter.return_value.first.return_value = knowledge

        self.assertTrue(scheduled_sync_web_knowledge.run(str(knowledge.id)))

        self.assertEqual(delay.call_args.args[-1], "complete")
        self.assertEqual(delay.call_args.args[4], strategy)
        self.assertTrue(delay.call_args.kwargs["record_log"])
        self.assertEqual(delay.call_args.kwargs["trigger_type"], KnowledgeSyncTrigger.SCHEDULED)

    @patch("knowledge.serializers.knowledge_sync.QuerySet")
    def test_setting_operation_accepts_lark_and_workflow_knowledge(self, query_set):
        for knowledge_type in [KnowledgeType.LARK, KnowledgeType.WORKFLOW]:
            with self.subTest(knowledge_type=knowledge_type):
                knowledge = MagicMock(type=knowledge_type, meta={})
                query_set.return_value.filter.return_value.first.return_value = knowledge
                serializer = KnowledgeSyncSettingOperationSerializer(
                    data={
                        "workspace_id": "workspace-id",
                        "knowledge_id": "00000000-0000-0000-0000-000000000024",
                    }
                )

                self.assertFalse(serializer.get_setting()["enabled"])

    @patch("knowledge.task.sync.celery_app.send_task")
    @patch("knowledge.task.sync.KnowledgeSyncLog.objects.create")
    @patch("knowledge.task.sync.QuerySet")
    def test_generic_scheduled_entry_dispatches_lark_task(self, query_set, create_log, send_task):
        knowledge = MagicMock(
            id="00000000-0000-0000-0000-000000000025",
            type=KnowledgeType.LARK,
            workspace_id="workspace-id",
            meta={"sync_setting": {"enabled": True}},
        )
        knowledge_query = MagicMock()
        knowledge_query.select_for_update.return_value.filter.return_value.first.return_value = knowledge
        log_query = MagicMock()
        log_query.filter.return_value.exists.return_value = False
        query_set.side_effect = lambda model: knowledge_query if model is Knowledge else log_query
        sync_log = MagicMock(id="00000000-0000-0000-0000-000000000030")
        create_log.return_value = sync_log

        with patch("knowledge.task.sync.transaction.atomic", return_value=nullcontext()):
            self.assertTrue(scheduled_sync_knowledge.run(str(knowledge.id)))

        send_task.assert_called_once_with(
            "celery:scheduled_sync_lark_knowledge", args=[str(knowledge.id), str(sync_log.id)]
        )
        self.assertEqual(create_log.call_args.kwargs["status"], KnowledgeSyncStatus.RUNNING)

    @patch("knowledge.task.sync.has_running_workflow_document_sync", return_value=False)
    @patch("knowledge.task.sync.scheduled_sync_workflow_knowledge.delay")
    @patch("knowledge.task.sync.KnowledgeSyncLog.objects.create")
    @patch("knowledge.task.sync.QuerySet")
    def test_generic_scheduled_entry_dispatches_workflow_task(self, query_set, create_log, delay, _running):
        knowledge = MagicMock(
            id="00000000-0000-0000-0000-000000000026",
            type=KnowledgeType.WORKFLOW,
            workspace_id="workspace-id",
            meta={"sync_setting": {"enabled": True}},
        )
        knowledge_query = MagicMock()
        knowledge_query.select_for_update.return_value.filter.return_value.first.return_value = knowledge
        log_query = MagicMock()
        log_query.filter.return_value.exists.return_value = False
        query_set.side_effect = lambda model: knowledge_query if model is Knowledge else log_query
        sync_log = MagicMock(id="00000000-0000-0000-0000-000000000031")
        create_log.return_value = sync_log

        with patch("knowledge.task.sync.transaction.atomic", return_value=nullcontext()):
            self.assertTrue(scheduled_sync_knowledge.run(str(knowledge.id)))

        delay.assert_called_once_with(str(knowledge.id), str(sync_log.id))

    @patch("knowledge.task.sync.celery_app.send_task")
    @patch("knowledge.task.sync.KnowledgeSyncLog.objects.create")
    @patch("knowledge.task.sync.QuerySet")
    def test_overlapping_schedule_is_skipped_with_a_log(self, query_set, create_log, send_task):
        knowledge = MagicMock(
            id="00000000-0000-0000-0000-000000000032",
            type=KnowledgeType.LARK,
            workspace_id="workspace-id",
            meta={"sync_setting": {"enabled": True, "sync_type": "incremental"}},
        )
        knowledge_query = MagicMock()
        knowledge_query.select_for_update.return_value.filter.return_value.first.return_value = knowledge
        log_query = MagicMock()
        log_query.filter.return_value.exists.return_value = True
        query_set.side_effect = lambda model: knowledge_query if model is Knowledge else log_query

        with patch("knowledge.task.sync.transaction.atomic", return_value=nullcontext()):
            self.assertFalse(scheduled_sync_knowledge.run(str(knowledge.id)))

        self.assertEqual(create_log.call_args.kwargs["status"], KnowledgeSyncStatus.SKIPPED)
        send_task.assert_not_called()


class WorkflowKnowledgeScheduleTests(SimpleTestCase):
    def setUp(self):
        super().setUp()
        heartbeat_patch = patch("knowledge.task.sync.start_sync_heartbeat", return_value=lambda: None)
        heartbeat_patch.start()
        self.addCleanup(heartbeat_patch.stop)
        heartbeat_patch = patch("knowledge.task.sync.recover_stale_sync_logs", return_value=lambda: None)
        heartbeat_patch.start()
        self.addCleanup(heartbeat_patch.stop)
        heartbeat_patch = patch(
            "knowledge.serializers.knowledge_workflow.start_sync_heartbeat", return_value=lambda: None
        )
        heartbeat_patch.start()
        self.addCleanup(heartbeat_patch.stop)

    @patch("knowledge.services.workflow_sync.schedule_workflow_document_embedding")
    @patch("knowledge.services.workflow_sync._delete_workflow_documents")
    @patch("knowledge.services.workflow_sync.QuerySet")
    def test_complete_snapshot_replaces_old_only_after_success(self, query_set, delete_documents, schedule_embedding):
        sync_log = MagicMock(knowledge_id="knowledge-id", create_time=timezone.now())
        document_query = MagicMock()
        new_query = MagicMock()
        old_query = MagicMock()
        new_query.values_list.return_value = ["new-id"]
        new_query.__iter__.return_value = [SimpleNamespace(id="new-id", name="new", meta={})]
        old_query.values_list.return_value = ["old-id"]
        document_query.filter.return_value = document_query
        document_query.filter.side_effect = lambda **filters: (
            new_query
            if "meta__workflow_sync_log_id" in filters
            else old_query
            if "create_time__lt" in filters
            else document_query
        )
        document_query.count.return_value = 1
        query_set.return_value = document_query
        delete_documents.side_effect = lambda document_ids: list(document_ids)

        source = {"source_scope": "scope"}
        success = finalize_workflow_complete_snapshot.__wrapped__(sync_log, True, source)
        self.assertEqual(success["synced_count"], 1)
        self.assertEqual(success["deleted_count"], 1)
        delete_documents.assert_called_with(["old-id"])
        schedule_embedding.assert_called_once_with(["new-id"], "knowledge-id")

        failure = finalize_workflow_complete_snapshot.__wrapped__(sync_log, False, source)
        self.assertEqual(failure["failed_count"], 1)
        delete_documents.assert_called_with(["new-id"])
        schedule_embedding.assert_called_once()

    @override("en-us")
    def test_schedule_accepts_web_and_tool_sources_but_rejects_local_source(self):
        for node_type in ("data-source-web-node", "tool-lib-node"):
            with self.subTest(node_type=node_type):
                validate_workflow_sync_source(
                    {"nodes": [{"id": "source", "type": node_type, "properties": {"kind": "data-source"}}]},
                    {"data_source": {"node_id": "source", "source_url": "https://example.com"}},
                )
        with self.assertRaisesRegex(ValueError, "Local file"):
            validate_workflow_sync_source(
                {"nodes": [{"id": "source", "type": "data-source-local-node", "properties": {"kind": "data-source"}}]},
                {"data_source": {"node_id": "source"}},
            )
        with self.assertRaisesRegex(ValueError, "no longer exists"):
            validate_workflow_sync_source({"nodes": []}, {"data_source": {"node_id": "source"}})
        with self.assertRaisesRegex(ValueError, "source URL"):
            validate_workflow_sync_source(
                {"nodes": [{"id": "source", "type": "data-source-web-node", "properties": {"kind": "data-source"}}]},
                {"data_source": {"node_id": "source"}},
            )

    @override("en-us")
    def test_schedule_accepts_remote_tool_folder_but_rejects_uploaded_files(self):
        tool_flow = {"nodes": [{"id": "source", "type": "tool-lib-node", "properties": {"kind": "data-source"}}]}
        validate_workflow_sync_source(
            tool_flow,
            {"data_source": {"node_id": "source", "file_list": [{"type": "folder", "token": "folder-token"}]}},
        )
        with self.assertRaisesRegex(ValueError, "Local file"):
            validate_workflow_sync_source(
                tool_flow,
                {"data_source": {"node_id": "source", "file_list": [{"file_id": "uploaded-file-id"}]}},
            )

    @patch("knowledge.task.sync.KnowledgeWorkflowActionSerializer")
    @patch("knowledge.task.sync.KnowledgeSyncLog.objects.create")
    @patch("knowledge.task.sync.QuerySet")
    def test_local_file_input_is_not_scheduled(self, query_set, create_log, action_serializer):
        knowledge = MagicMock(
            id="00000000-0000-0000-0000-000000000037",
            workspace_id="workspace-id",
            type=KnowledgeType.WORKFLOW,
            user=MagicMock(),
            meta={
                "sync_setting": {"enabled": True, "sync_type": "incremental"},
                "workflow_sync_input": {
                    "data_source": {"node_id": "start-node", "file_list": [{"file_id": "file-id"}]}
                },
            },
        )
        knowledge_query = MagicMock()
        knowledge_query.filter.return_value.first.return_value = knowledge
        log_query = MagicMock()
        log_query.filter.return_value.exists.return_value = False
        document_query = MagicMock()
        document_query.filter.return_value.count.return_value = 1
        workflow_query = MagicMock()
        workflow_query.filter.return_value.values_list.return_value.first.return_value = {
            "nodes": [{"id": "start-node", "type": "data-source-local-node", "properties": {"kind": "data-source"}}]
        }
        query_set.side_effect = lambda model: {
            Knowledge: knowledge_query,
            KnowledgeSyncLog: log_query,
            KnowledgeWorkflow: workflow_query,
        }.get(model, document_query)
        create_log.return_value = MagicMock(id="00000000-0000-0000-0000-000000000038")

        self.assertFalse(scheduled_sync_workflow_knowledge.run(str(knowledge.id)))

        action_serializer.assert_not_called()
        self.assertEqual(log_query.filter.return_value.update.call_args.kwargs["status"], KnowledgeSyncStatus.FAILURE)

    @patch("knowledge.serializers.knowledge_workflow.merge_workflow_incremental_snapshot")
    @patch("knowledge.serializers.knowledge_workflow.QuerySet")
    def test_incremental_workflow_uses_stable_snapshot_merge(self, query_set, merge_workflow_snapshot):
        sync_log = MagicMock(
            status=KnowledgeSyncStatus.RUNNING,
            id="00000000-0000-0000-0000-000000000032",
            knowledge_id="00000000-0000-0000-0000-000000000033",
            create_time=timezone.now(),
            sync_type=KnowledgeSyncType.INCREMENTAL,
        )
        action_query = MagicMock()
        log_query = MagicMock()
        log_query.filter.return_value.first.return_value = sync_log
        log_query.select_for_update.return_value.get.return_value = sync_log
        query_set.side_effect = lambda model: log_query if model is KnowledgeSyncLog else action_query
        merge_workflow_snapshot.return_value = {
            "total_count": 1,
            "synced_count": 0,
            "skipped_count": 1,
            "deleted_count": 0,
            "failed_count": 0,
        }
        document_cleanup = MagicMock()

        # 新引擎:完成收尾由 finalize_knowledge_action 内联处理,state/run_time 由调用方算好传入
        finalize_knowledge_action.__wrapped__(
            "00000000-0000-0000-0000-000000000036",
            KnowledgeActionState.SUCCESS,
            0.0,
            str(sync_log.id),
            document_cleanup,
        )

        merge_workflow_snapshot.assert_called_once_with(sync_log, None)
        update = log_query.filter.return_value.update.call_args.kwargs
        self.assertEqual(update["status"], KnowledgeSyncStatus.SUCCESS)
        self.assertEqual(update["synced_count"], 0)
        self.assertEqual(update["skipped_count"], 1)

    @patch("knowledge.task.sync.KnowledgeWorkflowActionSerializer")
    @patch("knowledge.task.sync.KnowledgeSyncLog.objects.create")
    @patch("knowledge.task.sync.QuerySet")
    def test_scheduled_workflow_uses_saved_input_and_starts_an_action(self, query_set, create_log, action_serializer):
        knowledge = MagicMock(
            id="00000000-0000-0000-0000-000000000027",
            workspace_id="workspace-id",
            type=KnowledgeType.WORKFLOW,
            user=MagicMock(),
            meta={
                "sync_setting": {"enabled": True, "sync_type": "incremental"},
                "workflow_sync_input": {
                    "data_source": {"node_id": "start-node", "source_url": "https://example.com"},
                    "knowledge_base": {},
                },
            },
        )
        knowledge_query = MagicMock()
        knowledge_query.filter.return_value.first.return_value = knowledge
        log_query = MagicMock()
        log_query.filter.return_value.exists.return_value = False
        document_query = MagicMock()
        document_query.filter.return_value.count.return_value = 2
        workflow_query = MagicMock()
        workflow_query.filter.return_value.values_list.return_value.first.return_value = {
            "nodes": [{"id": "start-node", "type": "data-source-web-node", "properties": {"kind": "data-source"}}]
        }
        query_set.side_effect = lambda model: {
            Knowledge: knowledge_query,
            KnowledgeSyncLog: log_query,
            KnowledgeWorkflow: workflow_query,
        }.get(model, document_query)
        sync_log = MagicMock(id="00000000-0000-0000-0000-000000000028")
        create_log.return_value = sync_log
        action_serializer.return_value.action.return_value = {"id": "00000000-0000-0000-0000-000000000029"}

        self.assertTrue(scheduled_sync_workflow_knowledge.run(str(knowledge.id)))

        workflow_input = action_serializer.return_value.action.call_args.args[0]
        self.assertEqual(workflow_input["data_source"], {"node_id": "start-node", "source_url": "https://example.com"})
        action_serializer.return_value.action.assert_called_once_with(
            workflow_input,
            knowledge.user,
            True,
            str(sync_log.id),
        )

        knowledge.meta["sync_setting"]["sync_type"] = "complete"
        with patch("knowledge.task.sync.delete_document_data") as delete_documents:
            self.assertTrue(scheduled_sync_workflow_knowledge.run(str(knowledge.id)))
        delete_documents.assert_not_called()

        knowledge.meta["sync_setting"]["sync_type"] = "incremental"
        knowledge.meta["workflow_sync_input"]["data_source"] = {
            "node_id": "start-node",
            "file_list": [{"type": "folder", "token": "folder-token"}],
        }
        workflow_query.filter.return_value.values_list.return_value.first.return_value = {
            "nodes": [{"id": "start-node", "type": "tool-lib-node", "properties": {"kind": "data-source"}}]
        }
        self.assertTrue(scheduled_sync_workflow_knowledge.run(str(knowledge.id)))
        self.assertEqual(
            action_serializer.return_value.action.call_args.args[0]["data_source"]["file_list"],
            [{"type": "folder", "token": "folder-token"}],
        )

    @patch("knowledge.serializers.knowledge_workflow.WorkflowRunRegistry")
    @patch("knowledge.serializers.knowledge_workflow.new_instance")
    @patch("knowledge.serializers.knowledge_workflow.WorkflowManage")
    @patch("knowledge.serializers.knowledge_workflow.KnowledgeAction.save")
    @patch("knowledge.serializers.knowledge_workflow.QuerySet")
    def test_manual_action_saves_input_for_later_scheduled_runs(
        self, query_set, _save_action, workflow_manage, _new_instance, _registry
    ):
        workflow = MagicMock(work_flow={})
        knowledge = MagicMock(
            id="00000000-0000-0000-0000-000000000030",
            name="workflow knowledge",
            desc="desc",
            workspace_id="workspace-id",
            meta={"existing": True},
        )

        def query_for(model):
            query = MagicMock()
            query.filter.return_value.first.return_value = (
                workflow if model.__name__ == "KnowledgeWorkflow" else knowledge
            )
            return query

        query_set.side_effect = query_for
        user = MagicMock(id="00000000-0000-0000-0000-000000000031", username="owner")
        workflow_input = {
            "data_source": {"node_id": "start-node", "files": ["a.docx"]},
            "knowledge_base": {"custom": "value"},
        }

        serializer = KnowledgeWorkflowActionSerializer(
            data={"workspace_id": knowledge.workspace_id, "knowledge_id": str(knowledge.id)}
        )
        serializer.is_valid(raise_exception=True)
        serializer.action(workflow_input, user, with_valid=False)

        self.assertEqual(
            knowledge.meta["workflow_sync_input"],
            {
                "data_source": {"node_id": "start-node", "files": ["a.docx"]},
                "knowledge_base": {"custom": "value"},
            },
        )
        knowledge.save.assert_called_once_with(update_fields=["meta", "update_time"])
        workflow_manage.return_value.run.assert_called_once_with()
