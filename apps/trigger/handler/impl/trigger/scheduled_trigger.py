# coding=utf-8
from django.db.models import QuerySet

from common.utils.logger import maxkb_logger
from ops import celery_app
from trigger.handler.base_trigger import BaseTrigger
from trigger.models import TriggerTask


def _parse_hhmm(value: str) -> tuple[int, int]:
    hour_str, minute_str = (value or "").split(":")
    hour = int(hour_str)
    minute = int(minute_str)
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError("hour/minute out of range")
    return hour, minute


def _weekday_to_cron(d: int | str) -> str:
    mapping = {1: "mon", 2: "tue", 3: "wed", 4: "thu", 5: "fri", 6: "sat", 7: "sun", 0: "sun"}
    di = int(d)
    if di not in mapping:
        raise ValueError("invalid weekday")
    return mapping[di]


def _get_active_trigger_tasks(trigger_id: str) -> list[dict]:
    return list(
        QuerySet(TriggerTask)
        .filter(trigger_id=trigger_id, is_active=True)
        .values("id", "source_type", "source_id", "parameter", "trigger")
    )


def _deploy_daily(trigger: dict, trigger_tasks: list[dict], setting: dict, trigger_id: str) -> None:
    from common.job import scheduler

    times = setting.get("time") or []
    for t in times:
        try:
            hour, minute = _parse_hhmm(t)
        except Exception:
            maxkb_logger.warning(f"invalid time={t}, trigger_id={trigger_id}")
            continue

        for task in trigger_tasks:
            job_id = f"trigger:{trigger_id}:task:{task['id']}:daily:{hour:02d}{minute:02d}"
            scheduler.add_job(
                ScheduledTrigger.execute,
                trigger="cron",
                hour=str(hour),
                minute=str(minute),
                id=job_id,
                kwargs={"trigger": trigger, "trigger_task": task},
                replace_existing=True,
                misfire_grace_time=60,
                max_instances=1,
            )


def _deploy_weekly(trigger: dict, trigger_tasks: list[dict], setting: dict, trigger_id: str) -> None:
    from common.job import scheduler

    times = setting.get("time") or []
    days = setting.get("days") or []
    if not times or not days:
        maxkb_logger.warning(f"empty weekly setting, trigger_id={trigger_id}")
        return

    for d in days:
        try:
            dow = _weekday_to_cron(d)
        except Exception:
            maxkb_logger.warning(f"invalid weekday={d}, trigger_id={trigger_id}")
            continue

        for t in times:
            try:
                hour, minute = _parse_hhmm(t)
            except Exception:
                maxkb_logger.warning(f"invalid time={t}, trigger_id={trigger_id}")
                continue

            for task in trigger_tasks:
                job_id = f"trigger:{trigger_id}:task:{task['id']}:weekly:{dow}:{hour:02d}{minute:02d}"
                scheduler.add_job(
                    ScheduledTrigger.execute,
                    trigger="cron",
                    day_of_week=dow,
                    hour=str(hour),
                    minute=str(minute),
                    id=job_id,
                    kwargs={"trigger": trigger, "trigger_task": task},
                    replace_existing=True,
                    misfire_grace_time=60,
                    max_instances=1,
                )


def _deploy_monthly(trigger: dict, trigger_tasks: list[dict], setting: dict, trigger_id: str) -> None:
    from common.job import scheduler

    times = setting.get("time") or []
    days = setting.get("days") or []
    if not times or not days:
        maxkb_logger.warning(f"empty monthly setting, trigger_id={trigger_id}")
        return

    for d in days:
        try:
            dom = int(d)
            if not (1 <= dom <= 31):
                raise ValueError("invalid day of month")
        except Exception:
            maxkb_logger.warning(f"invalid day={d}, trigger_id={trigger_id}")
            continue

        for t in times:
            try:
                hour, minute = _parse_hhmm(t)
            except Exception:
                maxkb_logger.warning(f"invalid time={t}, trigger_id={trigger_id}")
                continue

            for task in trigger_tasks:
                job_id = f"trigger:{trigger_id}:task:{task['id']}:monthly:{dom:02d}:{hour:02d}{minute:02d}"
                scheduler.add_job(
                    ScheduledTrigger.execute,
                    trigger="cron",
                    day=str(dom),
                    hour=str(hour),
                    minute=str(minute),
                    id=job_id,
                    kwargs={"trigger": trigger, "trigger_task": task},
                    replace_existing=True,
                    misfire_grace_time=60,
                    max_instances=1,
                )

def _deploy_cron(trigger: dict, trigger_tasks: list[dict], setting: dict, trigger_id: str) -> None:
    from common.job import scheduler
    from apscheduler.triggers.cron import CronTrigger

    cron_expression = setting.get('cron_expression')
    if not cron_expression:
        maxkb_logger.warning(f"empty cron_expression, trigger_id={trigger_id}")
        return

    try:
        cron_trigger = CronTrigger.from_crontab(cron_expression.strip())
    except ValueError:
        maxkb_logger.warning(f"invalid cron_expression={cron_expression}, trigger_id={trigger_id}")
        return

    for task in trigger_tasks:
        job_id = f"trigger:{trigger_id}:task:{task['id']}:cron:{cron_expression.strip()}"
        scheduler.add_job(
            ScheduledTrigger.execute,
            trigger=cron_trigger,
            id=job_id,
            kwargs={"trigger": trigger, "trigger_task": task},
            replace_existing=True,
            misfire_grace_time=60,
            max_instances=1,
        )

def _deploy_interval(trigger: dict, trigger_tasks: list[dict], setting: dict, trigger_id: str) -> None:
    from common.job import scheduler

    unit = (setting.get("interval_unit") or "").strip()
    value = setting.get("interval_value")

    try:
        value_i = int(value)
        if value_i <= 0:
            raise ValueError("interval_value must be positive")
    except Exception:
        maxkb_logger.warning(f"invalid interval_value={value}, trigger_id={trigger_id}")
        return

    if unit not in {"seconds", "minutes", "hours", "days"}:
        maxkb_logger.warning(f"invalid interval_unit={unit}, trigger_id={trigger_id}")
        return

    for task in trigger_tasks:
        job_id = f"trigger:{trigger_id}:task:{task['id']}:interval:{unit}:{value_i}"
        scheduler.add_job(
            ScheduledTrigger.execute,
            trigger="interval",
            id=job_id,
            kwargs={"trigger": trigger, "trigger_task": task},
            replace_existing=True,
            misfire_grace_time=60,
            max_instances=1,
            **{unit: value_i},
        )

@celery_app.task(name="celery:undeploy_scheduled_trigger")
def _remove_trigger_jobs(trigger_id: str) -> None:
    from common.job import scheduler

    prefix = f"trigger:{trigger_id}:"
    for job in scheduler.get_jobs():
        if getattr(job, "id", "").startswith(prefix):
            try:
                job.remove()
            except Exception as e:
                maxkb_logger.warning(f"remove job failed, job_id={job.id}, err={e}")


@celery_app.task(name="celery:deploy_scheduled_trigger")
def deploy_scheduled_trigger(trigger: dict, trigger_tasks: list[dict], setting: dict, schedule_type: str) -> None:
    _remove_trigger_jobs(trigger["id"])

    deployers = {
        "daily": _deploy_daily,
        "weekly": _deploy_weekly,
        "monthly": _deploy_monthly,
        "interval": _deploy_interval,
        'cron': _deploy_cron
    }
    fn = deployers.get(schedule_type)
    if not fn:
        maxkb_logger.warning(f"unsupported schedule_type={schedule_type}, trigger_id={trigger['id']}")
        return

    fn(trigger, trigger_tasks, setting, trigger["id"])


class ScheduledTrigger(BaseTrigger):
    """
    定时任务触发器
    """

    @staticmethod
    def execute(trigger, **kwargs):
        trigger_task = kwargs.get("trigger_task")
        if not trigger_task:
            maxkb_logger.warning(f"unsupported task={trigger_task}")
            return
        source_type = trigger_task["source_type"]

        if source_type == "APPLICATION":
            from trigger.handler.impl.task.application_task import ApplicationTask

            ApplicationTask.execute(trigger_task, **kwargs)
        elif source_type == "TOOL":
            from trigger.handler.impl.task.tool_task import ToolTask

            ToolTask.execute(trigger_task, **kwargs)
        else:
            maxkb_logger.warning(f"unsupported source_type={source_type}, task_id={trigger_task['id']}")

    def support(self, trigger, **kwargs):
        return trigger.get("trigger_type") == "SCHEDULED"

    def deploy(self, trigger, **kwargs):
        trigger_id = str(trigger["id"])
        setting = trigger.get("trigger_setting") or {}
        schedule_type = setting.get("schedule_type")

        if not trigger.get("is_active", True):
            self.undeploy(trigger, **kwargs)
            return

        if trigger.get("trigger_type") != "SCHEDULED":
            self.undeploy(trigger, **kwargs)
            return

        trigger_tasks = _get_active_trigger_tasks(trigger["id"])
        if not trigger_tasks:
            maxkb_logger.warning(f"no active trigger_tasks, trigger_id={trigger_id}")
            self.undeploy(trigger, **kwargs)
            return

        deploy_scheduled_trigger.delay(trigger, trigger_tasks, setting, schedule_type)

    def undeploy(self, trigger, **kwargs):
        trigger_id = str(trigger["id"])

        _remove_trigger_jobs.delay(trigger_id)
