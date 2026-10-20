from unittest.mock import MagicMock, patch
from uuid import UUID

from django.test import SimpleTestCase

from knowledge.models import SearchMode
from knowledge.vector.pg_vector import PGVector


class WorkflowImageScopeTests(SimpleTestCase):
    @patch("knowledge.vector.pg_vector.search_handle_list", new_callable=list)
    def test_every_text_and_image_query_keeps_document_and_paragraph_filters(self, search_handles):
        knowledge_id, disabled_document, selected_document, previous_hit = [UUID(int=index) for index in range(1, 5)]
        search_handle = MagicMock()
        search_handle.support.return_value = True
        search_handle.handle.side_effect = [
            [{"paragraph_id": "same-paragraph", "similarity": 0.7, "comprehensive_score": 0.7}],
            [{"paragraph_id": "same-paragraph", "similarity": 0.9, "comprehensive_score": 0.9}],
            [{"paragraph_id": "other-paragraph", "similarity": 0.8, "comprehensive_score": 0.8}],
        ]
        search_handles[:] = [search_handle]
        model = MagicMock()
        model.embed_query.return_value = [1.0, 0.0]
        model.embed_images.return_value = [[0.0, 1.0], [0.5, 0.5]]

        result = PGVector().hit_test(
            "chart",
            [str(knowledge_id)],
            [str(disabled_document)],
            2,
            0.6,
            SearchMode.blend,
            model,
            ["data:image/png;base64,AA==", "data:image/png;base64,AQ=="],
            document_id_list=[str(selected_document)],
            exclude_paragraph_id_list=[str(previous_hit)],
        )

        self.assertEqual([hit["paragraph_id"] for hit in result], ["same-paragraph", "other-paragraph"])
        self.assertEqual(result[0]["query_unit_type"], "image")
        self.assertEqual(result[0]["query_unit_index"], 1)
        for request in search_handle.handle.call_args_list:
            query = request.args[0].query
            sql, parameters = query.sql_with_params()
            # Each exclusion must be independent: NOT document AND NOT paragraph,
            # rather than excluding only rows that match both.
            self.assertEqual(sql.count("NOT ("), 2)
            for identifier in (knowledge_id, disabled_document, selected_document, previous_hit):
                self.assertIn(identifier, parameters)
            exclusions = [condition for condition in query.where.children if getattr(condition, "negated", False)]
            self.assertEqual(
                [condition.children[0].lhs.target.column for condition in exclusions],
                ["document_id", "paragraph_id"],
            )
        self.assertEqual(
            [request.args[5] for request in search_handle.handle.call_args_list],
            [
                SearchMode.blend,
                SearchMode.embedding,
                SearchMode.embedding,
            ],
        )

    def test_empty_document_scope_does_not_search_all_documents(self):
        model = MagicMock()

        result = PGVector().hit_test(
            "",
            ["knowledge"],
            [],
            3,
            0.6,
            SearchMode.embedding,
            model,
            ["image"],
            document_id_list=[],
        )

        self.assertEqual(result, [])
        model.embed_images.assert_not_called()
        model.embed_query.assert_not_called()
