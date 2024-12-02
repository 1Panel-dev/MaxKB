# coding=utf-8

import logging
import datetime

from django.db import transaction
from django.db.models.fields.json import KeyTextTransform
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from application.models import Application, Chat
from django.db.models import Q
from common.lock.impl.file_lock import FileLock
from dataset.models import File
from django.db.models.functions import Cast
from django.db import models

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")
lock = FileLock()


def clean_chat_log_job():
    logging.getLogger("max_kb").info('开始清理对话记录')
    now = timezone.now()

    applications = Application.objects.all().values('id', 'clean_time')
    cutoff_dates = {
        app['id']: now - datetime.timedelta(days=app['clean_time'] or 180)
        for app in applications
    }

    query_conditions = Q()
    for app_id, cutoff_date in cutoff_dates.items():
        query_conditions |= Q(application_id=app_id, create_time__lt=cutoff_date)

    batch_size = 500
    while True:
        with transaction.atomic():
            logs_to_delete = Chat.objects.filter(query_conditions).values_list('id', flat=True)[:batch_size]
            count = logs_to_delete.count()
            logs_to_delete_str = [str(uuid) for uuid in logs_to_delete]
            if count == 0:
                break
            deleted_count, _ = Chat.objects.filter(id__in=logs_to_delete).delete()
            # 删除对应的文件
            File.objects.filter(meta__chat_id__in=logs_to_delete_str).delete()
            if deleted_count < batch_size:
                break

    logging.getLogger("max_kb").info(f'结束清理对话记录')


def run():
    if lock.try_lock('clean_chat_log_job', 30 * 30):
        try:
            scheduler.start()
            existing_job = scheduler.get_job(job_id='clean_chat_log')
            if existing_job is not None:
                existing_job.remove()
            scheduler.add_job(clean_chat_log_job, 'cron',  hour='0', minute='5', id='clean_chat_log')
        finally:
            lock.un_lock('clean_chat_log_job')
