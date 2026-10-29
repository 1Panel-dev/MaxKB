from unittest.mock import MagicMock, patch

from common.exception.app_exception import AppApiException
from django.test import SimpleTestCase
from django.utils import timezone
from knowledge.models import (
    AssetProcessStatus,
    Document,
    FileSourceType,
    Knowledge,
    KnowledgeSyncStatus,
    KnowledgeSyncType,
    Paragraph,
    ParagraphAsset,
    ProblemParagraphMapping,
)
from knowledge.services.incremental_sync import MergeResult
from knowledge.services.paragraph_assets import (
    embed_paragraph_assets,
    process_visual_assets,
    resolve_visual_processor,
)
from knowledge.services.workflow_sync import (
    merge_workflow_incremental_snapshot,
    workflow_document_identity,
)


class WorkflowDocumentIdentityTests(SimpleTestCase):
    def test_stable_source_metadata_takes_priority_over_document_name(self):
        first = Document(name="Old name", meta={"source_key": "source-1"})
        renamed = Document(name="New name", meta={"source_key": "source-1"})

        self.assertEqual(workflow_document_identity(first), workflow_document_identity(renamed))

    @patch("knowledge.services.workflow_sync._delete_workflow_documents")
    @patch("knowledge.services.workflow_sync.defer_visual_assets")
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

    @patch("knowledge.services.workflow_sync.schedule_workflow_document_embedding")
    @patch("knowledge.services.workflow_sync._delete_workflow_documents")
    @patch("knowledge.services.workflow_sync.QuerySet")
    def test_replace_snapshot_keeps_unmatched_old_documents(self, query_set, delete_documents, schedule_embedding):
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
        schedule_embedding.assert_called_once_with([new_document.id], sync_log.knowledge_id)
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
        embedding_model.embed_documents.return_value = [[0.1, 0.2], [0.3, 0.4]]

        count = embed_paragraph_assets([asset.paragraph_id], embedding_model)

        self.assertEqual(count, 2)
        embedding_model.embed_documents.assert_called_once_with(["chart\nrevenue 100\nan upward trend", "chart"])
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
