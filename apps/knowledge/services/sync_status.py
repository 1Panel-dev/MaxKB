"""Heartbeat and recovery for scheduled knowledge synchronization."""

from datetime import timedelta
from threading import Event, Thread

from celery_once.helpers import import_backend, queue_once_key
from common.utils.logger import maxkb_logger
from django.db import close_old_connections, transaction
from django.db.models import Q, QuerySet
from django.utils import timezone

from knowledge.models import Document, Knowledge, KnowledgeSyncLog, KnowledgeSyncStatus, KnowledgeType
from knowledge.services.workflow_sync import _delete_workflow_documents

SYNC_HEARTBEAT_SECONDS = 60
SYNC_STALE_TIMEOUT = timedelta(hours=1)
SYNC_QUEUE_TASKS = {
    KnowledgeType.WEB: "celery:sync_replace_web_knowledge",
    KnowledgeType.LARK: "celery:scheduled_sync_lark_knowledge",
    KnowledgeType.WORKFLOW: "celery:scheduled_sync_workflow_knowledge",
}


def _clear_sync_queue_lock(knowledge):
    """Release only the interrupted knowledge's QueueOnce lock, under its database row lock."""
    from ops import celery_app

    task_name = SYNC_QUEUE_TASKS.get(knowledge.type)
    if task_name is not None:
        backend = import_backend(celery_app.conf.ONCE)
        backend.clear_lock(queue_once_key(task_name, {"knowledge_id": str(knowledge.id)}, ["knowledge_id"]))


def fail_running_sync_logs_on_startup():
    """End interrupted runs before the worker starts accepting new tasks; do not resume them."""
    knowledge_ids = list(
        QuerySet(KnowledgeSyncLog)
        .filter(status=KnowledgeSyncStatus.RUNNING)
        .order_by()
        .values_list("knowledge_id", flat=True)
        .distinct()
    )
    failed = 0
    for knowledge_id in knowledge_ids:
        with transaction.atomic():
            knowledge = QuerySet(Knowledge).select_for_update().filter(id=knowledge_id).first()
            running_logs = (
                QuerySet(KnowledgeSyncLog)
                .select_for_update()
                .filter(knowledge_id=knowledge_id, status=KnowledgeSyncStatus.RUNNING)
            )
            now = timezone.now()
            interrupted = 0
            for sync_log in running_logs:
                interrupted += (
                    QuerySet(KnowledgeSyncLog)
                    .filter(id=sync_log.id, status=KnowledgeSyncStatus.RUNNING)
                    .update(
                        status=KnowledgeSyncStatus.FAILURE,
                        failed_count=max(sync_log.failed_count, 1),
                        duration_ms=max(0, round((now - sync_log.create_time).total_seconds() * 1000)),
                        message="Synchronization interrupted by service restart",
                        update_time=now,
                    )
                )
            if interrupted and knowledge is not None:
                _clear_sync_queue_lock(knowledge)
            failed += interrupted
    return failed


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
