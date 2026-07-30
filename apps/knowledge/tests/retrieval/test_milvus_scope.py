from unittest.mock import MagicMock, call, patch
from uuid import UUID

from django.test import SimpleTestCase

from knowledge.models import SearchMode
from knowledge.vector.milvus_vector import MilvusVector


class MilvusWorkflowImageScopeTests(SimpleTestCase):
    @patch("knowledge.vector.milvus_vector.text_rank_by_ids", return_value={})
    @patch("knowledge.vector.milvus_vector.pg_vector_recall", return_value=[])
    @patch.object(MilvusVector, "_milvus_search")
    def test_text_and_images_keep_filters_in_milvus_and_pg_fallback(self, search, pg_recall, _text_rank):
        search.side_effect = [
            [{"id": "text", "paragraph_id": "same-paragraph", "similarity": 0.7}],
            [{"id": "image-1", "paragraph_id": "same-paragraph", "similarity": 0.9}],
            [{"id": "image-2", "paragraph_id": "other-paragraph", "similarity": 0.8}],
        ]
        model = MagicMock()
        model.embed_query.return_value = [1.0, 0.0]
        model.embed_images.return_value = [[0.0, 1.0], [0.5, 0.5]]

        result = MilvusVector().hit_test(
            "chart",
            ["knowledge"],
            ["disabled-document"],
            2,
            0.6,
            SearchMode.blend,
            model,
            ["image-1", "image-2"],
            document_id_list=["selected-document"],
            exclude_paragraph_id_list=["previous-hit"],
        )

        self.assertEqual([hit["paragraph_id"] for hit in result], ["same-paragraph", "other-paragraph"])
        self.assertEqual(result[0]["query_unit_type"], "image")
        self.assertEqual(result[0]["query_unit_index"], 1)
        embeddings = [[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]]
        self.assertEqual(
            search.call_args_list,
            [
                call("knowledge", vector, 2, True, ["selected-document"], ["disabled-document"], ["previous-hit"])
                for vector in embeddings
            ],
        )
        self.assertEqual(
            pg_recall.call_args_list,
            [
                call(vector, ["knowledge"], True, ["selected-document"], ["disabled-document"], ["previous-hit"], 2)
                for vector in embeddings
            ],
        )

    @patch("knowledge.vector.milvus_vector.KeywordsSearch.handle", return_value=[])
    def test_keyword_search_keeps_document_and_paragraph_filters(self, search):
        knowledge_id, disabled_document, selected_document, previous_hit = [UUID(int=index) for index in range(1, 5)]

        MilvusVector().hit_test(
            "chart",
            [str(knowledge_id)],
            [str(disabled_document)],
            2,
            0.6,
            SearchMode.keywords,
            MagicMock(),
            document_id_list=[str(selected_document)],
            exclude_paragraph_id_list=[str(previous_hit)],
        )

        search.assert_called_once()
        sql, parameters = search.call_args.args[0].query.sql_with_params()
        self.assertEqual(sql.count("NOT ("), 2)
        for identifier in (knowledge_id, disabled_document, selected_document, previous_hit):
            self.assertIn(identifier, parameters)

    @patch.object(MilvusVector, "_dispatch_search")
    def test_empty_document_scope_skips_embedding_and_search(self, search):
        model = MagicMock()
        for mode in (SearchMode.embedding, SearchMode.blend, SearchMode.keywords):
            with self.subTest(mode=mode):
                result = MilvusVector().hit_test(
                    "chart", ["knowledge"], [], 3, 0.6, mode, model, ["image"], document_id_list=[]
                )
                self.assertEqual(result, [])

        self.assertEqual(model.mock_calls, [])
        search.assert_not_called()
