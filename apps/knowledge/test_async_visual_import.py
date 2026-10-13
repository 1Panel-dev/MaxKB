"""Document import defers inline image enhancement to the committed embedding job."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

from django.test import SimpleTestCase
from rest_framework import serializers

from knowledge.models import AssetProcessStatus, KnowledgeType, ParagraphAsset, SyncState
from knowledge.serializers.document import DocumentSerializers
from knowledge.services.document_strategy import normalize_document_strategy
from knowledge.services.paragraph_assets import embed_paragraph_assets


class AsyncVisualImportTests(SimpleTestCase):
    def setUp(self):
        self.scope = {"workspace_id": "default", "knowledge_id": str(uuid4())}
        self.document = MagicMock(id=uuid4(), type=KnowledgeType.BASE)
        self.document.doc_strategy = normalize_document_strategy(
            {"visual": {"enabled": True, "strategy": "model", "model_id": str(uuid4())}}
        )
        self.paragraph = MagicMock(document_id=self.document.id, content="![chart](./oss/file/image-id)")
        self.asset = MagicMock(process_status=AssetProcessStatus.PENDING)
        model_data = {
            "document": self.document,
            "paragraph_model_list": [self.paragraph],
            "problem_paragraph_object_list": [],
        }
        self.enterContext(patch("django.db.transaction.Atomic.__enter__"))
        self.enterContext(patch("django.db.transaction.Atomic.__exit__", return_value=False))
        self.enterContext(patch("knowledge.serializers.document.DocumentInstanceSerializer"))
        self.enterContext(
            patch.object(DocumentSerializers.Create, "get_document_paragraph_model", return_value=model_data)
        )
        self.enterContext(patch("knowledge.serializers.document.Paragraph.objects"))
        self.query = self.enterContext(patch("knowledge.serializers.document.QuerySet"))
        self.query.return_value.filter.return_value.__iter__.return_value = [self.paragraph]
        problems = self.enterContext(patch("knowledge.serializers.document.ProblemParagraphManage"))
        problems.return_value.to_problem_model_list.return_value = ([], [])
        self.enterContext(patch("knowledge.serializers.document.IncrementalDocumentSync"))
        self.enterContext(patch("knowledge.serializers.document.bulk_create_in_batches"))
        self.sync_assets = self.enterContext(
            patch("knowledge.serializers.document.sync_paragraph_assets", return_value=[self.asset])
        )
        self.process = self.enterContext(patch("knowledge.serializers.document.process_visual_assets"))
        self.operation = self.enterContext(patch.object(DocumentSerializers, "Operate"))
        self.result = {"id": str(self.document.id)}
        self.operation.return_value.one.return_value = self.result
        self.enterContext(patch("knowledge.serializers.document.native_search", return_value=[self.result]))
        self.enterContext(patch("knowledge.serializers.document.get_file_content", return_value=""))

    def test_single_creation_returns_without_invoking_visual_model(self):
        creator = DocumentSerializers.Create(data=self.scope)
        serializers.Serializer.is_valid(creator, raise_exception=True)

        self.assertEqual(creator.save({"name": "guide.pdf"}, with_valid=False), self.result)

        self.sync_assets.assert_called_once()
        self.process.assert_not_called()
        self.assertEqual(self.asset.process_status, AssetProcessStatus.PENDING)
        self.operation.return_value.refresh.assert_called_once()

    def test_batch_import_returns_without_invoking_visual_model(self):
        batch = DocumentSerializers.Batch(data=self.scope)
        serializers.Serializer.is_valid(batch, raise_exception=True)
        self.enterContext(patch.object(batch, "link_file"))

        self.assertEqual(batch.batch_save([{"name": "guide.pdf"}], with_valid=False), [self.result])

        self.sync_assets.assert_called_once()
        self.process.assert_not_called()
        self.assertEqual(self.asset.process_status, AssetProcessStatus.PENDING)
        self.operation.return_value.refresh.assert_called_once()

    def test_disabled_visual_strategy_still_marks_assets_skipped_during_import(self):
        self.document.doc_strategy = normalize_document_strategy(None)
        creator = DocumentSerializers.Create(data=self.scope)
        serializers.Serializer.is_valid(creator, raise_exception=True)

        creator.save({"name": "guide.pdf"}, with_valid=False)

        self.process.assert_called_once_with([self.asset], self.document.doc_strategy)

    def test_external_document_creation_preserves_synchronous_visual_processing(self):
        self.document.type = KnowledgeType.WEB
        creator = DocumentSerializers.Create(data=self.scope)
        serializers.Serializer.is_valid(creator, raise_exception=True)

        creator.save({"name": "guide"}, with_valid=False)

        self.process.assert_called_once_with([self.asset], self.document.doc_strategy)


class VisualImportCommitTests(SimpleTestCase):
    def test_embedding_job_is_published_only_after_commit(self):
        document_id, knowledge_id, model_id = (str(uuid4()) for _ in range(3))
        operation = DocumentSerializers.Operate(data={"knowledge_id": knowledge_id, "document_id": document_id})
        serializers.Serializer.is_valid(operation, raise_exception=True)
        with (
            patch.object(operation, "is_valid"),
            patch("knowledge.serializers.document.QuerySet") as query,
            patch("knowledge.serializers.document.ListenerManagement"),
            patch("knowledge.serializers.document.transaction.on_commit") as on_commit,
            patch("knowledge.serializers.document.embedding_by_document.delay") as delay,
        ):
            query.return_value.filter.return_value.first.return_value = SimpleNamespace(embedding_model_id=model_id)

            operation.refresh()

            delay.assert_not_called()
            on_commit.assert_called_once()
            on_commit.call_args.args[0]()
            self.assertEqual(delay.call_args.args[:2], (document_id, model_id))


class PendingVisualEmbeddingTests(SimpleTestCase):
    def setUp(self):
        self.query = self.enterContext(
            patch("knowledge.services.paragraph_assets.ParagraphAsset.objects.select_related")
        )
        self.assets = []
        self.query.return_value.filter.return_value.order_by.return_value = self.assets
        self.bulk_create = self.enterContext(patch("knowledge.services.paragraph_assets.Embedding.objects.bulk_create"))
        self.write_description = self.enterContext(
            patch("knowledge.services.paragraph_assets._write_asset_description")
        )
        self.resolve = self.enterContext(patch("knowledge.services.paragraph_assets.resolve_visual_processor"))
        self.processor = self.resolve.return_value
        self.processor.return_value = {"description": "recognized chart", "ocr_text": "revenue 100"}
        self.embedding_model = MagicMock()
        self.embedding_model.supports_image_embedding.return_value = False
        self.embedding_model.embed_documents.side_effect = lambda texts: [[0.1, 0.2] for _ in texts]

    def asset(self, status=AssetProcessStatus.PENDING):
        asset = MagicMock(spec=ParagraphAsset)
        asset.id, asset.knowledge_id, asset.document_id, asset.paragraph_id = (uuid4() for _ in range(4))
        asset.position = 1
        asset.caption, asset.description, asset.ocr_text, asset.meta = "chart", "", "", {}
        asset.process_status = status
        asset.paragraph = SimpleNamespace(is_active=True)
        asset.document = SimpleNamespace(
            doc_strategy=normalize_document_strategy(
                {"visual": {"enabled": True, "strategy": "model", "model_id": str(uuid4())}}
            )
        )
        asset.knowledge = SimpleNamespace(workspace_id="workspace-1")
        self.assets.append(asset)
        return asset

    def embed(self):
        return embed_paragraph_assets([asset.paragraph_id for asset in self.assets], self.embedding_model)

    def test_pending_image_is_recognized_before_its_description_is_embedded(self):
        asset = self.asset()

        self.assertEqual(self.embed(), 1)

        self.resolve.assert_called_once_with(asset.document.doc_strategy["visual"], "workspace-1")
        self.processor.assert_called_once_with(asset, asset.document.doc_strategy["visual"])
        self.embedding_model.embed_documents.assert_called_once_with(["chart\nrevenue 100\nrecognized chart"])
        self.assertEqual(asset.process_status, AssetProcessStatus.SUCCESS)
        self.write_description.assert_called_once_with(asset)
        self.assertEqual(self.bulk_create.call_args.args[0][0].source_id, str(asset.id))

    def test_reembedding_completed_images_does_not_call_visual_model_again(self):
        self.asset()

        self.embed()
        self.embed()

        self.processor.assert_called_once()

    def test_failure_of_one_image_does_not_prevent_remaining_image_indexing(self):
        first, second = self.asset(), self.asset()
        second.document_id, second.document = first.document_id, first.document
        self.processor.side_effect = [RuntimeError("vision unavailable"), {"description": "second chart"}]

        self.assertEqual(self.embed(), 2)

        self.assertEqual(first.process_status, AssetProcessStatus.FAILURE)
        self.assertEqual(first.description, "chart")
        self.assertEqual(first.process_error, "vision unavailable")
        self.assertEqual(second.process_status, AssetProcessStatus.SUCCESS)
        self.embedding_model.embed_documents.assert_called_once_with(["chart\nchart", "chart\nsecond chart"])

    def test_each_document_uses_its_own_strategy_and_workspace(self):
        first, second = self.asset(), self.asset()
        second.knowledge.workspace_id = "workspace-2"

        self.embed()

        self.assertEqual(self.resolve.call_args_list[0].args, (first.document.doc_strategy["visual"], "workspace-1"))
        self.assertEqual(self.resolve.call_args_list[1].args, (second.document.doc_strategy["visual"], "workspace-2"))

    def test_completed_failed_and_disabled_images_are_not_reprocessed(self):
        for status in (AssetProcessStatus.SUCCESS, AssetProcessStatus.FAILURE, AssetProcessStatus.SKIPPED):
            self.asset(status)

        self.embed()

        self.resolve.assert_not_called()

    def test_no_assets_never_resolves_a_visual_model(self):
        self.assertEqual(self.embed(), 0)

        self.resolve.assert_not_called()
        self.embedding_model.embed_documents.assert_not_called()
        self.query.return_value.filter.assert_called_once_with(paragraph_id__in=[], sync_state=SyncState.ACTIVE)
