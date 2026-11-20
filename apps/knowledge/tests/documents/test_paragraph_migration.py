from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from time import monotonic, sleep

from common.exception.app_exception import AppApiException
from django.db import connection, connections, transaction
from django.test import TestCase, TransactionTestCase
from django.utils.translation import gettext as _

from knowledge.models import ContentOrigin, Document, Embedding, File, FileSourceType, Knowledge, KnowledgeFolder
from knowledge.models import KnowledgeType, LocalState, Paragraph
from knowledge.models import Problem, ProblemParagraphMapping, SourceType
from knowledge.serializers.paragraph import ParagraphSerializers
from knowledge.services.incremental_sync import IncrementalDocumentSync, prepare_remote_paragraphs
from knowledge.services.paragraph_assets import sync_paragraph_assets


class ParagraphMigrationTests(TestCase):
    def setUp(self):
        self.knowledge = Knowledge.objects.create(name="Source")
        self.source = Document.objects.create(knowledge=self.knowledge, name="Illustrations.docx", char_length=0)

    def imported_paragraph(self, document, text, *, with_image=False):
        if with_image:
            image = File(
                file_name="chart.png", source_type=FileSourceType.KNOWLEDGE, source_id=str(document.knowledge_id)
            )
            File.objects.bulk_create([image])
            text += f" ![chart](./oss/file/{image.id})"
        remote = prepare_remote_paragraphs([{"content": text}])[0]
        paragraph = Paragraph.objects.create(
            knowledge_id=document.knowledge_id,
            document=document,
            origin=ContentOrigin.SYNCED,
            source_snapshot={"title": "", "content": text},
            **remote,
        )
        sync_paragraph_assets([paragraph])
        return paragraph

    def migrate(self, target, *paragraphs):
        ParagraphSerializers.Migrate(
            data={
                "workspace_id": "default",
                "knowledge_id": str(self.knowledge.id),
                "document_id": str(self.source.id),
                "target_knowledge_id": str(target.knowledge_id),
                "target_document_id": str(target.id),
                "paragraph_id_list": [str(paragraph.id) for paragraph in paragraphs],
            }
        ).migrate()

    def test_move_untitled_illustrated_paragraph_to_another_knowledge(self):
        target = Document.objects.create(
            knowledge=Knowledge.objects.create(name="Target"), name="Table.csv", char_length=0
        )
        moved = self.imported_paragraph(self.source, "Chart", with_image=True)
        existing = self.imported_paragraph(target, "Table")
        asset = moved.assets.get()
        file_id = asset.file_id
        self.assertEqual(moved.source_key, existing.source_key)

        problem = Problem.objects.create(knowledge=self.knowledge, content="What does the chart show?")
        mapping = ProblemParagraphMapping.objects.create(
            knowledge=self.knowledge, document=self.source, paragraph=moved, problem=problem
        )
        embedding = Embedding.objects.create(
            id=str(asset.id),
            source_id=str(asset.id),
            source_type=SourceType.IMAGE,
            knowledge=self.knowledge,
            document=self.source,
            paragraph=moved,
        )

        self.migrate(target, moved)

        moved.refresh_from_db()
        asset.refresh_from_db()
        self.assertFalse(self.source.paragraph_set.exists())
        self.assertEqual((moved.document_id, moved.knowledge_id), (target.id, target.knowledge_id))
        self.assertEqual(
            (asset.document_id, asset.knowledge_id, asset.file_id), (target.id, target.knowledge_id, file_id)
        )
        self.assertIn(str(file_id), moved.content)
        self.assertEqual(list(target.paragraph_set.order_by("position")), [moved, existing])
        self.assertEqual(moved.origin, ContentOrigin.MANUAL)
        mapping.refresh_from_db()
        embedding.refresh_from_db()
        self.assertEqual((mapping.document_id, mapping.problem.knowledge_id), (target.id, target.knowledge_id))
        self.assertEqual(mapping.problem.content, problem.content)
        self.assertEqual((embedding.document_id, embedding.knowledge_id), (target.id, target.knowledge_id))
        IncrementalDocumentSync(target).merge([{"content": "Updated table"}])
        existing.refresh_from_db()
        moved.refresh_from_db()
        self.assertEqual(existing.content, "Updated table")
        self.assertIn(str(file_id), moved.content)

    def test_images_with_the_same_source_key_can_share_a_target_document(self):
        target = Document.objects.create(knowledge=self.knowledge, name="Other.docx", char_length=0)
        moved = self.imported_paragraph(self.source, "Source image", with_image=True)
        existing = self.imported_paragraph(target, "Target image", with_image=True)
        moved_asset, existing_asset = moved.assets.get(), existing.assets.get()
        self.assertEqual(moved_asset.source_asset_key, existing_asset.source_asset_key)

        self.migrate(target, moved)

        moved.refresh_from_db()
        moved_asset.refresh_from_db()
        existing_asset.refresh_from_db()
        self.assertNotEqual(moved_asset.source_asset_key, existing_asset.source_asset_key)
        block = next(block for block in moved.content_schema if block["type"] == "image")
        self.assertEqual(block["source_asset_key"], moved_asset.source_asset_key)
        self.assertEqual(sync_paragraph_assets([moved])[0].id, moved_asset.id)

    def test_batch_move_and_retry_preserve_paragraph_positions_and_totals(self):
        target = Document.objects.create(knowledge=self.knowledge, name="Target", char_length=0)
        first = self.imported_paragraph(self.source, "First")
        second = Paragraph.objects.create(knowledge=self.knowledge, document=self.source, content="Second", position=2)
        existing = self.imported_paragraph(target, "Existing")

        self.migrate(target, second, first)
        self.migrate(target, second, first)

        self.assertEqual(
            list(target.paragraph_set.order_by("position").values_list("id", "position")),
            [(first.id, 1), (second.id, 2), (existing.id, 3)],
        )
        self.source.refresh_from_db()
        target.refresh_from_db()
        self.assertEqual(self.source.char_length, 0)
        self.assertEqual(target.char_length, len(first.content + second.content + existing.content))

    def test_standalone_image_survives_asset_sync_after_moving(self):
        target = Document.objects.create(knowledge=self.knowledge, name="Target", char_length=0)
        moved = Paragraph.objects.create(knowledge=self.knowledge, document=self.source, content="Image description")
        image = File(file_name="image.png", source_type=FileSourceType.PARAGRAPH, source_id=str(moved.id))
        File.objects.bulk_create([image])
        asset = moved.assets.create(
            knowledge=self.knowledge,
            document=self.source,
            file=image,
            origin=ContentOrigin.MANUAL,
            source_asset_key=f"standalone:{image.id}",
            description="Recognized image",
        )

        self.migrate(target, moved)

        moved.refresh_from_db()
        synced = sync_paragraph_assets([moved])
        self.assertEqual(
            [(item.id, item.file_id, item.description) for item in synced], [(asset.id, image.id, "Recognized image")]
        )

    def test_batch_stays_at_start_after_web_source_changes_and_replaces_headings(self):
        target = Document.objects.create(knowledge=self.knowledge, name="Web", type=KnowledgeType.WEB, char_length=0)
        sync = IncrementalDocumentSync(target)
        sync.merge([{"title": "Old heading", "content": "Old"}])
        first = self.imported_paragraph(self.source, "First")
        second = Paragraph.objects.create(knowledge=self.knowledge, document=self.source, content="Second", position=2)
        self.migrate(target, second, first)

        for title in ("Replacement heading", "Another heading"):
            sync.merge([{"title": title, "content": title}])
            self.assertEqual(
                list(
                    target.paragraph_set.filter(is_active=True).order_by("position").values_list("content", flat=True)
                ),
                [first.content, second.content, title],
            )

    def test_move_into_empty_web_document_stays_before_first_sync(self):
        target = Document.objects.create(knowledge=self.knowledge, name="Web", type=KnowledgeType.WEB, char_length=0)
        moved = self.imported_paragraph(self.source, "Moved")
        self.migrate(target, moved)
        IncrementalDocumentSync(target).merge([{"content": "First remote paragraph"}])
        self.assertEqual(target.paragraph_set.earliest("position"), moved)

    def test_web_sync_keeps_user_insertions_ahead_of_a_previously_moved_paragraph(self):
        target = Document.objects.create(knowledge=self.knowledge, name="Web", type=KnowledgeType.WEB, char_length=0)
        self.imported_paragraph(target, "Old")
        moved = self.imported_paragraph(self.source, "Moved")
        self.migrate(target, moved)
        ParagraphSerializers.Create(
            data={"workspace_id": "default", "knowledge_id": str(self.knowledge.id), "document_id": str(target.id)}
        ).save({"content": "New note"}, with_embedding=False)

        IncrementalDocumentSync(target).merge([{"content": "Updated"}])
        self.assertEqual(
            list(target.paragraph_set.order_by("position").values_list("content", flat=True)),
            ["New note", "Moved", "Updated"],
        )

    def test_web_sync_preserves_existing_unanchored_prefix_and_trailing_note(self):
        target = Document.objects.create(knowledge=self.knowledge, name="Web", type=KnowledgeType.WEB, char_length=0)
        remote = self.imported_paragraph(target, "Original")
        remote.position = 2
        remote.save(update_fields=["position"])
        for position, content in [(1, "Previously moved"), (3, "Trailing note")]:
            Paragraph.objects.create(knowledge=self.knowledge, document=target, content=content, position=position)

        IncrementalDocumentSync(target).merge([{"content": "Updated"}])
        self.assertEqual(
            list(target.paragraph_set.order_by("position").values_list("content", flat=True)),
            ["Previously moved", "Updated", "Trailing note"],
        )

    def test_web_sync_counts_moved_and_disabled_content_and_excludes_local_deletions(self):
        target = Document.objects.create(knowledge=self.knowledge, name="Web", type=KnowledgeType.WEB, char_length=0)
        self.imported_paragraph(target, "Old")
        moved = self.imported_paragraph(self.source, "迁入段落")
        self.migrate(target, moved)
        Paragraph.objects.create(knowledge=self.knowledge, document=target, content="Disabled", is_active=False)
        Paragraph.objects.create(
            knowledge=self.knowledge,
            document=target,
            content="Deleted",
            local_state=LocalState.DELETED,
            is_active=False,
        )

        IncrementalDocumentSync(target).merge([{"content": "Changed"}])
        target.refresh_from_db()
        self.assertEqual(target.char_length, len("迁入段落DisabledChanged"))

    def test_batch_delete_from_stale_source_keeps_both_documents_intact(self):
        moved = self.imported_paragraph(self.source, "Moved")
        remaining = Paragraph.objects.create(knowledge=self.knowledge, document=self.source, content="Keep")
        target = Document.objects.create(knowledge=self.knowledge, name="Target", char_length=0)
        self.migrate(target, moved)
        batch = ParagraphSerializers.Batch(
            data={"workspace_id": "default", "knowledge_id": str(self.knowledge.id), "document_id": str(self.source.id)}
        )
        with self.assertRaises(AppApiException):
            batch.batch_delete({"id_list": [str(moved.id), str(remaining.id)]})
        self.assertEqual(target.paragraph_set.get(), moved)
        self.assertEqual(self.source.paragraph_set.get(), remaining)


class ConcurrentParagraphMigrationTests(TransactionTestCase):
    def setUp(self):
        KnowledgeFolder.objects.get_or_create(id="default", defaults={"name": "Root"})
        self.knowledge = Knowledge.objects.create(name="Knowledge")
        self.source = Document.objects.create(knowledge=self.knowledge, name="Source", char_length=0)
        self.target = Document.objects.create(knowledge=self.knowledge, name="Target", char_length=0)
        self.paragraph = Paragraph.objects.create(knowledge=self.knowledge, document=self.source, content="Original")
        self.scope = {
            "workspace_id": "default",
            "knowledge_id": str(self.knowledge.id),
            "document_id": str(self.source.id),
        }

    def migrate(self):
        ParagraphSerializers.Migrate(
            data={
                **self.scope,
                "target_knowledge_id": str(self.knowledge.id),
                "target_document_id": str(self.target.id),
                "paragraph_id_list": [str(self.paragraph.id)],
            }
        ).migrate()

    def edit(self):
        ParagraphSerializers.Operate(data={**self.scope, "paragraph_id": str(self.paragraph.id)}).edit(
            {"title": "Edit", "is_active": True}
        )

    def start_blocked_operation(self, pool, operation):
        worker_pid = Queue()

        def run():
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT pg_backend_pid()")
                    worker_pid.put(cursor.fetchone()[0])
                operation()
            finally:
                connections.close_all()

        future = pool.submit(run)
        pid = worker_pid.get(timeout=5)
        with connection.cursor() as cursor:
            deadline = monotonic() + 5
            while monotonic() < deadline:
                cursor.execute("SELECT pg_backend_pid() = ANY(pg_blocking_pids(%s))", [pid])
                if cursor.fetchone()[0]:
                    return future
                if future.done():
                    future.result()
                    break
                sleep(0.01)
        self.fail("The concurrent operation did not wait for the transaction")

    def test_edit_waits_for_migration_and_rejects_the_stale_source_document(self):
        with ThreadPoolExecutor(max_workers=1) as pool:
            with transaction.atomic():
                Document.objects.select_for_update().get(id=self.source.id)
                future = self.start_blocked_operation(pool, self.edit)
                self.migrate()
            with self.assertRaisesMessage(AppApiException, _("Paragraph id does not exist")):
                future.result(timeout=5)
        self.paragraph.refresh_from_db()
        self.assertEqual((self.paragraph.document_id, self.paragraph.title), (self.target.id, ""))

    def test_migration_waits_for_edit_and_moves_the_edited_content(self):
        with ThreadPoolExecutor(max_workers=1) as pool:
            with transaction.atomic():
                self.edit()
                future = self.start_blocked_operation(pool, self.migrate)
            future.result(timeout=5)
        self.paragraph.refresh_from_db()
        self.assertEqual((self.paragraph.document_id, self.paragraph.title), (self.target.id, "Edit"))
