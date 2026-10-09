from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.nodes.data_source_local_node.data_source_local_node import DataSourceLocalNode
from application.workflow.nodes.data_source_web_node.data_source_web_node import DataSourceWebNode
from application.workflow.nodes.document_extract_node.document_extract_node import DocumentExtractNode
from application.workflow.nodes.document_split_node.document_split_node import DocumentSplitNode
from application.workflow.nodes.knowledge_write_node.knowledge_write_node import (
    KnowledgeWriteNode,
    KnowledgeWriteParamSerializer,
    get_document_paragraph_model,
)
from application.workflow.nodes.tool_lib_node.tool_lib_node import ToolLibNode
from common.utils.fork import ChildLink
from knowledge.models import KnowledgeType


class WorkflowDocumentSourceTests(SimpleTestCase):
    def split_and_write(self, meta, source_file_id=None):
        node = DocumentSplitNode.__new__(DocumentSplitNode)
        node.get_parameters = MagicMock(return_value={"document_list": ["source", "document_list"]})
        node.get_workflow_parameters = MagicMock(return_value={"knowledge_id": "knowledge-id"})
        node.get_workflow_type = MagicMock(return_value=WorkflowType.KNOWLEDGE)
        node.get_reference_content = MagicMock(
            return_value=[{"id": source_file_id, "name": "renamed document", "content": "text", "meta": meta}]
        )
        node.write_context = MagicMock()
        node.execute()
        document = next(
            call.args[1][0] for call in node.write_context.call_args_list if call.args[0] == "paragraph_list"
        )
        request = KnowledgeWriteParamSerializer(data=document)
        request.is_valid(raise_exception=True)
        return get_document_paragraph_model("knowledge-id", request.data)["document"]

    def test_web_url_survives_same_title_extraction_split_and_write(self):
        node = DataSourceWebNode.__new__(DataSourceWebNode)
        node._check_cancelled = MagicMock()
        documents = []
        handler = node._get_collect_handler(documents, {"source_scope": "web-scope"}, ".content")
        response = SimpleNamespace(status=200, content="page text")
        for url in ("https://example.com/a", "https://example.com/b"):
            handler(ChildLink(url, SimpleNamespace(text="same title")), response)
        stored = [self.split_and_write(document["meta"]) for document in documents]
        self.assertEqual(
            [document.meta["source_url"] for document in stored], ["https://example.com/a", "https://example.com/b"]
        )
        self.assertTrue(all(document.meta["selector"] == ".content" for document in stored))
        self.assertTrue(all(document.type == KnowledgeType.WORKFLOW for document in stored))

    @patch("application.workflow.nodes.tool_lib_node.tool_lib_node.function_executor")
    @patch("application.workflow.nodes.tool_lib_node.tool_lib_node.valid_function")
    @patch("application.workflow.nodes.tool_lib_node.tool_lib_node.QuerySet")
    def test_downloaded_lark_token_survives_download_split_and_write(self, query_set, _valid, executor):
        tool = SimpleNamespace(
            code="tool code", input_field_list=[], init_field_list=[], init_params=None, name="飞书数据源"
        )
        query_set.return_value.filter.return_value.first.return_value = tool
        executor.exec_code.side_effect = [
            True,
            [{"token": "remote-document", "type": "docx", "access_token": "must-not-copy"}],
            {
                "name": "renamed.docx",
                "file_bytes": ["dGV4dA=="],
                "app_secret": "must-not-copy",
                "meta": {"source_type": "lark"},
            },
        ]
        node = ToolLibNode.__new__(ToolLibNode)
        node.node = SimpleNamespace(properties={"kind": "data-source"})
        node.get_parameters = MagicMock(return_value={"tool_lib_id": "tool-id"})
        node.get_workflow_parameters = MagicMock(return_value={"workflow_source": {"source_scope": "lark-scope"}})
        node.get_node_id = MagicMock(return_value="lark-node")
        node._check_cancelled = MagicMock()
        file_id = "00000000-0000-0000-0000-000000000001"
        node.upload_knowledge_file = MagicMock(return_value=file_id)
        node.write_context = MagicMock()
        node.execute()
        downloaded = node.write_context.call_args_list[-1].args[1][0]
        stored = self.split_and_write(downloaded["meta"], file_id)
        self.assertEqual(stored.meta["token"], "remote-document")
        self.assertEqual(stored.meta["source_document_type"], "docx")
        self.assertEqual(stored.meta["source_type"], "lark")
        self.assertEqual(stored.meta["source_tool_name"], "飞书数据源")
        self.assertNotIn("access_token", stored.meta)
        self.assertNotIn("app_secret", stored.meta)
        self.assertNotIn("file_bytes", stored.meta)
        self.assertNotIn("source_url", stored.meta)

    @patch("application.workflow.nodes.document_extract_node.document_extract_node.split_handles")
    @patch("application.workflow.nodes.document_extract_node.document_extract_node.parse_table_handle_list", [])
    @patch("application.workflow.nodes.document_extract_node.document_extract_node.QuerySet")
    def test_file_extraction_preserves_remote_metadata(self, query_set, split_handles):
        file_id = "00000000-0000-0000-0000-000000000002"
        file = MagicMock(id=file_id)
        file.get_bytes.return_value = b"text"
        query_set.return_value.filter.return_value.first.return_value = file
        parser = MagicMock()
        parser.get_content.return_value = "text"
        split_handles.__iter__.return_value = iter([parser])
        split_handles.__radd__.return_value = [parser]
        node = DocumentExtractNode.__new__(DocumentExtractNode)
        node.get_parameters = MagicMock(return_value={"document_list": ["source", "result"]})
        node.get_workflow_parameters = MagicMock(return_value={"knowledge_id": "knowledge-id"})
        node.get_workflow_type = MagicMock(return_value=WorkflowType.KNOWLEDGE)
        node.workflow_manage = MagicMock()
        node.workflow_manage.get_reference_field.return_value = [
            {"file_id": file_id, "name": "document.txt", "meta": {"token": "remote", "source_type": "lark"}}
        ]
        node.write_context = MagicMock()
        node.execute()
        extracted = node.write_context.call_args_list[-1].args[1][0]
        stored = self.split_and_write(extracted["meta"], extracted["id"])
        self.assertEqual(stored.meta["token"], "remote")
        self.assertEqual(stored.meta["source_file_id"], file_id)

    def test_local_upload_is_marked_local_without_a_fake_url(self):
        file_id = "00000000-0000-0000-0000-000000000003"
        node = DataSourceLocalNode.__new__(DataSourceLocalNode)
        node.get_workflow_parameters = MagicMock(
            return_value={"data_source": {"file_list": [{"file_id": file_id, "name": "local.txt"}]}}
        )
        node.write_context = MagicMock()
        node.execute()
        uploaded = node.write_context.call_args.args[1][0]
        stored = self.split_and_write(uploaded["meta"], file_id)
        self.assertEqual(stored.meta["source_type"], "local")
        self.assertNotIn("source_url", stored.meta)

    @patch("application.workflow.nodes.knowledge_write_node.knowledge_write_node.QuerySet")
    def test_scheduled_write_without_a_stable_remote_identity_fails_before_saving(self, query_set):
        node = KnowledgeWriteNode.__new__(KnowledgeWriteNode)
        node.get_workflow_parameters = MagicMock(
            return_value={"knowledge_action_id": "action-id", "sync_log_id": "log-id"}
        )
        with self.assertRaisesRegex(serializers.ValidationError, "stable source"):
            node.save([{"name": "document", "paragraphs": []}], None)
        query_set.assert_not_called()

    @patch("application.workflow.nodes.knowledge_write_node.knowledge_write_node.QuerySet")
    @patch("application.workflow.nodes.knowledge_write_node.knowledge_write_node.ProblemParagraphManage")
    def test_execution_marks_override_upstream_scope_and_log_id(self, problem_manager, _query_set):
        problem_manager.return_value.to_problem_model_list.return_value = ([], [])
        node = KnowledgeWriteNode.__new__(KnowledgeWriteNode)
        node.get_workflow_parameters = MagicMock(
            return_value={
                "knowledge_id": "knowledge",
                "workspace_id": "workspace",
                "knowledge_action_id": "action",
                "sync_log_id": "log",
                "workflow_source": {"source_scope": "trusted-scope", "source_type": "tool"},
            }
        )
        documents, _, _ = node.save(
            [
                {
                    "name": "document",
                    "meta": {"token": "remote", "source_scope": "wrong", "workflow_sync_log_id": "wrong"},
                    "paragraphs": [],
                }
            ],
            None,
        )
        self.assertEqual(documents[0].meta["source_scope"], "trusted-scope")
        self.assertEqual(documents[0].meta["workflow_sync_log_id"], "log")
        self.assertEqual(documents[0].meta["workflow_action_id"], "action")
