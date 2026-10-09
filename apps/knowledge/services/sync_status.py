"""Heartbeat and recovery for scheduled knowledge synchronization."""

from datetime import timedelta
from threading import Event, Thread

from common.utils.logger import maxkb_logger
from django.db import close_old_connections, transaction
from django.db.models import Q, QuerySet
from django.utils import timezone

from knowledge.models import Document, Knowledge, KnowledgeSyncLog, KnowledgeSyncStatus
from knowledge.services.workflow_sync import _delete_workflow_documents

SYNC_HEARTBEAT_SECONDS = 60
SYNC_STALE_TIMEOUT = timedelta(hours=1)


def start_sync_heartbeat(sync_log_id):
    """Return a stop callback; healthy long runs keep their lease regardless of duration."""
    if sync_log_id is None:
        return lambda: None
    stopped = Event()

    def touch():
        return (
            QuerySet(KnowledgeSyncLog)
            .filter(id=sync_log_id, status=KnowledgeSyncStatus.RUNNING)
            .update(update_time=timezone.now())
        )

    if not touch():
        raise ValueError("Synchronization is no longer running")

    def heartbeat():
        while not stopped.wait(SYNC_HEARTBEAT_SECONDS):
            close_old_connections()
            try:
                if not touch():
                    break
            except Exception:
                maxkb_logger.exception(f"Failed to refresh knowledge sync heartbeat: log_id={sync_log_id}")
            finally:
                close_old_connections()

    Thread(target=heartbeat, name=f"knowledge-sync-{sync_log_id}", daemon=True).start()
    return stopped.set


@transaction.atomic
def recover_stale_sync_logs(knowledge_id):
    """Caller and publishers share the knowledge lock so expired output cannot replace old data."""
    QuerySet(Knowledge).select_for_update().get(id=knowledge_id)
    now = timezone.now()
    expired_logs = (
        QuerySet(KnowledgeSyncLog)
        .select_for_update()
        .filter(knowledge_id=knowledge_id, status=KnowledgeSyncStatus.RUNNING, update_time__lt=now - SYNC_STALE_TIMEOUT)
    )
    recovered = 0
    for sync_log in expired_logs:
        output_ids = list(
            QuerySet(Document)
            .filter(knowledge_id=knowledge_id)
            .filter(Q(meta__workflow_sync_log_id=str(sync_log.id)) | Q(meta__web_sync_run_id=str(sync_log.id)))
            .values_list("id", flat=True)
        )
        _delete_workflow_documents(output_ids)
        QuerySet(KnowledgeSyncLog).filter(id=sync_log.id, status=KnowledgeSyncStatus.RUNNING).update(
            status=KnowledgeSyncStatus.FAILURE,
            failed_count=max(sync_log.failed_count, 1),
            duration_ms=max(0, round((now - sync_log.create_time).total_seconds() * 1000)),
            message="Synchronization heartbeat expired; incomplete output was discarded",
            update_time=now,
        )
        recovered += 1
    return recovered
