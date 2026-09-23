"""APScheduler integration for scheduled external knowledge synchronization."""

import importlib
import re
from datetime import timedelta

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from django.db.models import QuerySet
from django.utils import timezone

from common.utils.logger import maxkb_logger
from knowledge.models import Knowledge, KnowledgeType
from knowledge.task.sync import scheduled_sync_knowledge


KNOWLEDGE_SYNC_JOB_PREFIX = "knowledge:sync:"
LEGACY_WEB_SYNC_JOB_PREFIX = "knowledge:web-sync:"
DEFAULT_KNOWLEDGE_SYNC_SETTING = {
    "enabled": False,
    "schedule_type": "daily",
    "time": ["01:00"],
    "sync_type": "incremental",
}
KNOWLEDGE_SYNC_TYPES = {"incremental", "replace", "complete"}
SCHEDULED_KNOWLEDGE_TYPES = {KnowledgeType.WEB, KnowledgeType.LARK, KnowledgeType.WORKFLOW}
TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")
MIN_SYNC_INTERVAL = timedelta(minutes=5)


def _get_scheduler():
    """Load the scheduler only when a job is deployed, not during API module import."""
    return importlib.import_module("common.job.scheduler").scheduler


def knowledge_sync_job_id(knowledge_id) -> str:
    return f"{KNOWLEDGE_SYNC_JOB_PREFIX}{knowledge_id}"


def normalize_knowledge_sync_setting(setting=None) -> dict:
    value = setting or DEFAULT_KNOWLEDGE_SYNC_SETTING
    schedule_type = value.get("schedule_type")
    if schedule_type not in {"daily", "weekly", "monthly", "interval", "cron"}:
        raise ValueError("schedule_type must be daily, weekly, monthly, interval or cron")
    if value.get("sync_type") not in KNOWLEDGE_SYNC_TYPES:
        raise ValueError("sync_type must be incremental, replace or complete")
    normalized = {
        "enabled": bool(value.get("enabled", False)),
        "schedule_type": schedule_type,
        "sync_type": value["sync_type"],
    }
    if schedule_type in {"daily", "weekly", "monthly"}:
        times = value.get("time")
        times = [times] if isinstance(times, str) else times
        if (
            not isinstance(times, list)
            or not times
            or any(not isinstance(t, str) or not TIME_PATTERN.fullmatch(t) for t in times)
        ):
            raise ValueError("time must be a non-empty list of HH:MM values")
        normalized["time"] = times
        if schedule_type in {"weekly", "monthly"}:
            days = value.get("days")
            max_day = 7 if schedule_type == "weekly" else 31
            if (
                not isinstance(days, list)
                or not days
                or any(isinstance(day, bool) or not str(day).isdigit() or not 1 <= int(day) <= max_day for day in days)
            ):
                raise ValueError(f"days must contain values from 1 to {max_day}")
            normalized["days"] = [int(day) for day in days]
    elif schedule_type == "interval":
        unit = value.get("interval_unit")
        interval = value.get("interval_value")
        if unit not in {"minutes", "hours"} or isinstance(interval, bool) or not isinstance(interval, int):
            raise ValueError("interval requires an integer value in minutes or hours")
        normalized["interval_unit"] = unit
        normalized["interval_value"] = interval
    else:
        expression = str(value.get("cron_expression") or "").strip()
        if not expression:
            raise ValueError("cron_expression is required")
        CronTrigger.from_crontab(expression)
        normalized["cron_expression"] = expression
    _validate_min_frequency(knowledge_sync_triggers(normalized))
    return normalized


def knowledge_sync_triggers(setting: dict) -> list:
    schedule_type = setting["schedule_type"]
    if schedule_type == "cron":
        return [CronTrigger.from_crontab(setting["cron_expression"])]
    if schedule_type == "interval":
        return [IntervalTrigger(**{setting["interval_unit"]: setting["interval_value"]})]
    fields = {}
    if schedule_type == "weekly":
        fields["day_of_week"] = ",".join(str((day - 1) % 7) for day in setting["days"])
    elif schedule_type == "monthly":
        fields["day"] = ",".join(str(day) for day in setting["days"])
    return [CronTrigger(hour=int(time[:2]), minute=int(time[3:]), **fields) for time in setting["time"]]


def _validate_min_frequency(triggers: list) -> None:
    now = timezone.now()
    next_fires = [trigger.get_next_fire_time(None, now) for trigger in triggers]
    previous_fire = None
    for _ in range(512):
        pending = [(fire, index) for index, fire in enumerate(next_fires) if fire is not None]
        if not pending:
            break
        fire, index = min(pending)
        if previous_fire is not None and fire - previous_fire < MIN_SYNC_INTERVAL:
            raise ValueError("Synchronization interval must be at least 5 minutes")
        previous_fire = fire
        next_fires[index] = triggers[index].get_next_fire_time(fire, fire + timedelta(microseconds=1))


def enqueue_scheduled_knowledge_sync(knowledge_id: str):
    scheduled_sync_knowledge.delay(str(knowledge_id))


def remove_knowledge_sync_job(knowledge_id) -> None:
    scheduler = _get_scheduler()
    prefix = knowledge_sync_job_id(knowledge_id)
    for job in scheduler.get_jobs():
        if job.id in {prefix, f"{LEGACY_WEB_SYNC_JOB_PREFIX}{knowledge_id}"} or job.id.startswith(f"{prefix}:"):
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
    triggers = knowledge_sync_triggers(setting)
    for index, trigger in enumerate(triggers):
        scheduler.add_job(
            enqueue_scheduled_knowledge_sync,
            trigger=trigger,
            id=knowledge_sync_job_id(knowledge.id) + (f":{index}" if len(triggers) > 1 else ""),
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
            and job_id.removeprefix(KNOWLEDGE_SYNC_JOB_PREFIX).split(":", 1)[0] not in active_ids
        ):
            job.remove()
        elif job_id.startswith(LEGACY_WEB_SYNC_JOB_PREFIX):
            job.remove()
    for knowledge_id in active_ids:
        deploy_knowledge_sync_job(knowledge_id)
