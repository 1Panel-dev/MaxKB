# coding=utf-8
"""
@project: MaxKB
@Author：虎
@file： sync.py
@date：2024/8/20 21:37
@desc:
"""

import traceback
from copy import deepcopy
from time import perf_counter
from typing import List

from celery_once import AlreadyQueued, QueueOnce
from common.utils.fork import Fork, ForkManage
from common.utils.logger import maxkb_logger
from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from knowledge.models import (
    Document,
    DocumentResourceType,
    File,
    FileSourceType,
    Knowledge,
    KnowledgeSyncLog,
    KnowledgeSyncStatus,
    KnowledgeSyncTrigger,
    KnowledgeSyncType,
    KnowledgeType,
)
from knowledge.serializers.knowledge_workflow import KnowledgeWorkflowActionSerializer
from knowledge.services.document_cleanup import delete_document_data
from knowledge.task.handler import (
    get_save_handler,
    get_sync_handler,
    get_sync_web_document_handler,
    normalize_web_url,
)
from ops import celery_app

WEB_SYNC_TYPES = {"incremental", "replace", "complete"}
SCHEDULED_KNOWLEDGE_TYPES = {KnowledgeType.WEB, KnowledgeType.LARK, KnowledgeType.WORKFLOW}


def get_selector_list(selector: str | None) -> List[str]:
    return [item for item in (selector or "").split(" ") if item]


def _new_sync_stats():
    return {
        "total_count": 0,
        "synced_count": 0,
        "skipped_count": 0,
        "deleted_count": 0,
        "failed_count": 0,
        "message": "",
    }


def _finish_unstarted_scheduled_sync(sync_log_id, status, message):
    if sync_log_id is not None:
        updates = {"status": status, "message": message}
        if status == KnowledgeSyncStatus.FAILURE:
            updates["failed_count"] = 1
        QuerySet(KnowledgeSyncLog).filter(id=sync_log_id).update(**updates)


@celery_app.task(base=QueueOnce, once={"keys": ["knowledge_id"]}, name="celery:sync_web_knowledge")
def sync_web_knowledge(knowledge_id: str, user_id, url: str, selector: str, doc_strategy=None):
    try:
        maxkb_logger.info(
            _("Start--->Start synchronization web knowledge base:{knowledge_id}").format(knowledge_id=knowledge_id)
        )
        ForkManage(url, get_selector_list(selector)).fork(
            2, set(), get_save_handler(knowledge_id, user_id, selector, doc_strategy)
        )

        maxkb_logger.info(
            _("End--->End synchronization web knowledge base:{knowledge_id}").format(knowledge_id=knowledge_id)
        )
    except Exception as e:
        maxkb_logger.error(
            _("Synchronize web knowledge base:{knowledge_id} error{error}{traceback}").format(
                knowledge_id=knowledge_id, error=str(e), traceback=traceback.format_exc()
            )
        )


@celery_app.task(base=QueueOnce, once={"keys": ["knowledge_id"]}, name="celery:sync_replace_web_knowledge")
def sync_replace_web_knowledge(
    knowledge_id: str,
    user_id,
    url: str,
    selector: str,
    doc_strategy=None,
    sync_type: str = "incremental",
    record_log: bool = False,
    trigger_type: str = KnowledgeSyncTrigger.MANUAL,
    sync_log_id: str | None = None,
):
    started_at = perf_counter()
    stats = _new_sync_stats()
    sync_log = None
    try:
        if sync_type not in WEB_SYNC_TYPES:
            raise ValueError(f"Unsupported Web knowledge synchronization type: {sync_type}")
        knowledge = QuerySet(Knowledge).filter(id=knowledge_id, type=KnowledgeType.WEB).first()
        if knowledge is None:
            raise ValueError(f"Web knowledge does not exist: {knowledge_id}")
        initial_total = (
            QuerySet(Document)
            .filter(
                knowledge_id=knowledge_id,
                type=KnowledgeType.WEB,
                resource_type=DocumentResourceType.DOCUMENT,
            )
            .count()
        )
        stats["total_count"] = initial_total if isinstance(initial_total, int) else 0
        if record_log:
            sync_log = (
                QuerySet(KnowledgeSyncLog).get(id=sync_log_id)
                if sync_log_id is not None
                else KnowledgeSyncLog.objects.create(
                    knowledge=knowledge,
                    workspace_id=knowledge.workspace_id,
                    sync_type=sync_type,
                    trigger_type=trigger_type,
                )
            )
        maxkb_logger.info(
            _("Start--->Start synchronization web knowledge base:{knowledge_id}, type:{sync_type}").format(
                knowledge_id=knowledge_id, sync_type=sync_type
            )
        )
        if sync_type == "complete":
            document_ids = list(
                QuerySet(Document)
                .filter(
                    knowledge_id=knowledge_id,
                    type=KnowledgeType.WEB,
                    resource_type=DocumentResourceType.DOCUMENT,
                )
                .values_list("id", flat=True)
            )
            delete_document_data(document_ids)
            QuerySet(File).filter(
                source_type=FileSourceType.KNOWLEDGE,
                source_id=str(knowledge_id),
                meta__source_url__isnull=False,
            ).delete()
            ForkManage(url, get_selector_list(selector)).fork(
                2,
                set(),
                get_save_handler(knowledge_id, user_id, selector, doc_strategy, stats),
            )
            stats["deleted_count"] = len(document_ids)
        else:
            visited_urls, successful_urls = set(), set()
            ForkManage(url, get_selector_list(selector)).fork(
                2,
                visited_urls,
                get_sync_handler(knowledge_id, user_id, doc_strategy, sync_type, successful_urls, stats),
            )
            if sync_type == "incremental" and normalize_web_url(url) in successful_urls:
                crawled_urls = {normalize_web_url(item) for item in visited_urls}
                stale_document_ids = [
                    document.id
                    for document in QuerySet(Document).filter(
                        knowledge_id=knowledge_id,
                        type=KnowledgeType.WEB,
                        resource_type=DocumentResourceType.DOCUMENT,
                    )
                    if (document.meta or {}).get("source_url")
                    and normalize_web_url(document.meta["source_url"]) not in crawled_urls
                ]
                delete_document_data(stale_document_ids)
                stats["deleted_count"] += len(stale_document_ids)
        stats["total_count"] = max(
            stats["total_count"],
            stats["synced_count"] + stats["skipped_count"] + stats["failed_count"],
            stats["deleted_count"],
        )
        maxkb_logger.info(
            _("End--->End synchronization web knowledge base:{knowledge_id}").format(knowledge_id=knowledge_id)
        )
    except Exception as e:
        stats["failed_count"] += 1
        stats["message"] = str(e)
        if sync_log is None:
            _finish_unstarted_scheduled_sync(sync_log_id, KnowledgeSyncStatus.FAILURE, str(e))
        maxkb_logger.error(
            _("Synchronize web knowledge base:{knowledge_id} error{error}{traceback}").format(
                knowledge_id=knowledge_id, error=str(e), traceback=traceback.format_exc()
            )
        )
    finally:
        stats["duration_ms"] = max(0, round((perf_counter() - started_at) * 1000))
        stats["status"] = KnowledgeSyncStatus.FAILURE if stats["failed_count"] else KnowledgeSyncStatus.SUCCESS
        if sync_log is not None:
            QuerySet(KnowledgeSyncLog).filter(id=sync_log.id).update(
                status=stats["status"],
                total_count=stats["total_count"],
                synced_count=stats["synced_count"],
                skipped_count=stats["skipped_count"],
                deleted_count=stats["deleted_count"],
                failed_count=stats["failed_count"],
                duration_ms=stats["duration_ms"],
                message=stats["message"],
            )
    return stats


@celery_app.task(name="celery:scheduled_sync_web_knowledge")
def scheduled_sync_web_knowledge(knowledge_id: str, sync_type: str = "incremental", sync_log_id: str | None = None):
    """Unified entry point for a scheduler to synchronize a Web knowledge base."""
    if sync_type not in WEB_SYNC_TYPES:
        maxkb_logger.warning(f"Scheduled Web knowledge synchronization type is invalid: {sync_type}")
        _finish_unstarted_scheduled_sync(sync_log_id, KnowledgeSyncStatus.FAILURE, "Invalid synchronization type")
        return False
    knowledge = QuerySet(Knowledge).filter(id=knowledge_id, type=KnowledgeType.WEB).first()
    if knowledge is None:
        maxkb_logger.warning(f"Scheduled Web knowledge synchronization skipped: {knowledge_id}")
        _finish_unstarted_scheduled_sync(sync_log_id, KnowledgeSyncStatus.FAILURE, "Knowledge base no longer exists")
        return False
    meta = knowledge.meta or {}
    sync_setting = meta.get("sync_setting") or {}
    if not sync_setting.get("enabled", False):
        maxkb_logger.info(f"Scheduled Web knowledge synchronization is disabled: {knowledge_id}")
        _finish_unstarted_scheduled_sync(
            sync_log_id, KnowledgeSyncStatus.SKIPPED, "Scheduled synchronization is disabled"
        )
        return False
    sync_type = (
        QuerySet(KnowledgeSyncLog).get(id=sync_log_id).sync_type
        if sync_log_id is not None
        else sync_setting.get("sync_type", sync_type)
    )
    if sync_type not in WEB_SYNC_TYPES:
        maxkb_logger.warning(f"Scheduled Web knowledge synchronization type is invalid: {sync_type}")
        _finish_unstarted_scheduled_sync(sync_log_id, KnowledgeSyncStatus.FAILURE, "Invalid synchronization type")
        return False
    if not meta.get("source_url"):
        maxkb_logger.warning(f"Scheduled Web knowledge synchronization has no source URL: {knowledge_id}")
        _finish_unstarted_scheduled_sync(sync_log_id, KnowledgeSyncStatus.FAILURE, "Web knowledge has no source URL")
        return False
    try:
        sync_replace_web_knowledge.delay(
            str(knowledge.id),
            knowledge.user_id,
            meta.get("source_url"),
            meta.get("selector"),
            meta.get("doc_strategy"),
            sync_type,
            record_log=True,
            trigger_type=KnowledgeSyncTrigger.SCHEDULED,
            sync_log_id=sync_log_id,
        )
    except AlreadyQueued:
        _finish_unstarted_scheduled_sync(sync_log_id, KnowledgeSyncStatus.SKIPPED, "Synchronization is already running")
        return False
    except Exception as exc:
        _finish_unstarted_scheduled_sync(sync_log_id, KnowledgeSyncStatus.FAILURE, str(exc))
        raise
    return True


@celery_app.task(
    base=QueueOnce,
    once={"keys": ["knowledge_id"]},
    name="celery:scheduled_sync_workflow_knowledge",
)
def scheduled_sync_workflow_knowledge(knowledge_id: str, sync_log_id: str | None = None):
    """Run a workflow knowledge base with the most recently saved input snapshot."""
    started_at = perf_counter()
    sync_log = QuerySet(KnowledgeSyncLog).filter(id=sync_log_id).first() if sync_log_id is not None else None
    try:
        knowledge = QuerySet(Knowledge).filter(id=knowledge_id, type=KnowledgeType.WORKFLOW).first()
        if knowledge is None:
            raise ValueError(f"Workflow knowledge does not exist: {knowledge_id}")
        meta = knowledge.meta or {}
        setting = meta.get("sync_setting") or {}
        if not setting.get("enabled", False):
            maxkb_logger.info(f"Scheduled workflow knowledge synchronization is disabled: {knowledge_id}")
            _finish_unstarted_scheduled_sync(
                sync_log_id, KnowledgeSyncStatus.SKIPPED, "Scheduled synchronization is disabled"
            )
            return False
        running_logs = QuerySet(KnowledgeSyncLog).filter(knowledge_id=knowledge.id, status=KnowledgeSyncStatus.RUNNING)
        if sync_log_id is not None:
            running_logs = running_logs.exclude(id=sync_log_id)
        if running_logs.exists():
            maxkb_logger.info(f"Scheduled workflow knowledge synchronization is already running: {knowledge_id}")
            _finish_unstarted_scheduled_sync(
                sync_log_id, KnowledgeSyncStatus.SKIPPED, "Synchronization is already running"
            )
            return False
        sync_type = (
            sync_log.sync_type if sync_log is not None else setting.get("sync_type", KnowledgeSyncType.INCREMENTAL)
        )
        if sync_type not in WEB_SYNC_TYPES:
            raise ValueError(f"Unsupported workflow knowledge synchronization type: {sync_type}")
        total_count = (
            QuerySet(Document).filter(knowledge_id=knowledge.id, resource_type=DocumentResourceType.DOCUMENT).count()
        )
        if sync_log is None:
            sync_log = KnowledgeSyncLog.objects.create(
                knowledge=knowledge,
                workspace_id=knowledge.workspace_id,
                sync_type=sync_type,
                trigger_type=KnowledgeSyncTrigger.SCHEDULED,
                total_count=total_count,
            )
        else:
            QuerySet(KnowledgeSyncLog).filter(id=sync_log.id).update(total_count=total_count)
        workflow_input = deepcopy(meta.get("workflow_sync_input") or {})
        if not workflow_input.get("data_source"):
            raise ValueError("Workflow knowledge has no saved synchronization input")
        if workflow_input["data_source"].get("file_list"):
            raise ValueError("Local file data sources cannot be synchronized on a schedule")
        if knowledge.user is None:
            raise ValueError("Workflow knowledge has no owner available for scheduled synchronization")
        if sync_type == KnowledgeSyncType.COMPLETE:
            document_ids = list(
                QuerySet(Document)
                .filter(
                    knowledge_id=knowledge.id,
                    type=KnowledgeType.WORKFLOW,
                    resource_type=DocumentResourceType.DOCUMENT,
                )
                .values_list("id", flat=True)
            )
            delete_document_data(document_ids)
            QuerySet(KnowledgeSyncLog).filter(id=sync_log.id).update(deleted_count=len(document_ids))
        action = KnowledgeWorkflowActionSerializer(
            data={"workspace_id": knowledge.workspace_id, "knowledge_id": str(knowledge.id)}
        ).action(workflow_input, knowledge.user, True, str(sync_log.id))
        QuerySet(KnowledgeSyncLog).filter(id=sync_log.id).update(message=f"Workflow action started: {action['id']}")
        return True
    except Exception as exc:
        maxkb_logger.error(
            f"Scheduled workflow knowledge synchronization failed, knowledge_id={knowledge_id}: "
            f"{exc}\n{traceback.format_exc()}"
        )
        if sync_log is not None:
            QuerySet(KnowledgeSyncLog).filter(id=sync_log.id).update(
                status=KnowledgeSyncStatus.FAILURE,
                failed_count=1,
                duration_ms=max(0, round((perf_counter() - started_at) * 1000)),
                message=str(exc),
            )
        else:
            _finish_unstarted_scheduled_sync(sync_log_id, KnowledgeSyncStatus.FAILURE, str(exc))
        return False


@celery_app.task(name="celery:scheduled_sync_knowledge")
def scheduled_sync_knowledge(knowledge_id: str):
    """Dispatch one scheduled synchronization according to the knowledge source type."""
    with transaction.atomic():
        knowledge = (
            QuerySet(Knowledge).select_for_update().filter(id=knowledge_id, type__in=SCHEDULED_KNOWLEDGE_TYPES).first()
        )
        if knowledge is None:
            maxkb_logger.warning(f"Scheduled knowledge synchronization skipped: {knowledge_id}")
            return False
        setting = (knowledge.meta or {}).get("sync_setting") or {}
        if not setting.get("enabled", False):
            maxkb_logger.info(f"Scheduled knowledge synchronization is disabled: {knowledge_id}")
            return False
        sync_type = setting.get("sync_type", KnowledgeSyncType.INCREMENTAL)
        running = (
            QuerySet(KnowledgeSyncLog).filter(knowledge_id=knowledge.id, status=KnowledgeSyncStatus.RUNNING).exists()
        )
        sync_log = KnowledgeSyncLog.objects.create(
            knowledge=knowledge,
            workspace_id=knowledge.workspace_id,
            sync_type=sync_type,
            trigger_type=KnowledgeSyncTrigger.SCHEDULED,
            status=KnowledgeSyncStatus.SKIPPED if running else KnowledgeSyncStatus.RUNNING,
            message="Previous synchronization is still running" if running else "",
        )
    if running:
        return False
    try:
        if knowledge.type == KnowledgeType.WEB:
            scheduled_sync_web_knowledge.delay(str(knowledge.id), sync_log_id=str(sync_log.id))
        elif knowledge.type == KnowledgeType.LARK:
            celery_app.send_task("celery:scheduled_sync_lark_knowledge", args=[str(knowledge.id), str(sync_log.id)])
        elif knowledge.type == KnowledgeType.WORKFLOW:
            scheduled_sync_workflow_knowledge.delay(str(knowledge.id), str(sync_log.id))
    except AlreadyQueued:
        _finish_unstarted_scheduled_sync(sync_log.id, KnowledgeSyncStatus.SKIPPED, "Synchronization is already queued")
        return False
    except Exception as exc:
        _finish_unstarted_scheduled_sync(sync_log.id, KnowledgeSyncStatus.FAILURE, str(exc))
        raise
    return True


@celery_app.task(name="celery:sync_web_document")
def sync_web_document(knowledge_id, user_id, source_url_list: List[str], selector: str, doc_strategy=None):
    handler = get_sync_web_document_handler(knowledge_id, user_id, doc_strategy)
    for source_url in source_url_list:
        try:
            result = Fork(base_fork_url=source_url, selector_list=get_selector_list(selector)).fork()
            handler(source_url, selector, result)
        except Exception as e:
            maxkb_logger.error(
                _("Synchronize web document:{source_url} error{error}{traceback}").format(
                    source_url=source_url, error=str(e), traceback=traceback.format_exc()
                )
            )
