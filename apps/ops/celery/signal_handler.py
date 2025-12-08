# -*- coding: utf-8 -*-
#
import logging
import os

from celery import subtask
from celery.signals import (
    worker_ready, worker_shutdown, after_setup_logger, task_revoked, task_prerun
)
from django.core.cache import cache
from django_celery_beat.models import PeriodicTask

from common.utils.logger import maxkb_logger
from .decorator import get_after_app_ready_tasks, get_after_app_shutdown_clean_tasks
from .logger import CeleryThreadTaskFileHandler

logger = logging.getLogger(__file__)
safe_str = lambda x: x

def init_scheduler():
    from common import job

    job.run()

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
        periodic_task = PeriodicTask.objects.filter(task=task).first()
        if periodic_task and not periodic_task.enabled:
            logger.debug("Periodic task [{}] is disabled!".format(task))
            continue
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
    PeriodicTask.objects.filter(name__in=tasks).delete()


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
