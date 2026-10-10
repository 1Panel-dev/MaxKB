from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from application.workflow.nodes.data_source_web_node.data_source_web_node import DataSourceWebNode
from common.auth.struct.auth import Principal
from common.constants.authentication_type import UserType
from common.exception.app_exception import AppApiException
from common.utils.fork import Fork
from knowledge.models import (
    Document,
    DocumentResourceType,
    Knowledge,
    KnowledgeSyncLog,
    KnowledgeSyncStatus,
    KnowledgeSyncTrigger,
    KnowledgeSyncType,
    KnowledgeType,
    KnowledgeWorkflow,
    File,
)
from knowledge.models.knowledge_action import State
from knowledge.serializers.document import DocumentSerializers
from knowledge.serializers.knowledge_workflow import KnowledgeWorkflowActionSerializer, finalize_knowledge_action
from knowledge.services.workflow_document_sync import (
    sync_workflow_web_document,
    workflow_document_sync_input,
)
from knowledge.services.workflow_sync import (
    WorkflowDocumentSyncRun,
    finalize_workflow_complete_snapshot,
    merge_workflow_incremental_snapshot,
)
from knowledge.serializers.knowledge_sync import KnowledgeSyncLogQuerySerializer
from knowledge.models.knowledge_action import KnowledgeAction
from knowledge.test_workflow_sync import SnapshotQuery
from knowledge.views.document import DocumentView


KNOWLEDGE_ID = "00000000-0000-0000-0000-000000000021"
DOCUMENT_ID = "00000000-0000-0000-0000-000000000022"


class WorkflowDocumentRequestTests(SimpleTestCase):
    def setUp(self):
        self.user = SimpleNamespace(id="user", username="user")
        self.knowledge = SimpleNamespace(
            id=KNOWLEDGE_ID,
            type=KnowledgeType.WORKFLOW,
            workspace_id="default",
            user=self.user,
            meta={
                "sync_setting": {"enabled": False},
                "workflow_sync_input": {
                    "data_source": {"node_id": "local", "file_list": [{"file_id": "local-file"}]},
                    "knowledge_base": {"input": {"category": "docs"}},
                },
            },
        )
        self.workflow = SimpleNamespace(
            work_flow={
                "nodes": [
                    {"id": "web", "type": "data-source-web-node"},
                    {
                        "id": "extract",
                        "type": "document-extract-node",
                        "properties": {"node_data": {"extract_image": True}},
                    },
                    {"id": "split", "type": "document-split-node", "properties": {"node_data": {"chunk_size": 640}}},
                ],
                "edges": [
                    {"sourceNodeId": "web", "targetNodeId": "extract"},
                    {"sourceNodeId": "extract", "targetNodeId": "split"},
                ],
            }
        )
        self.document = SimpleNamespace(
            id=DOCUMENT_ID,
            knowledge_id=KNOWLEDGE_ID,
            name="selected page",
            type=KnowledgeType.WORKFLOW,
            resource_type=DocumentResourceType.DOCUMENT,
            meta={
                "source_type": "web",
                "source_node_id": "web",
                "source_scope": "original-scope",
                "source_url": "https://example.com/selected",
                "selector": "main",
            },
        )

    def test_input_keeps_original_branch_selector_and_knowledge_inputs_without_local_files(self):
        original_meta, original_graph = deepcopy(self.knowledge.meta), deepcopy(self.workflow.work_flow)
        workflow_input, target = workflow_document_sync_input(self.knowledge, self.workflow, self.document)
        self.assertEqual(
            workflow_input["data_source"],
            {"node_id": "web", "source_url": "https://example.com/selected", "selector": "main"},
        )
        self.assertEqual(workflow_input["knowledge_base"], {"input": {"category": "docs"}})
        self.assertEqual(target["source_meta"]["source_scope"], "original-scope")
        self.assertEqual(target["id"], DOCUMENT_ID)
        self.assertEqual(self.knowledge.meta, original_meta)
        self.assertEqual(self.workflow.work_flow, original_graph)

    def test_missing_or_changed_source_is_rejected(self):
        for field in ("source_scope", "source_url", "source_node_id"):
            with self.subTest(field=field):
                document = deepcopy(self.document)
                document.meta.pop(field)
                with self.assertRaises(AppApiException):
                    workflow_document_sync_input(self.knowledge, self.workflow, document)
        self.workflow.work_flow["nodes"][0]["type"] = "data-source-local-node"
        with self.assertRaises(AppApiException):
            workflow_document_sync_input(self.knowledge, self.workflow, self.document)

    @patch("knowledge.serializers.document.QuerySet")
    def test_document_endpoint_accepts_workflow_web_but_rejects_local_and_image_resources(self, query_set):
        query_set.return_value.filter.return_value.first.return_value = self.document
        for document_type, source_type, resource_type, supported in (
            (KnowledgeType.WEB, "web", DocumentResourceType.DOCUMENT, True),
            (KnowledgeType.WORKFLOW, "web", DocumentResourceType.DOCUMENT, True),
            (KnowledgeType.WORKFLOW, "local", DocumentResourceType.DOCUMENT, False),
            (KnowledgeType.WORKFLOW, "web", DocumentResourceType.IMAGE, False),
        ):
            with self.subTest(document_type=document_type, source_type=source_type, resource_type=resource_type):
                self.document.type, self.document.resource_type = document_type, resource_type
                self.document.meta["source_type"] = source_type
                serializer = DocumentSerializers.Sync(
                    data={"document_id": DOCUMENT_ID, "knowledge_id": KNOWLEDGE_ID, "workspace_id": "default"}
                )
                if supported:
                    serializer.is_valid(raise_exception=True)
                else:
                    with self.assertRaises(AppApiException):
                        serializer.is_valid(raise_exception=True)

    @patch("knowledge.serializers.document.Fork")
    @patch("knowledge.serializers.document.sync_workflow_web_document")
    @patch("knowledge.serializers.document.QuerySet")
    def test_document_endpoint_routes_to_workflow_instead_of_legacy_web_parser(self, query_set, sync, fetch):
        query_set.return_value.filter.return_value.first.return_value = self.document
        serializer = DocumentSerializers.Sync(data={"document_id": DOCUMENT_ID, "knowledge_id": KNOWLEDGE_ID})
        serializer.sync.__wrapped__(serializer, with_valid=False, user=self.user)
        sync.assert_called_once_with(self.document, self.user)
        fetch.assert_not_called()

    def test_document_view_passes_authenticated_profile_to_workflow_launcher(self):
        self.user.email, self.user.phone, self.user.nick_name = "", "", "user"
        request = SimpleNamespace(
            user=Principal(self.user.id, UserType.SYSTEM_USER, self.user),
            data={},
            query_params={},
            path="/document/sync",
            META={},
        )
        with (
            patch("common.auth.authentication._build") as permissions,
            patch("common.log.log.Log"),
            patch("knowledge.views.document.get_knowledge_operation_object"),
            patch("knowledge.views.document.get_document_operation_object"),
            patch("knowledge.views.document.DocumentSerializers.Sync") as serializer,
        ):
            permissions.return_value.hasPermission.return_value = True
            serializer.return_value.sync.return_value = True
            DocumentView.SyncWeb().put(
                request, workspace_id="default", knowledge_id=KNOWLEDGE_ID, document_id=DOCUMENT_ID
            )
            serializer.return_value.sync.assert_called_once_with(user=self.user)

    def query(self, model):
        return {
            Knowledge: self.knowledge_query,
            KnowledgeWorkflow: self.workflow_query,
            KnowledgeSyncLog: self.log_query,
        }[model]

    def configure_queries(self):
        self.knowledge_query, self.workflow_query, self.log_query = MagicMock(), MagicMock(), MagicMock()
        self.knowledge_query.select_for_update.return_value.get.return_value = self.knowledge
        self.workflow_query.filter.return_value.first.return_value = self.workflow
        self.log_query.filter.return_value.exists.return_value = False

    @patch("knowledge.services.workflow_document_sync.recover_stale_sync_logs")
    @patch("knowledge.services.workflow_document_sync.has_running_workflow_document_sync", return_value=False)
    @patch("knowledge.services.workflow_document_sync.KnowledgeSyncLog.objects.create")
    @patch("knowledge.services.workflow_document_sync.QuerySet")
    def test_manual_sync_starts_workflow_without_scheduled_log(self, query_set, create_log, _running, _recover):
        self.configure_queries()
        query_set.side_effect = self.query
        with patch("knowledge.serializers.knowledge_workflow.KnowledgeWorkflowActionSerializer") as action:
            self.assertTrue(sync_workflow_web_document.__wrapped__(self.document, self.user))
            create_log.assert_not_called()
            workflow_input, target = workflow_document_sync_input(self.knowledge, self.workflow, self.document)
            action.return_value.action.assert_called_once_with(workflow_input, self.user, True, sync_document=target)

    @patch("knowledge.services.workflow_document_sync.recover_stale_sync_logs")
    @patch("knowledge.services.workflow_document_sync.KnowledgeSyncLog.objects.create")
    @patch("knowledge.services.workflow_document_sync.QuerySet")
    def test_existing_knowledge_sync_prevents_overlapping_document_sync(self, query_set, create_log, _recover):
        self.configure_queries()
        self.log_query.filter.return_value.exists.return_value = True
        query_set.side_effect = self.query
        with self.assertRaises(AppApiException):
            sync_workflow_web_document.__wrapped__(self.document)
        create_log.assert_not_called()

    @patch("knowledge.services.workflow_document_sync.recover_stale_sync_logs")
    @patch("knowledge.services.workflow_document_sync.has_running_workflow_document_sync", return_value=True)
    @patch("knowledge.services.workflow_document_sync.QuerySet")
    @patch("knowledge.serializers.knowledge_workflow.KnowledgeWorkflowActionSerializer")
    def test_existing_manual_sync_prevents_overlap_without_log(self, action, query_set, _running, _recover):
        self.configure_queries()
        query_set.side_effect = self.query
        with self.assertRaises(AppApiException):
            sync_workflow_web_document.__wrapped__(self.document, self.user)
        action.assert_not_called()

    @patch("knowledge.serializers.knowledge_sync.page_search")
    @patch("knowledge.serializers.knowledge_sync.QuerySet")
    def test_scheduled_log_pagination_excludes_historical_manual_runs(self, query_set, page_search):
        query_set.return_value.filter.return_value.first.return_value = self.knowledge
        page_search.return_value = {"total": 1, "records": [], "current": 1, "size": 10}
        KnowledgeSyncLogQuerySerializer(data={"knowledge_id": KNOWLEDGE_ID, "workspace_id": "default"}).page(1, 10)
        query_set.return_value.filter.assert_any_call(
            knowledge_id=KNOWLEDGE_ID, trigger_type=KnowledgeSyncTrigger.SCHEDULED
        )


class WorkflowSinglePageFetchTests(SimpleTestCase):
    def setUp(self):
        self.node = object.__new__(DataSourceWebNode)
        self.parameters = {
            "data_source": {"node_id": "web", "source_url": "https://example.com/selected", "selector": "main"},
            "workflow_source": {"source_scope": "original-scope"},
            "workflow_sync_document": {"id": DOCUMENT_ID, "name": "selected page"},
        }
        self.node.get_workflow_parameters = lambda: self.parameters
        self.node._check_cancelled = MagicMock()
        self.node.get_node_id = lambda: "web"
        self.node.write_context = MagicMock()

    @patch("application.workflow.nodes.data_source_web_node.data_source_web_node.ForkManage")
    @patch("application.workflow.nodes.data_source_web_node.data_source_web_node.Fork")
    def test_single_document_fetch_never_follows_child_links(self, fetch, crawler):
        fetch.return_value.fork.return_value = Fork.Response.success("selected content", [MagicMock()])
        self.node.execute()
        fetch.assert_called_once_with("https://example.com/selected", ["main"])
        crawler.assert_not_called()
        document_list = self.node.write_context.call_args_list[0].args[1]
        self.assertEqual(len(document_list), 1)
        self.assertEqual(document_list[0]["name"], "selected page")
        self.assertEqual(document_list[0]["meta"]["source_scope"], "original-scope")

    @patch("application.workflow.nodes.data_source_web_node.data_source_web_node.maxkb_logger")
    @patch("application.workflow.nodes.data_source_web_node.data_source_web_node.Fork")
    def test_failed_page_fetch_does_not_publish_empty_workflow_output(self, fetch, _logger):
        fetch.return_value.fork.return_value = Fork.Response.error("unavailable")
        with self.assertRaisesRegex(ValueError, "unavailable"):
            self.node.execute()
        self.node.write_context.assert_not_called()

    @patch("application.workflow.nodes.data_source_web_node.data_source_web_node.ForkManage")
    @patch("application.workflow.nodes.data_source_web_node.data_source_web_node.Fork")
    def test_normal_full_source_runs_still_crawl_the_site(self, fetch, crawler):
        self.parameters.pop("workflow_sync_document")
        self.node.execute()
        fetch.assert_not_called()
        self.assertEqual(crawler.return_value.fork.call_args.args[:2], (3, set()))


class WorkflowDocumentMergeIsolationTests(SimpleTestCase):
    def setUp(self):
        self.log = SimpleNamespace(
            id="log", knowledge_id="knowledge", create_time=10, sync_type=KnowledgeSyncType.INCREMENTAL
        )
        self.source = {"source_scope": "web-scope"}
        self.documents = []
        for doc_id, scope, token, create_time, log_id in (
            (DOCUMENT_ID, "web-scope", "selected", 1, None),
            ("other-web", "web-scope", "other", 1, None),
            ("local", "local-scope", "local", 1, None),
            ("output", "web-scope", "selected", 11, "log"),
        ):
            self.documents.append(
                SimpleNamespace(
                    id=doc_id,
                    knowledge_id="knowledge",
                    name=doc_id,
                    type=KnowledgeType.WORKFLOW,
                    resource_type=DocumentResourceType.DOCUMENT,
                    create_time=create_time,
                    meta={
                        "source_scope": scope,
                        "token": token,
                        **({"workflow_sync_log_id": log_id} if log_id else {}),
                    },
                    doc_strategy={"split": {"child_length": 640}},
                    visual_strategy_hash="",
                    save=MagicMock(),
                )
            )

    def query(self, model):
        return SnapshotQuery(self.documents) if model is Document else MagicMock()

    def delete(self, ids):
        self.documents = [document for document in self.documents if document.id not in ids]
        return ids

    @patch("knowledge.services.workflow_sync._copy_document_relations")
    @patch("knowledge.services.workflow_sync.process_visual_assets")
    @patch("knowledge.services.workflow_sync.sync_paragraph_assets")
    @patch("knowledge.services.workflow_sync.transaction.atomic")
    @patch("knowledge.services.workflow_sync.IncrementalDocumentSync")
    def test_only_selected_document_is_merged_and_other_web_and_local_documents_survive(self, merger, *_mocks):
        merger.return_value.merge.return_value = SimpleNamespace(reembed_ids=[], disabled_ids=[])
        untouched = self.documents[1:3]
        with (
            patch("knowledge.services.workflow_sync.QuerySet", side_effect=self.query),
            patch("knowledge.services.workflow_sync._delete_workflow_documents", side_effect=self.delete),
        ):
            stats = merge_workflow_incremental_snapshot.__wrapped__(self.log, self.source, document_id=DOCUMENT_ID)
        self.assertEqual(stats["total_count"], 1)
        self.assertEqual(stats["skipped_count"], 1)
        self.assertEqual(stats["deleted_count"], 0)
        self.assertEqual({document.id for document in self.documents}, {DOCUMENT_ID, "other-web", "local"})
        merger.assert_called_once_with(
            self.documents[0], {"split": {"child_length": 640}}, source_authoritative=False, replace_content=False
        )
        for document in untouched:
            document.save.assert_not_called()

    def test_empty_or_unmatched_output_fails_without_deleting_any_stable_document(self):
        for invalid_output in ([], [deepcopy(self.documents[-1])]):
            with self.subTest(empty=not invalid_output):
                if invalid_output:
                    invalid_output[0].meta["token"] = "unexpected"
                self.documents = self.documents[:3] + invalid_output
                with (
                    patch("knowledge.services.workflow_sync.QuerySet", side_effect=self.query),
                    patch("knowledge.services.workflow_sync._delete_workflow_documents") as cleanup,
                    self.assertRaisesRegex(ValueError, "selected source document"),
                ):
                    merge_workflow_incremental_snapshot.__wrapped__(self.log, self.source, document_id=DOCUMENT_ID)
                cleanup.assert_not_called()

    def test_failed_run_discards_only_its_temporary_output(self):
        with (
            patch("knowledge.services.workflow_sync.QuerySet", side_effect=self.query),
            patch("knowledge.services.workflow_sync._delete_workflow_documents", side_effect=self.delete),
        ):
            stats = finalize_workflow_complete_snapshot.__wrapped__(
                self.log, False, self.source, document_id=DOCUMENT_ID
            )
        self.assertEqual(stats["failed_count"], 1)
        self.assertEqual({document.id for document in self.documents}, {DOCUMENT_ID, "other-web", "local"})

    def test_manual_failed_snapshot_discards_only_its_action_output(self):
        output = self.documents[-1]
        output.meta.pop("workflow_sync_log_id")
        output.meta["workflow_action_id"] = "manual-action"
        run = WorkflowDocumentSyncRun("manual-action", "knowledge", 10)
        with (
            patch("knowledge.services.workflow_sync.QuerySet", side_effect=self.query),
            patch("knowledge.services.workflow_sync._delete_workflow_documents", side_effect=self.delete),
        ):
            stats = finalize_workflow_complete_snapshot.__wrapped__(run, False, self.source, document_id=DOCUMENT_ID)
        self.assertEqual(stats["failed_count"], 1)
        self.assertEqual({document.id for document in self.documents}, {DOCUMENT_ID, "other-web", "local"})


class WorkflowDocumentEngineTests(SimpleTestCase):
    @patch("knowledge.serializers.knowledge_workflow.validate_knowledge_file_size")
    @patch("knowledge.serializers.knowledge_workflow.transaction.on_commit")
    @patch("knowledge.serializers.knowledge_workflow.KnowledgeAction")
    @patch("knowledge.serializers.knowledge_workflow.QuerySet")
    def test_manual_action_is_reserved_before_commit_and_keeps_saved_schedule_inputs(
        self, query_set, action_model, on_commit, _size
    ):
        knowledge = SimpleNamespace(id=KNOWLEDGE_ID, name="knowledge", desc="", workspace_id="default")
        workflow = SimpleNamespace(work_flow={"nodes": []}, default_model_setting={})
        knowledge_query, workflow_query = MagicMock(), MagicMock()
        knowledge_query.filter.return_value = knowledge_query
        knowledge_query.first.return_value = knowledge
        workflow_query.filter.return_value.first.return_value = workflow
        query_set.side_effect = lambda model: {
            Knowledge: knowledge_query,
            KnowledgeWorkflow: workflow_query,
            File: MagicMock(),
        }[model]
        serializer = KnowledgeWorkflowActionSerializer(data={"knowledge_id": KNOWLEDGE_ID, "workspace_id": "default"})
        target = {"id": DOCUMENT_ID}
        with (
            patch.object(serializer, "save_sync_input") as save_input,
            patch.object(serializer, "_launch_knowledge_workflow") as launch,
            patch("knowledge.serializers.knowledge_workflow.maxkb_logger"),
        ):
            serializer.action(
                {"data_source": {}, "knowledge_base": {}},
                SimpleNamespace(id="user", username="user"),
                sync_document=target,
            )
            action_model.return_value.save.assert_called_once()
            self.assertEqual(action_model.call_args.kwargs["meta"]["document_sync_id"], DOCUMENT_ID)
            save_input.assert_not_called()
            launch.assert_not_called()
            on_commit.call_args.args[0]()
            self.assertIsNone(launch.call_args.args[-1])
            self.assertEqual(launch.call_args.kwargs["sync_document"], target)
            launch.side_effect = RuntimeError("failed to start")
            with patch("knowledge.serializers.knowledge_workflow.QuerySet") as failure_query:
                on_commit.call_args.args[0]()
            failure_query.return_value.filter.return_value.update.assert_called_once_with(state=State.FAILURE)

    @patch("knowledge.serializers.knowledge_workflow.finalize_workflow_complete_snapshot")
    @patch("knowledge.serializers.knowledge_workflow.merge_workflow_incremental_snapshot")
    @patch("knowledge.serializers.knowledge_workflow.QuerySet")
    def test_manual_completion_merges_selected_output_without_touching_scheduled_logs(self, query_set, merge, cleanup):
        action = SimpleNamespace(id="manual-action", knowledge_id=KNOWLEDGE_ID, create_time=10, state=State.STARTED)
        action_query, knowledge_query = MagicMock(), MagicMock()
        action_query.get.return_value = action
        action_query.select_for_update.return_value.get.return_value = action
        query_set.side_effect = lambda model: {KnowledgeAction: action_query, Knowledge: knowledge_query}[model]
        merge.return_value = {"failed_count": 0}
        finalize_knowledge_action.__wrapped__(
            action.id, State.SUCCESS, 1.0, workflow_source={"source_scope": "scope"}, sync_document_id=DOCUMENT_ID
        )
        merge.assert_called_once_with(
            WorkflowDocumentSyncRun(action.id, KNOWLEDGE_ID, 10), {"source_scope": "scope"}, document_id=DOCUMENT_ID
        )
        action_query.filter.return_value.update.assert_called_once_with(state=State.SUCCESS, run_time=1.0)
        cleanup.assert_not_called()
        action.state = State.SUCCESS
        merge.reset_mock()
        finalize_knowledge_action.__wrapped__(action.id, State.SUCCESS, 1.0, sync_document_id=DOCUMENT_ID)
        merge.assert_not_called()

    @patch("knowledge.serializers.knowledge_workflow.start_sync_heartbeat", return_value=lambda: None)
    @patch("knowledge.serializers.knowledge_workflow.QuerySet")
    @patch("knowledge.serializers.knowledge_workflow.WorkflowRunRegistry")
    @patch("knowledge.serializers.knowledge_workflow.WorkflowManage")
    @patch("knowledge.serializers.knowledge_workflow.new_instance")
    def test_engine_preserves_original_graph_and_trusted_source_scope(
        self, _new, engine, _registry, _query, _heartbeat
    ):
        workflow = {
            "nodes": [
                {"id": "web", "type": "data-source-web-node"},
                {"id": "split", "type": "document-split-node", "properties": {"node_data": {"chunk_size": 640}}},
            ],
            "edges": [{"sourceNodeId": "web", "targetNodeId": "split"}],
        }
        original_graph = deepcopy(workflow)
        serializer = KnowledgeWorkflowActionSerializer(data={"knowledge_id": KNOWLEDGE_ID, "workspace_id": "default"})
        serializer.is_valid(raise_exception=True)
        target = {
            "id": DOCUMENT_ID,
            "name": "selected",
            "source_meta": {"source_scope": "original-scope", "source_type": "web", "source_node_id": "web"},
        }
        workflow_input = {
            "data_source": {"node_id": "web", "source_url": "https://example.com/selected"},
            "workflow_sync_document": {"id": "untrusted"},
        }
        serializer._launch_knowledge_workflow(
            workflow_input, SimpleNamespace(id="user"), "action", workflow, sync_log_id="log", sync_document=target
        )
        parameters = engine.call_args.args[1]
        self.assertEqual(parameters["workflow_source"]["source_scope"], "original-scope")
        self.assertEqual(parameters["workflow_sync_document"]["id"], DOCUMENT_ID)
        self.assertEqual(workflow, original_graph)
        _new.assert_called_once_with(workflow, _new.call_args.args[1])
        serializer._launch_knowledge_workflow(workflow_input, SimpleNamespace(id="user"), "action", workflow)
        self.assertIsNone(engine.call_args.args[1]["workflow_sync_document"])

    @patch("knowledge.serializers.knowledge_workflow.maxkb_logger")
    @patch("knowledge.serializers.knowledge_workflow.finalize_workflow_complete_snapshot")
    @patch("knowledge.serializers.knowledge_workflow.merge_workflow_incremental_snapshot")
    @patch("knowledge.serializers.knowledge_workflow.QuerySet")
    def test_bad_single_document_output_marks_log_failed_and_cleans_only_this_run(
        self, query_set, merger, cleanup, _logger
    ):
        log = SimpleNamespace(
            id="log",
            knowledge_id=KNOWLEDGE_ID,
            sync_type=KnowledgeSyncType.INCREMENTAL,
            status=KnowledgeSyncStatus.RUNNING,
        )
        query_set.return_value.filter.return_value.first.return_value = log
        query_set.return_value.select_for_update.return_value.get.return_value = log
        merger.side_effect = ValueError("invalid output")
        cleanup.return_value = {
            "total_count": 1,
            "synced_count": 0,
            "skipped_count": 0,
            "deleted_count": 1,
            "failed_count": 1,
        }
        finalize_knowledge_action.__wrapped__(
            "action", State.SUCCESS, 1.0, "log", MagicMock(), {"source_scope": "scope"}, DOCUMENT_ID
        )
        merger.assert_called_once_with(log, {"source_scope": "scope"}, document_id=DOCUMENT_ID)
        cleanup.assert_called_once_with(log, False, {"source_scope": "scope"}, document_id=DOCUMENT_ID)
        self.assertEqual(
            query_set.return_value.filter.return_value.update.call_args.kwargs["status"], KnowledgeSyncStatus.FAILURE
        )
        self.assertIn("FAILURE", query_set.return_value.filter.return_value.update.call_args.kwargs["message"])
