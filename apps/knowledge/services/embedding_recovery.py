"""Recover document embeddings during the existing service startup reset."""

import uuid

from celery_once.helpers import import_backend, queue_once_key
from common.event.listener_manage import ListenerManagement
from django.db import transaction
from django.db.models import Q
from django_redis import get_redis_connection
from ops import celery_app

from knowledge.models import Document, Paragraph, State, TaskType

EMBEDDING_GENERATION = "embedding_generation"


def recover_interrupted_embeddings():
    # Older versions reset documents alone, leaving their paragraphs and locks pending.
    interrupted_paragraphs = Paragraph.objects.filter(status__regex="[014]$")
    candidates = Document.objects.filter(
        Q(status__regex="[014]$")
        | Q(status__endswith=State.FAILURE.value, id__in=interrupted_paragraphs.values("document_id"))
    )
    recovered = 0
    for document_id in candidates.values_list("id", flat=True).iterator():
        with transaction.atomic():
            document = candidates.select_for_update().filter(id=document_id).first()
            if document is None:
                continue
            # Old broker deliveries must not process a newly submitted retry or release its lock.
            document.meta = {**document.meta, EMBEDDING_GENERATION: str(uuid.uuid4())}
            document.save(update_fields=["meta"])
            ListenerManagement.update_status(Document.objects.filter(id=document_id), TaskType.EMBEDDING, State.FAILURE)
            ListenerManagement.update_status(
                interrupted_paragraphs.filter(document_id=document_id), TaskType.EMBEDDING, State.FAILURE
            )
            ListenerManagement.get_aggregation_document_status(document_id)()
            transaction.on_commit(lambda document_id=document_id: _clear_embedding_locks(document_id))
            recovered += 1
    return recovered


def _clear_embedding_locks(document_id):
    backend = import_backend(celery_app.conf.ONCE)
    backend.clear_lock(
        queue_once_key("celery:embedding_by_document", {"document_id": str(document_id)}, ["document_id"])
    )
    get_redis_connection("default").delete(f"embedding:{document_id}")
