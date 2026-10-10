from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from knowledge.models import (
    Document,
    DocumentResourceType,
    KnowledgeSyncType,
    KnowledgeType,
    Knowledge,
    KnowledgeWorkflow,
    KnowledgeWorkflowVersion,
)
from knowledge.services.workflow_sync import (
    _delete_workflow_documents,
    finalize_workflow_complete_snapshot,
    merge_workflow_incremental_snapshot,
    workflow_document_identity,
)
from knowledge.services.workflow_sync_source import tool_document_source_meta, workflow_source_meta
from knowledge.serializers.knowledge_workflow import KnowledgeWorkflowActionSerializer, finalize_knowledge_action
from knowledge.models import KnowledgeSyncLog, KnowledgeSyncStatus
from knowledge.models.knowledge_action import State
from knowledge.serializers.knowledge_sync import KnowledgeSyncLogSerializer
from knowledge.task.sync import scheduled_sync_workflow_knowledge


class WorkflowSourceMetaTests(SimpleTestCase):
    def test_remote_folder_rename_and_selection_order_do_not_change_scope(self):
        workflow = {
            "nodes": [
                {"id": "source", "type": "tool-lib-node", "properties": {"node_data": {"tool_lib_id": "lark-tool"}}}
            ]
        }
        inputs = {"data_source": {"node_id": "source", "file_list": [{"token": "a", "name": "old"}, {"token": "b"}]}}
        first = workflow_source_meta(workflow, inputs)
        inputs["data_source"]["file_list"] = [{"token": "b"}, {"token": "a", "name": "renamed"}]
        self.assertEqual(first, workflow_source_meta(workflow, inputs))
        inputs["data_source"]["file_list"] = [{"token": "other-folder"}]
        self.assertNotEqual(first["source_scope"], workflow_source_meta(workflow, inputs)["source_scope"])

    def test_web_root_and_source_node_are_isolated_without_copying_credentials(self):
        workflow = {"nodes": [{"id": "source", "type": "data-source-web-node"}]}
        inputs = {
            "data_source": {"node_id": "source", "source_url": "https://example.com/a", "password": "do-not-store"}
        }
        first = workflow_source_meta(workflow, inputs)
        inputs["data_source"]["source_url"] = "https://example.com/b"
        self.assertNotEqual(first["source_scope"], workflow_source_meta(workflow, inputs)["source_scope"])
        self.assertNotIn("password", first)
        self.assertNotIn("do-not-store", str(first))

    def test_remote_token_alias_is_retained_without_download_secrets(self):
        meta = tool_document_source_meta(
            {"document_token": "remote", "type": "docx", "app_secret": "secret"},
            {"file_bytes": ["bytes"], "access_token": "secret"},
            "node",
            "tool",
            "飞书数据源",
        )
        self.assertEqual(meta["token"], "remote")
        self.assertEqual(meta["source_tool_id"], "tool")
        self.assertNotIn("secret", str(meta))
        nested = tool_document_source_meta({}, {"meta": {"file_token": "nested"}}, "node", "tool", "tool")
        self.assertEqual(nested["token"], "nested")

    def test_download_item_string_and_remote_id_are_stable_identifiers(self):
        self.assertEqual(
            tool_document_source_meta("remote-key", {}, "node", "tool", "tool")["source_key"], "remote-key"
        )
        self.assertEqual(
            tool_document_source_meta({"id": "remote-id"}, {}, "node", "tool", "tool")["source_id"], "remote-id"
        )

    def test_rename_matches_by_token_but_identical_tokens_in_other_sources_do_not(self):
        first = Document(name="old", meta={"source_scope": "scope-a", "token": "token"})
        renamed = Document(name="renamed", meta={"source_scope": "scope-a", "token": "token"})
        other = Document(name="old", meta={"source_scope": "scope-b", "token": "token"})
        self.assertEqual(workflow_document_identity(first), workflow_document_identity(renamed))
        self.assertNotEqual(workflow_document_identity(first), workflow_document_identity(other))


class SnapshotQuery:
    """Evaluate the queryset predicates against mixed-source regression fixtures."""

    def __init__(self, documents):
        self.documents = documents

    def filter(self, **filters):
        def matches(document):
            for lookup, expected in filters.items():
                value = document
                parts = lookup.split("__")
                less_than = parts[-1] == "lt"
                for field in parts[:-1] if less_than else parts:
                    value = value.get(field) if isinstance(value, dict) else getattr(value, field, None)
                if less_than:
                    if not value < expected:
                        return False
                elif value != expected:
                    return False
            return True

        return SnapshotQuery([document for document in self.documents if matches(document)])

    def none(self):
        return SnapshotQuery([])

    def values_list(self, field, flat=False):
        return [getattr(document, field) for document in self.documents]

    def count(self):
        return len(self.documents)

    def __iter__(self):
        return iter(self.documents)


class WorkflowSnapshotIsolationTests(SimpleTestCase):
    def setUp(self):
        self.sync_log = SimpleNamespace(
            id="log", knowledge_id="knowledge", create_time=10, sync_type=KnowledgeSyncType.INCREMENTAL
        )
        self.source = {"source_scope": "scope"}
        self.documents = [
            self.document("old", 1, {"source_scope": "scope", "token": "old"}),
            self.document("local", 1, {"source_scope": "local-scope", "source_type": "local"}),
            self.document("other-source", 1, {"source_scope": "other-scope"}),
            self.document("legacy", 1, {}),
            self.document("new", 11, {"source_scope": "scope", "workflow_sync_log_id": "log", "token": "new"}),
            self.document("concurrent", 12, {"source_scope": "scope", "workflow_sync_log_id": "other-log"}),
        ]

    def document(self, document_id, created_at, meta):
        return SimpleNamespace(
            id=document_id,
            name=document_id,
            knowledge_id="knowledge",
            create_time=created_at,
            type=KnowledgeType.WORKFLOW,
            resource_type=DocumentResourceType.DOCUMENT,
            meta=meta,
        )

    def query(self, model):
        return SnapshotQuery(self.documents) if model is Document else MagicMock()

    def delete(self, document_ids):
        self.documents = [document for document in self.documents if document.id not in document_ids]
        return document_ids

    def run_complete(self, success, source=None):
        with (
            patch("knowledge.services.workflow_sync.QuerySet", side_effect=self.query),
            patch(
                "knowledge.services.workflow_sync._delete_workflow_documents",
                side_effect=self.delete,
            ),
        ):
            return finalize_workflow_complete_snapshot.__wrapped__(self.sync_log, success, source)

    def test_complete_sync_deletes_only_older_documents_from_selected_source(self):
        stats = self.run_complete(True, self.source)
        self.assertEqual(stats["total_count"], 1)
        self.assertEqual(stats["deleted_count"], 1)
        self.assertEqual(
            {document.id for document in self.documents}, {"local", "other-source", "legacy", "new", "concurrent"}
        )

    def test_failed_run_deletes_only_its_own_output(self):
        stats = self.run_complete(False, self.source)
        self.assertEqual(stats["total_count"], 1)
        self.assertEqual(stats["failed_count"], 1)
        self.assertEqual(
            {document.id for document in self.documents}, {"old", "local", "other-source", "legacy", "concurrent"}
        )

    def test_missing_source_scope_never_deletes_legacy_documents(self):
        self.run_complete(True)
        self.assertIn("old", {document.id for document in self.documents})
        self.assertIn("legacy", {document.id for document in self.documents})

    def test_empty_incremental_snapshot_cleans_only_its_proven_source(self):
        self.documents = [document for document in self.documents if document.id != "new"]
        with (
            patch("knowledge.services.workflow_sync.QuerySet", side_effect=self.query),
            patch(
                "knowledge.services.workflow_sync._delete_workflow_documents",
                side_effect=self.delete,
            ),
        ):
            stats = merge_workflow_incremental_snapshot.__wrapped__(self.sync_log, self.source)
        self.assertEqual(stats["total_count"], 1)
        self.assertEqual(stats["deleted_count"], 1)
        self.assertEqual(
            {document.id for document in self.documents}, {"local", "other-source", "legacy", "concurrent"}
        )

    def test_empty_replace_snapshot_preserves_unmatched_documents(self):
        self.documents = [document for document in self.documents if document.id != "new"]
        self.sync_log.sync_type = KnowledgeSyncType.REPLACE
        with (
            patch("knowledge.services.workflow_sync.QuerySet", side_effect=self.query),
            patch(
                "knowledge.services.workflow_sync._delete_workflow_documents",
                side_effect=self.delete,
            ),
        ):
            stats = merge_workflow_incremental_snapshot.__wrapped__(self.sync_log, self.source)
        self.assertEqual(stats["total_count"], 0)
        self.assertEqual(stats["deleted_count"], 0)
        self.assertIn("old", {document.id for document in self.documents})

    @patch("knowledge.services.workflow_sync._copy_document_relations")
    @patch("knowledge.services.workflow_sync.process_visual_assets")
    @patch("knowledge.services.workflow_sync.sync_paragraph_assets")
    @patch("knowledge.services.workflow_sync.transaction.atomic")
    @patch("knowledge.services.workflow_sync.IncrementalDocumentSync")
    def test_unchanged_web_documents_exclude_local_upload_from_sync_total(self, merger, *_mocks):
        merger.return_value.merge.return_value = SimpleNamespace(reembed_ids=[], disabled_ids=[])
        for sync_type in (KnowledgeSyncType.INCREMENTAL, KnowledgeSyncType.REPLACE):
            with self.subTest(sync_type=sync_type):
                self.sync_log.sync_type = sync_type
                local_document = self.document("local", 1, {"source_scope": "local-scope", "source_type": "local"})
                self.documents = [local_document]
                for index in range(25):
                    meta = {"source_scope": "scope", "source_type": "web", "source_url": f"https://example.com/{index}"}
                    old_document = self.document(f"old-{index}", 1, meta)
                    new_document = self.document(f"new-{index}", 11, {**meta, "workflow_sync_log_id": "log"})
                    for document in (old_document, new_document):
                        document.doc_strategy = {}
                        document.visual_strategy_hash = ""
                        document.save = MagicMock()
                    self.documents.extend([old_document, new_document])
                with (
                    patch("knowledge.services.workflow_sync.QuerySet", side_effect=self.query),
                    patch("knowledge.services.workflow_sync._delete_workflow_documents", side_effect=self.delete),
                ):
                    stats = merge_workflow_incremental_snapshot.__wrapped__(self.sync_log, self.source)
                self.assertEqual(stats["total_count"], 25)
                self.assertEqual(stats["skipped_count"], 25)
                self.assertEqual(stats["synced_count"], 0)
                self.assertEqual(stats["deleted_count"], 0)
                self.assertEqual(stats["failed_count"], 0)
                self.assertIn(local_document, self.documents)

    def test_incremental_total_includes_new_and_deleted_source_documents_only(self):
        with (
            patch("knowledge.services.workflow_sync.QuerySet", side_effect=self.query),
            patch("knowledge.services.workflow_sync._delete_workflow_documents", side_effect=self.delete),
        ):
            stats = merge_workflow_incremental_snapshot.__wrapped__(self.sync_log, self.source)
        self.assertEqual(stats["total_count"], 2)
        self.assertEqual(stats["synced_count"], 1)
        self.assertEqual(stats["deleted_count"], 1)

    def test_duplicate_remote_identity_fails_before_changing_old_documents(self):
        duplicate = deepcopy(self.documents[4])
        duplicate.id = "duplicate"
        duplicate.name = "different title"
        self.documents.append(duplicate)
        with (
            patch("knowledge.services.workflow_sync.QuerySet", side_effect=self.query),
            self.assertRaisesRegex(ValueError, "duplicate source"),
        ):
            merge_workflow_incremental_snapshot.__wrapped__(self.sync_log, self.source)
        self.assertIn("old", {document.id for document in self.documents})

    def test_complete_sync_rejects_duplicate_output_and_preserves_old_data(self):
        duplicate = deepcopy(self.documents[4])
        duplicate.id = "duplicate"
        self.documents.append(duplicate)
        stats = self.run_complete(True, self.source)
        self.assertEqual(stats["failed_count"], 1)
        self.assertIn("old", {document.id for document in self.documents})
        self.assertNotIn("new", {document.id for document in self.documents})
        self.assertNotIn("duplicate", {document.id for document in self.documents})

    @patch("knowledge.services.workflow_sync.maxkb_logger")
    @patch("knowledge.services.workflow_sync.transaction.atomic")
    @patch("knowledge.services.workflow_sync.IncrementalDocumentSync")
    def test_merge_failure_keeps_old_snapshot_and_cleans_temporary_output(self, merger, _atomic, _logger):
        self.documents[4].meta["token"] = "old"
        self.documents[4].doc_strategy = {}
        merger.return_value.merge.side_effect = RuntimeError("merge failed")
        with (
            patch("knowledge.services.workflow_sync.QuerySet", side_effect=self.query),
            patch(
                "knowledge.services.workflow_sync._delete_workflow_documents",
                side_effect=self.delete,
            ),
        ):
            stats = merge_workflow_incremental_snapshot.__wrapped__(self.sync_log, self.source)
        self.assertEqual(stats["failed_count"], 1)
        self.assertEqual(stats["total_count"], 1)
        self.assertEqual(stats["deleted_count"], 0)
        self.assertIn("old", {document.id for document in self.documents})
        self.assertNotIn("new", {document.id for document in self.documents})


class WorkflowActionSourceTests(SimpleTestCase):
    def setUp(self):
        heartbeat_patch = patch(
            "knowledge.serializers.knowledge_workflow.start_sync_heartbeat", return_value=lambda: None
        )
        heartbeat_patch.start()
        self.addCleanup(heartbeat_patch.stop)

    @patch("knowledge.serializers.knowledge_workflow.KnowledgeAction")
    @patch("knowledge.serializers.knowledge_workflow.QuerySet")
    def test_published_remote_upload_also_saves_input_for_scheduling(self, query_set, _action):
        knowledge = SimpleNamespace(
            id="00000000-0000-0000-0000-000000000012",
            name="knowledge",
            desc="",
            workspace_id="workspace",
            meta={"sync_setting": {"enabled": True}},
            save=MagicMock(),
        )
        version = SimpleNamespace(
            work_flow={"nodes": [{"id": "web", "type": "data-source-web-node", "properties": {"kind": "data-source"}}]},
            default_model_setting={},
        )
        knowledge_query, workflow_query, version_query = MagicMock(), MagicMock(), MagicMock()
        knowledge_query.filter.return_value.first.return_value = knowledge
        workflow_query.filter.return_value.first.return_value = SimpleNamespace(is_publish=True)
        version_query.filter.return_value.order_by.return_value.__getitem__.return_value.first.return_value = version
        query_set.side_effect = lambda model: {
            Knowledge: knowledge_query,
            KnowledgeWorkflow: workflow_query,
            KnowledgeWorkflowVersion: version_query,
        }[model]
        serializer = KnowledgeWorkflowActionSerializer(
            data={"knowledge_id": str(knowledge.id), "workspace_id": "workspace"}
        )
        serializer.is_valid(raise_exception=True)
        source = {"node_id": "web", "source_url": "https://example.com"}
        with patch.object(serializer, "_launch_knowledge_workflow"):
            serializer.upload_document(
                {"data_source": source}, SimpleNamespace(id="user", username="user"), with_valid=False
            )
        self.assertEqual(knowledge.meta["workflow_sync_input"]["data_source"], source)
        knowledge.save.assert_called_once_with(update_fields=["meta", "update_time"])

    @patch("knowledge.serializers.knowledge_workflow.finalize_workflow_complete_snapshot")
    @patch("knowledge.serializers.knowledge_workflow.QuerySet")
    def test_failed_incremental_action_cleans_its_output_and_marks_log_failed(self, query_set, cleanup):
        log = SimpleNamespace(
            sync_type=KnowledgeSyncType.INCREMENTAL,
            status=KnowledgeSyncStatus.RUNNING,
            id="log",
            knowledge_id="knowledge",
        )
        log_query = MagicMock()
        log_query.filter.return_value.first.return_value = log
        log_query.select_for_update.return_value.get.return_value = log
        query_set.side_effect = lambda model: log_query if model is KnowledgeSyncLog else MagicMock()
        cleanup.return_value = {
            "total_count": 1,
            "synced_count": 0,
            "skipped_count": 0,
            "deleted_count": 1,
            "failed_count": 1,
        }
        source = {"source_scope": "scope"}
        finalize_knowledge_action.__wrapped__("action", State.FAILURE, 0.1, "log", MagicMock(), source)
        cleanup.assert_called_once_with(log, False, source)
        self.assertEqual(log_query.filter.return_value.update.call_args.kwargs["status"], KnowledgeSyncStatus.FAILURE)

    @patch("knowledge.serializers.knowledge_workflow.validate_knowledge_file_size")
    @patch("knowledge.serializers.knowledge_workflow.KnowledgeAction")
    @patch("knowledge.serializers.knowledge_workflow.QuerySet")
    def test_local_manual_upload_preserves_existing_scheduled_remote_input(self, query_set, _action, _size):
        remote_input = {"data_source": {"node_id": "web", "source_url": "https://example.com"}}
        knowledge = SimpleNamespace(
            id="00000000-0000-0000-0000-000000000010",
            name="knowledge",
            desc="",
            workspace_id="workspace",
            meta={"sync_setting": {"enabled": True}, "workflow_sync_input": deepcopy(remote_input)},
            save=MagicMock(),
        )
        workflow = SimpleNamespace(
            work_flow={
                "nodes": [{"id": "local", "type": "data-source-local-node", "properties": {"kind": "data-source"}}]
            },
            default_model_setting={},
        )
        query_set.return_value.filter.return_value.first.side_effect = [workflow, knowledge]
        serializer = KnowledgeWorkflowActionSerializer(
            data={"knowledge_id": str(knowledge.id), "workspace_id": "workspace"}
        )
        serializer.is_valid(raise_exception=True)
        with patch.object(serializer, "_launch_knowledge_workflow"):
            serializer.action(
                {"data_source": {"node_id": "local", "file_list": []}},
                SimpleNamespace(id="user", username="user"),
                with_valid=False,
            )
        self.assertEqual(knowledge.meta["workflow_sync_input"], remote_input)
        knowledge.save.assert_not_called()

    @patch("knowledge.serializers.knowledge_workflow.QuerySet")
    @patch("knowledge.serializers.knowledge_workflow.WorkflowRunRegistry")
    @patch("knowledge.serializers.knowledge_workflow.WorkflowManage")
    @patch("knowledge.serializers.knowledge_workflow.new_instance")
    def test_engine_receives_scope_and_sync_log_id(self, _new, workflow_manage, _registry, _query_set):
        serializer = KnowledgeWorkflowActionSerializer(
            data={"knowledge_id": "00000000-0000-0000-0000-000000000011", "workspace_id": "workspace"}
        )
        serializer.is_valid(raise_exception=True)
        workflow = {"nodes": [{"id": "web", "type": "data-source-web-node"}]}
        serializer._launch_knowledge_workflow(
            {"data_source": {"node_id": "web", "source_url": "https://example.com"}},
            SimpleNamespace(id="user"),
            "action",
            workflow,
            sync_log_id="log",
        )
        parameters = workflow_manage.call_args.args[1]
        self.assertEqual(parameters["sync_log_id"], "log")
        self.assertEqual(parameters["workflow_source"]["source_type"], "web")
        self.assertTrue(parameters["workflow_source"]["source_scope"])


class WorkflowSyncLogCountingTests(SimpleTestCase):
    def setUp(self):
        self.workflow_input = {"data_source": {"node_id": "web", "source_url": "https://example.com"}}
        self.workflow = {
            "nodes": [{"id": "web", "type": "data-source-web-node", "properties": {"kind": "data-source"}}]
        }
        self.source = workflow_source_meta(self.workflow, self.workflow_input)
        self.knowledge = SimpleNamespace(
            id="00000000-0000-0000-0000-000000000013",
            workspace_id="workspace",
            user=SimpleNamespace(id="user"),
            meta={"sync_setting": {"enabled": True}, "workflow_sync_input": self.workflow_input},
        )
        self.documents = [
            SimpleNamespace(
                knowledge_id=self.knowledge.id,
                type=KnowledgeType.WORKFLOW,
                resource_type=DocumentResourceType.DOCUMENT,
                meta={**self.source, "workflow_sync_log_id": "old-log"},
            )
            for _ in range(25)
        ]
        for meta in ({"source_scope": "local", "source_type": "local"}, {"source_scope": "other-source"}, {}):
            document = deepcopy(self.documents[0])
            document.meta = meta
            self.documents.append(document)
        image = deepcopy(self.documents[0])
        image.resource_type = DocumentResourceType.IMAGE
        self.documents.append(image)

    @patch("knowledge.task.sync.KnowledgeWorkflowActionSerializer")
    @patch("knowledge.task.sync.KnowledgeSyncLog.objects.create")
    @patch("knowledge.task.sync.QuerySet")
    def test_scheduled_run_starts_with_selected_web_source_total(self, query_set, create_log, action):
        knowledge_query, workflow_query, log_query = MagicMock(), MagicMock(), MagicMock()
        knowledge_query.filter.return_value.first.return_value = self.knowledge
        workflow_query.filter.return_value.values_list.return_value.first.return_value = self.workflow
        log_query.filter.return_value.exists.return_value = False
        query_set.side_effect = lambda model: {
            Knowledge: knowledge_query,
            KnowledgeWorkflow: workflow_query,
            KnowledgeSyncLog: log_query,
            Document: SnapshotQuery(self.documents),
        }[model]
        action.return_value.action.return_value = {"id": "action"}
        self.assertTrue(scheduled_sync_workflow_knowledge.run(self.knowledge.id))
        self.assertEqual(create_log.call_args.kwargs["total_count"], 25)
        action.return_value.action.assert_called_once_with(
            self.workflow_input, self.knowledge.user, True, str(create_log.return_value.id)
        )

    @patch("knowledge.serializers.knowledge_workflow.QuerySet")
    def test_completion_without_merger_counts_only_this_execution_output(self, query_set):
        log = SimpleNamespace(
            id="log",
            knowledge_id=self.knowledge.id,
            sync_type=KnowledgeSyncType.INCREMENTAL,
            status=KnowledgeSyncStatus.RUNNING,
            deleted_count=0,
        )
        log_query = MagicMock()
        log_query.filter.return_value.first.return_value = log
        log_query.select_for_update.return_value.get.return_value = log
        query_set.side_effect = lambda model: (
            SnapshotQuery(self.documents)
            if model is Document
            else log_query
            if model is KnowledgeSyncLog
            else MagicMock()
        )
        for _ in range(2):
            document = deepcopy(self.documents[0])
            document.meta["workflow_sync_log_id"] = "log"
            self.documents.append(document)
        finalize_knowledge_action.__wrapped__("action", State.SUCCESS, 1.0, "log")
        stats = log_query.filter.return_value.update.call_args.kwargs
        self.assertEqual(stats["total_count"], 2)
        self.assertEqual(stats["synced_count"], 2)
        self.assertEqual(stats["status"], KnowledgeSyncStatus.SUCCESS)


class HistoricalWorkflowSyncLogTests(SimpleTestCase):
    def serialize(self, *, knowledge_type=KnowledgeType.WORKFLOW, **counts):
        log = KnowledgeSyncLog(
            total_count=26,
            status=counts.pop("status", KnowledgeSyncStatus.SUCCESS),
            sync_type=counts.pop("sync_type", KnowledgeSyncType.INCREMENTAL),
            **counts,
        )
        return KnowledgeSyncLogSerializer(log, context={"knowledge_type": knowledge_type}).data

    def test_existing_mixed_source_log_displays_actual_sync_total(self):
        data = self.serialize(skipped_count=25)
        self.assertEqual(data["total_count"], 25)
        self.assertEqual(data["skipped_count"], 25)
        self.assertEqual(data["synced_count"], 0)

    def test_existing_incremental_log_includes_deletions(self):
        data = self.serialize(synced_count=2, skipped_count=22, deleted_count=1)
        self.assertEqual(data["total_count"], 25)

    def test_existing_complete_log_does_not_count_both_versions_of_the_snapshot(self):
        data = self.serialize(sync_type=KnowledgeSyncType.COMPLETE, synced_count=25, deleted_count=25)
        self.assertEqual(data["total_count"], 25)

    def test_running_failed_and_other_knowledge_logs_keep_recorded_total(self):
        for status in (KnowledgeSyncStatus.RUNNING, KnowledgeSyncStatus.FAILURE, KnowledgeSyncStatus.SKIPPED):
            with self.subTest(status=status):
                self.assertEqual(self.serialize(status=status, skipped_count=25)["total_count"], 26)
        for knowledge_type in (KnowledgeType.WEB, KnowledgeType.LARK):
            with self.subTest(knowledge_type=knowledge_type):
                self.assertEqual(self.serialize(knowledge_type=knowledge_type, skipped_count=25)["total_count"], 26)


class WorkflowSourceFileCleanupTests(SimpleTestCase):
    @patch("knowledge.services.workflow_sync._delete_problems_and_mappings")
    @patch("knowledge.services.workflow_sync.QuerySet")
    def test_cleanup_keeps_input_file_referenced_by_another_document(self, query_set, _problems):
        from knowledge.models import File

        document_query, file_query = MagicMock(), MagicMock()
        document_query.filter.return_value.values_list.side_effect = [["removed-document"], ["shared-file"]]
        document_query.exclude.return_value.filter.return_value.values_list.return_value = ["shared-file"]
        query_set.side_effect = lambda model: {Document: document_query, File: file_query}.get(model, MagicMock())
        _delete_workflow_documents(["removed-document"])
        file_query.filter.return_value.exclude.assert_called_once_with(id__in=["shared-file"])
