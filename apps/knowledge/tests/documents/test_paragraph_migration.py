from django.test import TestCase

from knowledge.models import ContentOrigin, Document, Embedding, File, FileSourceType, Knowledge, Paragraph
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
