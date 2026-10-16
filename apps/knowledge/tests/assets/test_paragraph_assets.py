from unittest.mock import MagicMock, patch

from common.exception.app_exception import AppApiException
from django.test import SimpleTestCase
from knowledge.models import (
    ContentOrigin,
    Knowledge,
    Paragraph,
    SyncState,
)
from knowledge.serializers.paragraph import ParagraphSerializers
from knowledge.services.paragraph_assets import (
    paragraph_asset_source_key,
    paragraph_content_schema,
    sync_paragraph_assets,
    validate_paragraph_file_references,
)
from knowledge.web_assets import _cache_web_image, internalize_web_images


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
