from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from knowledge.models import (
    ContentOrigin,
    Document,
    Knowledge,
    KnowledgeSyncStatus,
    KnowledgeType,
    LocalState,
    Paragraph,
    SyncState,
)
from knowledge.serializers.document import (
    DocumentSerializers,
)
from knowledge.services.document_strategy import (
    document_source_hash,
    normalize_document_strategy,
    strategy_hashes,
)
from knowledge.services.incremental_sync import IncrementalDocumentSync, MergeResult, prepare_remote_paragraphs
from knowledge.task.sync import (
    sync_replace_web_knowledge,
)


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

        def handler_factory(_knowledge_id, _user_id, _strategy, _sync_type, successful_urls, stats, **_kwargs):
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

        def handler_factory(_knowledge_id, _user_id, _strategy, _sync_type, success_set, _stats, **_kwargs):
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
        document_query.filter.return_value.__iter__.return_value = [
            SimpleNamespace(id="document-id", meta={"source_url": "https://example.com"})
        ]
        file_query = MagicMock()
        query_set.side_effect = lambda model: document_query if model is Document else file_query

        def cleanup(document_ids):
            events.append("cleanup")
            return document_ids

        delete_document_data.side_effect = cleanup

        def prepare(*_args, prepared_documents):
            prepared_documents.append({"name": "new"})
            return MagicMock()

        _get_save_handler.side_effect = prepare
        fork_manage.return_value.fork.side_effect = lambda *_args: events.append("crawl")

        with patch("knowledge.task.sync.DocumentSerializers.Create"):
            sync_replace_web_knowledge.run("knowledge-id", "user-id", "https://example.com", "body", {}, "complete")

        delete_document_data.assert_called_once_with(["document-id"])
        fork_manage.return_value.fork.assert_called_once()
        self.assertEqual(events, ["crawl", "cleanup"])


class IncrementalSyncTests(SimpleTestCase):
    def setUp(self):
        super().setUp()
        atomic_patch = patch("knowledge.serializers.document.transaction.atomic", return_value=nullcontext())
        atomic_patch.start()
        self.addCleanup(atomic_patch.stop)

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
    @patch("knowledge.serializers.document.defer_visual_assets")
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
    @patch("knowledge.serializers.document.defer_visual_assets")
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
        process_assets.assert_called_once_with(assets, strategy, schedule=True)
