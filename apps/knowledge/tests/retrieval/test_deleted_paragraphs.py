"""Live PostgreSQL searches must reject stale vectors belonging to deleted paragraphs."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

from django.contrib.postgres.search import SearchVector
from django.db.models import Value
from django.test import TestCase

from application.workflow.nodes.search_knowledge_node.search_knowledge_node import _list_paragraph
from knowledge.models import (
    ContentOrigin,
    Document,
    Embedding,
    Knowledge,
    LocalState,
    Paragraph,
    SearchMode,
    SourceType,
)
from knowledge.serializers.common import list_paragraph
from knowledge.serializers.knowledge import KnowledgeSerializer
from knowledge.services import external_retrieval
from knowledge.services.retrieval_access import RetrievalIdentity
from knowledge.vector.milvus_vector import MilvusVector
from knowledge.vector.pg_vector import PGVector


class DeletedParagraphRetrievalTests(TestCase):
    def setUp(self):
        self.knowledge = Knowledge.objects.create(name="Deleted paragraph search", desc="", workspace_id="default")
        self.document = Document.objects.create(knowledge=self.knowledge, name="Document", char_length=0)
        self.visible = self.create_paragraph()
        self.create_embedding(self.visible, "[0.8, 0.6]", weight="D")
        self.deleted = []
        # More than the vector candidate limit for top_n=1, all scoring above the visible row.
        for index in range(12):
            paragraph = self.create_paragraph(local_state=LocalState.DELETED, is_active=index == 0)
            self.deleted.append(paragraph)
            self.create_embedding(
                paragraph,
                "[1, 0]",
                weight="A",
                source_type=[SourceType.PARAGRAPH, SourceType.PROBLEM, SourceType.IMAGE][index % 3],
            )
        self.model = MagicMock()
        self.model.embed_query.return_value = [1.0, 0.0]
        self.model.embed_images.return_value = [[1.0, 0.0]]
        self.model.supports_image_embedding.return_value = True

    def create_paragraph(self, **values):
        return Paragraph.objects.create(
            knowledge=self.knowledge,
            document=self.document,
            title="Needle",
            content="needle",
            origin=ContentOrigin.SYNCED,
            **values,
        )

    def create_embedding(self, paragraph, vector, *, weight, source_type=SourceType.PARAGRAPH):
        return Embedding.objects.create(
            id=str(uuid4()),
            knowledge=self.knowledge,
            document=self.document,
            paragraph=paragraph,
            source_id=str(paragraph.id),
            source_type=source_type,
            is_active=True,
            embedding=vector,
            search_vector=SearchVector(Value("needle"), config="simple", weight=weight),
        )

    def assert_visible_hit(self, hits):
        self.assertEqual([str(hit["paragraph_id"]) for hit in hits], [str(self.visible.id)])
        self.assertEqual(Paragraph.objects.filter(local_state=LocalState.DELETED).count(), len(self.deleted))
        self.assertEqual(Embedding.objects.count(), 13)

    def test_all_vector_query_modes_filter_deleted_before_top_n(self):
        for mode in SearchMode:
            with self.subTest(mode=mode):
                hits = PGVector().query("needle", [1.0, 0.0], [str(self.knowledge.id)], [], [], [], True, 1, 0, mode)
                self.assert_visible_hit(hits)

    @patch.object(MilvusVector, "_has_collection", return_value=False)
    def test_milvus_pg_fallback_filters_deleted_and_missing_before_limit(self, _has_collection):
        orphan = self.create_embedding(self.visible, "[1, 0]", weight="A")
        Embedding.objects.filter(id=orphan.id).update(paragraph_id=uuid4())
        # Keep a lower-scoring live vector after the orphan and deleted candidates.
        Embedding.objects.filter(paragraph=self.visible).update(embedding="[0.8, 0.6]")
        for mode in (SearchMode.embedding, SearchMode.blend):
            with self.subTest(mode=mode):
                hits = MilvusVector().query(
                    "needle", [1.0, 0.0], [str(self.knowledge.id)], None, [], [], True, 1, 0, mode
                )
                self.assertEqual([hit["paragraph_id"] for hit in hits], [str(self.visible.id)])

    def test_text_and_image_hit_tests_filter_stale_vectors(self):
        for mode in SearchMode:
            with self.subTest(mode=mode):
                self.assert_visible_hit(
                    PGVector().hit_test("needle", [str(self.knowledge.id)], [], 1, 0, mode, self.model)
                )
        self.assert_visible_hit(
            PGVector().hit_test(
                "needle", [str(self.knowledge.id)], [], 1, 0, SearchMode.blend, self.model, ["test-image"]
            )
        )

    def test_paragraph_readers_filter_deleted_rows_even_from_stale_hit_lists(self):
        paragraphs = [self.visible, *self.deleted]
        ids = [str(paragraph.id) for paragraph in paragraphs]
        self.assertEqual([str(row["id"]) for row in list_paragraph(ids)], [str(self.visible.id)])
        matches = [{"paragraph_id": paragraph_id} for paragraph_id in ids]
        for scope in (None, [str(self.knowledge.id)]):
            with self.subTest(scope=scope):
                result = _list_paragraph(matches, MagicMock(), scope)
                self.assertEqual([str(row["id"]) for row in result], [str(self.visible.id)])
        self.assertEqual(Paragraph.objects.count(), len(paragraphs))

    def test_admin_hit_test_rechecks_deletion_after_vector_search(self):
        def stale_hits(*args, **kwargs):
            Paragraph.objects.filter(id=self.visible.id).update(local_state=LocalState.DELETED, is_active=False)
            return [
                {
                    "paragraph_id": str(self.visible.id),
                    "source_id": str(self.visible.id),
                    "source_type": SourceType.PARAGRAPH,
                    "similarity": 0.9,
                }
            ]

        with (
            patch("knowledge.serializers.knowledge.VectorStore.get_embedding_vector") as vector,
            patch("knowledge.serializers.knowledge.get_embedding_model_by_knowledge_id", return_value=self.model),
        ):
            vector.return_value.hit_test.side_effect = stale_hits
            hits = KnowledgeSerializer.HitTest(
                data={
                    "workspace_id": "default",
                    "knowledge_id": str(self.knowledge.id),
                    "query_text": "needle",
                    "top_number": 1,
                    "similarity": 0,
                    "search_mode": SearchMode.embedding,
                }
            ).hit_test()
        self.assertEqual(hits, [])
        self.assertTrue(Paragraph.objects.filter(id=self.visible.id).exists())

    def test_rest_and_mcp_retrieval_drop_deleted_paragraphs_even_if_enabled(self):
        matches = [
            {
                "paragraph_id": str(paragraph.id),
                "source_id": str(paragraph.id),
                "source_type": SourceType.PARAGRAPH,
                "similarity": 0.9,
            }
            for paragraph in [self.visible, self.deleted[0]]
        ]
        with (
            patch.object(external_retrieval, "authorize_external", return_value=self.knowledge),
            patch.object(external_retrieval, "refresh_identity", side_effect=lambda identity: identity),
            patch.object(external_retrieval.VectorStore, "get_embedding_vector") as vector,
            patch.object(external_retrieval, "record_recall_safely") as record,
        ):
            vector.return_value.hit_test.return_value = matches
            result = external_retrieval.retrieve(
                str(self.knowledge.id), RetrievalIdentity(), {"query_text": "needle", "search_mode": "keywords"}
            )
        self.assert_visible_hit(result["hits"])
        record.assert_called_once_with(matches[:1])
