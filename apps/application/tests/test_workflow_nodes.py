import json
from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch
from uuid import UUID

from django.db import connection
from django.test import SimpleTestCase

from application.models import ChatRecord
from application.workflow.common import WorkflowType
from application.workflow.nodes.ai_chat_node.ai_chat_node import AIChatNode, _get_upstream_knowledge_images
from application.workflow.nodes.data_source_web_node.data_source_web_node import DataSourceWebNode
from application.workflow.nodes.search_knowledge_node.search_knowledge_node import (
    _get_recalled_image_list,
    _get_result_content,
    _list_paragraph,
    _record_recalled_items,
    _reset_paragraph,
)
from knowledge.models import Document, DocumentResourceType, Knowledge, KnowledgeType, SourceType
from application.workflow.nodes.search_document_node.search_document_node import SearchDocumentNode
from common.utils.fork import ChildLink, Fork


class DataSourceWebNodeTests(SimpleTestCase):
    def test_failed_web_fetch_fails_workflow_instead_of_returning_an_empty_snapshot(self):
        node = DataSourceWebNode.__new__(DataSourceWebNode)
        node._check_cancelled = MagicMock()
        handler = node._get_collect_handler([])

        with self.assertRaisesRegex(ValueError, "unavailable"):
            handler(ChildLink("https://example.com", None), Fork.Response.error("unavailable"))


class SearchKnowledgeNodeTests(SimpleTestCase):
    def test_recall_and_sync_timestamps_can_be_saved_in_workflow_context(self):
        timestamp = datetime(2026, 10, 29, 10, 20, 30, tzinfo=timezone.utc)
        paragraph = {
            "id": UUID("00000000-0000-0000-0000-000000000001"),
            "knowledge_id": UUID("00000000-0000-0000-0000-000000000002"),
            "document_id": UUID("00000000-0000-0000-0000-000000000003"),
            "content": "recalled paragraph",
            "create_time": timestamp,
            "update_time": timestamp,
            "meta": {},
            "directly_return_similarity": 0.8,
            "hit_handling_method": "directly_return",
        }
        embedding = {"paragraph_id": str(paragraph["id"]), "similarity": 0.95}
        field = ChatRecord._meta.get_field("workflow_context")

        for last_hit_time, source_updated_at in (
            (None, None),
            (timestamp, None),
            (None, timestamp),
            (timestamp, timestamp),
        ):
            with self.subTest(last_hit_time=last_hit_time, source_updated_at=source_updated_at):
                row = {**paragraph, "last_hit_time": last_hit_time, "source_updated_at": source_updated_at}
                result = _reset_paragraph(row, [embedding])
                context = {"search": {"paragraph_list": [result], "is_hit_handling_method_list": [result]}}
                # Exercise the JSON encoder selected by the actual PostgreSQL field adapter.
                prepared = field.get_db_prep_value(context, connection)
                saved = json.loads(prepared.dumps(prepared.obj))["search"]["paragraph_list"][0]

                self.assertEqual(saved["create_time"], "2026-10-29 10:20:30")
                self.assertEqual(saved["update_time"], "2026-10-29 10:20:30")
                self.assertEqual(saved["last_hit_time"], "2026-10-29 10:20:30" if last_hit_time else None)
                self.assertEqual(saved["source_updated_at"], "2026-10-29 10:20:30" if source_updated_at else None)
                self.assertEqual(saved["id"], str(paragraph["id"]))
                self.assertTrue(saved["is_hit_handling_method"])
                self.assertIs(row["last_hit_time"], last_hit_time)

    def test_recalled_metadata_and_source_ids_are_json_serializable(self):
        timestamp = datetime(2026, 10, 29, 10, 20, 30)
        source_id = UUID("00000000-0000-0000-0000-000000000001")
        paragraph = {
            "id": "paragraph",
            "knowledge_id": "knowledge",
            "document_id": "document",
            "anchor_paragraph_id": source_id,
            "content": "recalled paragraph",
            "create_time": timestamp,
            "update_time": timestamp,
            "meta": {"allow_download": True, "entries": [{"timestamp": timestamp, "id": source_id}]},
            "directly_return_similarity": 0.8,
            "hit_handling_method": "normal",
        }
        embedding = {
            "paragraph_id": "paragraph",
            "source_id": source_id,
            "source_type": SourceType.IMAGE.value,
            "similarity": Decimal("0.95"),
        }
        asset = {"file_id": str(source_id), "caption": "chart", "last_hit_time": timestamp}

        result = _reset_paragraph(paragraph, [embedding], {str(source_id): asset})
        saved = json.loads(json.dumps(result))

        self.assertEqual(saved["source_id"], str(source_id))
        self.assertEqual(saved["anchor_paragraph_id"], str(source_id))
        self.assertEqual(saved["similarity"], 0.95)
        self.assertEqual(saved["meta"]["entries"], [{"timestamp": "2026-10-29 10:20:30", "id": str(source_id)}])
        self.assertEqual(saved["hit_asset"]["last_hit_time"], "2026-10-29 10:20:30")
        self.assertEqual(saved["retrieval_content"], "recalled paragraph\nchart")
        self.assertIs(paragraph["meta"]["entries"][0]["timestamp"], timestamp)
        self.assertIs(asset["last_hit_time"], timestamp)

    def test_image_document_text_hit_includes_original_image_in_reply_content(self):
        paragraph = {
            "document_resource_type": DocumentResourceType.IMAGE,
            "document_image_id": "original-image-file",
            "hit_asset": None,
            "retrieval_content": "google",
        }

        self.assertEqual(_get_result_content(paragraph), "![](./oss/file/original-image-file)\n\ngoogle")
        self.assertEqual(paragraph["retrieval_content"], "google")

    def test_inline_image_hit_includes_asset_and_visual_text(self):
        paragraph = {
            "document_resource_type": DocumentResourceType.DOCUMENT,
            "hit_asset": {"file_id": "chart-file"},
            "retrieval_content": "paragraph\nchart description",
        }

        self.assertEqual(_get_result_content(paragraph), "![](./oss/file/chart-file)\n\nparagraph\nchart description")

    def test_reply_content_preserves_existing_image_markdown(self):
        for image_path in ("./oss/file/chart-file", "/admin/oss/file/chart-file"):
            with self.subTest(image_path=image_path):
                content = f"chart\n![original caption]({image_path})"
                self.assertEqual(
                    _get_result_content({"content": content, "hit_asset": {"file_id": "chart-file"}}), content
                )

    def test_text_and_missing_image_results_keep_original_content(self):
        for paragraph in (
            {"content": "plain text"},
            {"content": "plain text", "document_resource_type": DocumentResourceType.IMAGE},
            {"content": "plain text", "hit_asset": {}},
        ):
            with self.subTest(paragraph=paragraph):
                self.assertEqual(_get_result_content(paragraph), "plain text")

    @patch("knowledge.services.multimodal_retrieval.QuerySet")
    @patch("application.workflow.nodes.search_knowledge_node.search_knowledge_node.native_search")
    def test_workflow_paragraph_query_includes_source_fields(self, native_search, query_set):
        paragraph_id = "00000000-0000-0000-0000-000000000001"
        native_search.return_value = [{"id": paragraph_id, "document_id": "image-document"}]
        query_set.return_value.filter.return_value.values_list.return_value = [
            ("image-document", KnowledgeType.BASE, DocumentResourceType.IMAGE, "original-image-file")
        ]

        result = _list_paragraph([{"paragraph_id": paragraph_id}], MagicMock())

        self.assertEqual(result[0]["knowledge_type"], KnowledgeType.BASE)
        self.assertEqual(result[0]["document_resource_type"], DocumentResourceType.IMAGE)
        self.assertEqual(result[0]["document_image_id"], "original-image-file")

    def test_image_hit_metadata_is_attached_to_recalled_paragraph(self):
        paragraph_id = "00000000-0000-0000-0000-000000000001"
        asset_id = "00000000-0000-0000-0000-000000000002"
        file_id = "00000000-0000-0000-0000-000000000003"
        created_at = datetime(2026, 9, 3, 10, 0, 0)
        paragraph = {
            "id": paragraph_id,
            "knowledge_id": "00000000-0000-0000-0000-000000000004",
            "document_id": "00000000-0000-0000-0000-000000000005",
            "directly_return_similarity": 0.8,
            "hit_handling_method": "normal",
            "update_time": created_at,
            "create_time": created_at,
            "meta": {},
            "knowledge_type": KnowledgeType.BASE,
            "document_resource_type": DocumentResourceType.IMAGE,
            "document_image_id": file_id,
        }
        embedding = {
            "paragraph_id": paragraph_id,
            "similarity": 0.91,
            "comprehensive_score": 0.93,
            "source_id": asset_id,
            "source_type": SourceType.IMAGE.value,
            "query_unit_type": "text",
            "query_unit_index": 0,
        }
        asset = {"id": asset_id, "file_id": file_id, "file_name": "chart.png"}

        result = _reset_paragraph(paragraph, [embedding], {asset_id: asset})

        self.assertEqual(result["hit_unit_type"], "image")
        self.assertEqual(result["hit_asset"], asset)
        self.assertEqual(result["comprehensive_score"], 0.93)
        self.assertEqual(result["knowledge_type"], KnowledgeType.BASE)
        self.assertEqual(result["document_resource_type"], DocumentResourceType.IMAGE)
        self.assertEqual(result["document_image_id"], file_id)
        self.assertEqual(_get_recalled_image_list([result, result]), [asset])

    def test_image_text_hit_adds_visual_text_to_retrieval_context(self):
        paragraph_id = "00000000-0000-0000-0000-000000000001"
        asset_id = "00000000-0000-0000-0000-000000000002"
        created_at = datetime(2026, 9, 3, 10, 0, 0)
        paragraph = {
            "id": paragraph_id,
            "knowledge_id": "00000000-0000-0000-0000-000000000004",
            "document_id": "00000000-0000-0000-0000-000000000005",
            "content": "paragraph text",
            "directly_return_similarity": 0.8,
            "hit_handling_method": "normal",
            "update_time": created_at,
            "create_time": created_at,
            "meta": {},
        }
        embedding = {
            "paragraph_id": paragraph_id,
            "similarity": 0.91,
            "comprehensive_score": 0.93,
            "source_id": asset_id,
            "source_type": SourceType.IMAGE.value,
            "meta": {"unit_type": "text", "content_type": "image_description"},
        }
        asset = {
            "id": asset_id,
            "file_id": "00000000-0000-0000-0000-000000000003",
            "caption": "chart",
            "ocr_text": "revenue 100",
            "description": "an upward trend",
        }

        result = _reset_paragraph(paragraph, [embedding], {asset_id: asset})

        self.assertEqual(result["hit_unit_type"], "text")
        self.assertEqual(result["retrieval_content"], "paragraph text\nchart\nrevenue 100\nan upward trend")

    @patch("application.workflow.nodes.search_knowledge_node.search_knowledge_node.record_recall_safely")
    @patch("application.workflow.nodes.search_knowledge_node.search_knowledge_node.get_recall_tracker")
    def test_records_only_embeddings_returned_to_the_user(self, get_tracker, record_recall):
        workflow_manage = MagicMock()
        tracker = {}
        get_tracker.return_value = tracker
        embedding_list = [
            {"paragraph_id": "paragraph-1", "source_type": SourceType.PARAGRAPH.value},
            {"paragraph_id": "paragraph-2", "source_type": SourceType.PARAGRAPH.value},
        ]

        _record_recalled_items(embedding_list, [{"id": "paragraph-2"}], workflow_manage)

        record_recall.assert_called_once_with([embedding_list[1]], tracker=tracker)

    @patch("application.workflow.nodes.search_knowledge_node.search_knowledge_node.record_recall_safely")
    def test_does_not_record_recall_in_debug_mode(self, record_recall):
        _record_recalled_items([{"paragraph_id": "paragraph-1"}], [{"id": "paragraph-1"}], MagicMock(), True)

        record_recall.assert_not_called()


class SearchDocumentNodeSourceTests(SimpleTestCase):
    @patch(
        "application.workflow.nodes.search_document_node.search_document_node.filter_workflow_knowledge",
        return_value=["knowledge-1"],
    )
    @patch(
        "application.workflow.nodes.search_document_node.search_document_node.filter_authorized_ids",
        return_value=["knowledge-1"],
    )
    @patch("application.workflow.nodes.search_document_node.search_document_node.QuerySet")
    def test_document_search_returns_source_fields_using_current_knowledge_type(
        self, query_set, _authorized, _workflow
    ):
        documents = MagicMock()
        knowledge = MagicMock()
        query_set.side_effect = {Document: documents, Knowledge: knowledge}.get
        documents.filter.return_value.values_list.return_value.__iter__.return_value = iter(["document-1"])
        documents.filter.return_value.values_list.return_value.distinct.return_value = ["knowledge-1"]
        documents.filter.return_value.values.return_value = [
            {
                "id": "document-1",
                "knowledge_id": "knowledge-1",
                "type": KnowledgeType.BASE,
                "resource_type": DocumentResourceType.IMAGE,
                "meta": {"source_file_id": "original-image-file"},
            }
        ]
        knowledge.filter.return_value.values.return_value = [{"id": "knowledge-1", "type": KnowledgeType.WEB}]
        node = SearchDocumentNode.__new__(SearchDocumentNode)
        node.get_parameters = MagicMock(return_value={"knowledge_id_list": ["knowledge-1"], "search_mode": "custom"})
        node.get_workflow_parameters = MagicMock(return_value={"workspace_id": "default"})
        node.workflow_manage = MagicMock()
        node.write_context = MagicMock()

        node.execute()

        output = next(call.args[1] for call in node.write_context.call_args_list if call.args[0] == "document_items")
        self.assertEqual(output[0]["knowledge_type"], KnowledgeType.WEB)
        self.assertEqual(output[0]["document_resource_type"], DocumentResourceType.IMAGE)
        self.assertEqual(output[0]["document_image_id"], "original-image-file")


class AIChatKnowledgeImageTests(SimpleTestCase):
    def setUp(self):
        search_node = SimpleNamespace(id="search", type="search-knowledge-node")
        condition_node = SimpleNamespace(id="condition", type="condition-node")
        start_node = SimpleNamespace(id="start", type="start-node")
        self.workflow_manage = MagicMock()
        self.workflow_manage.workflow.up_node_map = {
            "ai": [SimpleNamespace(node=condition_node)],
            "condition": [SimpleNamespace(node=search_node)],
            "search": [SimpleNamespace(node=start_node)],
        }
        self.asset = {
            "file_id": "00000000-0000-0000-0000-000000000006",
            "file_name": "chart.png",
        }
        self.workflow_manage.get_context.side_effect = lambda node_id, key: (
            [self.asset, self.asset] if node_id == "search" and key == "image_list" else None
        )

    def test_collects_deduplicated_images_from_upstream_knowledge_searches(self):
        self.assertEqual(_get_upstream_knowledge_images(self.workflow_manage, "ai"), [self.asset])

    @patch("application.workflow.nodes.ai_chat_node.ai_chat_node.filter_authorized_ids", return_value=[])
    @patch("application.workflow.nodes.ai_chat_node.ai_chat_node.get_model_instance_by_model_workspace_id")
    @patch("application.workflow.nodes.ai_chat_node.ai_chat_node._process_images")
    def test_vision_chat_receives_recalled_knowledge_images(self, process_images, get_model, _authorized):
        processed_image = {"type": "image_url", "image_url": {"url": "data:image/png;base64,image"}}
        process_images.return_value = [processed_image]
        self.workflow_manage.generate_prompt.side_effect = ["answer with the recalled context", "system prompt"]
        self.workflow_manage.workflow_type = WorkflowType.APPLICATION
        self.workflow_manage.get_parameters.return_value = {"workspace_id": "workspace"}
        node = AIChatNode(
            SimpleNamespace(id="ai"),
            self.workflow_manage,
            lambda _: {
                "model_id": "model",
                "model_params_setting": {},
                "prompt": "prompt",
                "system": "system",
                "vision": True,
                "stream": False,
            },
        )
        node._handle_mcp = MagicMock(return_value=False)
        node._invoke_response = MagicMock()

        node.execute()

        self.assertEqual(self.workflow_manage.generate_prompt.call_args_list, [call("prompt"), call("system")])
        get_model.return_value.invoke.assert_called_once()
        question = get_model.return_value.invoke.call_args.args[0][-1]
        process_images.assert_called_once_with([self.asset])
        self.assertEqual(question.content[0], processed_image)
        self.assertEqual(question.content[-1]["text"], "answer with the recalled context")
