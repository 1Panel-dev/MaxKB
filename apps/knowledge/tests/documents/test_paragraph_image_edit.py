"""Created and edited paragraph images are reflected in assets without losing the original image."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

from django.test import SimpleTestCase
from rest_framework import serializers

from knowledge.models import (
    AssetProcessStatus,
    ContentOrigin,
    Document,
    DocumentResourceType,
    File,
    LocalState,
    Paragraph,
    ParagraphAsset,
    SourceType,
)
from knowledge.serializers.paragraph import ParagraphSerializers
from knowledge.services.document_strategy import normalize_document_strategy, strategy_hashes
from knowledge.services.paragraph_assets import process_visual_assets, sync_edited_paragraph_assets


class ParagraphImageEditTests(SimpleTestCase):
    def setUp(self):
        self.knowledge_id = uuid4()
        self.strategy = normalize_document_strategy(
            {"visual": {"enabled": True, "strategy": "model", "model_id": str(uuid4())}}
        )
        self.document = Document(
            id=uuid4(),
            knowledge_id=self.knowledge_id,
            resource_type=DocumentResourceType.IMAGE,
            doc_strategy=self.strategy,
        )
        self.original = File(id=uuid4(), file_name="original.png", sha256_hash="original-hash")
        self.uploaded = File(id=uuid4(), file_name="added.png", sha256_hash="added-hash")
        self.files = [self.original, self.uploaded]
        self.file_queries = []
        self.content = f"edited description\n![](./oss/file/{self.uploaded.id})"
        self.paragraph = Paragraph(
            id=uuid4(),
            document=self.document,
            knowledge_id=self.knowledge_id,
            content=self.content,
            origin=ContentOrigin.MANUAL,
        )
        self.original_asset = ParagraphAsset(
            id=uuid4(),
            document=self.document,
            paragraph=self.paragraph,
            knowledge_id=self.knowledge_id,
            file=self.original,
            origin=ContentOrigin.MANUAL,
            source_asset_key="standalone:original-hash",
            source_hash=self.original.sha256_hash,
            position=1,
            caption="original caption",
            ocr_text="original text",
            description="original description",
            hit_num=7,
            process_status=AssetProcessStatus.SUCCESS,
            visual_strategy_hash=strategy_hashes(self.strategy)["visual_strategy_hash"],
        )
        self.assets = [self.original_asset]
        self.enterContext(patch("django.db.transaction.Atomic.__enter__"))
        self.enterContext(patch("django.db.transaction.Atomic.__exit__", return_value=False))
        self.enterContext(patch("knowledge.services.paragraph_assets.validate_paragraph_file_references"))
        self.enterContext(patch.object(ParagraphAsset, "save", autospec=True, side_effect=self.save_asset))
        self.enterContext(patch.object(Paragraph, "save", autospec=True))
        asset_objects = self.enterContext(patch("knowledge.services.paragraph_assets.ParagraphAsset.objects"))
        asset_objects.filter.side_effect = self.asset_query
        asset_objects.select_for_update.return_value.select_related.return_value.filter.return_value.order_by.return_value = self.assets
        self.file_objects = self.enterContext(patch("knowledge.services.paragraph_assets.File.objects"))
        self.file_objects.filter.side_effect = self.file_query
        self.embedding_objects = self.enterContext(patch("knowledge.services.paragraph_assets.Embedding.objects"))
        paragraphs = self.enterContext(patch("knowledge.services.paragraph_assets.Paragraph.objects"))
        paragraphs.select_for_update.return_value.filter.return_value.first.return_value = self.paragraph

    def save_asset(self, asset, *args, **kwargs):
        asset.document = self.document
        asset.paragraph = self.paragraph
        if not any(previous.id == asset.id for previous in self.assets):
            self.assets.append(asset)

    def asset_query(self, **filters):
        def matches(asset, conditions):
            for name, value in conditions.items():
                if name.endswith("__in"):
                    if str(getattr(asset, name[:-4])) not in {str(item) for item in value}:
                        return False
                elif str(getattr(asset, name)) != str(value):
                    return False
            return True

        return self.asset_query_result([asset for asset in self.assets if matches(asset, filters)], matches)

    def asset_query_result(self, assets, matches):
        query = MagicMock()
        query.values.return_value = [
            {
                "id": asset.id,
                "file_id": asset.file_id,
                "source_hash": asset.source_hash,
                "visual_strategy_hash": asset.visual_strategy_hash,
            }
            for asset in assets
        ]
        query.exclude.side_effect = lambda **conditions: self.asset_query_result(
            [asset for asset in assets if not matches(asset, conditions)], matches
        )

        def delete():
            deleted_ids = {asset.id for asset in assets}
            self.assets[:] = [asset for asset in self.assets if asset.id not in deleted_ids]

        query.delete.side_effect = delete
        return query

    def file_query(self, **filters):
        query = MagicMock()
        query.first.return_value = next((file for file in self.files if str(file.id) == str(filters.get("id"))), None)
        self.file_queries.append(query)
        return query

    def test_new_image_is_added_after_the_standalone_original_without_losing_recognition(self):
        with patch("knowledge.services.paragraph_assets.resolve_visual_processor") as resolve:
            sync_edited_paragraph_assets(self.paragraph)
        self.assertEqual([asset.file_id for asset in self.assets], [self.original.id, self.uploaded.id])
        self.assertEqual([asset.position for asset in self.assets], [1, 2])
        images = [block for block in self.paragraph.content_schema if block["type"] == "image"]
        self.assertEqual([block["file_id"] for block in images], [str(self.original.id), str(self.uploaded.id)])
        self.assertEqual(self.original_asset.description, "original description")
        self.assertEqual(self.original_asset.process_status, AssetProcessStatus.SUCCESS)
        self.assertEqual(self.original_asset.hit_num, 7)
        self.assertEqual(self.assets[1].process_status, AssetProcessStatus.PENDING)
        self.assertEqual(self.paragraph.local_state, LocalState.MODIFIED)
        self.assertEqual(self.paragraph.content, self.content)
        resolve.assert_not_called()

    def test_repeated_save_reuses_the_added_asset_and_its_completed_recognition(self):
        sync_edited_paragraph_assets(self.paragraph)
        asset = self.assets[1]
        asset_id = asset.id
        asset.process_status = AssetProcessStatus.SUCCESS
        asset.description = "recognized added image"
        sync_edited_paragraph_assets(self.paragraph)
        self.assertEqual(len(self.assets), 2)
        self.assertEqual(self.assets[1].id, asset_id)
        self.assertEqual(self.assets[1].process_status, AssetProcessStatus.SUCCESS)
        self.assertEqual(self.assets[1].description, "recognized added image")

    def test_image_recognition_updates_schema_without_replacing_user_edited_content(self):
        sync_edited_paragraph_assets(self.paragraph)
        process_visual_assets(
            [self.assets[1]],
            self.strategy,
            processor=MagicMock(return_value={"caption": "new caption", "description": "new description"}),
        )
        self.assertEqual(self.paragraph.content, self.content)
        images = [block for block in self.paragraph.content_schema if block["type"] == "image"]
        self.assertEqual(images[1]["description"], "new description")
        self.assertEqual(images[0]["description"], "original description")

    def test_disabled_enhancement_still_records_new_images_without_overwriting_content(self):
        self.document.doc_strategy = normalize_document_strategy(None)
        # The original result was already processed with this strategy and must be retained.
        self.original_asset.visual_strategy_hash = strategy_hashes(self.document.doc_strategy)["visual_strategy_hash"]
        sync_edited_paragraph_assets(self.paragraph)
        self.assertEqual(self.assets[1].process_status, AssetProcessStatus.SKIPPED)
        self.assertEqual(self.paragraph.content, self.content)
        self.assertEqual(self.original_asset.description, "original description")

    def test_regular_document_edits_also_record_uploaded_images(self):
        self.document.resource_type = DocumentResourceType.DOCUMENT
        self.assets.clear()
        sync_edited_paragraph_assets(self.paragraph)
        self.assertEqual(len(self.assets), 1)
        self.assertEqual(self.assets[0].file_id, self.uploaded.id)
        self.assertEqual(self.paragraph.content, self.content)
        self.assertEqual(self.paragraph.local_state, LocalState.CLEAN)

    def test_replacing_an_inline_image_clears_the_old_images_recognition(self):
        sync_edited_paragraph_assets(self.paragraph)
        added_asset = self.assets[1]
        added_asset.ocr_text = "stale text"
        added_asset.description = "stale description"
        added_asset.meta = {"visual_edited_fields": ["description"]}
        replacement = File(id=uuid4(), sha256_hash="replacement-hash")
        self.files.append(replacement)
        self.paragraph.content = f"edited again\n![](./oss/file/{replacement.id})"
        sync_edited_paragraph_assets(self.paragraph)
        self.assertEqual(len(self.assets), 2)
        self.assertEqual(added_asset.file_id, replacement.id)
        self.assertEqual(added_asset.ocr_text, "")
        self.assertEqual(added_asset.description, "")
        self.assertNotIn("visual_edited_fields", added_asset.meta)
        self.assertEqual(added_asset.process_status, AssetProcessStatus.PENDING)

    def test_removing_all_uploaded_images_keeps_only_the_original_and_cleans_image_embeddings(self):
        sync_edited_paragraph_assets(self.paragraph)
        removed_id = str(self.assets[1].id)
        self.paragraph.content = "edited description"
        sync_edited_paragraph_assets(self.paragraph)

        self.assertEqual(self.assets, [self.original_asset])
        images = [block for block in self.paragraph.content_schema if block["type"] == "image"]
        self.assertEqual([block["asset_id"] for block in images], [str(self.original_asset.id)])
        self.assertEqual(self.original_asset.description, "original description")
        self.assertEqual(self.original_asset.hit_num, 7)
        self.embedding_objects.filter.assert_called_once_with(
            paragraph_id=self.paragraph.id, source_type=SourceType.IMAGE, source_id__in={removed_id}
        )
        self.embedding_objects.filter.return_value.delete.assert_called_once_with()

        sync_edited_paragraph_assets(self.paragraph)
        self.assertEqual(self.assets, [self.original_asset])
        self.embedding_objects.filter.assert_called_once()

    def assert_removing_first_upload_preserves_second(self, same_bytes=False):
        second = File(id=uuid4(), sha256_hash=self.uploaded.sha256_hash if same_bytes else "second-hash")
        self.files.append(second)
        self.paragraph.content += f"\n![](./oss/file/{second.id})"
        sync_edited_paragraph_assets(self.paragraph)
        removed_id = str(self.assets[1].id)
        remaining = self.assets[2]
        remaining.description = "keep this recognition"
        remaining.hit_num = 9
        remaining.process_status = AssetProcessStatus.SUCCESS

        self.paragraph.content = f"edited description\n![](./oss/file/{second.id})"
        sync_edited_paragraph_assets(self.paragraph)

        self.assertEqual(self.assets, [self.original_asset, remaining])
        self.assertEqual(remaining.file_id, second.id)
        self.assertEqual(remaining.position, 2)
        self.assertEqual(remaining.description, "keep this recognition")
        self.assertEqual(remaining.hit_num, 9)
        self.assertEqual(remaining.process_status, AssetProcessStatus.SUCCESS)
        images = [block for block in self.paragraph.content_schema if block["type"] == "image"]
        self.assertEqual([block["asset_id"] for block in images], [str(self.original_asset.id), str(remaining.id)])
        self.embedding_objects.filter.assert_called_once_with(
            paragraph_id=self.paragraph.id, source_type=SourceType.IMAGE, source_id__in={removed_id}
        )

    def test_removing_one_upload_preserves_the_other_images_identity_and_recognition(self):
        self.assert_removing_first_upload_preserves_second()

    def test_removing_one_of_two_identical_uploads_preserves_the_remaining_file_identity(self):
        self.assert_removing_first_upload_preserves_second(same_bytes=True)

    def test_clearing_regular_paragraph_removes_assets_but_preserves_shared_files_and_other_paragraphs(self):
        self.document.resource_type = DocumentResourceType.DOCUMENT
        self.assets.clear()
        sync_edited_paragraph_assets(self.paragraph)
        removed_id = str(self.assets[0].id)
        shared_asset = ParagraphAsset(
            id=uuid4(),
            document=self.document,
            paragraph_id=uuid4(),
            file=self.uploaded,
            origin=ContentOrigin.MANUAL,
        )
        self.assets.append(shared_asset)

        self.paragraph.content = ""
        sync_edited_paragraph_assets(self.paragraph)

        self.assertEqual(self.assets, [shared_asset])
        self.assertEqual(self.paragraph.content_schema, [{"type": "text", "content": ""}])
        self.assertEqual(self.files, [self.original, self.uploaded])
        for query in self.file_queries:
            query.delete.assert_not_called()
        self.embedding_objects.filter.assert_called_once_with(
            paragraph_id=self.paragraph.id, source_type=SourceType.IMAGE, source_id__in={removed_id}
        )

    def test_removing_inline_reference_to_original_file_preserves_the_standalone_asset(self):
        self.paragraph.content = f"![](./oss/file/{self.original.id})"
        sync_edited_paragraph_assets(self.paragraph)
        self.assertEqual(len(self.assets), 2)
        self.paragraph.content = ""
        sync_edited_paragraph_assets(self.paragraph)

        self.assertEqual(self.assets, [self.original_asset])
        self.assertEqual(self.paragraph.content, "")
        images = [block for block in self.paragraph.content_schema if block["type"] == "image"]
        self.assertEqual([block["asset_id"] for block in images], [str(self.original_asset.id)])

    def test_explicit_edit_also_removes_unreferenced_assets_from_synced_paragraphs(self):
        self.paragraph.origin = ContentOrigin.SYNCED
        self.original_asset.origin = ContentOrigin.SYNCED
        sync_edited_paragraph_assets(self.paragraph)
        self.paragraph.content = "edited description"
        sync_edited_paragraph_assets(self.paragraph)

        self.assertEqual(self.assets, [self.original_asset])
        self.assertEqual(len([block for block in self.paragraph.content_schema if block["type"] == "image"]), 1)

    def edit(self, payload):
        operation = ParagraphSerializers.Operate(
            data={
                "workspace_id": "default",
                "knowledge_id": str(self.knowledge_id),
                "document_id": str(self.document.id),
                "paragraph_id": str(self.paragraph.id),
            }
        )
        serializers.Serializer.is_valid(operation, raise_exception=True)
        with (
            patch.object(operation, "is_valid"),
            patch.object(
                operation,
                "one",
                side_effect=lambda: {
                    "id": str(self.paragraph.id),
                    "content_schema": self.paragraph.content_schema,
                    "assets": [
                        {"id": str(asset.id), "file_id": str(asset.file_id)}
                        for asset in self.assets
                        if asset.paragraph_id == self.paragraph.id
                    ],
                },
            ),
            patch("knowledge.serializers.paragraph.QuerySet") as query,
            patch("knowledge.serializers.paragraph.validate_paragraph_file_references"),
            patch("knowledge.serializers.paragraph.update_document_char_length"),
            patch("knowledge.serializers.paragraph.get_embedding_model_id_by_knowledge_id"),
            patch("knowledge.serializers.paragraph.embedding_by_paragraph"),
            patch(
                "knowledge.serializers.paragraph.sync_edited_paragraph_assets", wraps=sync_edited_paragraph_assets
            ) as sync,
        ):
            query.return_value.get.return_value = self.paragraph
            result = operation.edit(payload)
            return result, sync

    def test_edit_response_contains_the_updated_image_schema(self):
        result, sync = self.edit({"content": self.content})
        sync.assert_called_once_with(self.paragraph)
        self.assertEqual(len([block for block in result["content_schema"] if block["type"] == "image"]), 2)

    def test_edit_response_removes_deleted_images_from_assets_and_schema(self):
        sync_edited_paragraph_assets(self.paragraph)
        result, _ = self.edit({"content": "edited description"})

        self.assertEqual(result["assets"], [{"id": str(self.original_asset.id), "file_id": str(self.original.id)}])
        images = [block for block in result["content_schema"] if block["type"] == "image"]
        self.assertEqual([block["asset_id"] for block in images], [str(self.original_asset.id)])

    def test_title_only_edit_does_not_resync_or_reprocess_images(self):
        _, sync = self.edit({"title": "renamed"})
        sync.assert_not_called()
        self.assertEqual(len(self.assets), 1)

    def create(self):
        self.document.resource_type = DocumentResourceType.DOCUMENT
        self.assets.clear()
        operation = ParagraphSerializers.Create(
            data={
                "workspace_id": "default",
                "knowledge_id": str(self.knowledge_id),
                "document_id": str(self.document.id),
            }
        )
        with (
            patch.object(
                operation,
                "get_paragraph_problem_model",
                return_value={"paragraph": self.paragraph, "problem_paragraph_object_list": []},
            ),
            patch.object(ParagraphSerializers.AdjustPosition, "adjust_position"),
            patch.object(
                ParagraphSerializers.Operate,
                "one",
                side_effect=lambda **kwargs: {
                    "id": str(self.paragraph.id),
                    "content": self.paragraph.content,
                    "content_schema": self.paragraph.content_schema,
                    "assets": [{"id": str(asset.id), "file_id": str(asset.file_id)} for asset in self.assets],
                },
            ),
            patch("knowledge.serializers.paragraph.QuerySet"),
            patch("knowledge.serializers.paragraph.validate_paragraph_file_references"),
            patch("knowledge.serializers.paragraph.update_document_char_length"),
        ):
            return operation.save({"content": self.paragraph.content}, with_embedding=False)

    def test_manual_creation_returns_image_assets_without_waiting_for_embedding(self):
        result = self.create()

        self.assertEqual(len(self.assets), 1)
        asset = self.assets[0]
        self.assertEqual(asset.file_id, self.uploaded.id)
        self.assertEqual(asset.paragraph_id, self.paragraph.id)
        self.assertEqual(asset.document_id, self.document.id)
        self.assertEqual(asset.knowledge_id, self.knowledge_id)
        self.assertEqual(asset.origin, ContentOrigin.MANUAL)
        self.assertEqual(asset.process_status, AssetProcessStatus.PENDING)
        self.assertEqual(result["assets"], [{"id": str(asset.id), "file_id": str(self.uploaded.id)}])
        image = next(block for block in result["content_schema"] if block["type"] == "image")
        self.assertEqual(image["asset_id"], str(asset.id))
        self.assertEqual(result["content"], self.content)

    def test_manual_creation_records_images_when_visual_enhancement_is_disabled(self):
        self.document.doc_strategy = normalize_document_strategy(None)
        result = self.create()

        self.assertEqual(len(result["assets"]), 1)
        self.assertEqual(self.assets[0].process_status, AssetProcessStatus.SKIPPED)
        self.assertEqual(result["content"], self.content)

    def test_manual_text_creation_does_not_create_image_assets(self):
        self.paragraph.content = "text only"
        result = self.create()

        self.assertEqual(result["assets"], [])
        self.assertEqual(result["content_schema"], [{"type": "text", "content": "text only"}])
