"""Visual enhancement writes inline image descriptions back to document Markdown."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

from django.test import SimpleTestCase

from knowledge.models import AssetProcessStatus, Document, KnowledgeType, LocalState, Paragraph, ParagraphAsset
from knowledge.services.paragraph_assets import (
    _write_asset_description,
    paragraph_content_schema,
    process_visual_assets,
)


class InlineVisualDescriptionTests(SimpleTestCase):
    def setUp(self):
        self.enterContext(patch("django.db.transaction.Atomic.__enter__"))
        self.enterContext(patch("django.db.transaction.Atomic.__exit__", return_value=False))
        self.file_id = uuid4()
        self.url = f'./oss/file/{self.file_id}?download=1 "原图"'
        self.original = f"正文\n![image]({self.url})\n后续文字"
        self.document = Document(id=uuid4(), source_hash="original-source-hash")
        self.paragraph = Paragraph(
            id=uuid4(),
            document=self.document,
            title="标题",
            content=self.original,
            chunks=[self.original],
            content_schema=paragraph_content_schema(self.original),
            source_hash="original-paragraph-hash",
        )
        self.paragraph.save = MagicMock()
        self.asset = ParagraphAsset(
            id=uuid4(),
            paragraph=self.paragraph,
            document=self.document,
            file_id=self.file_id,
            position=1,
            caption="简短标题",
            ocr_text="识别文字",
            description="图片中的流程从上传文档开始。",
            process_status=AssetProcessStatus.SUCCESS,
        )
        self.asset.save = MagicMock()
        paragraphs = self.enterContext(patch("knowledge.services.paragraph_assets.Paragraph.objects.select_for_update"))
        paragraphs.return_value.filter.return_value.first.return_value = self.paragraph
        self.documents = self.enterContext(patch("knowledge.services.paragraph_assets.Document.objects.filter"))

    def test_model_and_tool_results_replace_only_the_image_alt_text(self):
        for strategy in ("model", "tool"):
            with self.subTest(strategy=strategy):
                self.paragraph.content = self.original
                self.paragraph.content_schema = paragraph_content_schema(self.original)
                process_visual_assets(
                    [self.asset],
                    {"visual": {"enabled": True, "strategy": strategy, f"{strategy}_id": str(uuid4())}},
                    processor=lambda *_: {"description": "识别后的图片描述"},
                )

                expected = f"正文\n![识别后的图片描述]({self.url})\n后续文字"
                self.assertEqual(self.paragraph.content, expected)
                self.assertIn("识别后的图片描述", "".join(self.paragraph.chunks))
                image = self.paragraph.content_schema[1]
                self.assertEqual(image["raw"], f"![识别后的图片描述]({self.url})")
                self.assertEqual(image["description"], "识别后的图片描述")
                self.assertEqual(image["caption"], "简短标题")
                self.assertEqual(image["ocr_text"], "识别文字")
                self.assertEqual(self.paragraph.source_hash, "original-paragraph-hash")
                self.assertEqual(self.document.source_hash, "original-source-hash")
                self.assertIn("content", self.paragraph.save.call_args.kwargs["update_fields"])
                self.assertIn("chunks", self.paragraph.save.call_args.kwargs["update_fields"])
                length_update = self.documents.return_value.update.call_args.kwargs
                self.assertEqual(set(length_update), {"char_length"})
                self.assertEqual(length_update["char_length"].rhs.value, len(expected) - len(self.original))

    def test_repeated_images_are_updated_by_position_without_losing_other_descriptions(self):
        self.paragraph.content = f"![first]({self.url})\n![second]({self.url})"
        self.paragraph.content_schema = paragraph_content_schema(self.paragraph.content)
        self.asset.position = 2
        self.asset.description = "第二张图"

        _write_asset_description(self.asset)
        self.assertEqual(self.paragraph.content, f"![first]({self.url})\n![第二张图]({self.url})")

        self.asset.position = 1
        self.asset.description = "第一张图"
        _write_asset_description(self.asset)
        self.assertEqual(self.paragraph.content, f"![第一张图]({self.url})\n![第二张图]({self.url})")

    def test_special_characters_and_newlines_remain_a_parseable_image_on_reprocessing(self):
        self.asset.description = "第一行 [图表]\\路径\n第二行"

        _write_asset_description(self.asset)

        expected = f"正文\n![第一行 \\[图表\\]\\\\路径 第二行]({self.url})\n后续文字"
        self.assertEqual(self.paragraph.content, expected)
        schema = paragraph_content_schema(self.paragraph.content)
        self.assertEqual([block["type"] for block in schema], ["text", "image", "text"])
        self.assertEqual(schema[1]["file_id"], str(self.file_id))

        self.asset.description = "更新后的描述"
        _write_asset_description(self.asset)
        self.assertEqual(self.paragraph.content, f"正文\n![更新后的描述]({self.url})\n后续文字")

    def test_failure_or_disabled_enhancement_preserves_existing_markdown_and_chunks(self):
        for enabled in (True, False):
            with self.subTest(enabled=enabled):
                process_visual_assets(
                    [self.asset],
                    {"visual": {"enabled": enabled, "model_id": str(uuid4())}},
                    processor=MagicMock(side_effect=RuntimeError("recognition failed")),
                )
                self.assertEqual(self.paragraph.content, self.original)
                self.assertEqual(self.paragraph.chunks, [self.original])
                self.documents.assert_not_called()

    def test_blank_description_preserves_existing_alt_text(self):
        self.asset.description = " \n "

        _write_asset_description(self.asset)

        self.assertEqual(self.paragraph.content, self.original)
        self.documents.assert_not_called()

    def test_external_knowledge_sources_keep_their_original_markdown(self):
        for knowledge_type in (KnowledgeType.WEB, KnowledgeType.LARK, KnowledgeType.WORKFLOW):
            with self.subTest(knowledge_type=knowledge_type):
                self.document.type = knowledge_type

                _write_asset_description(self.asset)

                self.assertEqual(self.paragraph.content, self.original)
                self.assertEqual(self.paragraph.content_schema[1]["description"], self.asset.description)
                self.documents.assert_not_called()

    def test_repeating_the_same_result_does_not_change_the_character_count_again(self):
        _write_asset_description(self.asset)
        content = self.paragraph.content
        self.documents.reset_mock()

        _write_asset_description(self.asset)

        self.assertEqual(self.paragraph.content, content)
        self.documents.assert_not_called()

    def test_missing_schema_is_rebuilt_from_the_current_content(self):
        self.paragraph.content_schema = []

        _write_asset_description(self.asset)

        self.assertEqual(self.paragraph.content, f"正文\n![{self.asset.description}]({self.url})\n后续文字")
        self.assertEqual(self.paragraph.content_schema[1]["description"], self.asset.description)

    def test_changed_or_removed_image_is_not_replaced_by_an_old_result(self):
        for content in ("图片已移除", f"![new](./oss/file/{uuid4()})"):
            with self.subTest(content=content):
                self.paragraph.content = content

                _write_asset_description(self.asset)

                self.assertEqual(self.paragraph.content, content)
                self.documents.assert_not_called()

    def test_manual_text_edits_around_an_inline_image_are_preserved(self):
        self.paragraph.content = f"手动编辑的文字 ![image]({self.url}) 最新结尾"
        self.paragraph.local_state = LocalState.MODIFIED

        _write_asset_description(self.asset)

        self.assertEqual(self.paragraph.content, f"手动编辑的文字 ![{self.asset.description}]({self.url}) 最新结尾")
        self.assertEqual(self.paragraph.local_state, LocalState.MODIFIED)
