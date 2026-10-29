from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from application.workflow.nodes.search_knowledge_node import search_knowledge_node as search_module
from common.exception.app_exception import AppApiException
from knowledge.models import DocumentResourceType, SearchMode, SourceType


class SearchKnowledgeImageTests(SimpleTestCase):
    def setUp(self):
        self.params = {
            "knowledge_id_list": ["00000000-0000-0000-0000-000000000001"],
            "question_reference_address": ["start-node", "question"],
            "knowledge_setting": {
                "top_n": 3,
                "similarity": 0.6,
                "search_mode": "embedding",
                "max_paragraph_char_number": 5000,
            },
            "show_knowledge": False,
        }
        self.images = [{"file_id": "00000000-0000-0000-0000-000000000002"}]
        self.workflow = MagicMock()
        self.workflow.get_parameters.return_value = {"workspace_id": "default", "chat_user_id": "viewer"}
        self.workflow.get_reference_field.side_effect = lambda node_id, fields: {
            "question": "find this chart",
            "image": self.images,
            "documents": ["selected-document"],
        }[fields[0]]
        self.node = search_module.SearchKnowledgeNode(
            SimpleNamespace(id="search"), self.workflow, lambda _: self.params
        )
        self.authorized = self.enterContext(
            patch.object(search_module, "filter_authorized_ids", return_value=self.params["knowledge_id_list"])
        )
        self.enterContext(
            patch.object(search_module, "filter_workflow_knowledge", side_effect=lambda knowledge_ids, _: knowledge_ids)
        )
        self.enterContext(patch.object(search_module, "_get_embedding_id", return_value="embedding-model"))
        self.model = self.enterContext(
            patch.object(search_module, "get_model_instance_by_model_workspace_id")
        ).return_value
        self.model.embed_query.return_value = [1.0, 0.0]
        self.model.supports_image_embedding.return_value = True
        self.vector = self.enterContext(patch.object(search_module.VectorStore, "get_embedding_vector")).return_value
        self.vector.query.return_value = None
        self.vector.hit_test.return_value = None
        self.load_images = self.enterContext(
            patch.object(search_module, "load_image_query_inputs", return_value=["data:image/png;base64,AA=="])
        )
        self.documents = self.enterContext(patch.object(search_module, "QuerySet")).return_value
        self.documents.filter.return_value.__iter__.return_value = iter([SimpleNamespace(id="disabled-document")])
        self.enterContext(patch.object(search_module, "connection"))

    def test_old_workflow_without_images_keeps_text_retrieval(self):
        serializer = search_module.SearchKnowledgeNodeSerializer(data=self.params)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["image_list"], [])

        self.node.execute()

        self.vector.query.assert_called_once_with(
            "find this chart",
            [1.0, 0.0],
            self.params["knowledge_id_list"],
            None,
            ["disabled-document"],
            [],
            True,
            3,
            0.6,
            SearchMode.embedding,
        )
        self.vector.hit_test.assert_not_called()
        self.load_images.assert_not_called()

    def test_empty_image_reference_value_keeps_text_retrieval(self):
        self.params["image_list"] = ["start-node", "image"]
        self.images = []

        self.node.execute()

        self.vector.query.assert_called_once()
        self.vector.hit_test.assert_not_called()
        self.load_images.assert_not_called()

    def test_images_use_multimodal_retrieval_and_preserve_document_and_rechat_filters(self):
        self.params.update(
            {
                "image_list": ["start-node", "image"],
                "search_scope_type": "referencing",
                "search_scope_source": "document",
                "search_scope_reference": ["upstream", "documents"],
            }
        )
        self.documents.filter.return_value.values_list.return_value.distinct.return_value = self.params[
            "knowledge_id_list"
        ]
        self.workflow.get_parameters.return_value.update(
            {
                "re_chat": True,
                "history_chat_record": [
                    SimpleNamespace(
                        problem_text="find this chart",
                        details={"search": {"type": "search-dataset-node", "paragraph_list": [{"id": "previous-hit"}]}},
                    )
                ],
            }
        )

        self.node.execute()

        self.load_images.assert_called_once_with(self.images, "viewer")
        self.vector.hit_test.assert_called_once_with(
            "find this chart",
            self.params["knowledge_id_list"],
            ["disabled-document"],
            3,
            0.6,
            SearchMode.embedding,
            self.model,
            ["data:image/png;base64,AA=="],
            document_id_list=["selected-document"],
            exclude_paragraph_id_list=["previous-hit"],
        )
        self.vector.query.assert_not_called()
        self.model.embed_query.assert_not_called()

    def test_keyword_mode_rejects_images_instead_of_silently_ignoring_them(self):
        self.params["image_list"] = ["start-node", "image"]
        self.params["knowledge_setting"]["search_mode"] = "keywords"

        with self.assertRaises(AppApiException):
            self.node.execute()

        self.vector.hit_test.assert_not_called()
        self.load_images.assert_not_called()

    def test_model_without_image_support_fails_before_loading_files(self):
        self.params["image_list"] = ["start-node", "image"]
        self.model.supports_image_embedding.return_value = False

        with self.assertRaises(AppApiException):
            self.node.execute()

        self.vector.hit_test.assert_not_called()
        self.load_images.assert_not_called()

    def test_invalid_image_variable_has_a_validation_error(self):
        self.params["image_list"] = ["start-node", "question"]

        with self.assertRaises(AppApiException):
            self.node.execute()

        self.load_images.assert_not_called()

    def test_no_authorized_knowledge_skips_image_loading_and_retrieval(self):
        self.params["image_list"] = ["start-node", "image"]
        self.authorized.return_value = []

        self.node.execute()

        self.load_images.assert_not_called()
        self.vector.hit_test.assert_not_called()
        self.vector.query.assert_not_called()

    def test_image_file_access_failure_is_propagated(self):
        self.params["image_list"] = ["start-node", "image"]
        self.load_images.side_effect = AppApiException(403, "No permission to access the query image")

        with self.assertRaises(AppApiException):
            self.node.execute()

        self.vector.hit_test.assert_not_called()

    def test_image_query_returns_image_markdown_to_reply_node(self):
        self.params["image_list"] = ["start-node", "image"]
        now = datetime(2026, 10, 29)
        paragraph = {
            "id": "image-paragraph",
            "title": "google",
            "content": "google",
            "knowledge_id": self.params["knowledge_id_list"][0],
            "document_id": "image-document",
            "document_resource_type": DocumentResourceType.IMAGE,
            "document_image_id": "original-image-file",
            "meta": {"allow_download": False},
            "hit_handling_method": "directly_return",
            "directly_return_similarity": 0.8,
            "create_time": now,
            "update_time": now,
        }
        self.vector.hit_test.return_value = [
            {"paragraph_id": "image-paragraph", "similarity": 0.95, "source_type": SourceType.PARAGRAPH.value}
        ]
        self.enterContext(patch.object(search_module, "_list_paragraph", return_value=[paragraph]))
        self.enterContext(patch.object(search_module, "get_hit_asset_map", return_value={}))
        self.enterContext(patch.object(search_module, "_record_recalled_items"))

        self.node.execute()

        context = {call.args[1]: call.args[2] for call in self.workflow.write_context.call_args_list}
        image_content = "![](./oss/file/original-image-file)\n\ngoogle"
        self.assertEqual(context["data"], f"#### google\n{image_content}")
        self.assertEqual(context["directly_return"], image_content)
        self.assertEqual(context["paragraph_list"][0]["content"], "google")
        self.assertEqual(context["paragraph_list"][0]["meta"], {"allow_download": False})
