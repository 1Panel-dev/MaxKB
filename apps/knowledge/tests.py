from contextlib import nullcontext
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from common.exception.app_exception import AppApiException, AppUnauthorizedFailed
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from django.utils import timezone
from django.utils.datastructures import MultiValueDict
from knowledge.api.document import DocumentBatchAddTagAPI, DocumentSplitAPI
from knowledge.models import (
    AssetProcessStatus,
    ContentOrigin,
    Document,
    DocumentResourceType,
    File,
    FileSourceType,
    Knowledge,
    KnowledgeSyncLog,
    KnowledgeSyncStatus,
    KnowledgeSyncTrigger,
    KnowledgeSyncType,
    KnowledgeType,
    KnowledgeWorkflow,
    LocalState,
    Paragraph,
    ParagraphAsset,
    Problem,
    ProblemParagraphMapping,
    SearchMode,
    SourceType,
    SyncState,
)
from knowledge.models.knowledge import on_delete_paragraph
from knowledge.models.knowledge_action import State as KnowledgeActionState
from knowledge.serializers.document import (
    DocumentBatchAddTagSerializer,
    DocumentSerializers,
    DocumentWebInstanceSerializer,
)
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
from knowledge.serializers.knowledge_workflow import KnowledgeWorkflowActionSerializer, finalize_knowledge_action
from knowledge.serializers.problem import ProblemInstanceSerializer, ProblemSerializer
from knowledge.serializers.paragraph import ParagraphSerializers
from knowledge.services.document_cleanup import delete_synced_paragraph_data
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
    validate_paragraph_file_references,
)
from knowledge.services.paragraph_files import migrate_paragraph_files
from knowledge.services import validate_knowledge_file_size
from knowledge.services.retrieval_stats import (
    collect_recall_asset_ids,
    collect_recall_source_ids,
    get_recall_tracker,
    record_recall,
)
from knowledge.services.workflow_sync import (
    finalize_workflow_complete_snapshot,
    merge_workflow_incremental_snapshot,
    workflow_document_identity,
)
from knowledge.services.workflow_sync_source import validate_workflow_sync_source
from knowledge.task.handler import get_save_handler, get_sync_handler, normalize_web_url
from knowledge.task.sync import (
    get_selector_list,
    scheduled_sync_knowledge,
    scheduled_sync_web_knowledge,
    scheduled_sync_workflow_knowledge,
    sync_replace_web_knowledge,
)
from knowledge.vector.pg_vector import PGVector
from knowledge.views.document import _get_document_split_payload
from knowledge.web_assets import _cache_web_image, internalize_web_images
from oss.serializers.file import FileSerializer, _auth_system, _knowledge_id_for_file_source
from PIL import Image
from rest_framework.exceptions import ValidationError


class KnowledgeUploadSizeLimitTests(SimpleTestCase):
    def test_each_knowledge_base_uses_its_own_file_size_limit(self):
        file = SimpleUploadedFile("example.txt", b"x")
        file.size = 1024 * 1024 + 1
        small_knowledge = Knowledge(file_size_limit=1)
        large_knowledge = Knowledge(file_size_limit=2)

        with self.assertRaises(AppApiException):
            validate_knowledge_file_size(small_knowledge, [file])
        validate_knowledge_file_size(large_knowledge, [file])
        stored_file = MagicMock(spec=["file_size"], file_size=1024 * 1024 + 1)
        with self.assertRaises(AppApiException):
            validate_knowledge_file_size(small_knowledge, [stored_file])
        compressed_file = MagicMock(spec=["file_size", "meta"], file_size=1, meta={"original_size": 1024 * 1024 + 1})
        with self.assertRaises(AppApiException):
            validate_knowledge_file_size(small_knowledge, [compressed_file])

    def test_image_upload_uses_knowledge_limit_above_100_mb(self):
        image_buffer = BytesIO()
        Image.new("RGB", (1, 1)).save(image_buffer, format="PNG")
        file = SimpleUploadedFile("example.png", image_buffer.getvalue(), content_type="image/png")
        file.size = 101 * 1024 * 1024

        ImageDocumentService._validate_image(file, Knowledge(file_size_limit=200))
        with self.assertRaises(AppApiException):
            ImageDocumentService._validate_image(file, Knowledge(file_size_limit=50))

    @patch("knowledge.serializers.document.QuerySet")
    @patch("knowledge.serializers.document.Knowledge.objects.get")
    def test_imports_reject_oversize_file_before_parsing(self, get_knowledge, query_set):
        get_knowledge.return_value = Knowledge(file_size_limit=1)
        query_set.return_value.filter.return_value.exists.return_value = True
        file = SimpleUploadedFile("example.csv", b"x")
        file.size = 1024 * 1024 + 1
        for method_name, parser_name in (("save_qa", "parse_qa_file"), ("save_table", "parse_table_file")):
            with self.subTest(method=method_name):
                serializer = DocumentSerializers.Create(data={"knowledge_id": "00000000-0000-0000-0000-000000000001"})
                setattr(serializer, parser_name, MagicMock())

                with self.assertRaises(AppApiException):
                    getattr(serializer, method_name)({"file_list": [file]})
                getattr(serializer, parser_name).assert_not_called()

    @patch("knowledge.serializers.document.QuerySet")
    def test_replace_source_file_rejects_oversize_file(self, query_set):
        query_set.return_value.filter.return_value.filter.return_value.first.return_value = Knowledge(file_size_limit=1)
        file = SimpleUploadedFile("example.txt", b"x")
        file.size = 1024 * 1024 + 1
        serializer = DocumentSerializers.ReplaceSourceFile(
            data={
                "workspace_id": "workspace",
                "knowledge_id": "00000000-0000-0000-0000-000000000001",
                "document_id": "00000000-0000-0000-0000-000000000002",
                "file": file,
            }
        )

        with self.assertRaises(AppApiException):
            serializer.is_valid(raise_exception=True)

    @patch("oss.serializers.file.QuerySet")
    def test_knowledge_file_upload_rejects_oversize_file_before_storage(self, query_set):
        query_set.return_value.filter.return_value.first.return_value = Knowledge(file_size_limit=1)
        file = SimpleUploadedFile("example.txt", b"x")
        file.size = 1024 * 1024 + 1
        serializer = FileSerializer(
            data={
                "file": file,
                "source_id": "00000000-0000-0000-0000-000000000001",
                "source_type": FileSourceType.KNOWLEDGE.value,
            }
        )

        with self.assertRaises(AppApiException):
            serializer.upload()

    @patch("oss.serializers.file.File")
    @patch("oss.serializers.file.QuerySet")
    def test_document_file_upload_uses_its_knowledge_limit_before_storage(self, query_set, file_model):
        knowledge_id = "00000000-0000-0000-0000-000000000001"
        document_id = "00000000-0000-0000-0000-000000000002"
        document_query = MagicMock()
        document_query.filter.return_value.values_list.return_value.first.return_value = knowledge_id
        knowledge_query = MagicMock()
        knowledge_query.filter.return_value.first.return_value = Knowledge(file_size_limit=1)
        query_set.side_effect = lambda model: {Document: document_query, Knowledge: knowledge_query}[model]
        file = SimpleUploadedFile("example.txt", b"x")
        file.size = 1024 * 1024 + 1
        serializer = FileSerializer(
            data={"file": file, "source_id": document_id, "source_type": FileSourceType.DOCUMENT.value}
        )

        with self.assertRaises(AppApiException):
            serializer.upload()
        file_model.assert_not_called()

        knowledge_query.filter.return_value.first.return_value = Knowledge(file_size_limit=2)
        serializer = FileSerializer(
            data={"file": file, "source_id": document_id, "source_type": FileSourceType.DOCUMENT.value}
        )
        serializer.upload()
        file_model.return_value.save.assert_called_once_with(b"x")

    @patch("oss.serializers.file.File")
    @patch("oss.serializers.file.QuerySet")
    def test_paragraph_file_upload_uses_its_knowledge_limit_before_storage(self, query_set, file_model):
        knowledge_id = "00000000-0000-0000-0000-000000000001"
        paragraph_id = "00000000-0000-0000-0000-000000000003"
        paragraph_query = MagicMock()
        paragraph_query.filter.return_value.values_list.return_value.first.return_value = knowledge_id
        knowledge_query = MagicMock()
        knowledge_query.filter.return_value.first.return_value = Knowledge(file_size_limit=1)
        query_set.side_effect = lambda model: {Paragraph: paragraph_query, Knowledge: knowledge_query}[model]
        file = SimpleUploadedFile("attachment.pdf", b"x")
        file.size = 1024 * 1024 + 1
        serializer = FileSerializer(
            data={"file": file, "source_id": paragraph_id, "source_type": FileSourceType.PARAGRAPH.value}
        )

        with self.assertRaises(AppApiException):
            serializer.upload()
        file_model.assert_not_called()
        self.assertEqual(_knowledge_id_for_file_source(FileSourceType.PARAGRAPH, paragraph_id), knowledge_id)

        knowledge_query.filter.return_value.first.return_value = Knowledge(file_size_limit=2)
        serializer = FileSerializer(
            data={"file": file, "source_id": paragraph_id, "source_type": FileSourceType.PARAGRAPH.value}
        )
        serializer.upload()
        file_model.return_value.save.assert_called_once_with(b"x")

    @patch("knowledge.models.knowledge.File.objects")
    def test_deleting_paragraph_removes_its_owned_files(self, file_objects):
        paragraph = Paragraph(id="00000000-0000-0000-0000-000000000003")

        on_delete_paragraph(Paragraph, paragraph, "default")

        file_objects.using.return_value.filter.assert_called_once_with(
            source_type=FileSourceType.PARAGRAPH, source_id=str(paragraph.id)
        )
        file_objects.using.return_value.filter.return_value.delete.assert_called_once()

    @patch("oss.serializers.file._check_workspace_resource_permission")
    @patch("oss.serializers.file.get_auth")
    @patch("oss.serializers.file.QuerySet")
    def test_paragraph_file_read_uses_knowledge_permission(self, query_set, get_auth, check_permission):
        user_query, paragraph_query, knowledge_query = MagicMock(), MagicMock(), MagicMock()
        user_query.filter.return_value.first.return_value = MagicMock()
        paragraph_query.filter.return_value.values_list.return_value.first.return_value = "knowledge-id"
        knowledge_query.filter.return_value.first.return_value = Knowledge(
            id="00000000-0000-0000-0000-000000000001", workspace_id="workspace"
        )
        query_set.side_effect = lambda model: {
            "User": user_query,
            "Paragraph": paragraph_query,
            "Knowledge": knowledge_query,
        }[model.__name__]
        file = File(source_type=FileSourceType.PARAGRAPH, source_id="paragraph-id")

        _auth_system(file, "user-id")

        check_permission.assert_called_once_with(
            get_auth.return_value,
            "user-id",
            workspace_id="workspace",
            target_id=knowledge_query.filter.return_value.first.return_value.id,
            auth_target_type="KNOWLEDGE",
            read_permission="KNOWLEDGE:READ",
        )

        paragraph_query.filter.return_value.values_list.return_value.first.return_value = None
        with self.assertRaises(AppUnauthorizedFailed):
            _auth_system(file, "user-id")

    @patch("knowledge.serializers.knowledge_workflow.KnowledgeAction")
    @patch("knowledge.serializers.knowledge_workflow.QuerySet")
    def test_workflow_rejects_oversize_stored_file_before_starting(self, query_set, knowledge_action):
        knowledge_query = MagicMock()
        knowledge_query.filter.return_value.filter.return_value.exists.return_value = True
        knowledge_query.filter.return_value.first.return_value = Knowledge(file_size_limit=1)
        workflow_query = MagicMock()
        workflow_query.filter.return_value.first.return_value = MagicMock()
        file_query = MagicMock()
        file_query.filter.return_value = [MagicMock(spec=["file_size"], file_size=1024 * 1024 + 1)]
        query_set.side_effect = lambda model: {
            Knowledge: knowledge_query,
            KnowledgeWorkflow: workflow_query,
            File: file_query,
        }[model]
        serializer = KnowledgeWorkflowActionSerializer(
            data={"workspace_id": "workspace", "knowledge_id": "00000000-0000-0000-0000-000000000001"}
        )

        with self.assertRaises(AppApiException):
            serializer.action(
                {"data_source": {"file_list": [{"file_id": "00000000-0000-0000-0000-000000000002"}]}},
                MagicMock(),
            )
        knowledge_action.assert_not_called()


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
        strategy = normalize_document_strategy(
            {
                "split": {"child_length": 50},
                "visual": {
                    "enabled": True,
                    "strategy": "model",
                    "model_id": "00000000-0000-0000-0000-000000000046",
                },
                "index": {"title_as_question": True},
            }
        )
        file = MagicMock(
            id="00000000-0000-0000-0000-000000000043",
            file_name="scene.png",
            sha256_hash="image-hash",
            meta={
                "image_preview": {
                    "caption": "风景",
                    "ocr_text": "识别文字",
                    "description": "群山与草地" + "景" * 110,
                    "process_status": "success",
                    "process_error": "",
                    "doc_strategy": strategy,
                    "imported": False,
                }
            },
        )
        file_query = MagicMock()
        file_query.filter.return_value.select_for_update.return_value = [file]
        update_query = MagicMock()
        document = MagicMock(id="00000000-0000-0000-0000-000000000044")
        paragraph = MagicMock(id="00000000-0000-0000-0000-000000000045")
        document_model.return_value = document
        paragraph_model.return_value = paragraph
        service = ImageDocumentService("workspace", str(knowledge.id), "user-id")
        service.get_knowledge = MagicMock(return_value=knowledge)

        for file_name, title, caption in (("scene.png", "scene", "风景"), ("scene.v2.png", "scene.v2", "")):
            with self.subTest(file_name=file_name, caption=caption):
                file.file_name = file_name
                file.meta["image_preview"]["caption"] = caption
                query_set.side_effect = [file_query, update_query]
                update_query.reset_mock()
                incremental_sync.reset_mock()
                paragraph_model.reset_mock()
                expected_content = (caption + "\n识别文字\n群山与草地" + "景" * 110).strip()

                document_ids = ImageDocumentService.import_previews.__wrapped__(service, [file.id])

                self.assertEqual(document_ids, [str(document.id)])
                document_values = document_model.call_args.kwargs
                self.assertEqual(document_values["resource_type"], DocumentResourceType.IMAGE)
                self.assertEqual(document_values["name"], file_name)
                self.assertEqual(document_values["char_length"], len(expected_content))
                self.assertEqual(document_values["doc_strategy"], strategy)
                self.assertEqual(
                    document_values["source_hash"],
                    document_source_hash([{"title": title, "content": expected_content}]),
                )
                paragraph_model.assert_called_once()
                paragraph.save.assert_called_once()
                paragraph_values = paragraph_model.call_args.kwargs
                self.assertEqual(paragraph_values["title"], title)
                self.assertEqual(paragraph_values["content"], expected_content)
                self.assertGreater(len(paragraph_values["chunks"]), 1)
                self.assertTrue(all(len(chunk) <= 50 for chunk in paragraph_values["chunks"]))
                self.assertEqual(paragraph_values["content_schema"][0]["file_id"], str(file.id))
                self.assertEqual(paragraph_values["content_schema"][0]["caption"], caption)
                self.assertEqual(create_asset.call_args.kwargs["file_id"], file.id)
                update_query.filter.return_value.update.assert_called_once()
                update_values = update_query.filter.return_value.update.call_args.kwargs
                self.assertEqual(update_values["source_type"], FileSourceType.DOCUMENT)
                self.assertEqual(update_values["source_id"], str(document.id))
                incremental_sync.return_value._sync_title_questions.assert_called_once_with([paragraph])
                self.assertEqual(incremental_sync.call_args.args[1], strategy)


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


class KnowledgeModelUpdateTests(SimpleTestCase):
    @patch("knowledge.task.sync.QuerySet")
    @patch("knowledge.serializers.knowledge.sync_replace_web_knowledge.delay")
    @patch("knowledge.serializers.knowledge.update_resource_mapping_by_knowledge")
    @patch("knowledge.serializers.knowledge.QuerySet")
    def test_saved_strategy_takes_effect_on_next_manual_or_scheduled_sync(
        self, query_set, _update_mapping, delay, task_query_set
    ):
        knowledge = MagicMock(
            id="00000000-0000-0000-0000-000000000011",
            user_id="00000000-0000-0000-0000-000000000013",
            type=KnowledgeType.WEB,
            meta={
                "source_url": "https://example.com",
                "selector": "body",
                "doc_strategy": normalize_document_strategy(None),
                "sync_setting": {"enabled": True, "sync_type": "incremental"},
            },
        )
        query_set.return_value.get.return_value = knowledge
        task_query_set.return_value.filter.return_value.first.return_value = knowledge
        operation = KnowledgeSerializer.Operate(
            data={"workspace_id": "default", "knowledge_id": knowledge.id, "user_id": knowledge.user_id}
        )
        strategy = normalize_document_strategy(
            {
                "split": {"max_length": 1024},
                "visual": {"enabled": True, "model_id": "00000000-0000-0000-0000-000000000042"},
                "index": {"title_as_question": True},
            }
        )

        KnowledgeSerializer.Operate.edit.__wrapped__(operation, {"doc_strategy": strategy}, select_one=False)

        delay.assert_not_called()
        self.assertEqual(knowledge.meta["doc_strategy"], strategy)
        self.assertEqual(knowledge.meta["source_url"], "https://example.com")
        sync = KnowledgeSerializer.SyncWeb(data={"user_id": knowledge.user_id})
        for sync_type in ("incremental", "replace", "complete"):
            with self.subTest(sync_type=sync_type):
                delay.reset_mock()
                getattr(sync, f"{sync_type}_sync")(knowledge)
                delay.assert_called_once()
                self.assertEqual(delay.call_args.args[4], strategy)
                self.assertEqual(delay.call_args.args[5], sync_type)

                delay.reset_mock()
                knowledge.meta["sync_setting"]["sync_type"] = sync_type
                self.assertTrue(scheduled_sync_web_knowledge.run(str(knowledge.id)))
                delay.assert_called_once()
                self.assertEqual(delay.call_args.args[4], strategy)
                self.assertEqual(delay.call_args.args[5], sync_type)

    @patch("knowledge.serializers.knowledge.update_resource_mapping_by_knowledge")
    @patch("knowledge.serializers.knowledge.QuerySet")
    def test_model_update_preserves_meta_when_strategy_is_omitted_or_inapplicable_null(self, query_set, update_mapping):
        knowledge_id = "00000000-0000-0000-0000-000000000011"
        model_id = "00000000-0000-0000-0000-000000000012"
        for knowledge_type in KnowledgeType:
            payloads = [{"embedding_model_id": model_id}]
            if knowledge_type != KnowledgeType.WEB:
                payloads.append({"embedding_model_id": model_id, "doc_strategy": None})
            for payload in payloads:
                with self.subTest(knowledge_type=knowledge_type, payload=payload):
                    original_meta = {"sync_setting": {"enabled": True}}
                    if knowledge_type == KnowledgeType.WEB:
                        original_meta["doc_strategy"] = normalize_document_strategy({"split": {"max_length": 1024}})
                    knowledge = MagicMock(id=knowledge_id, type=knowledge_type, meta=original_meta.copy())
                    query_set.return_value.get.return_value = knowledge
                    operation = KnowledgeSerializer.Operate(
                        data={
                            "user_id": "00000000-0000-0000-0000-000000000013",
                            "workspace_id": "workspace-id",
                            "knowledge_id": knowledge_id,
                        }
                    )

                    # Exercise the edit path with mocked persistence, without opening a database transaction.
                    KnowledgeSerializer.Operate.edit.__wrapped__(operation, payload, select_one=False)

                    self.assertEqual(knowledge.embedding_model_id, model_id)
                    self.assertEqual(knowledge.meta, original_meta)
                    knowledge.save.assert_called_once_with()
                    update_mapping.assert_called_with(knowledge_id)

    @patch("knowledge.serializers.knowledge.update_resource_mapping_by_knowledge")
    @patch("knowledge.serializers.knowledge.QuerySet")
    def test_web_knowledge_explicit_null_strategy_still_resets_to_defaults(self, query_set, _update_mapping):
        knowledge = MagicMock(
            type=KnowledgeType.WEB,
            meta={"selector": "body", "doc_strategy": {"split": {"max_length": 1024}}},
        )
        query_set.return_value.get.return_value = knowledge
        operation = KnowledgeSerializer.Operate(
            data={
                "user_id": "00000000-0000-0000-0000-000000000013",
                "workspace_id": "workspace-id",
                "knowledge_id": "00000000-0000-0000-0000-000000000011",
            }
        )

        KnowledgeSerializer.Operate.edit.__wrapped__(operation, {"doc_strategy": None}, select_one=False)

        self.assertEqual(knowledge.meta, {"selector": "body", "doc_strategy": normalize_document_strategy(None)})
        knowledge.save.assert_called_once_with()


class WebKnowledgeSyncTaskTests(SimpleTestCase):
    def setUp(self):
        transaction_patch = patch("knowledge.task.sync.transaction.atomic", return_value=nullcontext())
        transaction_patch.start()
        self.addCleanup(transaction_patch.stop)
        super().setUp()
        heartbeat_patch = patch("knowledge.task.sync.start_sync_heartbeat", return_value=lambda: None)
        heartbeat_patch.start()
        self.addCleanup(heartbeat_patch.stop)
        heartbeat_patch = patch("knowledge.task.sync.recover_stale_sync_logs", return_value=lambda: None)
        heartbeat_patch.start()
        self.addCleanup(heartbeat_patch.stop)
        heartbeat_patch = patch(
            "knowledge.serializers.knowledge_workflow.start_sync_heartbeat", return_value=lambda: None
        )
        heartbeat_patch.start()
        self.addCleanup(heartbeat_patch.stop)

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
        sync_log = MagicMock(id="log-id", status=KnowledgeSyncStatus.RUNNING)
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
    def test_complete_sync_replaces_documents_after_successful_crawl(
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
        self.assertEqual(events, ["crawl", "cleanup"])


class KnowledgeScheduleTests(SimpleTestCase):
    def setUp(self):
        super().setUp()
        heartbeat_patch = patch("knowledge.task.sync.start_sync_heartbeat", return_value=lambda: None)
        heartbeat_patch.start()
        self.addCleanup(heartbeat_patch.stop)
        heartbeat_patch = patch("knowledge.task.sync.recover_stale_sync_logs", return_value=lambda: None)
        heartbeat_patch.start()
        self.addCleanup(heartbeat_patch.stop)
        heartbeat_patch = patch(
            "knowledge.serializers.knowledge_workflow.start_sync_heartbeat", return_value=lambda: None
        )
        heartbeat_patch.start()
        self.addCleanup(heartbeat_patch.stop)

    def test_daily_setting_uses_trigger_schedule_fields(self):
        serializer = KnowledgeSyncSettingRequest(
            data={
                "enabled": True,
                "schedule_type": "daily",
                "time": "01:30",
                "sync_type": "incremental",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data,
            {
                "enabled": True,
                "schedule_type": "daily",
                "time": ["01:30"],
                "sync_type": "incremental",
            },
        )

    def test_only_active_trigger_schedule_fields_are_returned(self):
        self.assertEqual(
            normalize_knowledge_sync_setting(
                {
                    "enabled": True,
                    "schedule_type": "interval",
                    "interval_unit": "minutes",
                    "interval_value": 5,
                    "time": ["01:00"],
                    "days": [1],
                    "cron_expression": "0 1 * * *",
                    "sync_type": "replace",
                }
            ),
            {
                "enabled": True,
                "schedule_type": "interval",
                "interval_unit": "minutes",
                "interval_value": 5,
                "sync_type": "replace",
            },
        )

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

    def test_preset_periods_and_minimum_interval(self):
        for setting in [
            {"schedule_type": "weekly", "days": [1], "time": ["01:00"]},
            {"schedule_type": "monthly", "days": [31], "time": ["01:00"]},
            {"schedule_type": "interval", "interval_unit": "hours", "interval_value": 1},
            {"schedule_type": "interval", "interval_unit": "minutes", "interval_value": 5},
        ]:
            with self.subTest(setting=setting):
                serializer = KnowledgeSyncSettingRequest(data={"enabled": True, "sync_type": "incremental", **setting})
                self.assertTrue(serializer.is_valid(), serializer.errors)
        for setting in [
            {"schedule_type": "interval", "interval_unit": "minutes", "interval_value": 4},
            {"schedule_type": "cron", "cron_expression": "*/4 * * * *"},
            {"schedule_type": "daily", "time": ["01:00", "01:03"]},
        ]:
            with self.subTest(setting=setting):
                serializer = KnowledgeSyncSettingRequest(data={"enabled": True, "sync_type": "incremental", **setting})
                self.assertFalse(serializer.is_valid())

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
    def test_scheduled_entry_uses_saved_strategy_and_sync_type_and_records_log(self, query_set, delay):
        strategy = normalize_document_strategy(
            {"visual": {"enabled": True, "strategy": "model", "model_id": "00000000-0000-0000-0000-000000000043"}}
        )
        knowledge = MagicMock(
            id="00000000-0000-0000-0000-000000000022",
            user_id="00000000-0000-0000-0000-000000000023",
            meta={
                "source_url": "https://example.com",
                "selector": "body",
                "doc_strategy": strategy,
                "sync_setting": {"enabled": True, "sync_type": "complete"},
            },
        )
        query_set.return_value.filter.return_value.first.return_value = knowledge

        self.assertTrue(scheduled_sync_web_knowledge.run(str(knowledge.id)))

        self.assertEqual(delay.call_args.args[-1], "complete")
        self.assertEqual(delay.call_args.args[4], strategy)
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
    @patch("knowledge.task.sync.KnowledgeSyncLog.objects.create")
    @patch("knowledge.task.sync.QuerySet")
    def test_generic_scheduled_entry_dispatches_lark_task(self, query_set, create_log, send_task):
        knowledge = MagicMock(
            id="00000000-0000-0000-0000-000000000025",
            type=KnowledgeType.LARK,
            workspace_id="workspace-id",
            meta={"sync_setting": {"enabled": True}},
        )
        knowledge_query = MagicMock()
        knowledge_query.select_for_update.return_value.filter.return_value.first.return_value = knowledge
        log_query = MagicMock()
        log_query.filter.return_value.exists.return_value = False
        query_set.side_effect = lambda model: knowledge_query if model is Knowledge else log_query
        sync_log = MagicMock(id="00000000-0000-0000-0000-000000000030")
        create_log.return_value = sync_log

        with patch("knowledge.task.sync.transaction.atomic", return_value=nullcontext()):
            self.assertTrue(scheduled_sync_knowledge.run(str(knowledge.id)))

        send_task.assert_called_once_with(
            "celery:scheduled_sync_lark_knowledge", args=[str(knowledge.id), str(sync_log.id)]
        )
        self.assertEqual(create_log.call_args.kwargs["status"], KnowledgeSyncStatus.RUNNING)

    @patch("knowledge.task.sync.has_running_workflow_document_sync", return_value=False)
    @patch("knowledge.task.sync.scheduled_sync_workflow_knowledge.delay")
    @patch("knowledge.task.sync.KnowledgeSyncLog.objects.create")
    @patch("knowledge.task.sync.QuerySet")
    def test_generic_scheduled_entry_dispatches_workflow_task(self, query_set, create_log, delay, _running):
        knowledge = MagicMock(
            id="00000000-0000-0000-0000-000000000026",
            type=KnowledgeType.WORKFLOW,
            workspace_id="workspace-id",
            meta={"sync_setting": {"enabled": True}},
        )
        knowledge_query = MagicMock()
        knowledge_query.select_for_update.return_value.filter.return_value.first.return_value = knowledge
        log_query = MagicMock()
        log_query.filter.return_value.exists.return_value = False
        query_set.side_effect = lambda model: knowledge_query if model is Knowledge else log_query
        sync_log = MagicMock(id="00000000-0000-0000-0000-000000000031")
        create_log.return_value = sync_log

        with patch("knowledge.task.sync.transaction.atomic", return_value=nullcontext()):
            self.assertTrue(scheduled_sync_knowledge.run(str(knowledge.id)))

        delay.assert_called_once_with(str(knowledge.id), str(sync_log.id))

    @patch("knowledge.task.sync.celery_app.send_task")
    @patch("knowledge.task.sync.KnowledgeSyncLog.objects.create")
    @patch("knowledge.task.sync.QuerySet")
    def test_overlapping_schedule_is_skipped_with_a_log(self, query_set, create_log, send_task):
        knowledge = MagicMock(
            id="00000000-0000-0000-0000-000000000032",
            type=KnowledgeType.LARK,
            workspace_id="workspace-id",
            meta={"sync_setting": {"enabled": True, "sync_type": "incremental"}},
        )
        knowledge_query = MagicMock()
        knowledge_query.select_for_update.return_value.filter.return_value.first.return_value = knowledge
        log_query = MagicMock()
        log_query.filter.return_value.exists.return_value = True
        query_set.side_effect = lambda model: knowledge_query if model is Knowledge else log_query

        with patch("knowledge.task.sync.transaction.atomic", return_value=nullcontext()):
            self.assertFalse(scheduled_sync_knowledge.run(str(knowledge.id)))

        self.assertEqual(create_log.call_args.kwargs["status"], KnowledgeSyncStatus.SKIPPED)
        send_task.assert_not_called()


class WorkflowKnowledgeScheduleTests(SimpleTestCase):
    def setUp(self):
        super().setUp()
        heartbeat_patch = patch("knowledge.task.sync.start_sync_heartbeat", return_value=lambda: None)
        heartbeat_patch.start()
        self.addCleanup(heartbeat_patch.stop)
        heartbeat_patch = patch("knowledge.task.sync.recover_stale_sync_logs", return_value=lambda: None)
        heartbeat_patch.start()
        self.addCleanup(heartbeat_patch.stop)
        heartbeat_patch = patch(
            "knowledge.serializers.knowledge_workflow.start_sync_heartbeat", return_value=lambda: None
        )
        heartbeat_patch.start()
        self.addCleanup(heartbeat_patch.stop)

    @patch("knowledge.services.workflow_sync._delete_workflow_documents")
    @patch("knowledge.services.workflow_sync.QuerySet")
    def test_complete_snapshot_replaces_old_only_after_success(self, query_set, delete_documents):
        sync_log = MagicMock(knowledge_id="knowledge-id", create_time=timezone.now())
        document_query = MagicMock()
        new_query = MagicMock()
        old_query = MagicMock()
        new_query.values_list.return_value = ["new-id"]
        new_query.__iter__.return_value = [SimpleNamespace(id="new-id", name="new", meta={})]
        old_query.values_list.return_value = ["old-id"]
        document_query.filter.return_value = document_query
        document_query.filter.side_effect = lambda **filters: (
            new_query
            if "meta__workflow_sync_log_id" in filters
            else old_query
            if "create_time__lt" in filters
            else document_query
        )
        document_query.count.return_value = 1
        query_set.return_value = document_query
        delete_documents.side_effect = lambda document_ids: list(document_ids)

        source = {"source_scope": "scope"}
        success = finalize_workflow_complete_snapshot.__wrapped__(sync_log, True, source)
        self.assertEqual(success["synced_count"], 1)
        self.assertEqual(success["deleted_count"], 1)
        delete_documents.assert_called_with(["old-id"])

        failure = finalize_workflow_complete_snapshot.__wrapped__(sync_log, False, source)
        self.assertEqual(failure["failed_count"], 1)
        delete_documents.assert_called_with(["new-id"])

    def test_schedule_accepts_web_and_tool_sources_but_rejects_local_source(self):
        for node_type in ("data-source-web-node", "tool-lib-node"):
            with self.subTest(node_type=node_type):
                validate_workflow_sync_source(
                    {"nodes": [{"id": "source", "type": node_type, "properties": {"kind": "data-source"}}]},
                    {"data_source": {"node_id": "source", "source_url": "https://example.com"}},
                )
        with self.assertRaisesRegex(ValueError, "Local file"):
            validate_workflow_sync_source(
                {"nodes": [{"id": "source", "type": "data-source-local-node", "properties": {"kind": "data-source"}}]},
                {"data_source": {"node_id": "source"}},
            )
        with self.assertRaisesRegex(ValueError, "no longer exists"):
            validate_workflow_sync_source({"nodes": []}, {"data_source": {"node_id": "source"}})
        with self.assertRaisesRegex(ValueError, "source URL"):
            validate_workflow_sync_source(
                {"nodes": [{"id": "source", "type": "data-source-web-node", "properties": {"kind": "data-source"}}]},
                {"data_source": {"node_id": "source"}},
            )

    def test_schedule_accepts_remote_tool_folder_but_rejects_uploaded_files(self):
        tool_flow = {"nodes": [{"id": "source", "type": "tool-lib-node", "properties": {"kind": "data-source"}}]}
        validate_workflow_sync_source(
            tool_flow,
            {"data_source": {"node_id": "source", "file_list": [{"type": "folder", "token": "folder-token"}]}},
        )
        with self.assertRaisesRegex(ValueError, "Local file"):
            validate_workflow_sync_source(
                tool_flow,
                {"data_source": {"node_id": "source", "file_list": [{"file_id": "uploaded-file-id"}]}},
            )

    @patch("knowledge.task.sync.KnowledgeWorkflowActionSerializer")
    @patch("knowledge.task.sync.KnowledgeSyncLog.objects.create")
    @patch("knowledge.task.sync.QuerySet")
    def test_local_file_input_is_not_scheduled(self, query_set, create_log, action_serializer):
        knowledge = MagicMock(
            id="00000000-0000-0000-0000-000000000037",
            workspace_id="workspace-id",
            type=KnowledgeType.WORKFLOW,
            user=MagicMock(),
            meta={
                "sync_setting": {"enabled": True, "sync_type": "incremental"},
                "workflow_sync_input": {
                    "data_source": {"node_id": "start-node", "file_list": [{"file_id": "file-id"}]}
                },
            },
        )
        knowledge_query = MagicMock()
        knowledge_query.filter.return_value.first.return_value = knowledge
        log_query = MagicMock()
        log_query.filter.return_value.exists.return_value = False
        document_query = MagicMock()
        document_query.filter.return_value.count.return_value = 1
        workflow_query = MagicMock()
        workflow_query.filter.return_value.values_list.return_value.first.return_value = {
            "nodes": [{"id": "start-node", "type": "data-source-local-node", "properties": {"kind": "data-source"}}]
        }
        query_set.side_effect = lambda model: {
            Knowledge: knowledge_query,
            KnowledgeSyncLog: log_query,
            KnowledgeWorkflow: workflow_query,
        }.get(model, document_query)
        create_log.return_value = MagicMock(id="00000000-0000-0000-0000-000000000038")

        self.assertFalse(scheduled_sync_workflow_knowledge.run(str(knowledge.id)))

        action_serializer.assert_not_called()
        self.assertEqual(log_query.filter.return_value.update.call_args.kwargs["status"], KnowledgeSyncStatus.FAILURE)

    @patch("knowledge.serializers.knowledge_workflow.merge_workflow_incremental_snapshot")
    @patch("knowledge.serializers.knowledge_workflow.QuerySet")
    def test_incremental_workflow_uses_stable_snapshot_merge(self, query_set, merge_workflow_snapshot):
        sync_log = MagicMock(
            status=KnowledgeSyncStatus.RUNNING,
            id="00000000-0000-0000-0000-000000000032",
            knowledge_id="00000000-0000-0000-0000-000000000033",
            create_time=timezone.now(),
            sync_type=KnowledgeSyncType.INCREMENTAL,
        )
        action_query = MagicMock()
        log_query = MagicMock()
        log_query.filter.return_value.first.return_value = sync_log
        log_query.select_for_update.return_value.get.return_value = sync_log
        query_set.side_effect = lambda model: log_query if model is KnowledgeSyncLog else action_query
        merge_workflow_snapshot.return_value = {
            "total_count": 1,
            "synced_count": 0,
            "skipped_count": 1,
            "deleted_count": 0,
            "failed_count": 0,
        }
        document_cleanup = MagicMock()

        # 新引擎:完成收尾由 finalize_knowledge_action 内联处理,state/run_time 由调用方算好传入
        finalize_knowledge_action.__wrapped__(
            "00000000-0000-0000-0000-000000000036",
            KnowledgeActionState.SUCCESS,
            0.0,
            str(sync_log.id),
            document_cleanup,
        )

        merge_workflow_snapshot.assert_called_once_with(sync_log, None)
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
                    "data_source": {"node_id": "start-node", "source_url": "https://example.com"},
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
        workflow_query = MagicMock()
        workflow_query.filter.return_value.values_list.return_value.first.return_value = {
            "nodes": [{"id": "start-node", "type": "data-source-web-node", "properties": {"kind": "data-source"}}]
        }
        query_set.side_effect = lambda model: {
            Knowledge: knowledge_query,
            KnowledgeSyncLog: log_query,
            KnowledgeWorkflow: workflow_query,
        }.get(model, document_query)
        sync_log = MagicMock(id="00000000-0000-0000-0000-000000000028")
        create_log.return_value = sync_log
        action_serializer.return_value.action.return_value = {"id": "00000000-0000-0000-0000-000000000029"}

        self.assertTrue(scheduled_sync_workflow_knowledge.run(str(knowledge.id)))

        workflow_input = action_serializer.return_value.action.call_args.args[0]
        self.assertEqual(workflow_input["data_source"], {"node_id": "start-node", "source_url": "https://example.com"})
        action_serializer.return_value.action.assert_called_once_with(
            workflow_input,
            knowledge.user,
            True,
            str(sync_log.id),
        )

        knowledge.meta["sync_setting"]["sync_type"] = "complete"
        with patch("knowledge.task.sync.delete_document_data") as delete_documents:
            self.assertTrue(scheduled_sync_workflow_knowledge.run(str(knowledge.id)))
        delete_documents.assert_not_called()

        knowledge.meta["sync_setting"]["sync_type"] = "incremental"
        knowledge.meta["workflow_sync_input"]["data_source"] = {
            "node_id": "start-node",
            "file_list": [{"type": "folder", "token": "folder-token"}],
        }
        workflow_query.filter.return_value.values_list.return_value.first.return_value = {
            "nodes": [{"id": "start-node", "type": "tool-lib-node", "properties": {"kind": "data-source"}}]
        }
        self.assertTrue(scheduled_sync_workflow_knowledge.run(str(knowledge.id)))
        self.assertEqual(
            action_serializer.return_value.action.call_args.args[0]["data_source"]["file_list"],
            [{"type": "folder", "token": "folder-token"}],
        )

    @patch("knowledge.serializers.knowledge_workflow.WorkflowRunRegistry")
    @patch("knowledge.serializers.knowledge_workflow.new_instance")
    @patch("knowledge.serializers.knowledge_workflow.WorkflowManage")
    @patch("knowledge.serializers.knowledge_workflow.KnowledgeAction.save")
    @patch("knowledge.serializers.knowledge_workflow.QuerySet")
    def test_manual_action_saves_input_for_later_scheduled_runs(
        self, query_set, _save_action, workflow_manage, _new_instance, _registry
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
    @patch("knowledge.web_assets.File")
    @patch("knowledge.web_assets.QuerySet")
    @patch("knowledge.web_assets.Fork.requests_get")
    def test_remote_image_over_knowledge_limit_is_not_stored(self, requests_get, query_set, file_model):
        requests_get.return_value.status_code = 200
        requests_get.return_value.content = b"x" * (1024 * 1024 + 1)
        query_set.return_value.filter.return_value.first.return_value = Knowledge(file_size_limit=1)

        self.assertIsNone(_cache_web_image("https://example.com/image.png", "knowledge-id"))
        file_model.assert_not_called()

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
    def test_manual_paragraphs_never_match_remote_keys_hashes_or_titles(self):
        service = IncrementalDocumentSync(Document())
        remote = prepare_remote_paragraphs([{"title": "Title", "content": "remote"}])[0]
        for fields in (
            {"source_key": remote["source_key"]},
            {"source_hash": remote["source_hash"]},
            {},
        ):
            with self.subTest(fields=fields):
                manual = Paragraph(title="Title", content="manual", position=1, origin=ContentOrigin.MANUAL, **fields)
                self.assertIsNone(service._match(remote, [manual]))

    def test_source_authoritative_update_overwrites_changed_imported_content(self):
        service = IncrementalDocumentSync(Document(), source_authoritative=True)
        paragraph = Paragraph(
            title="Title",
            content="local edit",
            source_hash="old",
            source_snapshot={"title": "Title", "content": "base"},
            origin=ContentOrigin.SYNCED,
            local_state=LocalState.MODIFIED,
            hit_num=7,
        )
        original_id = paragraph.id
        paragraph.save = MagicMock()
        remote = prepare_remote_paragraphs([{"title": "Title", "content": "remote edit"}])[0]
        result = MergeResult()

        service._merge_matched(paragraph, remote, result)

        self.assertEqual(paragraph.id, original_id)
        self.assertEqual(paragraph.hit_num, 7)
        self.assertEqual(paragraph.content, "remote edit")
        self.assertEqual(paragraph.source_hash, remote["source_hash"])
        self.assertEqual(paragraph.local_state, LocalState.CLEAN)
        self.assertEqual(paragraph.sync_state, SyncState.ACTIVE)
        self.assertEqual(result.updated_ids, [str(original_id)])
        self.assertEqual(result.conflict_ids, [])

    def test_source_authoritative_matches_titles_without_position_limit(self):
        service = IncrementalDocumentSync(Document(), source_authoritative=True)
        paragraph = Paragraph(title="Title", content="old", position=20, origin=ContentOrigin.SYNCED)
        remote = prepare_remote_paragraphs([{"title": "Title", "content": "new"}])[0]

        self.assertIs(service._match(remote, [paragraph]), paragraph)

    def test_source_authoritative_new_title_does_not_reuse_an_old_key(self):
        service = IncrementalDocumentSync(Document(), source_authoritative=True)
        paragraph = Paragraph(title="Old", content="old", source_key="block-1", origin=ContentOrigin.SYNCED)
        remote = prepare_remote_paragraphs([{"title": "New", "content": "new", "source_key": "block-1"}])[0]

        self.assertIsNone(service._match(remote, [paragraph]))

    @patch("knowledge.services.incremental_sync.Paragraph.objects")
    @patch("knowledge.services.incremental_sync.Document.objects")
    def test_source_authoritative_reserves_unchanged_duplicate_headings_before_updates(self, documents, paragraphs):
        strategy = normalize_document_strategy(None)
        document = Document(doc_strategy=strategy, sync_version=1, **strategy_hashes(strategy))
        document.save = MagicMock()
        originals = prepare_remote_paragraphs(
            [
                {"title": "Title", "content": "first"},
                {"title": "Title", "content": "second"},
            ]
        )
        first, second = [
            Paragraph(
                title=item["title"],
                content=item["content"],
                source_key=item["source_key"],
                source_hash=item["source_hash"],
                origin=ContentOrigin.SYNCED,
            )
            for item in originals
        ]
        first.save, second.save = MagicMock(), MagicMock()
        documents.select_for_update.return_value.get.return_value = document
        paragraphs.select_for_update.return_value.filter.return_value.order_by.return_value = [first, second]
        service = IncrementalDocumentSync(document, source_authoritative=True)
        with patch.object(service, "_reorder"), patch.object(service, "_sync_title_questions"):
            result = IncrementalDocumentSync.merge.__wrapped__(
                service,
                [
                    {"title": "Title", "content": "changed"},
                    {"title": "Title", "content": "first"},
                ],
            )

        self.assertEqual(result.unchanged_ids, [str(first.id)])
        self.assertEqual(result.updated_ids, [str(second.id)])
        self.assertEqual(first.content, "first")
        self.assertEqual(second.content, "changed")
        self.assertEqual(first.source_key, originals[1]["source_key"])
        self.assertEqual(second.source_key, originals[0]["source_key"])
        paragraphs.filter.assert_called_once_with(document=document, id__in=[second.id, first.id])
        paragraphs.filter.return_value.update.assert_called_once_with(source_key="")
        paragraphs.create.assert_not_called()

    def test_source_authoritative_unchanged_chunk_preserves_local_content(self):
        service = IncrementalDocumentSync(Document(), source_authoritative=True)
        remote = prepare_remote_paragraphs([{"title": "Title", "content": "base"}])[0]
        paragraph = Paragraph(
            title="Title",
            content="local edit",
            source_key=remote["source_key"],
            source_hash=remote["source_hash"],
            origin=ContentOrigin.SYNCED,
            local_state=LocalState.MODIFIED,
        )
        paragraph.save = MagicMock()
        result = MergeResult()

        service._merge_matched(paragraph, remote, result)

        self.assertEqual(paragraph.content, "local edit")
        paragraph.save.assert_not_called()
        self.assertEqual(result.unchanged_ids, [str(paragraph.id)])

    def test_replace_content_overwrites_local_edit_with_unchanged_source_hash(self):
        service = IncrementalDocumentSync(Document(), source_authoritative=True, replace_content=True)
        remote = prepare_remote_paragraphs([{"title": "Title", "content": "base"}])[0]
        paragraph = Paragraph(
            title="Title",
            content="local edit",
            source_key=remote["source_key"],
            source_hash=remote["source_hash"],
            origin=ContentOrigin.SYNCED,
            local_state=LocalState.MODIFIED,
            hit_num=7,
        )
        paragraph.save = MagicMock()
        result = MergeResult()

        service._merge_matched(paragraph, remote, result)

        self.assertEqual(paragraph.content, "base")
        self.assertEqual(paragraph.hit_num, 7)
        self.assertEqual(paragraph.local_state, LocalState.CLEAN)
        self.assertEqual(result.updated_ids, [str(paragraph.id)])
        paragraph.save.assert_called_once()

    def test_source_authoritative_custom_child_length_rechunks_unchanged_content(self):
        service = IncrementalDocumentSync(
            Document(doc_strategy=normalize_document_strategy(None)),
            {"split": {"child_length": 50}},
            source_authoritative=True,
        )
        remote = prepare_remote_paragraphs([{"title": "Title", "content": "x" * 120}])[0]
        paragraph = Paragraph(
            title="Title",
            content="x" * 120,
            source_hash=remote["source_hash"],
            chunks=["x" * 120],
            origin=ContentOrigin.SYNCED,
        )
        paragraph.save = MagicMock()
        result = MergeResult()

        service._merge_matched(paragraph, remote, result)

        self.assertGreater(len(paragraph.chunks), 1)
        self.assertEqual("".join(paragraph.chunks), paragraph.content)
        self.assertEqual(result.updated_ids, [str(paragraph.id)])

    @patch("knowledge.services.incremental_sync.delete_synced_paragraph_data")
    def test_source_authoritative_deletes_missing_imported_but_not_manual_paragraphs(self, cleanup):
        document = Document()
        service = IncrementalDocumentSync(document, source_authoritative=True)
        synced = Paragraph(origin=ContentOrigin.SYNCED)
        edited = Paragraph(origin=ContentOrigin.SYNCED, local_state=LocalState.MODIFIED)
        manual = Paragraph(origin=ContentOrigin.MANUAL)
        cleanup.return_value = [str(synced.id), str(edited.id)]
        result = MergeResult()

        service._handle_remote_deletes([synced, manual, edited], result)

        cleanup.assert_called_once_with(document.id, [synced.id, edited.id])
        self.assertEqual(result.deleted_ids, cleanup.return_value)
        self.assertEqual(result.disabled_ids, [])
        self.assertEqual(result.conflict_ids, [])

    @patch("knowledge.services.incremental_sync.delete_synced_paragraph_data")
    def test_three_way_policy_still_retains_remote_deleted_paragraphs(self, cleanup):
        synced = Paragraph(origin=ContentOrigin.SYNCED)
        synced.save = MagicMock()
        result = MergeResult()

        IncrementalDocumentSync(Document())._handle_remote_deletes([synced], result)

        cleanup.assert_not_called()
        self.assertFalse(synced.is_active)
        self.assertEqual(synced.sync_state, SyncState.REMOTE_DELETED)
        self.assertEqual(result.disabled_ids, [str(synced.id)])

    @patch("knowledge.services.incremental_sync.delete_synced_paragraph_data")
    @patch("knowledge.services.incremental_sync.Paragraph.objects")
    @patch("knowledge.services.incremental_sync.Document.objects")
    def test_authoritative_empty_snapshot_does_not_delete_existing_content(self, documents, paragraphs, cleanup):
        document = Document()
        documents.select_for_update.return_value.get.return_value = document
        paragraphs.select_for_update.return_value.filter.return_value.order_by.return_value = [
            Paragraph(origin=ContentOrigin.SYNCED),
        ]
        service = IncrementalDocumentSync(document, source_authoritative=True)

        with self.assertRaisesRegex(ValueError, "empty paragraph snapshot"):
            IncrementalDocumentSync.merge.__wrapped__(service, [])

        cleanup.assert_not_called()

    @patch("knowledge.services.incremental_sync.Paragraph.objects")
    @patch("knowledge.services.incremental_sync.Document.objects")
    def test_authoritative_merge_keeps_manual_content_and_saves_new_strategy(self, documents, paragraphs):
        document = Document(knowledge=Knowledge(), doc_strategy=normalize_document_strategy(None), sync_version=1)
        document.save = MagicMock()
        manual = Paragraph(title="Title", content="manual", origin=ContentOrigin.MANUAL)
        manual.save = MagicMock()
        documents.select_for_update.return_value.get.return_value = document
        paragraphs.select_for_update.return_value.filter.return_value.order_by.return_value = [manual]
        created = Paragraph(title="Title", content="remote", origin=ContentOrigin.SYNCED)
        paragraphs.create.return_value = created
        active = paragraphs.filter.return_value.filter.return_value
        active.values_list.return_value = [created.id]
        service = IncrementalDocumentSync(document, {"split": {"child_length": 50}}, source_authoritative=True)
        with patch.object(service, "_reorder"), patch.object(service, "_sync_title_questions"):
            result = IncrementalDocumentSync.merge.__wrapped__(service, [{"title": "Title", "content": "remote"}])

        self.assertEqual(result.created_ids, [str(created.id)])
        self.assertEqual(manual.content, "manual")
        manual.save.assert_not_called()
        paragraphs.filter.return_value.filter.assert_called_once_with(origin=ContentOrigin.SYNCED)
        self.assertEqual(document.doc_strategy["split"]["child_length"], 50)
        self.assertEqual(document.sync_version, 2)

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

    @patch("knowledge.serializers.document.IncrementalDocumentSync")
    @patch("knowledge.serializers.document.process_visual_assets")
    @patch("knowledge.serializers.document.sync_paragraph_assets")
    @patch("knowledge.serializers.document.internalize_web_images", side_effect=lambda content, _knowledge_id: content)
    @patch("knowledge.serializers.document.parse_web_content")
    @patch("knowledge.serializers.document.ListenerManagement")
    @patch("knowledge.serializers.document.QuerySet")
    def test_enabling_visual_strategy_reprocesses_unchanged_source(
        self, query_set, _listener, parse_content, _internalize_images, sync_assets, process_assets, incremental_sync
    ):
        paragraphs = [{"title": "Overview", "content": "![chart](./oss/file/00000000-0000-0000-0000-000000000031)"}]
        old_strategy = normalize_document_strategy(None)
        strategy = normalize_document_strategy(
            {"visual": {"enabled": True, "strategy": "model", "model_id": "00000000-0000-0000-0000-000000000032"}}
        )
        document = Document(
            id="00000000-0000-0000-0000-000000000033",
            knowledge_id="00000000-0000-0000-0000-000000000034",
            name="docs",
            type=KnowledgeType.WEB,
            meta={"source_url": "https://example.com", "selector": "body"},
            doc_strategy=old_strategy,
            source_hash=document_source_hash(prepare_remote_paragraphs(paragraphs)),
            **strategy_hashes(old_strategy),
        )
        paragraph_id = "00000000-0000-0000-0000-000000000035"
        incremental_sync.return_value.merge.return_value = MergeResult(updated_ids=[paragraph_id])
        document_query = MagicMock()
        document_query.filter.return_value.first.return_value = document
        paragraph_query = MagicMock()
        query_set.side_effect = lambda model: document_query if model is Document else paragraph_query
        parse_content.return_value = paragraphs
        assets = [MagicMock()]
        sync_assets.return_value = assets
        serializer = DocumentSerializers.Sync(
            data={
                "knowledge_id": str(document.knowledge_id),
                "document_id": str(document.id),
                "strategy_mode": "custom",
                "doc_strategy": strategy,
            }
        )
        serializer._validated_data = {"strategy_mode": "custom", "doc_strategy": strategy}
        with patch.object(serializer, "is_valid"):
            DocumentSerializers.Sync.sync.__wrapped__(
                serializer, with_embedding=False, response=MagicMock(status=200, content=paragraphs[0]["content"])
            )

        incremental_sync.assert_called_once_with(document, strategy)
        incremental_sync.return_value.merge.assert_called_once_with(paragraphs)
        paragraph_query.filter.assert_any_call(id__in=[paragraph_id])
        process_assets.assert_called_once_with(assets, strategy)


class SyncedParagraphCleanupTests(SimpleTestCase):
    @patch("knowledge.services.document_cleanup.delete_embedding_by_paragraph_ids")
    @patch("knowledge.services.document_cleanup.QuerySet")
    def test_cleanup_is_scoped_and_preserves_shared_problems(self, query_set, delete_vectors):
        paragraph_query, mapping_query, problem_query = MagicMock(), MagicMock(), MagicMock()
        query_set.side_effect = lambda model: {
            Paragraph: paragraph_query,
            ProblemParagraphMapping: mapping_query,
            Problem: problem_query,
        }[model]
        paragraph_query.filter.return_value.values_list.return_value = ["synced-id"]
        removed_mappings, remaining_mappings = MagicMock(), MagicMock()
        mapping_query.filter.side_effect = [removed_mappings, remaining_mappings]
        removed_mappings.values_list.return_value = ["shared-problem", "orphan-problem"]
        remaining_mappings.values_list.return_value = ["shared-problem"]

        result = delete_synced_paragraph_data("doc-id", ["synced-id", "manual-id", "other-doc-id"])

        paragraph_query.filter.assert_called_once_with(
            document_id="doc-id",
            id__in=["synced-id", "manual-id", "other-doc-id"],
            origin=ContentOrigin.SYNCED,
        )
        removed_mappings.delete.assert_called_once()
        problem_query.filter.assert_called_once_with(id__in={"orphan-problem"})
        delete_vectors.assert_called_once_with(["synced-id"])
        paragraph_query.filter.return_value.delete.assert_called_once()
        self.assertEqual(result, ["synced-id"])


class ParagraphFileMigrationTests(SimpleTestCase):
    @patch("knowledge.serializers.paragraph.QuerySet")
    def test_target_document_must_belong_to_target_knowledge(self, query_set):
        source_knowledge_id = "00000000-0000-0000-0000-000000000001"
        target_knowledge_id = "00000000-0000-0000-0000-000000000002"
        source_document_id = "00000000-0000-0000-0000-000000000003"
        target_document_id = "00000000-0000-0000-0000-000000000004"
        knowledge_query = MagicMock()
        knowledge_query.filter.return_value.exists.return_value = True
        document_query = MagicMock()
        document_query.filter.return_value = [
            Document(id=source_document_id, knowledge_id=source_knowledge_id),
            Document(id=target_document_id, knowledge_id=source_knowledge_id),
        ]
        query_set.side_effect = lambda model: {Knowledge: knowledge_query, Document: document_query}[model]
        serializer = ParagraphSerializers.Migrate(
            data={
                "workspace_id": "workspace",
                "knowledge_id": source_knowledge_id,
                "target_knowledge_id": target_knowledge_id,
                "document_id": source_document_id,
                "target_document_id": target_document_id,
                "paragraph_id_list": ["00000000-0000-0000-0000-000000000005"],
            }
        )

        with self.assertRaises(AppApiException):
            serializer.is_valid(raise_exception=True)

    @patch("knowledge.serializers.paragraph.update_document_char_length")
    @patch("knowledge.serializers.paragraph.update_embedding_document_id")
    @patch("knowledge.serializers.paragraph.migrate_paragraph_files")
    @patch("knowledge.serializers.paragraph.Paragraph.objects")
    @patch("knowledge.serializers.paragraph.QuerySet")
    def test_paragraph_migration_moves_files_before_owner_update(
        self, query_set, paragraph_objects, move_files, _update_embedding, _update_char_length
    ):
        knowledge_id = "00000000-0000-0000-0000-000000000001"
        source_document_id = "00000000-0000-0000-0000-000000000002"
        target_document_id = "00000000-0000-0000-0000-000000000003"
        paragraph = Paragraph(id="00000000-0000-0000-0000-000000000004")
        paragraph_list = MagicMock()
        paragraph_list.__iter__.return_value = iter([paragraph])
        paragraph_query = MagicMock()
        paragraph_query.filter.return_value = paragraph_list
        knowledge_query = MagicMock()
        target_knowledge = Knowledge(id=knowledge_id)
        knowledge_query.filter.return_value.first.return_value = target_knowledge
        mapping_query = MagicMock()
        mapping_query.filter.return_value = []
        query_set.side_effect = lambda model: {
            Paragraph: paragraph_query,
            Knowledge: knowledge_query,
            ProblemParagraphMapping: mapping_query,
        }[model]
        paragraph_objects.filter.return_value.__iter__.return_value = iter([])
        serializer = MagicMock(
            data={
                "knowledge_id": knowledge_id,
                "target_knowledge_id": knowledge_id,
                "document_id": source_document_id,
                "target_document_id": target_document_id,
                "paragraph_id_list": [str(paragraph.id)],
            }
        )

        ParagraphSerializers.Migrate.migrate.__wrapped__(serializer, with_valid=False)

        move_files.assert_called_once_with(paragraph_list, target_document_id, target_knowledge)
        paragraph_list.update.assert_called_once_with(document_id=target_document_id)

    @patch.object(Paragraph, "save")
    @patch.object(File, "save", autospec=True)
    @patch("knowledge.services.paragraph_files.File.objects")
    @patch("knowledge.services.paragraph_files.ParagraphAsset.objects")
    def test_document_owned_file_is_copied_with_moved_paragraph(
        self, asset_objects, file_objects, save_file, save_paragraph
    ):
        file_id = "00000000-0000-0000-0000-000000000001"
        paragraph_id = "00000000-0000-0000-0000-000000000002"
        asset_id = "00000000-0000-0000-0000-000000000003"
        source_file = File(
            id=file_id,
            file_name="image.png",
            source_type=FileSourceType.DOCUMENT,
            source_id="old-document",
            meta={"content_type": "image/png", "original_size": 5},
        )
        source_file.get_bytes = MagicMock(return_value=b"image")
        file_objects.filter.return_value = [source_file]
        asset_objects.filter.return_value.values.return_value = [
            {"id": asset_id, "paragraph_id": paragraph_id, "file_id": file_id}
        ]
        paragraph = Paragraph(
            id=paragraph_id,
            knowledge_id="old-knowledge",
            document_id="old-document",
            content=f"![image](./oss/file/{file_id})",
            content_schema=[{"type": "image", "file_id": file_id}],
            source_snapshot={"content": f"![image](./oss/file/{file_id})"},
            chunks=[f"./oss/file/{file_id}"],
        )
        target_knowledge = Knowledge(id="new-knowledge", file_size_limit=1)

        migrate_paragraph_files([paragraph], "new-document", target_knowledge)

        copied, content = save_file.call_args.args
        self.assertEqual(content, b"image")
        self.assertEqual(copied.source_type, FileSourceType.PARAGRAPH)
        self.assertEqual(copied.source_id, paragraph_id)
        self.assertEqual(copied.meta["original_size"], len(content))
        self.assertIn(str(copied.id), paragraph.content)
        self.assertEqual(paragraph.content_schema[0]["file_id"], str(copied.id))
        self.assertIn(str(copied.id), paragraph.source_snapshot["content"])
        self.assertIn(str(copied.id), paragraph.chunks[0])
        save_paragraph.assert_called_once()
        asset_objects.filter.return_value.update.assert_any_call(file_id=str(copied.id))
        asset_objects.filter.return_value.update.assert_any_call(
            document_id="new-document", knowledge_id=target_knowledge.id
        )
        self.assertEqual(source_file.source_id, "old-document")

    @patch.object(Paragraph, "save")
    @patch.object(File, "save", autospec=True)
    @patch("knowledge.services.paragraph_files.File.objects")
    @patch("knowledge.services.paragraph_files.ParagraphAsset.objects")
    def test_same_knowledge_document_move_copies_document_attachment(
        self, asset_objects, file_objects, save_file, save_paragraph
    ):
        file_id = "00000000-0000-0000-0000-000000000001"
        paragraph_id = "00000000-0000-0000-0000-000000000002"
        source_file = File(
            id=file_id,
            file_name="attachment.pdf",
            source_type=FileSourceType.DOCUMENT,
            source_id="old-document",
        )
        source_file.get_bytes = MagicMock(return_value=b"attachment")
        file_objects.filter.return_value = [source_file]
        asset_objects.filter.return_value.values.return_value = []
        paragraph = Paragraph(
            id=paragraph_id,
            knowledge_id="same-knowledge",
            document_id="old-document",
            content=f"[attachment](./oss/file/{file_id})",
        )

        migrate_paragraph_files([paragraph], "new-document", Knowledge(id="same-knowledge"))

        copied = save_file.call_args.args[0]
        self.assertEqual(copied.source_type, FileSourceType.PARAGRAPH)
        self.assertEqual(copied.source_id, paragraph_id)
        self.assertIn(str(copied.id), paragraph.content)
        save_paragraph.assert_called_once()
        asset_objects.filter.return_value.update.assert_called_once_with(
            document_id="new-document", knowledge_id="same-knowledge"
        )

    @patch.object(Paragraph, "save")
    @patch.object(File, "save", autospec=True)
    @patch("knowledge.services.paragraph_files.File.objects")
    @patch("knowledge.services.paragraph_files.ParagraphAsset.objects")
    def test_paragraph_owned_file_keeps_its_id_when_owner_moves(
        self, asset_objects, file_objects, save_file, save_paragraph
    ):
        paragraph_id = "00000000-0000-0000-0000-000000000002"
        file_id = "00000000-0000-0000-0000-000000000001"
        file_objects.filter.return_value = [
            File(id=file_id, source_type=FileSourceType.PARAGRAPH, source_id=paragraph_id, meta={"original_size": 5})
        ]
        asset_objects.filter.return_value.values.return_value = [
            {"id": "asset-id", "paragraph_id": paragraph_id, "file_id": file_id}
        ]
        paragraph = Paragraph(
            id=paragraph_id,
            knowledge_id="old-knowledge",
            document_id="old-document",
            content=f"![image](./oss/file/{file_id})",
        )
        target_knowledge = Knowledge(id="new-knowledge", file_size_limit=1)

        migrate_paragraph_files([paragraph], "new-document", target_knowledge)

        save_file.assert_not_called()
        save_paragraph.assert_not_called()
        self.assertIn(file_id, paragraph.content)
        asset_objects.filter.return_value.update.assert_called_once_with(
            document_id="new-document", knowledge_id=target_knowledge.id
        )

    @patch.object(Paragraph, "save")
    @patch.object(File, "save", autospec=True)
    @patch("knowledge.services.paragraph_files.File.objects")
    @patch("knowledge.services.paragraph_files.ParagraphAsset.objects")
    def test_cross_knowledge_move_checks_target_limit_before_copy(
        self, asset_objects, file_objects, save_file, save_paragraph
    ):
        file_id = "00000000-0000-0000-0000-000000000001"
        file_objects.filter.return_value = [
            File(
                id=file_id,
                source_type=FileSourceType.PARAGRAPH,
                source_id="00000000-0000-0000-0000-000000000002",
                meta={"original_size": 1024 * 1024 + 1},
            )
        ]
        asset_objects.filter.return_value.values.return_value = []
        paragraph = Paragraph(id="00000000-0000-0000-0000-000000000002", knowledge_id="old-knowledge")

        with self.assertRaises(AppApiException):
            migrate_paragraph_files([paragraph], "new-document", Knowledge(id="new-knowledge", file_size_limit=1))

        save_file.assert_not_called()
        save_paragraph.assert_not_called()
        asset_objects.filter.return_value.update.assert_not_called()

    @patch.object(File, "save", autospec=True)
    @patch("knowledge.services.paragraph_files.File.objects")
    @patch("knowledge.services.paragraph_files.ParagraphAsset.objects")
    def test_migration_rejects_file_owned_by_another_resource(self, asset_objects, file_objects, save_file):
        file_id = "00000000-0000-0000-0000-000000000001"
        file_objects.filter.return_value = [File(id=file_id, source_type=FileSourceType.CHAT, source_id="chat-id")]
        asset_objects.filter.return_value.values.return_value = []
        paragraph = Paragraph(
            id="00000000-0000-0000-0000-000000000002",
            knowledge_id="old-knowledge",
            document_id="old-document",
            content=f"[attachment](./oss/file/{file_id})",
        )

        with self.assertRaises(AppApiException):
            migrate_paragraph_files([paragraph], "new-document", Knowledge(id="new-knowledge"))

        save_file.assert_not_called()
        asset_objects.filter.return_value.update.assert_not_called()


class ParagraphAssetTests(SimpleTestCase):
    @patch("knowledge.services.paragraph_assets.Knowledge.objects")
    @patch("knowledge.services.paragraph_assets.File.objects")
    def test_paragraph_image_and_attachment_use_knowledge_limit(self, file_objects, knowledge_objects):
        file_id = "00000000-0000-0000-0000-000000000003"
        file_objects.filter.return_value = [
            MagicMock(spec=["file_size", "meta"], file_size=1, meta={"original_size": 1024 * 1024 + 1})
        ]
        knowledge_objects.filter.return_value.first.return_value = Knowledge(file_size_limit=1)
        contents = [
            f"![image](./oss/file/{file_id})",
            f"[attachment](./oss/file/{file_id})",
            f'<video src="./oss/file/{file_id}"></video>',
        ]

        with self.assertRaises(AppApiException):
            validate_paragraph_file_references("knowledge-id", contents)
        file_objects.filter.assert_called_once_with(id__in={file_id})

        knowledge_objects.filter.return_value.first.return_value = Knowledge(file_size_limit=2)
        validate_paragraph_file_references("knowledge-id", contents)

    @patch(
        "knowledge.serializers.paragraph.validate_paragraph_file_references",
        side_effect=AppApiException(500, "too large"),
    )
    @patch("knowledge.serializers.paragraph.Paragraph.objects")
    def test_manual_paragraph_rejects_oversize_reference_before_saving(self, paragraph_objects, validate_references):
        serializer = MagicMock(
            data={
                "knowledge_id": "00000000-0000-0000-0000-000000000001",
                "document_id": "00000000-0000-0000-0000-000000000002",
            },
        )
        content = "[attachment](./oss/file/00000000-0000-0000-0000-000000000003)"

        with self.assertRaises(AppApiException):
            ParagraphSerializers.Create.save.__wrapped__(serializer, {"content": content}, with_valid=False)
        validate_references.assert_called_once_with(serializer.data["knowledge_id"], [content])
        paragraph_objects.filter.assert_not_called()

    @patch(
        "knowledge.services.paragraph_assets.validate_paragraph_file_references",
        side_effect=AppApiException(500, "too large"),
    )
    @patch("knowledge.services.paragraph_assets.ParagraphAsset.objects")
    def test_document_paragraph_rejects_oversize_reference_before_asset_sync(self, asset_objects, validate_references):
        paragraph = Paragraph(
            id="00000000-0000-0000-0000-000000000001",
            document_id="00000000-0000-0000-0000-000000000002",
            knowledge_id="00000000-0000-0000-0000-000000000003",
            content="![image](./oss/file/00000000-0000-0000-0000-000000000004)",
        )

        with self.assertRaises(AppApiException):
            sync_paragraph_assets.__wrapped__([paragraph])
        validate_references.assert_called_once()
        self.assertEqual(validate_references.call_args.args[0], paragraph.knowledge_id)
        self.assertEqual(list(validate_references.call_args.args[1]), [paragraph.content])
        asset_objects.select_for_update.assert_not_called()

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
            status=KnowledgeSyncStatus.RUNNING,
            knowledge_id="00000000-0000-0000-0000-000000000081",
            create_time=timezone.now(),
            sync_type=KnowledgeSyncType.INCREMENTAL,
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
            if "meta__workflow_sync_log_id" in kwargs:
                result.__iter__.return_value = iter([new_document])
            elif "create_time__lt" in kwargs:
                result.__iter__.return_value = iter([old_document])
            else:
                return document_query
            return result

        document_query.filter.side_effect = filter_documents
        document_query.count.return_value = 1
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

        with patch("knowledge.services.workflow_sync.transaction.atomic"):
            stats = merge_workflow_incremental_snapshot.__wrapped__(sync_log, {"source_scope": "scope"})

        incremental_sync.assert_called_once_with(
            old_document, new_document.doc_strategy, source_authoritative=False, replace_content=False
        )
        delete_documents.assert_called_once_with([str(new_document.id)])
        self.assertEqual(old_document.id, "00000000-0000-0000-0000-000000000082")
        self.assertEqual(stats["skipped_count"], 1)

    @patch("knowledge.services.workflow_sync._delete_workflow_documents")
    @patch("knowledge.services.workflow_sync.QuerySet")
    def test_replace_snapshot_keeps_unmatched_old_documents(self, query_set, delete_documents):
        sync_log = MagicMock(
            status=KnowledgeSyncStatus.RUNNING,
            knowledge_id="00000000-0000-0000-0000-000000000091",
            create_time=timezone.now(),
            sync_type=KnowledgeSyncType.REPLACE,
        )
        old_document = Document(id="00000000-0000-0000-0000-000000000092", name="Old", meta={})
        new_document = Document(id="00000000-0000-0000-0000-000000000093", name="New", meta={})
        document_query = MagicMock()

        def filter_documents(**kwargs):
            result = MagicMock()
            if "meta__workflow_sync_log_id" in kwargs:
                result.__iter__.return_value = iter([new_document])
            elif "create_time__lt" in kwargs:
                result.__iter__.return_value = iter([old_document])
            else:
                return document_query
            return result

        document_query.filter.side_effect = filter_documents
        document_query.count.return_value = 2
        query_set.side_effect = lambda model: document_query if model is Document else MagicMock()

        stats = merge_workflow_incremental_snapshot.__wrapped__(sync_log, {"source_scope": "scope"})

        delete_documents.assert_not_called()
        self.assertEqual(stats["deleted_count"], 0)
        self.assertEqual(stats["synced_count"], 1)

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
