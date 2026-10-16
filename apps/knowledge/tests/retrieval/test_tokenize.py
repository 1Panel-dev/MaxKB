from contextlib import nullcontext
from unittest.mock import MagicMock, call, patch

from celery_once import AlreadyQueued
from common.exception.app_exception import AppApiException
from django.test import SimpleTestCase
from django.urls import resolve
from knowledge.models import Document, Paragraph, State, TaskType
from knowledge.serializers.knowledge import KnowledgeSerializer
from knowledge.task.embedding import tokenize_by_knowledge
from knowledge.views.knowledge import KnowledgeView


class KnowledgeTokenizeTests(SimpleTestCase):
    knowledge_id = "00000000-0000-0000-0000-000000000001"
    user_id = "00000000-0000-0000-0000-000000000002"

    def serializer(self, workspace_id="workspace-1"):
        return KnowledgeSerializer.Operate(
            data={"knowledge_id": self.knowledge_id, "workspace_id": workspace_id, "user_id": self.user_id}
        )

    @patch("knowledge.serializers.knowledge.tokenize_by_knowledge.delay")
    @patch("knowledge.serializers.knowledge.QuerySet")
    def test_submit_validates_workspace_without_loading_embedding_model(self, query_set, delay):
        for workspace_id in ("workspace-1", "None"):
            with self.subTest(workspace_id=workspace_id):
                query_set.reset_mock()
                delay.reset_mock()
                self.serializer(workspace_id).tokenize()

                query_set.assert_called_once()
                query_set.return_value.filter.assert_called_once_with(id=self.knowledge_id)
                query_set.return_value.filter.return_value.filter.assert_called_once_with(workspace_id=workspace_id)
                delay.assert_called_once_with(self.knowledge_id)

    @patch("knowledge.serializers.knowledge.tokenize_by_knowledge.delay")
    @patch("knowledge.serializers.knowledge.QuerySet")
    def test_missing_or_other_workspace_knowledge_is_not_queued(self, query_set, delay):
        query_set.return_value.filter.return_value.filter.return_value.exists.return_value = False
        with self.assertRaises(AppApiException):
            self.serializer().tokenize()
        delay.assert_not_called()

    @patch("knowledge.serializers.knowledge.tokenize_by_knowledge.delay", side_effect=AlreadyQueued(10))
    @patch("knowledge.serializers.knowledge.QuerySet")
    def test_duplicate_knowledge_task_returns_api_error(self, _query_set, _delay):
        with self.assertRaises(AppApiException):
            self.serializer().tokenize()

    def test_workspace_route_uses_tokenize_view(self):
        match = resolve(f"/workspace/workspace-1/knowledge/{self.knowledge_id}/tokenize", urlconf="knowledge.urls")
        self.assertIs(match.func.view_class, KnowledgeView.Tokenize)


class KnowledgeTokenizeTaskTests(SimpleTestCase):
    def setUp(self):
        self.query_patch = patch("knowledge.task.embedding.QuerySet")
        self.query_set = self.query_patch.start()
        self.addCleanup(self.query_patch.stop)
        self.listener_patch = patch("knowledge.task.embedding.ListenerManagement")
        self.listener = self.listener_patch.start()
        self.addCleanup(self.listener_patch.stop)
        self.atomic_patch = patch("knowledge.task.embedding.transaction.atomic", side_effect=nullcontext)
        self.atomic_patch.start()
        self.addCleanup(self.atomic_patch.stop)
        self.delay_patch = patch("knowledge.task.embedding.tokenize_by_document.delay")
        self.delay = self.delay_patch.start()
        self.addCleanup(self.delay_patch.stop)
        self.documents, self.paragraphs = MagicMock(), MagicMock()
        self.query_set.side_effect = {Document: self.documents, Paragraph: self.paragraphs}.__getitem__

    def set_documents(self, document_ids):
        self.documents.filter.return_value.values_list.return_value.iterator.return_value = iter(document_ids)

    def test_rebuilds_all_document_states_and_only_tokenize_status(self):
        self.set_documents(["doc-1", "doc-2"])

        tokenize_by_knowledge.run("knowledge-1")

        self.documents.filter.assert_has_calls([call(knowledge_id="knowledge-1")])
        self.paragraphs.filter.assert_called_once_with(knowledge_id="knowledge-1")
        self.listener.update_status.assert_has_calls(
            [
                call(self.documents.filter.return_value, TaskType.TOKENIZE, State.PENDING),
                call(self.paragraphs.filter.return_value, TaskType.TOKENIZE, State.PENDING),
            ]
        )
        self.assertEqual(self.listener.update_status.call_count, 2)
        self.listener.get_aggregation_document_status_by_knowledge_id.assert_called_once_with("knowledge-1")
        state_list = [state.value for state in State]
        self.assertIn(State.IGNORED.value, state_list)
        self.delay.assert_has_calls([call("doc-1", state_list), call("doc-2", state_list)])

    def test_duplicate_document_does_not_block_remaining_documents(self):
        self.set_documents(["doc-1", "doc-2"])
        self.delay.side_effect = [AlreadyQueued(10), None]

        tokenize_by_knowledge.run("knowledge-1")

        self.assertEqual(self.delay.call_count, 2)
        self.assertEqual(self.delay.call_args.args[0], "doc-2")

    def test_empty_knowledge_does_not_queue_document_tasks(self):
        self.set_documents([])
        tokenize_by_knowledge.run("empty-knowledge")
        self.delay.assert_not_called()

    def test_broker_errors_are_not_silently_ignored(self):
        self.set_documents(["doc-1"])
        self.delay.side_effect = RuntimeError("broker unavailable")
        with self.assertRaises(RuntimeError):
            tokenize_by_knowledge.run("knowledge-1")
