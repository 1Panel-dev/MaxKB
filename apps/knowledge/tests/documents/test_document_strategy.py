from contextlib import nullcontext
from unittest.mock import MagicMock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from django.utils.datastructures import MultiValueDict
from knowledge.api.document import DocumentBatchAddTagAPI, DocumentSplitAPI
from knowledge.models import (
    DocumentResourceType,
    Knowledge,
    KnowledgeSyncTrigger,
    KnowledgeType,
)
from knowledge.serializers.document import (
    DocumentBatchAddTagSerializer,
    DocumentWebInstanceSerializer,
)
from knowledge.serializers.document_strategy import DocumentSyncStrategySerializer
from knowledge.serializers.knowledge import (
    KnowledgeEditRequest,
    KnowledgeSerializer,
    KnowledgeWebCreateRequest,
)
from knowledge.services.document_strategy import (
    apply_length_strategy,
    normalize_document_strategy,
    parse_web_content,
    strategy_hashes,
)
from knowledge.task.handler import get_save_handler, get_sync_handler, normalize_web_url
from knowledge.task.sync import (
    get_selector_list,
)
from knowledge.views.document import _get_document_split_payload
from rest_framework.exceptions import ValidationError


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
    def setUp(self):
        super().setUp()
        atomic_patch = patch("knowledge.task.handler.transaction.atomic", return_value=nullcontext())
        atomic_patch.start()
        self.addCleanup(atomic_patch.stop)

    def test_document_split_multipart_payload_includes_json_strategy(self):
        request = MagicMock()
        request.FILES.getlist.return_value = [SimpleUploadedFile("example.txt", b"content")]
        request.data = MultiValueDict(
            {
                "doc_strategy": ['{"split":{"max_length":1024}}'],
                "patterns": ["# ", "## "],
            }
        )

        payload = _get_document_split_payload(request)

        self.assertEqual(payload["doc_strategy"]["split"]["max_length"], 1024)
        self.assertEqual(payload["patterns"], ["# ", "## "])

    def test_document_split_openapi_describes_strategy_and_file_list(self):
        schema = DocumentSplitAPI.get_request()["multipart/form-data"]

        self.assertIn("doc_strategy", schema["properties"])
        self.assertEqual(schema["properties"]["file"]["type"], "array")
        self.assertEqual(schema["properties"]["patterns"]["type"], "array")

    def test_batch_add_tag_request_exposes_resource_type(self):
        serializer = DocumentBatchAddTagSerializer(
            data={
                "document_ids": ["00000000-0000-0000-0000-000000000001"],
                "tag_ids": ["00000000-0000-0000-0000-000000000002"],
                "resource_type": DocumentResourceType.IMAGE,
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["resource_type"], DocumentResourceType.IMAGE)
        self.assertIs(DocumentBatchAddTagAPI.get_request(), DocumentBatchAddTagSerializer)
        self.assertEqual(len(DocumentBatchAddTagAPI.get_parameters()), 2)

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
        for knowledge_type in KnowledgeType:
            if knowledge_type == KnowledgeType.WEB:
                continue
            for strategy in ({}, {"split": {"max_length": 2048}}):
                with self.subTest(knowledge_type=knowledge_type, strategy=strategy):
                    serializer = KnowledgeEditRequest(data={"doc_strategy": strategy})

                    with self.assertRaises(ValidationError):
                        serializer.is_valid(knowledge=MagicMock(type=knowledge_type))

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
        self.assertFalse(delay.call_args.kwargs["record_log"])
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

    @patch("knowledge.serializers.document.DocumentSerializers.Create")
    @patch("knowledge.task.handler.internalize_web_images", side_effect=lambda content, _knowledge_id: content)
    @patch("knowledge.task.handler.QuerySet")
    def test_new_url_uses_saved_processing_strategy_in_every_knowledge_sync_mode(
        self, query_set, _internalize_web_images, create_document
    ):
        strategy = normalize_document_strategy(
            {
                "split": {"max_length": 50, "child_length": 50},
                "visual": {"enabled": True, "model_id": "00000000-0000-0000-0000-000000000041"},
                "index": {"title_as_question": True},
            }
        )
        knowledge = MagicMock(id="knowledge-id", meta={"selector": "body", "doc_strategy": strategy})
        knowledge_query = MagicMock()
        knowledge_query.filter.return_value.first.return_value = knowledge
        document_query = MagicMock()
        document_query.filter.return_value.__iter__.return_value = []
        query_set.side_effect = lambda model: knowledge_query if model is Knowledge else document_query
        content = "a" * 120
        source_url = "https://example.com/new-page"

        for sync_type in ("incremental", "replace", "complete"):
            with self.subTest(sync_type=sync_type):
                create_document.reset_mock()
                if sync_type == "complete":
                    handler = get_save_handler(knowledge.id, "user-id", "body")
                else:
                    handler = get_sync_handler(knowledge.id, "user-id", sync_type=sync_type)
                handler(MagicMock(tag=None, url=source_url), MagicMock(status=200, content=content))

                create_document.return_value.save.assert_called_once()
                instance = create_document.return_value.save.call_args.args[0]
                self.assertEqual(instance["meta"]["source_url"], source_url)
                self.assertEqual(instance["doc_strategy"], strategy)
                self.assertEqual([p["content"] for p in instance["paragraphs"]], ["a" * 50, "a" * 50, "a" * 20])

    @patch("knowledge.serializers.document.DocumentSerializers.Sync")
    @patch("knowledge.task.handler.QuerySet")
    def test_incremental_crawl_reuses_response_and_preserves_document_strategy(self, query_set, sync_document):
        strategy = normalize_document_strategy(
            {"visual": {"enabled": True, "strategy": "model", "model_id": "00000000-0000-0000-0000-000000000041"}}
        )
        knowledge = MagicMock(id="knowledge-id", meta={"doc_strategy": strategy})
        existing = MagicMock(
            id="document-id",
            type=KnowledgeType.WEB,
            meta={"source_url": "https://example.com/docs/"},
            doc_strategy=normalize_document_strategy(None),
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

        sync_document.assert_called_once_with(
            data={
                "knowledge_id": knowledge.id,
                "document_id": existing.id,
                "strategy_mode": "default",
            }
        )
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

        strategy = normalize_document_strategy(
            {
                "split": {"max_length": 888},
                "visual": {"enabled": True, "strategy": "model", "model_id": "00000000-0000-0000-0000-000000000042"},
            }
        )
        handler = get_sync_handler("knowledge-id", "user-id", doc_strategy=strategy, sync_type="replace")
        handler(MagicMock(tag=None, url="https://example.com/docs"), MagicMock(status=200, content="updated"))

        instance = create_document.return_value.save.call_args.args[0]
        self.assertEqual(instance["doc_strategy"], normalize_document_strategy(existing.doc_strategy))
        self.assertEqual(instance["meta"]["selector"], ".content")
        delete_document_data.assert_called_once_with(["old-document-id"])

    @patch("knowledge.task.handler.delete_document_data")
    @patch("knowledge.serializers.document.DocumentSerializers.Create")
    @patch("knowledge.task.handler.internalize_web_images", side_effect=lambda content, _knowledge_id: content)
    @patch("knowledge.task.handler.QuerySet")
    def test_recreated_existing_urls_keep_their_strategy_while_new_urls_use_knowledge_strategy(
        self, query_set, _internalize_web_images, create_document, delete_document_data
    ):
        old_strategy = normalize_document_strategy(
            {
                "split": {"max_length": 50, "child_length": 50},
                "visual": {"enabled": True, "model_id": "00000000-0000-0000-0000-000000000041"},
                "index": {"title_as_question": True},
            }
        )
        new_strategy = normalize_document_strategy({"split": {"max_length": 80, "child_length": 80}})
        knowledge = MagicMock(id="knowledge-id", meta={"selector": "body", "doc_strategy": new_strategy})
        existing = MagicMock(
            id="old-document-id",
            meta={"source_url": "https://example.com/existing/"},
            doc_strategy=old_strategy,
        )
        knowledge_query = MagicMock()
        knowledge_query.filter.return_value.first.return_value = knowledge
        document_query = MagicMock()
        document_query.filter.return_value.__iter__.return_value = [existing]
        query_set.side_effect = lambda model: knowledge_query if model is Knowledge else document_query
        create_document.return_value.save.return_value = {}

        for sync_type in ("replace", "complete"):
            with self.subTest(sync_type=sync_type):
                create_document.reset_mock()
                delete_document_data.reset_mock()
                if sync_type == "complete":
                    handler = get_save_handler(knowledge.id, "user-id", "body", new_strategy)
                else:
                    handler = get_sync_handler(knowledge.id, "user-id", new_strategy, sync_type)
                for url in ("https://example.com/existing#top", "https://example.com/new"):
                    handler(MagicMock(tag=None, url=url), MagicMock(status=200, content="a" * 120))

                self.assertEqual(create_document.return_value.save.call_count, 2)
                old_instance, new_instance = [call.args[0] for call in create_document.return_value.save.call_args_list]
                self.assertEqual(old_instance["doc_strategy"], old_strategy)
                self.assertEqual(new_instance["doc_strategy"], new_strategy)
                self.assertEqual([p["content"] for p in old_instance["paragraphs"]], ["a" * 50, "a" * 50, "a" * 20])
                self.assertEqual([p["content"] for p in new_instance["paragraphs"]], ["a" * 80, "a" * 40])
                if sync_type == "replace":
                    delete_document_data.assert_called_once_with([existing.id])
                else:
                    delete_document_data.assert_not_called()

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
