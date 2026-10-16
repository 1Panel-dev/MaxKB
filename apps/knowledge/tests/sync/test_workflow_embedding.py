from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from application.workflow.nodes.knowledge_write_node.knowledge_write_node import KnowledgeWriteNode
from common.event.listener_manage import ListenerManagement
from knowledge.models import Document, State, Status, TaskType
from knowledge.serializers.common import create_knowledge_index
from knowledge.services.workflow_sync import schedule_workflow_document_embedding


class WorkflowWriteEmbeddingTests(SimpleTestCase):
    def test_sync_snapshots_defer_embedding_while_normal_uploads_still_embed(self):
        for parameters, should_embed in (
            ({"workflow_source": {"source_type": "local"}}, True),
            ({"workflow_source": {"source_type": "web"}}, True),
            ({"sync_log_id": "scheduled-sync"}, False),
            ({"workflow_sync_document": {"id": "selected"}}, False),
        ):
            with self.subTest(parameters=parameters):
                node = KnowledgeWriteNode.__new__(KnowledgeWriteNode)
                node.get_parameters = MagicMock(return_value={})
                node.get_workflow_parameters = MagicMock(return_value=parameters)
                node.save = MagicMock(return_value=([SimpleNamespace(id="output")], "knowledge", "workspace"))
                node.post_embedding = MagicMock()
                node.write_context = MagicMock()
                node.execute()
                node.save.assert_called_once_with([], None)
                if should_embed:
                    node.post_embedding.assert_called_once_with(node.save.return_value[0], "knowledge", "workspace")
                else:
                    node.post_embedding.assert_not_called()


class WorkflowEmbeddingDispatchTests(SimpleTestCase):
    @patch("knowledge.services.workflow_sync.celery_app.send_task")
    @patch("knowledge.services.workflow_sync.transaction.on_commit")
    @patch("knowledge.services.workflow_sync.QuerySet")
    def test_retained_documents_are_queued_only_after_commit(self, query_set, on_commit, send_task):
        query_set.return_value.filter.return_value.values_list.return_value.first.return_value = "model"
        schedule_workflow_document_embedding(["retained"], "knowledge")
        send_task.assert_not_called()
        on_commit.assert_called_once()
        on_commit.call_args.args[0]()
        send_task.assert_called_once_with("celery:embedding_by_document_list", args=[["retained"], "model"])

    @patch("knowledge.services.workflow_sync.transaction.on_commit")
    @patch("knowledge.services.workflow_sync.QuerySet")
    def test_empty_output_and_missing_model_do_not_queue_tasks(self, query_set, on_commit):
        schedule_workflow_document_embedding([], "knowledge")
        query_set.assert_not_called()
        query_set.return_value.filter.return_value.values_list.return_value.first.return_value = None
        schedule_workflow_document_embedding(["retained"], "knowledge")
        on_commit.assert_not_called()


class DeletedDocumentEmbeddingTests(SimpleTestCase):
    def setUp(self):
        self.query_set = self.enterContext(patch("common.event.listener_manage.QuerySet"))
        self.document_query = MagicMock()
        self.query_set.side_effect = lambda model: self.document_query if model is Document else MagicMock()
        self.lock = self.enterContext(patch("common.event.listener_manage.RedisLock")).return_value
        self.lock.try_lock.return_value = True
        self.logger = self.enterContext(patch("common.event.listener_manage.maxkb_logger"))
        self.index = self.enterContext(patch("common.event.listener_manage.create_knowledge_index"))
        self.update_status = self.enterContext(patch.object(ListenerManagement, "update_status"))
        self.aggregate = self.enterContext(patch.object(ListenerManagement, "get_aggregation_document_status"))
        self.page = self.enterContext(patch("common.event.listener_manage.page_desc"))

    def test_retained_document_still_creates_index_and_updates_status(self):
        self.document_query.filter.return_value.first.return_value = SimpleNamespace(
            status=str(Status()), status_meta={}
        )
        ListenerManagement.embedding_by_document("retained", MagicMock())
        self.page.assert_called_once()
        self.index.assert_called_once_with(document_id="retained")
        self.document_query.filter.assert_any_call(id="retained")
        self.logger.error.assert_not_called()
        self.lock.un_lock.assert_called_once_with("embedding:retained")

    def test_task_for_an_already_deleted_document_exits_and_releases_lock(self):
        self.document_query.filter.return_value.first.return_value = None
        ListenerManagement.embedding_by_document("deleted", MagicMock())
        self.page.assert_not_called()
        self.index.assert_not_called()
        self.update_status.assert_not_called()
        self.logger.error.assert_not_called()
        self.lock.un_lock.assert_called_once_with("embedding:deleted")

    def test_document_deleted_during_embedding_does_not_fail_at_index_or_status_update(self):
        status = Status()
        status[TaskType.EMBEDDING] = State.STARTED
        document = SimpleNamespace(status=str(status), status_meta={})
        self.document_query.filter.return_value.first.side_effect = [document, None, None]
        ListenerManagement.embedding_by_document("temporary", MagicMock())
        self.page.assert_called_once()
        self.index.assert_not_called()
        self.update_status.assert_called_once()
        self.logger.error.assert_not_called()
        self.lock.un_lock.assert_called_once_with("embedding:temporary")

    def test_lock_is_released_even_when_status_finalization_fails(self):
        self.document_query.filter.return_value.first.return_value = None
        with (
            patch.object(ListenerManagement, "post_update_document_status", side_effect=RuntimeError("database")),
            self.assertRaisesRegex(RuntimeError, "database"),
        ):
            ListenerManagement.embedding_by_document("deleted", MagicMock())
        self.lock.un_lock.assert_called_once_with("embedding:deleted")

    @patch("knowledge.serializers.common.sql_execute")
    @patch("knowledge.serializers.common.QuerySet")
    def test_document_deleted_before_index_lookup_skips_index_sql(self, query_set, execute_sql):
        query_set.return_value.filter.return_value.first.return_value = None
        create_knowledge_index(document_id="deleted")
        execute_sql.assert_not_called()
