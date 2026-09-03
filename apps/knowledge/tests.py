from contextlib import nullcontext
from io import BytesIO
from unittest.mock import MagicMock, patch

from application.flow.i_step_node import KnowledgeWorkflowPostHandler
from common.exception.app_exception import AppApiException
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from django.utils import timezone
from knowledge.models import (
    AssetProcessStatus,
    ContentOrigin,
    Document,
    DocumentResourceType,
    FileSourceType,
    Knowledge,
    KnowledgeSyncLog,
    KnowledgeSyncStatus,
    KnowledgeSyncTrigger,
    KnowledgeSyncType,
    KnowledgeType,
    LocalState,
    Paragraph,
    Problem,
    ProblemParagraphMapping,
    SearchMode,
    SourceType,
    SyncState,
    ParagraphAsset,
)
from knowledge.models.knowledge_action import State as KnowledgeActionState
from knowledge.serializers.document import DocumentSerializers, DocumentWebInstanceSerializer
from knowledge.serializers.document_strategy import DocumentSyncStrategySerializer
from knowledge.serializers.image_document import ImagePreviewUpdateRequest
from knowledge.serializers.knowledge import (
    HitTestSerializer,
    KnowledgeEditRequest,
    KnowledgeSerializer,
    KnowledgeWebCreateRequest,
)
from knowledge.serializers.knowledge_sync import (
    KnowledgeSyncSettingOperationSerializer,
    KnowledgeSyncSettingRequest,
)
from knowledge.serializers.knowledge_workflow import KnowledgeWorkflowActionSerializer
from knowledge.serializers.problem import ProblemInstanceSerializer, ProblemSerializer
from knowledge.services.document_strategy import (
    apply_length_strategy,
    document_source_hash,
    normalize_document_strategy,
    parse_web_content,
    strategy_hashes,
)
from knowledge.services.image_documents import ImageDocumentService
from knowledge.services.incremental_sync import IncrementalDocumentSync, MergeResult, prepare_remote_paragraphs
from knowledge.services.knowledge_sync_schedule import (
    deploy_knowledge_sync_job,
    normalize_knowledge_sync_setting,
)
from knowledge.services.multimodal_retrieval import get_hit_asset_map, load_image_query_inputs
from knowledge.services.paragraph_assets import (
    embed_paragraph_assets,
    paragraph_asset_source_key,
    paragraph_content_schema,
    process_visual_assets,
    resolve_visual_processor,
    sync_paragraph_assets,
)
from knowledge.services.retrieval_stats import (
    collect_recall_asset_ids,
    collect_recall_source_ids,
    get_recall_tracker,
    record_recall,
)
from knowledge.services.workflow_sync import merge_workflow_incremental_snapshot, workflow_document_identity
from knowledge.task.handler import get_save_handler, get_sync_handler, normalize_web_url
from knowledge.task.sync import (
    get_selector_list,
    scheduled_sync_knowledge,
    scheduled_sync_web_knowledge,
    scheduled_sync_workflow_knowledge,
    sync_replace_web_knowledge,
)
from knowledge.vector.pg_vector import PGVector
from knowledge.web_assets import internalize_web_images
from PIL import Image
from rest_framework.exceptions import ValidationError


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


class ImageDocumentTests(SimpleTestCase):
    def test_document_list_defaults_to_document_resources(self):
        serializer = DocumentSerializers.Query(
            data={
                "workspace_id": "workspace",
                "knowledge_id": "00000000-0000-0000-0000-000000000037",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["resource_type"], DocumentResourceType.DOCUMENT)

    def test_generic_document_creation_cannot_forge_an_image_resource(self):
        result = DocumentSerializers.Create.get_document_paragraph_model(
            "00000000-0000-0000-0000-000000000039",
            "user-id",
            {
                "name": "forged-image.png",
                "paragraphs": [],
                "resource_type": DocumentResourceType.IMAGE,
            },
        )

        self.assertEqual(result["document"].resource_type, DocumentResourceType.DOCUMENT)

    @patch("knowledge.services.image_documents.QuerySet")
    def test_standalone_images_are_rejected_for_external_knowledge_bases(self, query_set):
        query_set.return_value.filter.return_value.first.return_value = Knowledge(
            id="00000000-0000-0000-0000-000000000038",
            workspace_id="workspace",
            name="web",
            desc="",
            type=KnowledgeType.WEB,
        )

        with self.assertRaises(AppApiException):
            ImageDocumentService("workspace", "00000000-0000-0000-0000-000000000038").get_knowledge()

    def test_preview_edit_accepts_name_and_description(self):
        serializer = ImagePreviewUpdateRequest(data={"name": "renamed.png", "description": "updated"})

        self.assertTrue(serializer.is_valid(), serializer.errors)

    @patch("knowledge.services.image_documents.QuerySet")
    @patch("knowledge.services.image_documents.File")
    def test_upload_creates_an_editable_preview_without_visual_processing(self, file_model, query_set):
        knowledge = Knowledge(
            id="00000000-0000-0000-0000-000000000040",
            workspace_id="workspace",
            name="base",
            desc="",
            type=KnowledgeType.BASE,
            file_size_limit=100,
            file_count_limit=50,
        )
        service = ImageDocumentService("workspace", str(knowledge.id))
        service.get_knowledge = MagicMock(return_value=knowledge)
        stored_file = MagicMock(
            id="00000000-0000-0000-0000-000000000041",
            file_name="scene.png",
            file_size=3,
            meta={"knowledge_id": str(knowledge.id), "upload_size": 3},
        )
        file_model.return_value = stored_file
        query_set.return_value.filter.return_value.update.return_value = 1
        image_buffer = BytesIO()
        Image.new("RGB", (1, 1)).save(image_buffer, format="PNG")
        image_bytes = image_buffer.getvalue()
        upload = SimpleUploadedFile("scene.png", image_bytes, content_type="image/png")

        previews = service.create_previews([upload])

        self.assertEqual(previews[0]["name"], "scene.png")
        self.assertEqual(previews[0]["process_status"], "skipped")
        stored_file.save.assert_called_once_with(image_bytes)
        file_model.assert_called_once()

    @patch("knowledge.services.image_documents.IncrementalDocumentSync")
    @patch("knowledge.services.image_documents.ParagraphAsset.objects.create")
    @patch("knowledge.services.image_documents.Paragraph")
    @patch("knowledge.services.image_documents.Document")
    @patch("knowledge.services.image_documents.QuerySet")
    def test_import_creates_an_image_document_and_moves_the_source_file(
        self,
        query_set,
        document_model,
        paragraph_model,
        create_asset,
        incremental_sync,
    ):
        knowledge = Knowledge(
            id="00000000-0000-0000-0000-000000000042",
            workspace_id="workspace",
            name="base",
            desc="",
            type=KnowledgeType.BASE,
        )
        file = MagicMock(
            id="00000000-0000-0000-0000-000000000043",
            file_name="scene.png",
            sha256_hash="image-hash",
            meta={
                "image_preview": {
                    "caption": "风景",
                    "ocr_text": "",
                    "description": "群山与草地",
                    "process_status": "success",
                    "process_error": "",
                    "doc_strategy": normalize_document_strategy(None),
                    "imported": False,
                }
            },
        )
        file_query = MagicMock()
        file_query.filter.return_value.select_for_update.return_value = [file]
        update_query = MagicMock()
        query_set.side_effect = [file_query, update_query]
        document = MagicMock(id="00000000-0000-0000-0000-000000000044")
        paragraph = MagicMock(id="00000000-0000-0000-0000-000000000045")
        document_model.return_value = document
        paragraph_model.return_value = paragraph
        service = ImageDocumentService("workspace", str(knowledge.id), "user-id")
        service.get_knowledge = MagicMock(return_value=knowledge)

        document_ids = ImageDocumentService.import_previews.__wrapped__(service, [file.id])

        self.assertEqual(document_ids, [str(document.id)])
        self.assertEqual(document_model.call_args.kwargs["resource_type"], DocumentResourceType.IMAGE)
        self.assertEqual(document_model.call_args.kwargs["char_length"], len("风景\n群山与草地"))
        self.assertEqual(paragraph_model.call_args.kwargs["content_schema"][0]["file_id"], str(file.id))
        self.assertEqual(create_asset.call_args.kwargs["file_id"], file.id)
        update_query.filter.return_value.update.assert_called_once()
        update_values = update_query.filter.return_value.update.call_args.kwargs
        self.assertEqual(update_values["source_type"], FileSourceType.DOCUMENT)
        self.assertEqual(update_values["source_id"], str(document.id))
        incremental_sync.return_value._sync_title_questions.assert_called_once_with([paragraph])


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


class DocumentStrategyTests(SimpleTestCase):
    def test_visual_enhancement_is_disabled_by_default_and_hashes_are_stable(self):
        strategy = normalize_document_strategy(None)

        self.assertFalse(strategy["visual"]["enabled"])
        self.assertEqual(strategy_hashes(strategy), strategy_hashes(strategy))

    def test_enabled_visual_strategy_requires_selected_model_or_tool(self):
        with self.assertRaises(ValueError):
            normalize_document_strategy({"visual": {"enabled": True, "strategy": "model"}})

    def test_short_tail_is_merged_into_previous_paragraph(self):
        paragraphs = [{"content": "a" * 10}, {"content": "tail"}]
        result = apply_length_strategy(paragraphs, {"split": {"min_length": 5, "max_length": 10}})

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["content"], "a" * 10 + "\ntail")

    def test_empty_patterns_keep_whole_paragraph(self):
        content = "x" * 200
        result = apply_length_strategy(
            [{"content": content}], {"split": {"patterns": [], "min_length": 0, "max_length": 50}}
        )

        self.assertEqual(result, [{"title": "", "content": content}])

    def test_web_parser_applies_empty_pattern_no_split_strategy(self):
        content = "x" * 200

        result = parse_web_content(content, {"split": {"patterns": [], "max_length": 50}})

        self.assertEqual(result, [{"title": "", "content": content}])


class WebDocumentStrategyRequestTests(SimpleTestCase):
    def test_web_document_request_uses_normalized_defaults(self):
        serializer = DocumentWebInstanceSerializer(
            data={
                "source_url_list": ["https://example.com/a", "https://example.com/a"],
                "selector": "",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["source_url_list"], ["https://example.com/a"])
        self.assertEqual(serializer.validated_data["selector"], "body")
        self.assertEqual(serializer.validated_data["doc_strategy"], normalize_document_strategy(None))

    def test_web_document_request_accepts_single_label_intranet_host(self):
        serializer = DocumentWebInstanceSerializer(data={"source_url_list": ["http://wiki/docs"]})

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_web_document_request_normalizes_custom_strategy(self):
        model_id = "00000000-0000-0000-0000-000000000001"
        serializer = DocumentWebInstanceSerializer(
            data={
                "source_url_list": ["https://example.com/a"],
                "doc_strategy": {
                    "split": {
                        "patterns": [r"(?m)^# .*"],
                        "min_length": 100,
                        "max_length": 2000,
                        "child_length": 512,
                        "auto_clean": True,
                    },
                    "visual": {"enabled": True, "strategy": "model", "model_id": model_id},
                    "index": {"title_as_question": True},
                },
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        strategy = serializer.validated_data["doc_strategy"]
        self.assertEqual(strategy["split"]["mode"], "advanced")
        self.assertEqual(strategy["split"]["child_length"], 512)
        self.assertEqual(strategy["visual"]["model_id"], model_id)
        self.assertTrue(strategy["index"]["title_as_question"])

    def test_web_document_request_rejects_invalid_custom_strategy(self):
        serializer = DocumentWebInstanceSerializer(
            data={
                "source_url_list": ["not-a-url"],
                "doc_strategy": {
                    "split": {"min_length": 500, "max_length": 100},
                    "visual": {"enabled": True, "strategy": "tool"},
                },
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("source_url_list", serializer.errors)
        self.assertIn("doc_strategy", serializer.errors)

    def test_smart_split_rejects_advanced_paragraph_identifiers(self):
        serializer = DocumentWebInstanceSerializer(
            data={
                "source_url_list": ["https://example.com"],
                "doc_strategy": {"split": {"mode": "smart", "patterns": [r"(?m)^# .* "]}},
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("doc_strategy", serializer.errors)

    def test_web_knowledge_request_captures_strategy_for_later_sync(self):
        serializer = KnowledgeWebCreateRequest(
            data={
                "name": "docs",
                "folder_id": "folder-id",
                "embedding_model_id": "embedding-id",
                "source_url": "https://example.com",
                "doc_strategy": {"split": {"max_length": 1024}},
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["selector"], "body")
        self.assertEqual(serializer.validated_data["doc_strategy"]["split"]["max_length"], 1024)

    def test_custom_document_sync_requires_a_strategy(self):
        serializer = DocumentSyncStrategySerializer(data={"strategy_mode": "custom"})

        self.assertFalse(serializer.is_valid())
        self.assertIn("doc_strategy", serializer.errors)

    def test_web_knowledge_edit_normalizes_top_level_strategy_without_replacing_meta(self):
        knowledge = MagicMock(type=KnowledgeType.WEB)
        serializer = KnowledgeEditRequest(data={"doc_strategy": {"split": {"max_length": 2048}}})

        serializer.is_valid(knowledge=knowledge)

        self.assertEqual(serializer.validated_data["doc_strategy"]["split"]["max_length"], 2048)

    def test_non_web_knowledge_rejects_document_strategy_settings(self):
        serializer = KnowledgeEditRequest(data={"doc_strategy": {"split": {"max_length": 2048}}})

        with self.assertRaises(ValidationError):
            serializer.is_valid(knowledge=MagicMock(type=KnowledgeType.BASE))

    def test_knowledge_sync_type_supports_all_three_modes(self):
        field = KnowledgeSerializer.SyncWeb().fields["sync_type"]

        self.assertEqual(field.run_validation("incremental"), "incremental")
        self.assertEqual(field.run_validation("replace"), "replace")
        self.assertEqual(field.run_validation("complete"), "complete")

    @patch("knowledge.serializers.knowledge.sync_replace_web_knowledge.delay")
    def test_knowledge_sync_dispatches_selected_mode(self, delay):
        knowledge = MagicMock(
            id="00000000-0000-0000-0000-000000000011",
            meta={"source_url": "https://example.com", "selector": "body", "doc_strategy": {}},
        )
        serializer = KnowledgeSerializer.SyncWeb(data={"user_id": "00000000-0000-0000-0000-000000000012"})

        serializer.incremental_sync(knowledge)

        self.assertEqual(delay.call_args.args[-1], "incremental")
        self.assertTrue(delay.call_args.kwargs["record_log"])
        self.assertEqual(delay.call_args.kwargs["trigger_type"], KnowledgeSyncTrigger.MANUAL)

    def test_selector_list_ignores_extra_spaces(self):
        self.assertEqual(get_selector_list("body   .article "), ["body", ".article"])

    def test_web_url_identity_ignores_fragment_trailing_slash_and_host_case(self):
        self.assertEqual(
            normalize_web_url("HTTPS://EXAMPLE.COM/docs/#section"),
            "https://example.com/docs",
        )

    @patch("knowledge.serializers.document.DocumentSerializers.Create")
    @patch("knowledge.task.handler.internalize_web_images", side_effect=lambda content, _knowledge_id: content)
    @patch("knowledge.task.handler.QuerySet")
    def test_legacy_task_call_falls_back_to_strategy_saved_on_knowledge(
        self, query_set, _internalize_web_images, create_document
    ):
        knowledge = MagicMock(meta={"doc_strategy": {"split": {"max_length": 777}}})
        query_set.return_value.filter.return_value.first.return_value = knowledge
        response = MagicMock(status=200, content="content")
        child_link = MagicMock(tag=None, url="https://example.com/docs")

        get_save_handler("knowledge-id", "user-id", "body")(child_link, response)

        instance = create_document.return_value.save.call_args.args[0]
        self.assertEqual(instance["doc_strategy"]["split"]["max_length"], 777)

    @patch("knowledge.serializers.document.DocumentSerializers.Sync")
    @patch("knowledge.task.handler.QuerySet")
    def test_incremental_crawl_reuses_response_and_document_strategy(self, query_set, sync_document):
        knowledge = MagicMock(id="knowledge-id", meta={"doc_strategy": {}})
        existing = MagicMock(
            id="document-id",
            type=KnowledgeType.WEB,
            meta={"source_url": "https://example.com/docs/"},
        )
        knowledge_query = MagicMock()
        knowledge_query.filter.return_value.first.return_value = knowledge
        document_query = MagicMock()
        document_query.filter.return_value.__iter__.return_value = [existing]
        query_set.side_effect = lambda model: knowledge_query if model is Knowledge else document_query
        response = MagicMock(status=200, content="updated")
        successful_urls = set()

        handler = get_sync_handler("knowledge-id", "user-id", successful_urls=successful_urls)
        handler(MagicMock(tag=None, url="https://example.com/docs#top"), response)

        sync_document.return_value.sync.assert_called_once_with(response=response)
        self.assertEqual(successful_urls, {"https://example.com/docs"})

    @patch("knowledge.task.handler.delete_document_data")
    @patch("knowledge.serializers.document.DocumentSerializers.Create")
    @patch("knowledge.task.handler.internalize_web_images", side_effect=lambda content, _knowledge_id: content)
    @patch("knowledge.task.handler.QuerySet")
    def test_replace_crawl_creates_new_document_before_deleting_old(
        self, query_set, _internalize_web_images, create_document, delete_document_data
    ):
        knowledge = MagicMock(id="knowledge-id", meta={"selector": "body", "doc_strategy": {}})
        existing = MagicMock(
            id="old-document-id",
            type=KnowledgeType.WEB,
            meta={"source_url": "https://example.com/docs", "selector": ".content"},
            doc_strategy={"split": {"max_length": 777}},
        )
        knowledge_query = MagicMock()
        knowledge_query.filter.return_value.first.return_value = knowledge
        document_query = MagicMock()
        document_query.filter.return_value.__iter__.return_value = [existing]
        query_set.side_effect = lambda model: knowledge_query if model is Knowledge else document_query
        create_document.return_value.save.return_value = {"id": "new-document-id"}

        handler = get_sync_handler("knowledge-id", "user-id", sync_type="replace")
        handler(MagicMock(tag=None, url="https://example.com/docs"), MagicMock(status=200, content="updated"))

        instance = create_document.return_value.save.call_args.args[0]
        self.assertEqual(instance["doc_strategy"]["split"]["max_length"], 777)
        self.assertEqual(instance["meta"]["selector"], ".content")
        delete_document_data.assert_called_once_with(["old-document-id"])

    @patch("knowledge.task.handler.delete_document_data")
    @patch("knowledge.serializers.document.DocumentSerializers.Create")
    @patch("knowledge.task.handler.internalize_web_images", side_effect=lambda content, _knowledge_id: content)
    @patch("knowledge.task.handler.QuerySet")
    def test_replace_crawl_keeps_old_document_when_new_document_creation_fails(
        self, query_set, _internalize_web_images, create_document, delete_document_data
    ):
        knowledge = MagicMock(id="knowledge-id", meta={"selector": "body", "doc_strategy": {}})
        existing = MagicMock(
            id="old-document-id",
            type=KnowledgeType.WEB,
            meta={"source_url": "https://example.com/docs"},
            doc_strategy={},
        )
        knowledge_query = MagicMock()
        knowledge_query.filter.return_value.first.return_value = knowledge
        document_query = MagicMock()
        document_query.filter.return_value.__iter__.return_value = [existing]
        query_set.side_effect = lambda model: knowledge_query if model is Knowledge else document_query
        create_document.return_value.save.side_effect = RuntimeError("create failed")

        handler = get_sync_handler("knowledge-id", "user-id", sync_type="replace")
        handler(MagicMock(tag=None, url="https://example.com/docs"), MagicMock(status=200, content="updated"))

        delete_document_data.assert_not_called()


class WebKnowledgeSyncTaskTests(SimpleTestCase):
    @patch("knowledge.task.sync.delete_document_data")
    @patch("knowledge.task.sync.KnowledgeSyncLog.objects.create")
    @patch("knowledge.task.sync.QuerySet")
    @patch("knowledge.task.sync.get_sync_handler")
    @patch("knowledge.task.sync.ForkManage")
    def test_recorded_sync_persists_counts_and_duration(
        self, fork_manage, get_handler, query_set, create_log, _delete_document_data
    ):
        root_url = "https://example.com"
        knowledge = MagicMock(id="knowledge-id", workspace_id="workspace-id")
        knowledge_query = MagicMock()
        knowledge_query.filter.return_value.first.return_value = knowledge
        document_query = MagicMock()
        document_query.filter.return_value.count.return_value = 2
        document_query.filter.return_value.__iter__.return_value = []
        log_query = MagicMock()
        query_set.side_effect = lambda model: {
            Knowledge: knowledge_query,
            Document: document_query,
        }.get(model, log_query)
        sync_log = MagicMock(id="log-id")
        create_log.return_value = sync_log

        def handler_factory(_knowledge_id, _user_id, _strategy, _sync_type, successful_urls, stats):
            successful_urls.add(root_url)
            stats["synced_count"] = 1
            stats["skipped_count"] = 1
            return MagicMock()

        get_handler.side_effect = handler_factory
        fork_manage.return_value.fork.side_effect = lambda _level, visited, _handler: visited.add(root_url)

        result = sync_replace_web_knowledge.run(
            "knowledge-id",
            "user-id",
            root_url,
            "body",
            {},
            "incremental",
            record_log=True,
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["total_count"], 2)
        log_query.filter.return_value.update.assert_called_once()
        update = log_query.filter.return_value.update.call_args.kwargs
        self.assertEqual(update["synced_count"], 1)
        self.assertEqual(update["skipped_count"], 1)
        self.assertGreaterEqual(update["duration_ms"], 0)

    @patch("knowledge.task.sync.delete_document_data")
    @patch("knowledge.task.sync.QuerySet")
    @patch("knowledge.task.sync.get_sync_handler")
    @patch("knowledge.task.sync.ForkManage")
    def test_incremental_sync_deletes_urls_missing_from_successful_crawl(
        self, fork_manage, get_handler, query_set, delete_document_data
    ):
        root_url = "https://example.com"
        successful_urls = None

        def handler_factory(_knowledge_id, _user_id, _strategy, _sync_type, success_set, _stats):
            nonlocal successful_urls
            successful_urls = success_set
            return MagicMock()

        get_handler.side_effect = handler_factory

        def crawl(_level, visited, _handler):
            visited.update({root_url, f"{root_url}/kept"})
            successful_urls.add(root_url)

        fork_manage.return_value.fork.side_effect = crawl
        kept = MagicMock(id="kept-id", meta={"source_url": f"{root_url}/kept"})
        stale = MagicMock(id="stale-id", meta={"source_url": f"{root_url}/removed"})
        document_query = MagicMock()
        document_query.filter.return_value.__iter__.return_value = [kept, stale]
        query_set.side_effect = lambda model: document_query

        sync_replace_web_knowledge.run("knowledge-id", "user-id", root_url, "body", {}, "incremental")

        delete_document_data.assert_called_once_with(["stale-id"])

    @patch("knowledge.task.sync.delete_document_data")
    @patch("knowledge.task.sync.QuerySet")
    @patch("knowledge.task.sync.get_sync_handler")
    @patch("knowledge.task.sync.ForkManage")
    def test_incremental_sync_does_not_prune_documents_when_root_fetch_fails(
        self, fork_manage, get_handler, _query_set, delete_document_data
    ):
        root_url = "https://example.com"
        get_handler.return_value = MagicMock()
        fork_manage.return_value.fork.side_effect = lambda _level, visited, _handler: visited.add(root_url)

        sync_replace_web_knowledge.run("knowledge-id", "user-id", root_url, "body", {}, "incremental")

        delete_document_data.assert_not_called()

    @patch("knowledge.task.sync.get_save_handler")
    @patch("knowledge.task.sync.ForkManage")
    @patch("knowledge.task.sync.delete_document_data")
    @patch("knowledge.task.sync.QuerySet")
    def test_complete_sync_cleans_documents_before_crawling(
        self, query_set, delete_document_data, fork_manage, _get_save_handler
    ):
        events = []
        document_query = MagicMock()
        document_query.filter.return_value.values_list.return_value = ["document-id"]
        file_query = MagicMock()
        query_set.side_effect = lambda model: document_query if model is Document else file_query
        delete_document_data.side_effect = lambda _document_ids: events.append("cleanup")
        fork_manage.return_value.fork.side_effect = lambda *_args: events.append("crawl")

        sync_replace_web_knowledge.run("knowledge-id", "user-id", "https://example.com", "body", {}, "complete")

        delete_document_data.assert_called_once_with(["document-id"])
        fork_manage.return_value.fork.assert_called_once()
        self.assertEqual(events, ["cleanup", "crawl"])


class KnowledgeScheduleTests(SimpleTestCase):
    def test_daily_setting_is_normalized_to_cron(self):
        serializer = KnowledgeSyncSettingRequest(
            data={
                "enabled": True,
                "schedule_type": "daily",
                "time": "01:30",
                "sync_type": "incremental",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["cron_expression"], "30 1 * * *")

    def test_custom_cron_is_validated(self):
        self.assertEqual(
            normalize_knowledge_sync_setting(
                {
                    "enabled": True,
                    "schedule_type": "cron",
                    "cron_expression": "*/15 * * * *",
                    "sync_type": "replace",
                }
            )["cron_expression"],
            "*/15 * * * *",
        )
        serializer = KnowledgeSyncSettingRequest(
            data={
                "enabled": True,
                "schedule_type": "cron",
                "cron_expression": "invalid",
                "sync_type": "replace",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    @patch("knowledge.services.knowledge_sync_schedule._get_scheduler")
    @patch("knowledge.services.knowledge_sync_schedule.QuerySet")
    def test_enabled_setting_deploys_one_replaceable_job(self, query_set, get_scheduler):
        scheduler = get_scheduler.return_value
        scheduler.get_job.return_value = None
        knowledge = MagicMock(
            id="00000000-0000-0000-0000-000000000021",
            meta={
                "sync_setting": {
                    "enabled": True,
                    "schedule_type": "daily",
                    "time": "02:00",
                    "sync_type": "incremental",
                }
            },
        )
        query_set.return_value.filter.return_value.first.return_value = knowledge

        self.assertTrue(deploy_knowledge_sync_job(knowledge.id))

        self.assertEqual(scheduler.add_job.call_count, 1)
        self.assertTrue(scheduler.add_job.call_args.kwargs["replace_existing"])
        self.assertEqual(scheduler.add_job.call_args.kwargs["id"], f"knowledge:sync:{knowledge.id}")

    @patch("knowledge.task.sync.sync_replace_web_knowledge.delay")
    @patch("knowledge.task.sync.QuerySet")
    def test_scheduled_entry_uses_saved_sync_type_and_records_log(self, query_set, delay):
        knowledge = MagicMock(
            id="00000000-0000-0000-0000-000000000022",
            user_id="00000000-0000-0000-0000-000000000023",
            meta={
                "source_url": "https://example.com",
                "selector": "body",
                "doc_strategy": {},
                "sync_setting": {"enabled": True, "sync_type": "complete"},
            },
        )
        query_set.return_value.filter.return_value.first.return_value = knowledge

        self.assertTrue(scheduled_sync_web_knowledge.run(str(knowledge.id)))

        self.assertEqual(delay.call_args.args[-1], "complete")
        self.assertTrue(delay.call_args.kwargs["record_log"])
        self.assertEqual(delay.call_args.kwargs["trigger_type"], KnowledgeSyncTrigger.SCHEDULED)

    @patch("knowledge.serializers.knowledge_sync.QuerySet")
    def test_setting_operation_accepts_lark_and_workflow_knowledge(self, query_set):
        for knowledge_type in [KnowledgeType.LARK, KnowledgeType.WORKFLOW]:
            with self.subTest(knowledge_type=knowledge_type):
                knowledge = MagicMock(type=knowledge_type, meta={})
                query_set.return_value.filter.return_value.first.return_value = knowledge
                serializer = KnowledgeSyncSettingOperationSerializer(
                    data={
                        "workspace_id": "workspace-id",
                        "knowledge_id": "00000000-0000-0000-0000-000000000024",
                    }
                )

                self.assertFalse(serializer.get_setting()["enabled"])

    @patch("knowledge.task.sync.celery_app.send_task")
    @patch("knowledge.task.sync.QuerySet")
    def test_generic_scheduled_entry_dispatches_lark_task(self, query_set, send_task):
        knowledge = MagicMock(
            id="00000000-0000-0000-0000-000000000025",
            type=KnowledgeType.LARK,
            meta={"sync_setting": {"enabled": True}},
        )
        query_set.return_value.filter.return_value.first.return_value = knowledge

        self.assertTrue(scheduled_sync_knowledge.run(str(knowledge.id)))

        send_task.assert_called_once_with("celery:scheduled_sync_lark_knowledge", args=[str(knowledge.id)])

    @patch("knowledge.task.sync.scheduled_sync_workflow_knowledge.delay")
    @patch("knowledge.task.sync.QuerySet")
    def test_generic_scheduled_entry_dispatches_workflow_task(self, query_set, delay):
        knowledge = MagicMock(
            id="00000000-0000-0000-0000-000000000026",
            type=KnowledgeType.WORKFLOW,
            meta={"sync_setting": {"enabled": True}},
        )
        query_set.return_value.filter.return_value.first.return_value = knowledge

        self.assertTrue(scheduled_sync_knowledge.run(str(knowledge.id)))

        delay.assert_called_once_with(str(knowledge.id))


class WorkflowKnowledgeScheduleTests(SimpleTestCase):
    @patch("application.flow.i_step_node.merge_workflow_incremental_snapshot")
    @patch("application.flow.i_step_node.get_workflow_state", return_value=KnowledgeActionState.SUCCESS)
    @patch("application.flow.i_step_node.QuerySet")
    def test_incremental_workflow_uses_stable_snapshot_merge(
        self, query_set, _get_workflow_state, merge_workflow_snapshot
    ):
        sync_log = MagicMock(
            id="00000000-0000-0000-0000-000000000032",
            knowledge_id="00000000-0000-0000-0000-000000000033",
            create_time=timezone.now(),
            sync_type=KnowledgeSyncType.INCREMENTAL,
        )
        action_query = MagicMock()
        log_query = MagicMock()
        log_query.filter.return_value.first.return_value = sync_log
        query_set.side_effect = lambda model: log_query if model is KnowledgeSyncLog else action_query
        merge_workflow_snapshot.return_value = {
            "total_count": 1,
            "synced_count": 0,
            "skipped_count": 1,
            "deleted_count": 0,
            "failed_count": 0,
        }
        workflow = MagicMock(context={"start_time": timezone.now().timestamp()})
        document_cleanup = MagicMock()

        KnowledgeWorkflowPostHandler(
            None,
            "00000000-0000-0000-0000-000000000036",
            str(sync_log.id),
            document_cleanup,
        ).handler(workflow)

        merge_workflow_snapshot.assert_called_once_with(sync_log)
        update = log_query.filter.return_value.update.call_args.kwargs
        self.assertEqual(update["status"], KnowledgeSyncStatus.SUCCESS)
        self.assertEqual(update["synced_count"], 0)
        self.assertEqual(update["skipped_count"], 1)

    @patch("knowledge.task.sync.KnowledgeWorkflowActionSerializer")
    @patch("knowledge.task.sync.KnowledgeSyncLog.objects.create")
    @patch("knowledge.task.sync.QuerySet")
    def test_scheduled_workflow_uses_saved_input_and_starts_an_action(self, query_set, create_log, action_serializer):
        knowledge = MagicMock(
            id="00000000-0000-0000-0000-000000000027",
            workspace_id="workspace-id",
            type=KnowledgeType.WORKFLOW,
            user=MagicMock(),
            meta={
                "sync_setting": {"enabled": True, "sync_type": "incremental"},
                "workflow_sync_input": {
                    "data_source": {"node_id": "start-node"},
                    "knowledge_base": {},
                },
            },
        )
        knowledge_query = MagicMock()
        knowledge_query.filter.return_value.first.return_value = knowledge
        log_query = MagicMock()
        log_query.filter.return_value.exists.return_value = False
        document_query = MagicMock()
        document_query.filter.return_value.count.return_value = 2
        query_set.side_effect = lambda model: {
            Knowledge: knowledge_query,
            KnowledgeSyncLog: log_query,
        }.get(model, document_query)
        sync_log = MagicMock(id="00000000-0000-0000-0000-000000000028")
        create_log.return_value = sync_log
        action_serializer.return_value.action.return_value = {"id": "00000000-0000-0000-0000-000000000029"}

        self.assertTrue(scheduled_sync_workflow_knowledge.run(str(knowledge.id)))

        workflow_input = action_serializer.return_value.action.call_args.args[0]
        self.assertEqual(workflow_input["data_source"], {"node_id": "start-node"})
        action_serializer.return_value.action.assert_called_once_with(
            workflow_input,
            knowledge.user,
            True,
            str(sync_log.id),
        )

    @patch("knowledge.serializers.knowledge_workflow.Workflow.new_instance")
    @patch("knowledge.serializers.knowledge_workflow.KnowledgeWorkflowManage")
    @patch("knowledge.serializers.knowledge_workflow.KnowledgeAction.save")
    @patch("knowledge.serializers.knowledge_workflow.QuerySet")
    def test_manual_action_saves_input_for_later_scheduled_runs(
        self, query_set, _save_action, workflow_manage, _new_workflow
    ):
        workflow = MagicMock(work_flow={})
        knowledge = MagicMock(
            id="00000000-0000-0000-0000-000000000030",
            name="workflow knowledge",
            desc="desc",
            workspace_id="workspace-id",
            meta={"existing": True},
        )

        def query_for(model):
            query = MagicMock()
            query.filter.return_value.first.return_value = (
                workflow if model.__name__ == "KnowledgeWorkflow" else knowledge
            )
            return query

        query_set.side_effect = query_for
        user = MagicMock(id="00000000-0000-0000-0000-000000000031", username="owner")
        workflow_input = {
            "data_source": {"node_id": "start-node", "files": ["a.docx"]},
            "knowledge_base": {"custom": "value"},
        }

        serializer = KnowledgeWorkflowActionSerializer(
            data={"workspace_id": knowledge.workspace_id, "knowledge_id": str(knowledge.id)}
        )
        serializer.is_valid(raise_exception=True)
        serializer.action(workflow_input, user, with_valid=False)

        self.assertEqual(
            knowledge.meta["workflow_sync_input"],
            {
                "data_source": {"node_id": "start-node", "files": ["a.docx"]},
                "knowledge_base": {"custom": "value"},
            },
        )
        knowledge.save.assert_called_once_with(update_fields=["meta", "update_time"])
        workflow_manage.return_value.run.assert_called_once_with()


class WebImageAssetTests(SimpleTestCase):
    @patch(
        "knowledge.web_assets._cache_web_image",
        return_value="00000000-0000-0000-0000-000000000001",
    )
    def test_remote_images_are_replaced_with_internal_references_and_deduplicated(self, cache_web_image):
        source = "before ![chart](https://example.com/chart.png) ![again](https://example.com/chart.png)"

        result = internalize_web_images(source, "knowledge-id")

        self.assertEqual(cache_web_image.call_count, 1)
        self.assertIn("![chart](./oss/file/00000000-0000-0000-0000-000000000001)", result)
        self.assertIn("![again](./oss/file/00000000-0000-0000-0000-000000000001)", result)

    @patch("knowledge.web_assets._cache_web_image", return_value=None)
    def test_remote_image_failure_does_not_block_document_content(self, _cache_web_image):
        source = "before ![chart](https://example.com/chart.png) after"

        self.assertEqual(internalize_web_images(source, "knowledge-id"), source)


class IncrementalSyncTests(SimpleTestCase):
    def test_fallback_source_key_survives_content_change(self):
        first = prepare_remote_paragraphs([{"title": "Overview", "content": "v1"}])
        second = prepare_remote_paragraphs([{"title": "Overview", "content": "v2"}])

        self.assertEqual(first[0]["source_key"], second[0]["source_key"])
        self.assertNotEqual(first[0]["source_hash"], second[0]["source_hash"])

    def test_three_way_conflict_preserves_local_content(self):
        document = Document(id="00000000-0000-0000-0000-000000000001", name="doc", char_length=0)
        service = IncrementalDocumentSync(document)
        paragraph = Paragraph(
            id="00000000-0000-0000-0000-000000000002",
            title="Title",
            content="local edit",
            source_snapshot={"title": "Title", "content": "base"},
            source_key="block-1",
            source_hash="old",
            origin=ContentOrigin.SYNCED,
            local_state=LocalState.MODIFIED,
        )
        paragraph.save = MagicMock()
        result = MergeResult()

        service._merge_matched(
            paragraph,
            {
                "title": "Title",
                "content": "remote edit",
                "source_key": "block-1",
                "source_hash": "new",
            },
            result,
        )

        self.assertEqual(paragraph.content, "local edit")
        self.assertEqual(paragraph.sync_state, SyncState.CONFLICT)
        self.assertEqual(result.conflict_ids, [str(paragraph.id)])

    @patch("knowledge.services.incremental_sync.Paragraph.objects")
    @patch("knowledge.services.incremental_sync.Document.objects")
    def test_empty_remote_snapshot_keeps_existing_synced_paragraphs(self, document_objects, paragraph_objects):
        document = Document(id="00000000-0000-0000-0000-000000000001", name="doc", char_length=4)
        synced_paragraph = Paragraph(
            id="00000000-0000-0000-0000-000000000002",
            document=document,
            knowledge_id="00000000-0000-0000-0000-000000000003",
            title="Title",
            content="body",
            origin=ContentOrigin.SYNCED,
            sync_state=SyncState.ACTIVE,
        )
        document_objects.select_for_update.return_value.get.return_value = document
        paragraph_objects.select_for_update.return_value.filter.return_value.order_by.return_value = [synced_paragraph]
        synced_paragraph.save = MagicMock()
        service = IncrementalDocumentSync(document)

        with self.assertRaisesRegex(ValueError, "empty paragraph snapshot"):
            IncrementalDocumentSync.merge.__wrapped__(service, [])

        document_objects.select_for_update.assert_called_once_with()
        synced_paragraph.save.assert_not_called()

    @patch("knowledge.serializers.document.IncrementalDocumentSync")
    @patch("knowledge.serializers.document.process_visual_assets")
    @patch("knowledge.serializers.document.sync_paragraph_assets", return_value=[])
    @patch("knowledge.serializers.document.internalize_web_images", side_effect=lambda content, _knowledge_id: content)
    @patch("knowledge.serializers.document.parse_web_content")
    @patch("knowledge.serializers.document.ListenerManagement")
    @patch("knowledge.serializers.document.QuerySet")
    def test_document_hash_skips_paragraph_merge_and_embedding(
        self,
        query_set,
        _listener,
        parse_content,
        _internalize_images,
        _sync_assets,
        _process_assets,
        incremental_sync,
    ):
        paragraphs = [{"title": "Overview", "content": "unchanged"}]
        strategy = normalize_document_strategy(None)
        hashes = strategy_hashes(strategy)
        document = Document(
            id="00000000-0000-0000-0000-000000000021",
            knowledge_id="00000000-0000-0000-0000-000000000022",
            name="docs",
            char_length=9,
            type=KnowledgeType.WEB,
            meta={"source_url": "https://example.com", "selector": "body"},
            doc_strategy=strategy,
            source_hash=document_source_hash(prepare_remote_paragraphs(paragraphs)),
            **hashes,
        )
        document.save = MagicMock()
        document_query = MagicMock()
        document_query.filter.return_value.first.return_value = document
        paragraph_query = MagicMock()
        query_set.side_effect = lambda model: document_query if model is Document else paragraph_query
        parse_content.return_value = paragraphs

        serializer = DocumentSerializers.Sync(
            data={"knowledge_id": str(document.knowledge_id), "document_id": str(document.id)}
        )
        DocumentSerializers.Sync.sync.__wrapped__(
            serializer,
            with_valid=False,
            with_embedding=False,
            response=MagicMock(status=200, content="unchanged"),
        )

        incremental_sync.assert_not_called()
        document.save.assert_called_once_with(update_fields=["last_sync_time", "update_time"])


class ParagraphAssetTests(SimpleTestCase):
    def test_image_is_kept_inside_paragraph_schema(self):
        content = "before ![chart](./oss/file/00000000-0000-0000-0000-000000000003) after"
        schema = paragraph_content_schema(content)

        self.assertEqual([block["type"] for block in schema], ["text", "image", "text"])
        self.assertEqual(schema[1]["caption"], "chart")

    def test_asset_source_key_does_not_change_with_file_content(self):
        paragraph = Paragraph(
            id="00000000-0000-0000-0000-000000000001",
            source_key="heading:overview:1",
        )

        source_key = paragraph_asset_source_key(paragraph, 1)

        self.assertEqual(source_key, "heading:overview:1:image:1")
        self.assertNotIn("hash", source_key)

    @patch("knowledge.services.paragraph_assets.File.objects")
    @patch("knowledge.services.paragraph_assets.ParagraphAsset.objects")
    def test_synced_asset_moves_by_hash_without_changing_identity(self, asset_objects, file_objects):
        old_asset = MagicMock(
            id="00000000-0000-0000-0000-000000000061",
            document_id="00000000-0000-0000-0000-000000000062",
            paragraph_id="00000000-0000-0000-0000-000000000063",
            origin=ContentOrigin.SYNCED,
            source_asset_key="heading:old:1:image:1",
            source_hash="same-image",
            caption="old",
            ocr_text="ocr",
            description="description",
            paragraph=MagicMock(is_active=False, sync_state=SyncState.REMOTE_DELETED),
        )
        asset_objects.select_for_update.return_value.select_related.return_value.filter.return_value.order_by.return_value = [
            old_asset
        ]
        image_file = MagicMock(
            id="00000000-0000-0000-0000-000000000064",
            sha256_hash="same-image",
        )
        file_objects.filter.return_value.first.return_value = image_file
        paragraph = Paragraph(
            id="00000000-0000-0000-0000-000000000065",
            document_id=old_asset.document_id,
            knowledge_id="00000000-0000-0000-0000-000000000066",
            title="new",
            content=f"![image](./oss/file/{image_file.id})",
            origin=ContentOrigin.SYNCED,
        )
        paragraph.save = MagicMock()

        assets = sync_paragraph_assets.__wrapped__([paragraph])

        self.assertEqual(assets, [old_asset])
        self.assertEqual(old_asset.paragraph_id, paragraph.id)
        self.assertEqual(old_asset.source_asset_key, "heading:old:1:image:1")
        asset_objects.filter.assert_called_once_with(
            paragraph_id__in={paragraph.id},
            origin=ContentOrigin.SYNCED,
        )

    @patch("knowledge.services.paragraph_assets.ParagraphAsset.objects")
    def test_remote_delete_cleanup_is_limited_to_synced_assets(self, asset_objects):
        asset_objects.select_for_update.return_value.select_related.return_value.filter.return_value.order_by.return_value = []
        paragraph = Paragraph(
            id="00000000-0000-0000-0000-000000000067",
            document_id="00000000-0000-0000-0000-000000000068",
            knowledge_id="00000000-0000-0000-0000-000000000069",
            title="manual",
            content="text only",
            origin=ContentOrigin.MANUAL,
        )
        paragraph.save = MagicMock()

        sync_paragraph_assets.__wrapped__([paragraph])

        asset_objects.filter.assert_called_once_with(
            paragraph_id__in={paragraph.id},
            origin=ContentOrigin.SYNCED,
        )


class DocumentResourceIsolationTests(SimpleTestCase):
    @patch("knowledge.serializers.document.QuerySet")
    def test_batch_document_operation_rejects_image_ids_by_default(self, query_set):
        document_query = MagicMock()
        document_query.filter.return_value.values_list.return_value = []
        query_set.return_value = document_query
        serializer = DocumentSerializers.Batch(
            data={
                "workspace_id": "workspace-id",
                "knowledge_id": "00000000-0000-0000-0000-000000000071",
            }
        )

        with self.assertRaises(AppApiException):
            serializer.validate_document_ids({"id_list": ["00000000-0000-0000-0000-000000000072"]})

        document_query.filter.assert_called_once_with(
            id__in=["00000000-0000-0000-0000-000000000072"],
            knowledge_id="00000000-0000-0000-0000-000000000071",
            resource_type=DocumentResourceType.DOCUMENT,
        )


class WorkflowDocumentIdentityTests(SimpleTestCase):
    def test_stable_source_metadata_takes_priority_over_document_name(self):
        first = Document(name="Old name", meta={"source_key": "source-1"})
        renamed = Document(name="New name", meta={"source_key": "source-1"})

        self.assertEqual(workflow_document_identity(first), workflow_document_identity(renamed))

    @patch("knowledge.services.workflow_sync._delete_workflow_documents")
    @patch("knowledge.services.workflow_sync.process_visual_assets")
    @patch("knowledge.services.workflow_sync.sync_paragraph_assets", return_value=[])
    @patch("knowledge.services.workflow_sync.IncrementalDocumentSync")
    @patch("knowledge.services.workflow_sync.QuerySet")
    def test_incremental_snapshot_merges_into_old_document_id(
        self,
        query_set,
        incremental_sync,
        _sync_assets,
        _process_assets,
        delete_documents,
    ):
        sync_log = MagicMock(
            knowledge_id="00000000-0000-0000-0000-000000000081",
            create_time=timezone.now(),
        )
        old_document = MagicMock(
            id="00000000-0000-0000-0000-000000000082",
            knowledge_id=sync_log.knowledge_id,
            name="Old",
            meta={"source_key": "source-1"},
            doc_strategy={},
            visual_strategy_hash="visual",
        )
        new_document = MagicMock(
            id="00000000-0000-0000-0000-000000000083",
            knowledge_id=sync_log.knowledge_id,
            name="Renamed",
            meta={"source_key": "source-1"},
            doc_strategy={},
        )
        source_paragraph = MagicMock(
            id="00000000-0000-0000-0000-000000000084",
            title="Title",
            content="Content",
            source_key="block-1",
            source_updated_at=None,
        )
        target_paragraph = MagicMock(source_key="block-1")
        document_query = MagicMock()

        def filter_documents(**kwargs):
            result = MagicMock()
            if "create_time__gte" in kwargs:
                result.__iter__.return_value = iter([new_document])
            elif "create_time__lt" in kwargs:
                result.__iter__.return_value = iter([old_document])
            else:
                result.count.return_value = 1
            return result

        document_query.filter.side_effect = filter_documents
        paragraph_query = MagicMock()

        def filter_paragraphs(**kwargs):
            result = MagicMock()
            if kwargs.get("document_id") == new_document.id:
                result.order_by.return_value = [source_paragraph]
            else:
                result.__iter__.return_value = iter([target_paragraph])
            return result

        paragraph_query.filter.side_effect = filter_paragraphs
        empty_relation_query = MagicMock()
        empty_relation_query.filter.return_value.__iter__.return_value = iter([])
        empty_relation_query.filter.return_value.values_list.return_value = []
        file_query = MagicMock()
        knowledge_query = MagicMock()
        query_set.side_effect = lambda model: {
            Document: document_query,
            Paragraph: paragraph_query,
            ProblemParagraphMapping: empty_relation_query,
            FileSourceType: file_query,
            Knowledge: knowledge_query,
        }.get(model, empty_relation_query)
        incremental_sync.return_value.merge.return_value = MergeResult()
        delete_documents.return_value = [str(new_document.id)]

        stats = merge_workflow_incremental_snapshot.__wrapped__(sync_log)

        incremental_sync.assert_called_once_with(old_document, new_document.doc_strategy)
        delete_documents.assert_called_once_with([str(new_document.id)])
        self.assertEqual(old_document.id, "00000000-0000-0000-0000-000000000082")
        self.assertEqual(stats["skipped_count"], 1)

    @patch("knowledge.services.paragraph_assets._write_asset_description")
    def test_visual_failure_preserves_existing_text_as_description(self, write_description):
        asset = MagicMock()
        asset.caption = "original caption"
        asset.ocr_text = ""
        asset.description = ""
        asset.meta = {}

        process_visual_assets(
            [asset],
            {"visual": {"enabled": True, "strategy": "model", "model_id": "model-id"}},
            processor=MagicMock(side_effect=RuntimeError("vision failed")),
        )

        self.assertEqual(asset.process_status, AssetProcessStatus.FAILURE)
        self.assertEqual(asset.description, "original caption")
        asset.save.assert_called_once()
        write_description.assert_called_once_with(asset)

    @patch("knowledge.services.paragraph_assets.get_model_by_id")
    def test_rejects_non_vision_model_for_visual_processing(self, get_model_by_id):
        get_model_by_id.return_value.model_type = "LLM"

        with self.assertRaises(AppApiException):
            resolve_visual_processor(
                {"strategy": "model", "model_id": "00000000-0000-0000-0000-000000000001"},
                "workspace-1",
            )

    @patch("knowledge.services.paragraph_assets.Tool.objects.filter")
    @patch("knowledge.services.paragraph_assets.filter_authorized_ids", return_value=[])
    def test_rejects_unauthorized_visual_tool(self, filter_authorized_ids, tool_filter):
        tool_filter.return_value.first.return_value = None
        with self.assertRaises(AppApiException):
            resolve_visual_processor(
                {"strategy": "tool", "tool_id": "00000000-0000-0000-0000-000000000001"},
                "workspace-1",
            )

        filter_authorized_ids.assert_called_once()
        tool_filter.assert_called_once_with(id__in=[], is_active=True)

    @patch("knowledge.services.paragraph_assets.Embedding.objects.bulk_create")
    @patch("knowledge.services.paragraph_assets.ParagraphAsset.objects.select_related")
    def test_text_only_embedding_model_indexes_image_description(self, select_related, bulk_create):
        asset = MagicMock(spec=ParagraphAsset)
        asset.id = "00000000-0000-0000-0000-000000000001"
        asset.knowledge_id = "00000000-0000-0000-0000-000000000002"
        asset.document_id = "00000000-0000-0000-0000-000000000003"
        asset.paragraph_id = "00000000-0000-0000-0000-000000000004"
        asset.position = 1
        asset.caption = "chart"
        asset.ocr_text = "revenue 100"
        asset.description = "an upward trend"
        asset.paragraph.is_active = True
        select_related.return_value.filter.return_value.order_by.return_value = [asset]
        embedding_model = MagicMock()
        embedding_model.supports_image_embedding.return_value = False
        embedding_model.embed_documents.return_value = [[0.1, 0.2]]

        count = embed_paragraph_assets([asset.paragraph_id], embedding_model)

        self.assertEqual(count, 1)
        embedding_model.embed_documents.assert_called_once_with(["chart\nrevenue 100\nan upward trend"])
        embedding_model.embed_images.assert_not_called()
        row = bulk_create.call_args.args[0][0]
        self.assertEqual(row.meta["unit_type"], "text")
        self.assertEqual(row.meta["content_type"], "image_description")

    @patch("knowledge.services.paragraph_assets.Embedding.objects.bulk_create")
    @patch("knowledge.services.paragraph_assets.ParagraphAsset.objects.select_related")
    def test_rejects_incomplete_image_embedding_result(self, select_related, bulk_create):
        asset = MagicMock(spec=ParagraphAsset)
        asset.id = "00000000-0000-0000-0000-000000000001"
        asset.knowledge_id = "00000000-0000-0000-0000-000000000002"
        asset.document_id = "00000000-0000-0000-0000-000000000003"
        asset.paragraph_id = "00000000-0000-0000-0000-000000000004"
        asset.position = 1
        asset.caption = ""
        asset.ocr_text = ""
        asset.description = ""
        asset.paragraph.is_active = True
        asset.file.file_name = "chart.png"
        asset.file.get_bytes.return_value = b"image"
        select_related.return_value.filter.return_value.order_by.return_value = [asset]
        embedding_model = MagicMock()
        embedding_model.supports_image_embedding.return_value = True
        embedding_model.embed_images.return_value = []

        with self.assertRaises(AppApiException):
            embed_paragraph_assets([asset.paragraph_id], embedding_model)

        bulk_create.assert_not_called()
