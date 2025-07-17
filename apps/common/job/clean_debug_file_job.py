# coding=utf-8
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from common.job.scheduler import scheduler
from common.utils.lock import lock, RedisLock
from common.utils.logger import maxkb_logger
from knowledge.models import File, FileSourceType


def clean_debug_file():
    clean_debug_file_lock()


@lock(lock_key='clean_debug_file_execute', timeout=30)
def clean_debug_file_lock():
    from django.utils.translation import gettext_lazy as _
    maxkb_logger.debug(_('start clean debug file'))
    minutes_30_ago = timezone.now() - timedelta(minutes=30)
    two_hours_ago = timezone.now() - timedelta(hours=2)
    one_days_ago = timezone.now() - timedelta(hours=24)
    # 删除对应的文件
    File.objects.filter(
        Q(create_time__lt=one_days_ago, source_type=FileSourceType.TEMPORARY_1_DAY.value) |
        Q(create_time__lt=two_hours_ago, source_type=FileSourceType.TEMPORARY_120_MINUTE.value) |
        Q(create_time__lt=minutes_30_ago, source_type=FileSourceType.TEMPORARY_30_MINUTE.value)
    ).delete()
    maxkb_logger.debug(_('end clean debug file'))


def run():
    rlock = RedisLock()
    if rlock.try_lock('clean_debug_file', 30 * 30):
        try:
            maxkb_logger.debug('get lock clean_debug_file')

            clean_debug_file_job = scheduler.get_job(job_id='clean_debug_file')
            if clean_debug_file_job is not None:
                clean_debug_file_job.remove()
            scheduler.add_job(clean_debug_file, 'cron', hour='*', minute='*/30', second='0', id='clean_debug_file')
        finally:
            rlock.un_lock('clean_debug_file')
