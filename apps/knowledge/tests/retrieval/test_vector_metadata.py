from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from knowledge.models import Document, DocumentResourceType, Knowledge, SearchMode, SourceType
from knowledge.serializers.knowledge import KnowledgeSerializer
from knowledge.vector.pg_vector import BlendSearch, EmbeddingSearch, KeywordsSearch, PGVector


class VectorSearchMetadataTests(SimpleTestCase):
    @patch("knowledge.vector.pg_vector.select_list")
    @patch("knowledge.vector.pg_vector.generate_sql_by_query_dict", return_value=("SELECT", []))
    def test_all_search_modes_return_object_metadata(self, _generate_sql, select_list):
        metadata_cases = [
            (
                {"unit_type": "text", "content_type": "image_description"},
                {"unit_type": "text", "content_type": "image_description"},
            ),
            (
                '{"unit_type": "text", "content_type": "image_description"}',
                {"unit_type": "text", "content_type": "image_description"},
            ),
            ("{}", {}),
            (None, {}),
            ("", {}),
            ("invalid json", {}),
            ("null", {}),
            ('["text"]', {}),
            ('"text"', {}),
            ("1", {}),
            ([], {}),
            (1, {}),
        ]
        for search, mode in (
            (EmbeddingSearch(), SearchMode.embedding),
            (KeywordsSearch(), SearchMode.keywords),
            (BlendSearch(), SearchMode.blend),
        ):
            for meta, expected_meta in metadata_cases:
                with self.subTest(mode=mode, meta=meta):
                    row = {
                        "paragraph_id": "paragraph-1",
                        "source_id": "asset-1",
                        "source_type": SourceType.IMAGE.value,
                        "similarity": 0.9,
                        "comprehensive_score": 0.95,
                        "meta": meta,
                    }
                    select_list.return_value = [row]
                    expected_result = [{**row, "meta": expected_meta}]

                    result = search.handle(MagicMock(), "chart", [1.0, 0.0], 5, 0.6, mode)

                    self.assertEqual(result, expected_result)

    @patch("knowledge.vector.pg_vector.select_list", return_value=[])
    @patch("knowledge.vector.pg_vector.generate_sql_by_query_dict", return_value=("SELECT", []))
    def test_search_with_no_hits_still_returns_an_empty_list(self, _generate_sql, _select_list):
        for search, mode in (
            (EmbeddingSearch(), SearchMode.embedding),
            (KeywordsSearch(), SearchMode.keywords),
            (BlendSearch(), SearchMode.blend),
        ):
            with self.subTest(mode=mode):
                self.assertEqual(search.handle(MagicMock(), "chart", [1.0, 0.0], 5, 0.6, mode), [])

    @patch("knowledge.serializers.knowledge.get_hit_asset_map")
    @patch("knowledge.serializers.knowledge.list_paragraph")
    @patch("knowledge.serializers.knowledge.get_embedding_model_by_knowledge_id")
    @patch("knowledge.serializers.knowledge.QuerySet")
    @patch("knowledge.serializers.knowledge.VectorStore.get_embedding_vector", return_value=PGVector())
    @patch("knowledge.vector.pg_vector.select_list")
    @patch("knowledge.vector.pg_vector.generate_sql_by_query_dict", return_value=("SELECT", []))
    def test_hit_test_decodes_sql_metadata_and_preserves_image_description_hit_type(
        self, _generate_sql, select_list, _get_vector, query_set, get_model, list_paragraph, get_asset_map
    ):
        knowledge_id = "00000000-0000-0000-0000-000000000001"
        paragraph_id = "00000000-0000-0000-0000-000000000002"
        asset_id = "00000000-0000-0000-0000-000000000003"
        paragraph = {"id": paragraph_id, "content": "paragraph text", "meta": {"allow_download": True}}
        asset = {"id": asset_id, "file_name": "chart.png"}
        query_set.return_value.filter.return_value.exists.return_value = True
        query_set.return_value.filter.return_value.__iter__.return_value = iter([])
        get_model.return_value.embed_query.return_value = [1.0, 0.0]
        list_paragraph.return_value = [paragraph]
        get_asset_map.return_value = {asset_id: asset}
        select_list.return_value = [
            {
                "paragraph_id": paragraph_id,
                "source_id": asset_id,
                "source_type": SourceType.IMAGE.value,
                "similarity": 0.9,
                "comprehensive_score": 0.95,
                "meta": '{"unit_type": "text", "content_type": "image_description"}',
            }
        ]

        result = KnowledgeSerializer.HitTest(
            data={
                "workspace_id": "default",
                "knowledge_id": knowledge_id,
                "query_text": "chart",
                "top_number": 5,
                "similarity": 0.6,
                "search_mode": SearchMode.embedding.value,
            }
        ).hit_test()

        self.assertEqual(
            result,
            [
                {
                    **paragraph,
                    "document_resource_type": DocumentResourceType.DOCUMENT,
                    "similarity": 0.9,
                    "comprehensive_score": 0.95,
                    "source_id": asset_id,
                    "source_type": SourceType.IMAGE.value,
                    "hit_unit_type": "text",
                    "query_unit_type": "text",
                    "query_unit_index": 0,
                    "hit_asset": asset,
                }
            ],
        )

    @patch("knowledge.serializers.knowledge.get_hit_asset_map", return_value={})
    @patch("knowledge.serializers.knowledge.list_paragraph")
    @patch("knowledge.serializers.knowledge.get_embedding_model_by_knowledge_id")
    @patch("knowledge.serializers.knowledge.QuerySet")
    @patch("knowledge.serializers.knowledge.VectorStore.get_embedding_vector")
    def test_hit_test_reports_document_origin_independently_of_vector_type(
        self, get_vector, query_set, _get_model, list_paragraph, _get_asset_map
    ):
        knowledge_id = "00000000-0000-0000-0000-000000000001"
        knowledge_query = MagicMock()
        knowledge_query.filter.return_value.exists.return_value = True
        document_query = MagicMock()
        query_set.side_effect = {Knowledge: knowledge_query, Document: document_query}.get
        document_query.filter.return_value.values_list.return_value = [
            ("image-document", DocumentResourceType.IMAGE),
            ("ordinary-document", DocumentResourceType.DOCUMENT),
        ]
        paragraphs = [
            {"id": "image-text", "document_id": "image-document"},
            {"id": "image-vector", "document_id": "image-document"},
            {"id": "ordinary-text", "document_id": "ordinary-document"},
            {"id": "ordinary-image", "document_id": "ordinary-document"},
        ]
        list_paragraph.return_value = paragraphs
        get_vector.return_value.hit_test.return_value = [
            {
                "paragraph_id": paragraph["id"],
                "source_type": source_type,
                "meta": {"unit_type": unit_type},
            }
            for paragraph, source_type, unit_type in zip(
                paragraphs,
                [SourceType.PARAGRAPH, SourceType.IMAGE, SourceType.PARAGRAPH, SourceType.IMAGE],
                ["text", "image", "text", "image"],
            )
        ]

        result = KnowledgeSerializer.HitTest(
            data={
                "workspace_id": "default",
                "knowledge_id": knowledge_id,
                "query_text": "chart",
                "top_number": 5,
                "similarity": 0.6,
                "search_mode": SearchMode.embedding.value,
            }
        ).hit_test()

        self.assertEqual(
            [row["document_resource_type"] for row in result],
            [
                DocumentResourceType.IMAGE,
                DocumentResourceType.IMAGE,
                DocumentResourceType.DOCUMENT,
                DocumentResourceType.DOCUMENT,
            ],
        )
        self.assertEqual([row["hit_unit_type"] for row in result], ["text", "image", "text", "image"])
        document_query.filter.return_value.values_list.assert_called_once_with("id", "resource_type")
