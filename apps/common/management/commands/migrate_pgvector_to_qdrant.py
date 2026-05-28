"""
Management command to migrate vector data from pgvector to Qdrant.

Usage:
    python apps/manage.py migrate_pgvector_to_qdrant --knowledge-id <id>
    python apps/manage.py migrate_pgvector_to_qdrant --all
    python apps/manage.py migrate_pgvector_to_qdrant --verify
"""
import logging

from django.core.management.base import BaseCommand
from knowledge.models import Knowledge, Embedding, SourceType
from knowledge.vector.qdrant_store import QdrantVectorStore, _make_collection_name, _build_embedding_id
from qdrant_client.http.models import PointStruct

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Migrate vectors from pgvector to Qdrant"

    def add_arguments(self, parser):
        parser.add_argument(
            "--knowledge-id",
            type=str,
            help="Migrate a specific knowledge base by ID",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Migrate all knowledge bases",
        )
        parser.add_argument(
            "--verify",
            action="store_true",
            help="Verify migration results",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=500,
            help="Batch size for upsert (default: 500)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Count vectors without actually migrating",
        )

    def handle(self, *args, **options):
        if options["verify"]:
            self.verify_migration(options)
            return

        knowledge_ids = []
        if options["knowledge_id"]:
            knowledge_ids = [options["knowledge_id"]]
        elif options["all"]:
            knowledge_ids = list(
                Knowledge.objects.all().values_list("id", flat=True)
            )
        else:
            self.stderr.write("Use --knowledge-id <id> or --all")
            return

        store = QdrantVectorStore()
        batch_size = options["batch_size"]
        dry_run = options["dry_run"]

        for kid in knowledge_ids:
            self.migrate_knowledge(store, kid, batch_size, dry_run)

    def migrate_knowledge(self, store, knowledge_id, batch_size, dry_run):
        embeddings = Embedding.objects.filter(knowledge_id=knowledge_id)
        total = embeddings.count()

        if total == 0:
            self.stdout.write(f"Knowledge {knowledge_id}: no vectors, skipping")
            return

        if dry_run:
            self.stdout.write(f"Knowledge {knowledge_id}: would migrate {total} vectors")
            return

        self.stdout.write(f"Migrating knowledge {knowledge_id}: {total} vectors...")

        collection_name = _make_collection_name(knowledge_id)
        first = embeddings.first()
        vector_size = len(first.embedding) if first and first.embedding else 768
        store._ensure_collection(knowledge_id, vector_size)

        migrated = 0
        for offset in range(0, total, batch_size):
            batch = embeddings[offset : offset + batch_size]
            points = []
            for emb in batch:
                point_id = _build_embedding_id(emb.source_id, str(emb.source_type))
                points.append(PointStruct(
                    id=point_id,
                    vector=[float(x) for x in emb.embedding] if emb.embedding else [],
                    payload={
                        "knowledge_id": str(emb.knowledge_id),
                        "document_id": str(emb.document_id),
                        "paragraph_id": str(emb.paragraph_id),
                        "source_id": emb.source_id,
                        "source_type": str(emb.source_type),
                        "is_active": emb.is_active,
                        "content": "",
                    },
                ))
            store.client.upsert(
                collection_name=collection_name,
                points=points,
                wait=True,
            )
            migrated += len(points)
            self.stdout.write(f"  {migrated}/{total}")

        # Update knowledge base vector_store_type
        Knowledge.objects.filter(id=knowledge_id).update(vector_store_type="qdrant")
        self.stdout.write(f"Knowledge {knowledge_id}: migration complete")

    def verify_migration(self, options):
        store = QdrantVectorStore()
        knowledge_ids = []
        if options["knowledge_id"]:
            knowledge_ids = [options["knowledge_id"]]
        elif options["all"]:
            knowledge_ids = list(
                Knowledge.objects.all().values_list("id", flat=True)
            )

        for kid in knowledge_ids:
            pg_count = Embedding.objects.filter(knowledge_id=kid).count()
            collection_name = _make_collection_name(kid)
            try:
                info = store.client.get_collection(collection_name=collection_name)
                qdrant_count = info.points_count or 0
            except Exception:
                qdrant_count = 0

            if pg_count == qdrant_count:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"OK  {kid}: pgvector={pg_count}, qdrant={qdrant_count}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"MISMATCH {kid}: pgvector={pg_count}, qdrant={qdrant_count}"
                    )
                )
