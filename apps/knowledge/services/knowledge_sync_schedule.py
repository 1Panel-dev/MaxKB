"""APScheduler integration for scheduled external knowledge synchronization."""

import importlib
import re

from apscheduler.triggers.cron import CronTrigger
from django.db.models import QuerySet

from common.utils.logger import maxkb_logger
from knowledge.models import Knowledge, KnowledgeType
from knowledge.task.sync import scheduled_sync_knowledge


KNOWLEDGE_SYNC_JOB_PREFIX = "knowledge:sync:"
LEGACY_WEB_SYNC_JOB_PREFIX = "knowledge:web-sync:"
DEFAULT_KNOWLEDGE_SYNC_SETTING = {
    "enabled": False,
    "schedule_type": "daily",
    "time": "01:00",
    "cron_expression": "0 1 * * *",
    "sync_type": "incremental",
}
KNOWLEDGE_SYNC_TYPES = {"incremental", "replace", "complete"}
SCHEDULED_KNOWLEDGE_TYPES = {KnowledgeType.WEB, KnowledgeType.LARK, KnowledgeType.WORKFLOW}
TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


def _get_scheduler():
    """Load the scheduler only when a job is deployed, not during API module import."""
    return importlib.import_module("common.job.scheduler").scheduler


def knowledge_sync_job_id(knowledge_id) -> str:
    return f"{KNOWLEDGE_SYNC_JOB_PREFIX}{knowledge_id}"


def normalize_knowledge_sync_setting(setting=None) -> dict:
    value = {**DEFAULT_KNOWLEDGE_SYNC_SETTING, **(setting or {})}
    value["enabled"] = bool(value.get("enabled", False))
    if value.get("schedule_type") not in {"daily", "cron"}:
        raise ValueError("schedule_type must be daily or cron")
    if value.get("sync_type") not in KNOWLEDGE_SYNC_TYPES:
        raise ValueError("sync_type must be incremental, replace or complete")
    if value["schedule_type"] == "daily":
        time_value = str(value.get("time") or "").strip()
        match = TIME_PATTERN.fullmatch(time_value)
        if match is None:
            raise ValueError("time must use HH:MM format")
        value["time"] = time_value
        value["cron_expression"] = f"{int(match.group(2))} {int(match.group(1))} * * *"
    else:
        expression = str(value.get("cron_expression") or "").strip()
        if not expression:
            raise ValueError("cron_expression is required")
        CronTrigger.from_crontab(expression)
        value["cron_expression"] = expression
    return value


def enqueue_scheduled_knowledge_sync(knowledge_id: str):
    scheduled_sync_knowledge.delay(str(knowledge_id))


def remove_knowledge_sync_job(knowledge_id) -> None:
    scheduler = _get_scheduler()
    for job_id in [knowledge_sync_job_id(knowledge_id), f"{LEGACY_WEB_SYNC_JOB_PREFIX}{knowledge_id}"]:
        job = scheduler.get_job(job_id)
        if job is not None:
            job.remove()


def deploy_knowledge_sync_job(knowledge_id) -> bool:
    scheduler = _get_scheduler()
    remove_knowledge_sync_job(knowledge_id)
    knowledge = QuerySet(Knowledge).filter(id=knowledge_id, type__in=SCHEDULED_KNOWLEDGE_TYPES).first()
    if knowledge is None:
        return False
    try:
        setting = normalize_knowledge_sync_setting((knowledge.meta or {}).get("sync_setting"))
    except ValueError as exc:
        maxkb_logger.warning(f"Invalid knowledge sync setting, knowledge_id={knowledge_id}: {exc}")
        return False
    if not setting["enabled"]:
        return False
    scheduler.add_job(
        enqueue_scheduled_knowledge_sync,
        trigger=CronTrigger.from_crontab(setting["cron_expression"]),
        id=knowledge_sync_job_id(knowledge.id),
        args=[str(knowledge.id)],
        replace_existing=True,
        misfire_grace_time=300,
        max_instances=1,
        coalesce=True,
    )
    return True


def restore_knowledge_sync_jobs() -> None:
    scheduler = _get_scheduler()
    active_ids = {
        str(knowledge_id)
        for knowledge_id in QuerySet(Knowledge)
        .filter(type__in=SCHEDULED_KNOWLEDGE_TYPES, meta__sync_setting__enabled=True)
        .values_list("id", flat=True)
    }
    for job in scheduler.get_jobs():
        job_id = getattr(job, "id", "")
        if (
            job_id.startswith(KNOWLEDGE_SYNC_JOB_PREFIX)
            and job_id.removeprefix(KNOWLEDGE_SYNC_JOB_PREFIX) not in active_ids
        ):
            job.remove()
        elif job_id.startswith(LEGACY_WEB_SYNC_JOB_PREFIX):
            job.remove()
    for knowledge_id in active_ids:
        deploy_knowledge_sync_job(knowledge_id)
