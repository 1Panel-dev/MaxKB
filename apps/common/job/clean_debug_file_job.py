# coding=utf-8

import logging
from datetime import timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from django.db.models import Q
from django.utils import timezone
from django_apscheduler.jobstores import DjangoJobStore

from common.lock.impl.file_lock import FileLock
from dataset.models import File

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")
lock = FileLock()


def clean_debug_file():
    from django.utils.translation import gettext_lazy as _
    logging.getLogger("max_kb").info(_('start clean debug file'))
    two_hours_ago = timezone.now() - timedelta(hours=2)
    # 删除对应的文件
    File.objects.filter(Q(create_time__lt=two_hours_ago) & Q(meta__debug=True)).delete()
    logging.getLogger("max_kb").info(_('end clean debug file'))


def run():
    if lock.try_lock('clean_debug_file', 30 * 30):
        try:
            scheduler.start()
            clean_debug_file_job = scheduler.get_job(job_id='clean_debug_file')
            if clean_debug_file_job is not None:
                clean_debug_file_job.remove()
            scheduler.add_job(clean_debug_file, 'cron', hour='2', minute='0', second='0', id='clean_debug_file')
        finally:
            lock.un_lock('clean_debug_file')
