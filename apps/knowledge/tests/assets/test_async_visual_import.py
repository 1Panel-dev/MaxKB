"""Document import defers inline image enhancement to the committed embedding job."""

from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

from django.test import SimpleTestCase
from rest_framework import serializers

from knowledge.models import AssetProcessStatus, KnowledgeType, ParagraphAsset, SyncState
from knowledge.serializers.document import DocumentSerializers
from knowledge.services.document_strategy import normalize_document_strategy, strategy_hashes
from knowledge.services.paragraph_assets import defer_visual_assets, embed_paragraph_assets, process_visual_assets


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
        self.process = self.enterContext(patch("knowledge.services.paragraph_assets.process_visual_assets"))
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

    def test_other_document_types_also_defer_visual_processing(self):
        for knowledge_type in (KnowledgeType.WEB, KnowledgeType.LARK, KnowledgeType.WORKFLOW, KnowledgeType.YUQUE):
            with self.subTest(knowledge_type=knowledge_type):
                self.document.type = knowledge_type
                creator = DocumentSerializers.Create(data=self.scope)
                serializers.Serializer.is_valid(creator, raise_exception=True)

                creator.save({"name": "guide"}, with_valid=False)

                self.process.assert_not_called()
                self.assertEqual(self.asset.process_status, AssetProcessStatus.PENDING)


class VisualImportCommitTests(SimpleTestCase):
    def test_embedding_job_is_published_only_after_commit(self):
        document_id, knowledge_id, model_id = (str(uuid4()) for _ in range(3))
        state_list = ["0", "3"]
        operation = DocumentSerializers.Operate(data={"knowledge_id": knowledge_id, "document_id": document_id})
        serializers.Serializer.is_valid(operation, raise_exception=True)
        with (
            patch.object(operation, "is_valid"),
            patch("knowledge.serializers.document.QuerySet") as query,
            patch("knowledge.serializers.document.ListenerManagement") as listener,
            patch("knowledge.serializers.document.transaction.atomic", return_value=nullcontext()) as atomic,
            patch("knowledge.serializers.document.transaction.on_commit") as on_commit,
            patch("knowledge.serializers.document.embedding_by_document.delay") as delay,
        ):
            query.return_value.filter.return_value.first.return_value = SimpleNamespace(embedding_model_id=model_id)
            query.return_value.select_for_update.return_value.filter.return_value.exists.return_value = True

            operation.refresh(state_list)

            delay.assert_not_called()
            atomic.assert_not_called()
            listener.update_status.assert_not_called()
            query.return_value.select_for_update.assert_not_called()
            on_commit.assert_called_once()
            on_commit.call_args.args[0]()
            atomic.assert_called_once_with()
            query.return_value.select_for_update.return_value.filter.assert_called_once_with(id=document_id)
            listener.update_status.assert_called()
            delay.assert_called_once_with(document_id, model_id, state_list)


class VisualAssetDeferralTests(SimpleTestCase):
    def setUp(self):
        self.strategy = normalize_document_strategy(
            {"visual": {"enabled": True, "strategy": "model", "model_id": str(uuid4())}}
        )
        self.asset = MagicMock(
            id=uuid4(),
            paragraph_id=uuid4(),
            process_status=AssetProcessStatus.SUCCESS,
            process_error="old error",
            description="previous image description",
        )
        self.process = self.enterContext(patch("knowledge.services.paragraph_assets.process_visual_assets"))
        self.on_commit = self.enterContext(patch("knowledge.services.paragraph_assets.transaction.on_commit"))
        self.delay = self.enterContext(patch("knowledge.tasks.process_paragraph_visual_assets.delay"))

    def test_changed_assets_are_pending_even_if_previously_processed(self):
        for status in (AssetProcessStatus.SUCCESS, AssetProcessStatus.FAILURE, AssetProcessStatus.SKIPPED):
            with self.subTest(status=status):
                self.asset.process_status = status

                defer_visual_assets([self.asset], self.strategy)

                self.assertEqual(self.asset.process_status, AssetProcessStatus.PENDING)
                self.assertEqual(self.asset.process_error, "")
                self.assertEqual(self.asset.description, "previous image description")
                self.assertEqual(
                    self.asset.visual_strategy_hash, strategy_hashes(self.strategy)["visual_strategy_hash"]
                )
                self.process.assert_not_called()
                self.delay.assert_not_called()
                self.on_commit.assert_not_called()

    def test_tool_recognition_is_also_deferred(self):
        strategy = {"visual": {"enabled": True, "strategy": "tool", "tool_id": str(uuid4())}}

        defer_visual_assets([self.asset], strategy)

        self.assertEqual(self.asset.process_status, AssetProcessStatus.PENDING)
        self.process.assert_not_called()

    def test_sync_without_embedding_recognizes_only_after_commit(self):
        other = MagicMock(id=uuid4(), paragraph_id=self.asset.paragraph_id)

        defer_visual_assets([self.asset, other], self.strategy, schedule=True)

        self.process.assert_not_called()
        self.delay.assert_not_called()
        self.on_commit.assert_called_once()
        self.assertTrue(self.on_commit.call_args.kwargs["robust"])
        self.on_commit.call_args.args[0]()
        self.delay.assert_called_once_with([str(self.asset.paragraph_id)])

    def test_queue_failure_marks_assets_failed_without_losing_the_sync(self):
        self.delay.side_effect = RuntimeError("broker unavailable")
        assets = self.enterContext(patch("knowledge.services.paragraph_assets.ParagraphAsset.objects.filter"))

        defer_visual_assets([self.asset], self.strategy, schedule=True)
        self.on_commit.call_args.args[0]()

        assets.assert_called_once_with(id__in=[str(self.asset.id)], process_status=AssetProcessStatus.PENDING)
        assets.return_value.update.assert_called_once_with(
            process_status=AssetProcessStatus.FAILURE, process_error="broker unavailable"
        )

    def test_empty_snapshot_never_schedules_recognition(self):
        defer_visual_assets([], self.strategy, schedule=True)

        self.process.assert_not_called()
        self.on_commit.assert_not_called()


class PendingVisualEmbeddingTests(SimpleTestCase):
    def setUp(self):
        self.enterContext(patch("django.db.transaction.Atomic.__enter__"))
        self.enterContext(patch("django.db.transaction.Atomic.__exit__", return_value=False))
        paragraphs = self.enterContext(patch("knowledge.services.paragraph_assets.Paragraph.objects.select_for_update"))
        paragraphs.return_value.filter.return_value.exists.return_value = True
        self.current_assets = self.enterContext(
            patch("knowledge.services.paragraph_assets.ParagraphAsset.objects.select_for_update")
        )
        self.current_assets.return_value.filter.return_value.exists.return_value = True
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

        self.assertEqual(self.embed(), 2)

        self.resolve.assert_called_once_with(asset.document.doc_strategy["visual"], "workspace-1")
        self.processor.assert_called_once_with(asset, asset.document.doc_strategy["visual"])
        self.embedding_model.embed_documents.assert_called_once_with(["chart\nrevenue 100\nrecognized chart", "chart"])
        self.assertEqual(asset.process_status, AssetProcessStatus.SUCCESS)
        self.write_description.assert_called_once_with(asset)
        self.assertEqual(self.bulk_create.call_args.args[0][0].source_id, str(asset.id))

    def test_reembedding_completed_images_does_not_call_visual_model_again(self):
        self.asset()

        self.embed()
        self.embed()

        self.processor.assert_called_once()

    def test_changed_strategy_reprocesses_an_existing_successful_asset_in_worker(self):
        asset = self.asset()
        self.embed()
        self.processor.reset_mock()
        strategy = normalize_document_strategy(
            {"visual": {"enabled": True, "strategy": "model", "model_id": str(uuid4())}}
        )
        asset.document.doc_strategy = strategy

        defer_visual_assets([asset], strategy)
        self.processor.assert_not_called()
        self.embed()

        self.processor.assert_called_once_with(asset, strategy["visual"])
        self.assertEqual(asset.process_status, AssetProcessStatus.SUCCESS)
        self.assertEqual(asset.visual_strategy_hash, strategy_hashes(strategy)["visual_strategy_hash"])

    def test_replaced_or_deleted_image_discards_the_inflight_recognition_result(self):
        asset = self.asset()
        asset.source_hash = "original-image"
        asset.visual_strategy_hash = "original-strategy"
        self.current_assets.return_value.filter.return_value.exists.return_value = False

        process_visual_assets([asset], asset.document.doc_strategy, processor=self.processor, guard_snapshot=True)

        asset.save.assert_not_called()
        self.write_description.assert_not_called()
        snapshot = self.current_assets.return_value.filter.call_args.kwargs
        self.assertEqual(snapshot["source_hash"], "original-image")
        self.assertEqual(snapshot["visual_strategy_hash"], "original-strategy")
        self.assertEqual(snapshot["paragraph_id"], asset.paragraph_id)
        self.assertEqual(snapshot["position"], asset.position)

    def test_success_is_saved_with_matching_snapshot_before_writing_paragraph_result(self):
        asset = self.asset()

        process_visual_assets([asset], asset.document.doc_strategy, processor=self.processor, guard_snapshot=True)

        asset.save.assert_called_once()
        self.write_description.assert_called_once_with(asset)
        self.assertEqual(
            self.current_assets.return_value.filter.call_args.kwargs["process_status"], AssetProcessStatus.PENDING
        )

    def test_failure_of_one_image_does_not_prevent_remaining_image_indexing(self):
        first, second = self.asset(), self.asset()
        second.document_id, second.document = first.document_id, first.document
        self.processor.side_effect = [RuntimeError("vision unavailable"), {"description": "second chart"}]

        self.assertEqual(self.embed(), 3)

        self.assertEqual(first.process_status, AssetProcessStatus.FAILURE)
        self.assertEqual(first.description, "chart")
        self.assertEqual(first.process_error, "vision unavailable")
        self.assertEqual(second.process_status, AssetProcessStatus.SUCCESS)
        self.embedding_model.embed_documents.assert_called_once_with(["chart\nchart", "chart\nsecond chart", "chart"])

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
