from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from knowledge.models import DocumentResourceType, KnowledgeType, ProblemParagraphMapping, SearchMode, SourceType
from knowledge.serializers.common import list_paragraph as query_paragraphs
from knowledge.serializers.knowledge import KnowledgeSerializer
from knowledge.serializers.problem import ProblemSerializers
from knowledge.services.multimodal_retrieval import enrich_paragraph_sources
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
        paragraph = {
            "id": paragraph_id,
            "content": "paragraph text",
            "meta": {"allow_download": True},
            "knowledge_type": KnowledgeType.BASE,
            "document_resource_type": DocumentResourceType.DOCUMENT,
            "document_image_id": None,
        }
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
                    "knowledge_type": KnowledgeType.BASE,
                    "document_resource_type": DocumentResourceType.DOCUMENT,
                    "document_image_id": None,
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

    @patch("knowledge.services.multimodal_retrieval.QuerySet")
    def test_paragraph_sources_report_document_origin_independently_of_vector_type(self, query_set):
        image_file_id = "00000000-0000-0000-0000-000000000010"
        query_set.return_value.filter.return_value.values_list.return_value = [
            ("image-document", KnowledgeType.BASE, DocumentResourceType.IMAGE, image_file_id),
            ("ordinary-document", KnowledgeType.WORKFLOW, DocumentResourceType.DOCUMENT, "ordinary-file"),
            ("image-without-file", KnowledgeType.BASE, DocumentResourceType.IMAGE, None),
        ]
        paragraphs = [
            {"id": "image-text", "document_id": "image-document", "hit_unit_type": "text"},
            {"id": "image-vector", "document_id": "image-document", "hit_unit_type": "image"},
            {"id": "ordinary-text", "document_id": "ordinary-document", "hit_unit_type": "text"},
            {"id": "ordinary-image", "document_id": "ordinary-document", "hit_unit_type": "image"},
            {"id": "image-without-file", "document_id": "image-without-file"},
        ]

        result = enrich_paragraph_sources(paragraphs)

        self.assertEqual(
            [row["document_resource_type"] for row in result],
            [
                DocumentResourceType.IMAGE,
                DocumentResourceType.IMAGE,
                DocumentResourceType.DOCUMENT,
                DocumentResourceType.DOCUMENT,
                DocumentResourceType.IMAGE,
            ],
        )
        self.assertEqual([row.get("hit_unit_type") for row in result], ["text", "image", "text", "image", None])
        self.assertEqual([row["knowledge_type"] for row in result], [0, 0, 4, 4, 0])
        self.assertEqual([row["document_image_id"] for row in result], [image_file_id, image_file_id, None, None, None])
        self.assertTrue(all("source_file_id" not in row and "image_id" not in row for row in result))
        self.assertNotIn("document_resource_type", paragraphs[0])
        query_set.return_value.filter.return_value.values_list.assert_called_once_with(
            "id", "knowledge__type", "resource_type", "meta__source_file_id"
        )

    @patch("knowledge.services.multimodal_retrieval.QuerySet")
    def test_complete_sources_and_empty_results_do_not_query_documents(self, query_set):
        paragraph = {
            "document_id": "document-1",
            "knowledge_type": KnowledgeType.BASE,
            "document_resource_type": DocumentResourceType.DOCUMENT,
            "document_image_id": None,
        }

        self.assertEqual(enrich_paragraph_sources([paragraph]), [paragraph])
        self.assertEqual(enrich_paragraph_sources([]), [])
        query_set.assert_not_called()

    @patch("knowledge.services.multimodal_retrieval.QuerySet")
    def test_deleted_document_preserves_known_source_fields(self, query_set):
        query_set.return_value.filter.return_value.values_list.return_value = []
        result = enrich_paragraph_sources([{"document_id": "deleted", "knowledge_type": KnowledgeType.LARK}])

        self.assertEqual(result[0]["knowledge_type"], KnowledgeType.LARK)
        self.assertIsNone(result[0]["document_image_id"])

    @patch("knowledge.services.multimodal_retrieval.QuerySet")
    @patch("knowledge.serializers.common.native_search")
    def test_common_paragraph_query_includes_source_fields(self, native_search, query_set):
        native_search.return_value = [{"id": "paragraph-1", "document_id": "document-1"}]
        query_set.return_value.filter.return_value.values_list.return_value = [
            ("document-1", KnowledgeType.WEB, DocumentResourceType.DOCUMENT, "source-file")
        ]

        result = query_paragraphs(["00000000-0000-0000-0000-000000000001"])

        self.assertEqual(result[0]["knowledge_type"], KnowledgeType.WEB)
        self.assertEqual(result[0]["document_resource_type"], DocumentResourceType.DOCUMENT)
        self.assertIsNone(result[0]["document_image_id"])

    @patch("knowledge.services.multimodal_retrieval.QuerySet")
    @patch("knowledge.serializers.problem.native_search")
    @patch("knowledge.serializers.problem.QuerySet")
    def test_problem_paragraph_query_includes_source_fields(self, problem_query, native_search, query_set):
        mapping_query = MagicMock()
        mapping_query.filter.return_value = [MagicMock(paragraph_id="paragraph-1")]
        problem_query.side_effect = lambda model: mapping_query if model == ProblemParagraphMapping else MagicMock()
        native_search.return_value = [{"id": "paragraph-1", "document_id": "document-1"}]
        query_set.return_value.filter.return_value.values_list.return_value = [
            ("document-1", KnowledgeType.BASE, DocumentResourceType.IMAGE, "image-file")
        ]

        result = ProblemSerializers.Operate(
            data={
                "workspace_id": "default",
                "knowledge_id": "00000000-0000-0000-0000-000000000001",
                "problem_id": "00000000-0000-0000-0000-000000000002",
            }
        ).list_paragraph()

        self.assertEqual(result[0]["document_image_id"], "image-file")
