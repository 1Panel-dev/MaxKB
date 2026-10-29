"""Short image subjects remain searchable alongside detailed visual descriptions."""

import os
from unittest import skipUnless
from unittest.mock import MagicMock, patch
from uuid import uuid4

from common.exception.app_exception import AppApiException
from django.test import SimpleTestCase
from models_provider.impl.aliyun_bai_lian_model_provider.model.embedding import AliyunBaiLianEmbedding
from models_provider.tests.image_helpers import image_data_url

from knowledge.models import AssetProcessStatus, File, Paragraph, ParagraphAsset, SourceType
from knowledge.services.paragraph_assets import embed_paragraph_assets


class ImageCaptionEmbeddingTests(SimpleTestCase):
    def setUp(self):
        self.assets = []
        query = self.enterContext(patch("knowledge.services.paragraph_assets.ParagraphAsset.objects.select_related"))
        query.return_value.filter.return_value.order_by.return_value = self.assets
        self.bulk_create = self.enterContext(patch("knowledge.services.paragraph_assets.Embedding.objects.bulk_create"))
        self.model = MagicMock()
        self.model.supports_image_embedding.return_value = False
        self.model.embed_documents.side_effect = lambda texts: [[float(len(text)), 1.0] for text in texts]

    def asset(self, caption="古风女性肖像", description="一位女子穿着汉服，佩戴花饰，背景是街道和灯笼。", **kwargs):
        paragraph = Paragraph(id=uuid4(), knowledge_id=uuid4(), document_id=uuid4(), is_active=False)
        asset = ParagraphAsset(
            id=uuid4(),
            paragraph=paragraph,
            knowledge_id=paragraph.knowledge_id,
            document_id=paragraph.document_id,
            file=File(id=uuid4(), file_name="portrait.png"),
            caption=caption,
            description=description,
            position=len(self.assets) + 1,
            process_status=AssetProcessStatus.SUCCESS,
            **kwargs,
        )
        self.assets.append(asset)
        return asset

    def embed(self):
        return embed_paragraph_assets([asset.paragraph_id for asset in self.assets], self.model)

    def test_short_subject_and_full_details_have_independent_vectors_for_the_same_asset(self):
        asset = self.asset(ocr_text="摄影作品")

        self.assertEqual(self.embed(), 2)

        full_text = f"{asset.caption}\n{asset.ocr_text}\n{asset.description}"
        self.model.embed_documents.assert_called_once_with([full_text, asset.caption])
        description, caption = self.bulk_create.call_args.args[0]
        self.assertEqual(description.meta["content_type"], "image_description")
        self.assertEqual(caption.meta["content_type"], "image_caption")
        self.assertEqual(caption.embedding, [float(len(asset.caption)), 1.0])
        self.assertNotEqual(caption.embedding, description.embedding)
        for row in (description, caption):
            self.assertEqual(row.source_type, SourceType.IMAGE)
            self.assertEqual(row.source_id, str(asset.id))
            self.assertEqual(row.paragraph_id, asset.paragraph_id)
            self.assertEqual(row.document_id, asset.document_id)
            self.assertEqual(row.knowledge_id, asset.knowledge_id)
            self.assertFalse(row.is_active)
            self.assertEqual(row.meta["unit_type"], "text")
            self.assertEqual(row.meta["asset_id"], str(asset.id))

    def test_filename_and_empty_captions_do_not_gain_extra_retrieval_vectors(self):
        for caption in ("", "  ", "image.png", "photo.JPG", "a photo.webp", "图片.svg", "portrait.png"):
            with self.subTest(caption=caption):
                self.assets.clear()
                self.asset(caption=caption)
                self.assertEqual(self.embed(), 1)
                self.assertEqual(len(self.model.embed_documents.call_args.args[0]), 1)

    def test_filename_without_extension_does_not_become_a_subject_vector(self):
        asset = self.asset(caption="IMG_001")
        asset.file.file_name = asset.caption

        self.assertEqual(self.embed(), 1)

    def test_caption_only_and_repeated_caption_do_not_gain_duplicate_vectors(self):
        for description in ("", "古风女性肖像", " 古风女性肖像 "):
            with self.subTest(description=description):
                self.assets.clear()
                self.asset(description=description)
                self.assertEqual(self.embed(), 1)

    def test_caption_can_be_combined_with_ocr_without_a_description(self):
        asset = self.asset(description="", ocr_text="摄影作品")

        self.assertEqual(self.embed(), 2)
        self.model.embed_documents.assert_called_once_with([f"{asset.caption}\n摄影作品", asset.caption])

    def test_more_than_twenty_units_are_batched_without_losing_asset_associations(self):
        for index in range(11):
            self.asset(caption=f"人物肖像 {index}")

        self.assertEqual(self.embed(), 22)

        self.assertEqual([len(call.args[0]) for call in self.model.embed_documents.call_args_list], [10, 10, 2])
        rows = self.bulk_create.call_args.args[0]
        self.assertEqual([row.source_id for row in rows], [str(asset.id) for asset in self.assets for _ in range(2)])
        self.assertEqual(len({row.id for row in rows}), 22)

    def test_incomplete_later_batch_does_not_persist_partial_units(self):
        for _ in range(6):
            self.asset()
        self.model.embed_documents.side_effect = [[[0.1, 0.2]] * 10, [[0.3, 0.4]]]

        with self.assertRaises(AppApiException):
            self.embed()

        self.bulk_create.assert_not_called()

    def test_image_vectors_still_reference_the_correct_asset_after_adding_captions(self):
        self.asset()
        self.asset(caption="仰望的黑猫", description="黑猫坐在灰色地面上，抬头看着镜头。")
        self.model.supports_image_embedding.return_value = True
        self.model.embed_images.return_value = [[0.3, 0.4], [0.5, 0.6]]
        with patch("knowledge.services.paragraph_assets._image_data_url", side_effect=["first-image", "second-image"]):
            self.assertEqual(self.embed(), 6)

        self.model.embed_images.assert_called_once_with(["first-image", "second-image"])
        image_rows = [row for row in self.bulk_create.call_args.args[0] if row.meta["unit_type"] == "image"]
        self.assertEqual([row.source_id for row in image_rows], [str(asset.id) for asset in self.assets])
        self.assertEqual([row.embedding for row in image_rows], [[0.3, 0.4], [0.5, 0.6]])

    def test_empty_assets_do_not_call_the_text_model(self):
        self.asset(caption="", description="")

        self.assertEqual(self.embed(), 0)
        self.model.embed_documents.assert_not_called()
        self.bulk_create.assert_not_called()

    @skipUnless(os.environ.get("ALIYUN_EMBEDDING_TEST_URL"), "Start the local Aliyun Postman simulation")
    def test_caption_batches_and_images_pass_through_the_real_provider_http_client(self):
        import dashscope

        self.addCleanup(setattr, dashscope, "api_key", dashscope.api_key)
        self.addCleanup(setattr, dashscope, "base_http_api_url", dashscope.base_http_api_url)
        self.model = AliyunBaiLianEmbedding(
            "test-key", "qwen3-vl-embedding", os.environ["ALIYUN_EMBEDDING_TEST_URL"], {"dimension": 256}
        )
        for index in range(11):
            self.asset(caption=f"人物肖像 {index}")
        with patch("knowledge.services.paragraph_assets._image_data_url", return_value=image_data_url((32, 32))):
            self.assertEqual(self.embed(), 33)

        rows = self.bulk_create.call_args.args[0]
        self.assertEqual([row.embedding[0] for row in rows[:22]], list(range(10)) * 2 + [0, 1])
        self.assertEqual([row.meta["content_type"] for row in rows[:22]], ["image_description", "image_caption"] * 11)
        self.assertEqual([row.source_id for row in rows[22:]], [str(asset.id) for asset in self.assets])
        self.assertTrue(all(len(row.embedding) == 256 for row in rows))
