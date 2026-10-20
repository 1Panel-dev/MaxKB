from io import BytesIO
from unittest.mock import MagicMock, patch

from common.exception.app_exception import AppApiException, AppUnauthorizedFailed
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from django.utils.translation import override
from knowledge.models import (
    ContentOrigin,
    Document,
    DocumentResourceType,
    File,
    FileSourceType,
    Knowledge,
    KnowledgeType,
    KnowledgeWorkflow,
    Paragraph,
    Problem,
    ProblemParagraphMapping,
)
from knowledge.models.knowledge import on_delete_paragraph
from knowledge.serializers.document import (
    DocumentBatchRefreshSerializer,
    DocumentSerializers,
)
from knowledge.serializers.image_document import ImagePreviewUpdateRequest
from knowledge.serializers.knowledge_workflow import KnowledgeWorkflowActionSerializer
from knowledge.serializers.paragraph import ParagraphSerializers
from knowledge.services import validate_knowledge_file_size
from knowledge.services.document_cleanup import delete_synced_paragraph_data
from knowledge.services.document_strategy import (
    document_source_hash,
    normalize_document_strategy,
)
from knowledge.services.image_documents import ImageDocumentService
from knowledge.services.paragraph_files import migrate_paragraph_files
from oss.serializers.file import FileSerializer, _auth_system, _knowledge_id_for_file_source
from PIL import Image


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


class ImageDocumentTests(SimpleTestCase):
    @patch("knowledge.serializers.document.DocumentSerializers.Operate")
    @patch("knowledge.serializers.document.QuerySet")
    def test_batch_refresh_accepts_images_and_preserves_the_document_default(self, query_set, operate):
        knowledge_id = "00000000-0000-0000-0000-000000000037"
        document_id = "00000000-0000-0000-0000-000000000038"
        query_set.return_value.filter.return_value.exists.return_value = True
        query_set.return_value.filter.return_value.values_list.return_value = [document_id]
        for resource_type in (None, DocumentResourceType.DOCUMENT, DocumentResourceType.IMAGE):
            with self.subTest(resource_type=resource_type):
                operate.reset_mock()
                payload = {"id_list": [document_id], "state_list": ["0", "1"]}
                if resource_type is not None:
                    payload["resource_type"] = resource_type
                request = DocumentBatchRefreshSerializer(data=payload)
                self.assertTrue(request.is_valid(), request.errors)
                serializer = DocumentSerializers.Batch(data={"workspace_id": "default", "knowledge_id": knowledge_id})

                serializer.batch_refresh(request.validated_data)

                query_set.return_value.filter.assert_any_call(
                    id__in=[document_id],
                    knowledge_id=knowledge_id,
                    resource_type=resource_type or DocumentResourceType.DOCUMENT,
                )
                operate.assert_called_once_with(data={"knowledge_id": knowledge_id, "document_id": document_id})
                operate.return_value.refresh.assert_called_once_with(payload["state_list"])

    @patch("knowledge.serializers.document.DocumentSerializers.Operate")
    @patch("knowledge.serializers.document.QuerySet")
    def test_batch_refresh_rejects_resource_mismatch_before_enqueuing(self, query_set, operate):
        query_set.return_value.filter.return_value.exists.return_value = True
        query_set.return_value.filter.return_value.values_list.return_value = []
        serializer = DocumentSerializers.Batch(
            data={"workspace_id": "default", "knowledge_id": "00000000-0000-0000-0000-000000000037"}
        )

        with self.assertRaises(AppApiException):
            serializer.batch_refresh(
                {
                    "id_list": ["00000000-0000-0000-0000-000000000038"],
                    "state_list": ["0", "1"],
                    "resource_type": DocumentResourceType.IMAGE,
                }
            )

        operate.assert_not_called()

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

        previews = service.create_previews.__wrapped__(service, [upload])

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
    def test_documents_must_belong_to_their_knowledge_in_each_language(self, query_set):
        source_knowledge_id = "00000000-0000-0000-0000-000000000001"
        target_knowledge_id = "00000000-0000-0000-0000-000000000002"
        source_document_id = "00000000-0000-0000-0000-000000000003"
        target_document_id = "00000000-0000-0000-0000-000000000004"
        knowledge_query = MagicMock()
        knowledge_query.filter.return_value.exists.return_value = True
        document_query = MagicMock()
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

        for language in ("en-us", "zh-cn", "zh-hant"):
            for invalid_document_id in (source_document_id, target_document_id):
                with self.subTest(language=language, invalid_document_id=invalid_document_id), override(language):
                    document_query.filter.return_value = [
                        Document(
                            id=source_document_id,
                            knowledge_id=(
                                target_knowledge_id
                                if invalid_document_id == source_document_id
                                else source_knowledge_id
                            ),
                        ),
                        Document(
                            id=target_document_id,
                            knowledge_id=(
                                source_knowledge_id
                                if invalid_document_id == target_document_id
                                else target_knowledge_id
                            ),
                        ),
                    ]
                    with self.assertRaises(AppApiException) as raised:
                        serializer.is_valid(raise_exception=True)
                    self.assertEqual(raised.exception.code, 5000)
                    self.assertIn(invalid_document_id, str(raised.exception.message))
                    self.assertIn(
                        {"en-us": "document id", "zh-cn": "文档ID", "zh-hant": "文檔ID"}[language],
                        str(raised.exception.message),
                    )

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
