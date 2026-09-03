from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from application.workflow.nodes.ai_chat_node.ai_chat_node import AIChatNode, _get_upstream_knowledge_images
from application.workflow.nodes.search_knowledge_node.search_knowledge_node import (
    _get_recalled_image_list,
    _record_recalled_items,
    _reset_paragraph,
)
from knowledge.models import SourceType


class SearchKnowledgeNodeTests(SimpleTestCase):
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

    @patch("application.workflow.nodes.ai_chat_node.ai_chat_node._process_images")
    def test_vision_chat_receives_recalled_knowledge_images(self, process_images):
        processed_image = {"type": "image_url", "image_url": {"url": "data:image/png;base64,image"}}
        process_images.return_value = [processed_image]
        self.workflow_manage.generate_prompt.return_value = "answer with the recalled context"
        node = AIChatNode.__new__(AIChatNode)
        node.node = SimpleNamespace(id="ai")
        node.workflow_manage = self.workflow_manage

        question = node._generate_prompt_question("prompt", MagicMock(), True, None, None)

        process_images.assert_called_once_with([self.asset])
        self.assertEqual(question.content[0], processed_image)
        self.assertEqual(question.content[-1]["text"], "answer with the recalled context")
