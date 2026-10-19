from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from application.serializers.application_chat_record import ApplicationChatRecordQuerySerializers
from knowledge.models import DocumentResourceType, KnowledgeType


class ChatRecordSourceTests(SimpleTestCase):
    def setUp(self):
        self.paragraph = {"id": "paragraph-1", "document_id": "document-1", "knowledge_id": "knowledge-1"}
        self.record = SimpleNamespace(
            details={
                "search": {"type": "search-knowledge-node", "show_knowledge": True, "paragraph_list": [self.paragraph]}
            },
            improve_paragraph_id_list=[],
        )
        serializer = patch("application.serializers.application_chat_record.ChatRecordSerializerModel")
        serializer.start().return_value.data = {}
        self.addCleanup(serializer.stop)

    @patch("knowledge.services.multimodal_retrieval.QuerySet")
    def test_legacy_chat_sources_include_document_metadata_without_changing_snapshot(self, query_set):
        query_set.return_value.filter.return_value.values_list.return_value = [
            ("document-1", KnowledgeType.WORKFLOW, DocumentResourceType.IMAGE, "original-image-file")
        ]

        result = ApplicationChatRecordQuerySerializers.reset_chat_record(self.record, True, False)

        self.assertEqual(result["paragraph_list"][0]["knowledge_type"], KnowledgeType.WORKFLOW)
        self.assertEqual(result["paragraph_list"][0]["document_resource_type"], DocumentResourceType.IMAGE)
        self.assertEqual(result["paragraph_list"][0]["document_image_id"], "original-image-file")
        self.assertEqual(result["knowledge_list"][0]["knowledge_type"], KnowledgeType.WORKFLOW)
        self.assertNotIn("document_image_id", self.paragraph)

    @patch("knowledge.services.multimodal_retrieval.QuerySet")
    def test_hidden_sources_do_not_load_metadata(self, query_set):
        result = ApplicationChatRecordQuerySerializers.reset_chat_record(self.record, False, False)

        self.assertNotIn("paragraph_list", result)
        query_set.assert_not_called()

    @patch("knowledge.services.multimodal_retrieval.QuerySet")
    def test_reranker_sources_include_metadata(self, query_set):
        self.record.details = {
            "rerank": {"type": "reranker-node", "show_knowledge": True, "result_list": [{"metadata": self.paragraph}]}
        }
        query_set.return_value.filter.return_value.values_list.return_value = [
            ("document-1", KnowledgeType.LARK, DocumentResourceType.DOCUMENT, "ordinary-file")
        ]

        result = ApplicationChatRecordQuerySerializers.reset_chat_record(self.record, True, False)

        self.assertEqual(result["paragraph_list"][0]["knowledge_type"], KnowledgeType.LARK)
        self.assertEqual(result["paragraph_list"][0]["document_resource_type"], DocumentResourceType.DOCUMENT)
        self.assertIsNone(result["paragraph_list"][0]["document_image_id"])
