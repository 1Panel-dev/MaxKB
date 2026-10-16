from contextlib import nullcontext
from unittest.mock import MagicMock, patch

from common.exception.app_exception import AppApiException
from django.test import SimpleTestCase
from django.utils import timezone
from knowledge.models import (
    Document,
    Paragraph,
    ParagraphAsset,
    Problem,
    ProblemParagraphMapping,
    SearchMode,
    SourceType,
)
from knowledge.serializers.knowledge import (
    HitTestSerializer,
)
from knowledge.serializers.problem import ProblemInstanceSerializer, ProblemSerializer
from knowledge.services.multimodal_retrieval import get_hit_asset_map, load_image_query_inputs
from knowledge.services.retrieval_stats import (
    collect_recall_asset_ids,
    collect_recall_source_ids,
    get_recall_tracker,
    record_recall,
)
from knowledge.vector.pg_vector import PGVector


class ProblemRecallSerializerTests(SimpleTestCase):
    def test_problem_serializers_include_recall_statistics(self):
        recalled_at = timezone.now()
        problem = Problem(
            id="00000000-0000-0000-0000-000000000040",
            knowledge_id="00000000-0000-0000-0000-000000000041",
            content="How does image retrieval work?",
            hit_num=7,
            last_hit_time=recalled_at,
        )

        model_data = ProblemSerializer(problem).data
        instance_data = ProblemInstanceSerializer(problem).data

        self.assertEqual(model_data["hit_num"], 7)
        self.assertIsNotNone(model_data["last_hit_time"])
        self.assertEqual(instance_data["hit_num"], 7)
        self.assertIsNotNone(instance_data["last_hit_time"])


class MultimodalHitTestTests(SimpleTestCase):
    request_data = {
        "top_number": 5,
        "similarity": 0.6,
        "search_mode": SearchMode.embedding.value,
    }

    def test_accepts_an_image_only_query(self):
        serializer = HitTestSerializer(
            data={
                **self.request_data,
                "image_list": [
                    {
                        "file_id": "00000000-0000-0000-0000-000000000001",
                        "name": "query.png",
                        "url": "./oss/file/00000000-0000-0000-0000-000000000001",
                    }
                ],
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["query_text"], "")

    def test_requires_text_or_at_least_one_image(self):
        serializer = HitTestSerializer(data=self.request_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_rejects_images_in_keyword_search(self):
        serializer = HitTestSerializer(
            data={
                **self.request_data,
                "query_text": "breakfast",
                "search_mode": SearchMode.keywords.value,
                "image_list": [{"file_id": "00000000-0000-0000-0000-000000000001"}],
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("search_mode", serializer.errors)

    @patch("knowledge.services.multimodal_retrieval.QuerySet")
    def test_uploaded_image_is_converted_to_a_data_url(self, query_set):
        file = MagicMock(
            id="00000000-0000-0000-0000-000000000001",
            file_name="query.png",
            meta={"user_id": "00000000-0000-0000-0000-000000000002"},
        )
        file.get_bytes.return_value = b"image-content"
        query_set.return_value.filter.return_value = [file]

        image_inputs = load_image_query_inputs(
            [{"file_id": file.id}],
            user_id="00000000-0000-0000-0000-000000000002",
        )

        self.assertEqual(image_inputs, ["data:image/png;base64,aW1hZ2UtY29udGVudA=="])

    @patch("knowledge.services.multimodal_retrieval.ParagraphAsset.objects.select_related")
    def test_image_hit_includes_asset_recall_statistics(self, select_related):
        recalled_at = timezone.now()
        asset = MagicMock(
            id="00000000-0000-0000-0000-000000000004",
            file_id="00000000-0000-0000-0000-000000000005",
            position=1,
            caption="chart",
            ocr_text="revenue 100",
            description="upward trend",
            hit_num=7,
            last_hit_time=recalled_at,
        )
        asset.file.file_name = "chart.png"
        select_related.return_value.filter.return_value = [asset]

        result = get_hit_asset_map(
            [
                {
                    "source_id": str(asset.id),
                    "source_type": SourceType.IMAGE.value,
                }
            ]
        )

        self.assertEqual(result[str(asset.id)]["hit_num"], 7)
        self.assertEqual(result[str(asset.id)]["last_hit_time"], recalled_at.isoformat())


class MultimodalVectorSearchTests(SimpleTestCase):
    @patch("knowledge.vector.pg_vector.search_handle_list", new_callable=list)
    @patch("knowledge.vector.pg_vector.QuerySet")
    def test_text_and_images_are_searched_independently_and_fused_by_best_score(self, query_set, search_handles):
        query_set.return_value.filter.return_value.exclude.return_value = MagicMock()
        search_handle = MagicMock()
        search_handle.support.return_value = True
        search_handle.handle.side_effect = [
            [
                {
                    "paragraph_id": "paragraph-1",
                    "source_id": "paragraph-1",
                    "source_type": SourceType.PARAGRAPH.value,
                    "similarity": 0.7,
                    "comprehensive_score": 0.7,
                },
                {
                    "paragraph_id": "paragraph-2",
                    "source_id": "paragraph-2",
                    "source_type": SourceType.PARAGRAPH.value,
                    "similarity": 0.6,
                    "comprehensive_score": 0.6,
                },
            ],
            [
                {
                    "paragraph_id": "paragraph-1",
                    "source_id": "asset-1",
                    "source_type": SourceType.IMAGE.value,
                    "similarity": 0.8,
                    "comprehensive_score": 0.8,
                }
            ],
        ]
        search_handles[:] = [search_handle]
        embedding_model = MagicMock()
        embedding_model.supports_image_embedding.return_value = True
        embedding_model.embed_query.return_value = [1.0, 0.0]
        embedding_model.embed_images.return_value = [[0.0, 1.0]]

        result = PGVector().hit_test(
            "breakfast",
            ["knowledge-1"],
            [],
            5,
            0.6,
            SearchMode.embedding,
            embedding_model,
            ["data:image/png;base64,AA=="],
        )

        self.assertEqual([item["paragraph_id"] for item in result], ["paragraph-1", "paragraph-2"])
        self.assertEqual(result[0]["source_type"], SourceType.IMAGE.value)
        self.assertEqual(result[0]["query_unit_type"], "image")
        self.assertEqual(search_handle.handle.call_count, 2)

    @patch("knowledge.vector.pg_vector.QuerySet")
    def test_rejects_image_query_when_embedding_model_has_no_image_capability(self, query_set):
        embedding_model = MagicMock()
        embedding_model.supports_image_embedding.return_value = False

        with self.assertRaises(AppApiException):
            PGVector().hit_test(
                "",
                ["knowledge-1"],
                [],
                5,
                0.6,
                SearchMode.embedding,
                embedding_model,
                ["data:image/png;base64,AA=="],
            )

        query_set.assert_not_called()


class RecallStatisticsTests(SimpleTestCase):
    def test_collects_unique_paragraph_and_winning_problem_mapping_ids(self):
        recall_items = [
            {"paragraph_id": "paragraph-1", "source_type": SourceType.PROBLEM.value, "source_id": "mapping-1"},
            {"paragraph_id": "paragraph-1", "source_type": SourceType.PROBLEM.value, "source_id": "mapping-1"},
            {"paragraph_id": "paragraph-2", "source_type": SourceType.PARAGRAPH.value, "source_id": "paragraph-2"},
        ]

        paragraph_ids, problem_mapping_ids = collect_recall_source_ids(recall_items)

        self.assertEqual(paragraph_ids, {"paragraph-1", "paragraph-2"})
        self.assertEqual(problem_mapping_ids, {"mapping-1"})

    def test_collects_unique_winning_image_asset_ids(self):
        recall_items = [
            {"paragraph_id": "paragraph-1", "source_type": SourceType.IMAGE.value, "source_id": "asset-1"},
            {"paragraph_id": "paragraph-1", "source_type": SourceType.IMAGE.value, "source_id": "asset-1"},
            {"paragraph_id": "paragraph-2", "source_type": SourceType.PARAGRAPH.value, "source_id": "asset-2"},
        ]

        self.assertEqual(collect_recall_asset_ids(recall_items), {"asset-1"})

    def test_ignores_problem_mapping_when_paragraph_content_wins(self):
        paragraph_ids, problem_mapping_ids = collect_recall_source_ids(
            [{"paragraph_id": "paragraph-1", "source_type": SourceType.PARAGRAPH.value, "source_id": "mapping-1"}]
        )

        self.assertEqual(paragraph_ids, {"paragraph-1"})
        self.assertEqual(problem_mapping_ids, set())

    def test_reuses_one_tracker_for_the_same_retrieval_owner(self):
        owner = object.__new__(type("RecallOwner", (), {}))

        tracker = get_recall_tracker(owner)
        tracker["paragraph_ids"] = {"paragraph-1"}

        self.assertIs(get_recall_tracker(owner), tracker)
        self.assertEqual(get_recall_tracker(owner)["paragraph_ids"], {"paragraph-1"})

    @patch("knowledge.services.retrieval_stats.transaction.atomic", side_effect=lambda: nullcontext())
    @patch("knowledge.services.retrieval_stats.QuerySet")
    def test_updates_each_resource_once_and_deduplicates_with_tracker(self, query_set, _atomic):
        paragraph_query = MagicMock()
        paragraph_filter = paragraph_query.filter.return_value
        paragraph_filter.values_list.return_value = [
            ("paragraph-1", "document-1"),
            ("paragraph-2", "document-1"),
        ]
        mapping_query = MagicMock()
        mapping_query.filter.return_value.values_list.return_value = ["problem-1", "problem-1"]
        document_query = MagicMock()
        problem_query = MagicMock()
        asset_query = MagicMock()
        queries = {
            Paragraph: paragraph_query,
            ProblemParagraphMapping: mapping_query,
            Document: document_query,
            Problem: problem_query,
            ParagraphAsset: asset_query,
        }
        query_set.side_effect = lambda model: queries[model]
        recall_items = [
            {"paragraph_id": "paragraph-1", "source_type": SourceType.PROBLEM.value, "source_id": "mapping-1"},
            {"paragraph_id": "paragraph-2", "source_type": SourceType.PARAGRAPH.value, "source_id": "paragraph-2"},
            {"paragraph_id": "paragraph-2", "source_type": SourceType.IMAGE.value, "source_id": "asset-1"},
        ]
        recalled_at = timezone.now()
        tracker = {}

        record_recall(recall_items, tracker=tracker, recalled_at=recalled_at)
        record_recall(recall_items, tracker=tracker, recalled_at=recalled_at)

        self.assertEqual(paragraph_filter.update.call_count, 1)
        self.assertEqual(document_query.filter.return_value.update.call_count, 1)
        self.assertEqual(problem_query.filter.return_value.update.call_count, 1)
        self.assertEqual(asset_query.filter.return_value.update.call_count, 1)
        self.assertEqual(paragraph_filter.update.call_args.kwargs["last_hit_time"], recalled_at)
        self.assertEqual(document_query.filter.return_value.update.call_args.kwargs["last_hit_time"], recalled_at)
        self.assertEqual(problem_query.filter.return_value.update.call_args.kwargs["last_hit_time"], recalled_at)
        self.assertEqual(asset_query.filter.return_value.update.call_args.kwargs["last_hit_time"], recalled_at)
