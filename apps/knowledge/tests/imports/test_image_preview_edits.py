"""Image preview drafts survive import together with their question associations."""

from uuid import uuid4
from unittest.mock import patch

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from common.exception.app_exception import AppApiException
from knowledge.models import (
    AssetProcessStatus,
    Document,
    File,
    FileSourceType,
    Knowledge,
    LocalState,
    Paragraph,
    ParagraphAsset,
    Problem,
    ProblemParagraphMapping,
)
from knowledge.serializers.image_document import ImageDocumentSerializers
from knowledge.services.document_strategy import normalize_document_strategy
from knowledge.services.paragraph_assets import _write_asset_description


class ImagePreviewEditImportTests(TestCase):
    def setUp(self):
        self.user_id = str(uuid4())
        self.knowledge = Knowledge.objects.create(name="Images", workspace_id="default")
        self.file = File(
            file_name="image.png",
            meta={
                "user_id": self.user_id,
                "image_preview": {
                    "knowledge_id": str(self.knowledge.id),
                    "caption": "识别内容",
                    "process_status": AssetProcessStatus.SUCCESS,
                    "doc_strategy": normalize_document_strategy({"index": {"title_as_question": True}}),
                },
            },
        )
        File.objects.bulk_create([self.file])
        self.refresh = self.enterContext(
            patch("knowledge.serializers.image_document.DocumentSerializers.Operate.refresh")
        )

    def import_file(self, *, content=None, preview_list=None):
        payload = {"file_id_list": [str(self.file.id)]}
        if content is not None:
            payload["preview_list"] = [{"source_file_id": str(self.file.id), "content": content}]
        elif preview_list is not None:
            payload["preview_list"] = preview_list
        return ImageDocumentSerializers.Preview(
            data={
                "workspace_id": "default",
                "knowledge_id": str(self.knowledge.id),
                "user_id": self.user_id,
            }
        ).batch_create(payload)

    def test_import_persists_edits_and_reuses_questions_only_in_current_knowledge(self):
        existing = Problem.objects.create(knowledge=self.knowledge, content="已有问题")
        other = Knowledge.objects.create(name="Other", workspace_id="default")
        foreign = Problem.objects.create(knowledge=other, content="新问题")
        self.import_file(
            content=[
                {
                    "title": "编辑标题",
                    "content": "编辑后的正文",
                    "problem_list": [
                        {"content": "已有问题"},
                        {"content": "新问题"},
                        {"content": "新问题"},
                        {"content": "编辑标题"},
                    ],
                }
            ]
        )
        paragraph = Paragraph.objects.get(knowledge=self.knowledge)
        document = paragraph.document
        self.assertEqual(paragraph.title, "编辑标题")
        self.assertEqual(paragraph.content, "编辑后的正文")
        self.assertEqual(document.char_length, len(paragraph.content))
        self.assertEqual(paragraph.local_state, LocalState.MODIFIED)
        mappings = ProblemParagraphMapping.objects.filter(paragraph=paragraph)
        self.assertEqual(mappings.count(), 3)
        self.assertEqual(set(mappings.values_list("problem__content", flat=True)), {"已有问题", "新问题", "编辑标题"})
        self.assertTrue(mappings.filter(problem=existing).exists())
        self.assertFalse(mappings.filter(problem=foreign).exists())
        self.assertEqual(ParagraphAsset.objects.get(paragraph=paragraph).file_id, self.file.id)
        self.file.refresh_from_db()
        self.assertEqual(self.file.source_type, FileSourceType.DOCUMENT)
        self.assertEqual(self.file.source_id, str(document.id))
        self.refresh.assert_called_once_with(with_valid=False)

        asset = ParagraphAsset.objects.get(paragraph=paragraph)
        asset.description = "重新识别的内容"
        _write_asset_description(asset)
        paragraph.refresh_from_db()
        self.assertEqual(paragraph.content, "编辑后的正文")

    def test_legacy_file_id_import_preserves_generated_content(self):
        self.import_file()
        paragraph = Paragraph.objects.get(knowledge=self.knowledge)
        self.assertEqual(paragraph.content, "识别内容")
        self.assertEqual(paragraph.local_state, LocalState.CLEAN)

    def test_draft_ids_must_match_the_imported_files(self):
        draft = {"source_file_id": str(self.file.id), "content": [{"content": "编辑内容"}]}
        for previews in ([], [draft, draft], [{**draft, "source_file_id": str(uuid4())}]):
            with self.subTest(previews=previews), self.assertRaises((ValidationError, AppApiException)):
                self.import_file(preview_list=previews)
        self.assertFalse(Document.objects.filter(knowledge=self.knowledge).exists())
        self.refresh.assert_not_called()

    def test_invalid_draft_questions_are_rejected_before_creating_documents(self):
        for content in ("", "q" * 257):
            with self.subTest(content=content), self.assertRaises(ValidationError):
                self.import_file(content=[{"content": "正文", "problem_list": [{"content": content}]}])
        self.assertFalse(Document.objects.filter(knowledge=self.knowledge).exists())

    def test_drafts_do_not_bypass_upload_ownership(self):
        File.objects.filter(id=self.file.id).update(meta={**self.file.meta, "user_id": str(uuid4())})
        with self.assertRaises(AppApiException):
            self.import_file(content=[{"content": "正文", "problem_list": [{"content": "问题"}]}])
        self.assertFalse(Document.objects.filter(knowledge=self.knowledge).exists())
