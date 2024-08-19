# -*- coding: utf-8 -*-
#
import logging
import os
import uuid

from django.conf import settings
from django_celery_beat.models import (
    PeriodicTasks
)

from smartdoc.const import PROJECT_DIR

logger = logging.getLogger(__file__)


def disable_celery_periodic_task(task_name):
    from django_celery_beat.models import PeriodicTask
    PeriodicTask.objects.filter(name=task_name).update(enabled=False)
    PeriodicTasks.update_changed()


def delete_celery_periodic_task(task_name):
    from django_celery_beat.models import PeriodicTask
    PeriodicTask.objects.filter(name=task_name).delete()
    PeriodicTasks.update_changed()


def get_celery_periodic_task(task_name):
    from django_celery_beat.models import PeriodicTask
    task = PeriodicTask.objects.filter(name=task_name).first()
    return task


def make_dirs(name, mode=0o755, exist_ok=False):
    """ 默认权限设置为 0o755 """
    return os.makedirs(name, mode=mode, exist_ok=exist_ok)


def get_task_log_path(base_path, task_id, level=2):
    task_id = str(task_id)
    try:
        uuid.UUID(task_id)
    except:
        return os.path.join(PROJECT_DIR, 'data', 'caution.txt')

    rel_path = os.path.join(*task_id[:level], task_id + '.log')
    path = os.path.join(base_path, rel_path)
    make_dirs(os.path.dirname(path), exist_ok=True)
    return path


def get_celery_task_log_path(task_id):
    return get_task_log_path(settings.CELERY_LOG_DIR, task_id)


def get_celery_status():
    from . import app
    i = app.control.inspect()
    ping_data = i.ping() or {}
    active_nodes = [k for k, v in ping_data.items() if v.get('ok') == 'pong']
    active_queue_worker = set([n.split('@')[0] for n in active_nodes if n])
    # Celery Worker 数量: 2
    if len(active_queue_worker) < 2:
        print("Not all celery worker worked")
        return False
    else:
        return True
