# -*- coding: utf-8 -*-
#
import logging
import os
import uuid_utils.compat as uuid

from celery import subtask
from celery.signals import (
    worker_ready, worker_shutdown, after_setup_logger, task_revoked, task_prerun
)
from django.core.cache import cache
from django_apscheduler.models import DjangoJob

from common.utils.logger import maxkb_logger
from .decorator import get_after_app_ready_tasks, get_after_app_shutdown_clean_tasks
from .logger import CeleryThreadTaskFileHandler

logger = logging.getLogger(__file__)
safe_str = lambda x: x


def init_scheduler():
    from common import job
    from common.init import init_template
    from trigger.models import Trigger

    job.run()
    init_template.run()

    # 清理已经不存在的 trigger job
    trigger_jobs = DjangoJob.objects.filter(id__startswith="trigger:")
    # 从 job id 中提取 trigger_id (格式: trigger:<trigger_id>:task:...)
    trigger_ids_from_jobs = set()
    job_id_to_trigger_id = {}  # 映射 job_id -> trigger_id

    for job in trigger_jobs:
        parts = job.id.split(':')
        if len(parts) >= 2:
            trigger_id = uuid.UUID(parts[1])  # 提取 trigger_id
            trigger_ids_from_jobs.add(trigger_id)
            job_id_to_trigger_id[job.id] = trigger_id

    # 获取所有有效的 Trigger ID
    valid_trigger_ids = set(Trigger.objects.filter(
        id__in=trigger_ids_from_jobs, is_active=True
    ).values_list('id', flat=True))

    # 找出需要删除的 job (trigger 已不存在的)
    jobs_to_delete = [
        job_id for job_id, trigger_id in job_id_to_trigger_id.items()
        if trigger_id not in valid_trigger_ids
    ]

    if jobs_to_delete:
        DjangoJob.objects.filter(id__in=jobs_to_delete).delete()
        logger.info(f"Cleaned up {len(jobs_to_delete)} orphaned trigger jobs")

    try:
        from xpack import job as xpack_job

        xpack_job.run()
    except ImportError:
        pass


@worker_ready.connect
def on_app_ready(sender=None, headers=None, **kwargs):
    if cache.get("CELERY_APP_READY", 0) == 1:
        return
    cache.set("CELERY_APP_READY", 1, 10)
    # 初始化定时任务
    init_scheduler()

    tasks = get_after_app_ready_tasks()
    logger.debug("Work ready signal recv")
    logger.debug("Start need start task: [{}]".format(", ".join(tasks)))
    for task in tasks:
        subtask(task).delay()


def delete_files(directory):
    if os.path.isdir(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)


@worker_shutdown.connect
def after_app_shutdown_periodic_tasks(sender=None, **kwargs):
    if cache.get("CELERY_APP_SHUTDOWN", 0) == 1:
        return
    cache.set("CELERY_APP_SHUTDOWN", 1, 10)
    tasks = get_after_app_shutdown_clean_tasks()
    logger.debug("Worker shutdown signal recv")
    logger.debug("Clean period tasks: [{}]".format(', '.join(tasks)))


@after_setup_logger.connect
def add_celery_logger_handler(sender=None, logger=None, loglevel=None, format=None, **kwargs):
    if not logger:
        return
    task_handler = CeleryThreadTaskFileHandler()
    task_handler.setLevel(loglevel)
    formatter = logging.Formatter(format)
    task_handler.setFormatter(formatter)
    logger.addHandler(task_handler)


@task_revoked.connect
def on_task_revoked(request, terminated, signum, expired, **kwargs):
    maxkb_logger.info('task_revoked', terminated)


@task_prerun.connect
def on_taskaa_start(sender, task_id, **kwargs):
    pass
    # sender.update_state(state='REVOKED',
#                     meta={'exc_type': 'Exception', 'exc': 'Exception', 'message': '暂停任务', 'exc_message': ''})
