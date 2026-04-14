# coding=utf-8

import datetime

from django.db import transaction
from django.db.models import Q, Max
from django.utils import timezone

from application.models import Application, Chat, ChatRecord
from common.job.scheduler import scheduler
from common.utils.lock import lock, RedisLock
from common.utils.logger import maxkb_logger
from knowledge.models import File


def clean_chat_log_job():
    clean_chat_log_job_lock()


@lock(lock_key='clean_chat_log_job_execute', timeout=30)
def clean_chat_log_job_lock():
    from django.utils.translation import gettext_lazy as _
    maxkb_logger.info(_('start clean chat log'))
    now = timezone.now()

    applications = Application.objects.all().values('id', 'clean_time', 'file_clean_time')
    cutoff_dates = {
        app['id']: now - datetime.timedelta(days=app['clean_time'] or 180)
        for app in applications
    }
    file_cutoff_dates = {
        app['id']: now - datetime.timedelta(days=app['file_clean_time'] or app['clean_time'] or 180)
        for app in applications
    }
    file_conditions = Q()
    for app_id, cutoff_date in file_cutoff_dates.items():
        file_conditions |= Q(chat__application_id=app_id, create_time__lt=cutoff_date)
    clean_method(file_conditions, clean_log=False)

    query_conditions = Q()
    for app_id, cutoff_date in cutoff_dates.items():
        query_conditions |= Q(chat__application_id=app_id, create_time__lt=cutoff_date)
    clean_method(query_conditions)

    maxkb_logger.info(_('end clean chat log'))


def clean_method(query_conditions, clean_log=True):
    batch_size = 500
    while True:
        with transaction.atomic():
            chat_records = ChatRecord.objects.filter(query_conditions).select_related('chat').only('id', 'chat_id',
                                                                                                   'create_time')[
                           :batch_size]
            if not chat_records:
                break
            chat_record_ids = [record.id for record in chat_records]
            chat_ids = {record.chat_id for record in chat_records}

            # 计算每个 chat_id 的最大 create_time
            max_create_times = ChatRecord.objects.filter(id__in=chat_record_ids).values('chat_id').annotate(
                max_create_time=Max('create_time'))

            # 收集需要删除的文件
            files_to_delete = []
            for record in chat_records:
                max_create_time = next(
                    (item['max_create_time'] for item in max_create_times if
                     str(item['chat_id']) == str(record.chat_id)), None)
                if max_create_time:
                    files_to_delete.extend(
                        File.objects.filter(source_id=str(record.chat_id), create_time__lt=max_create_time)
                    )
            # 删除 ChatRecord
            deleted_count = 0
            if clean_log:
                deleted_count = ChatRecord.objects.filter(id__in=chat_record_ids).delete()[0]

                from django.db.models import Count
                updated_counts = ChatRecord.objects.filter(chat_id__in=chat_ids) \
                    .values('chat_id') \
                    .annotate(count=Count('id'))

                count_map = {item['chat_id']: item['count'] for item in updated_counts}

                for chat_id in chat_ids:
                    count = count_map.get(chat_id, 0)  # 如果没有记录则为0
                    Chat.objects.filter(id=chat_id).update(chat_record_count=count)

                # 删除没有关联 ChatRecord 的 Chat
                Chat.objects.filter(chatrecord__isnull=True, id__in=chat_ids).delete()
            File.objects.filter(loid__in=[file.loid for file in files_to_delete]).delete()

            if deleted_count < batch_size:
                break


def run():
    rlock = RedisLock()
    if rlock.try_lock('clean_chat_log_job', 30 * 30):
        try:
            maxkb_logger.debug('get lock clean_chat_log_job')

            existing_job = scheduler.get_job(job_id='clean_chat_log')
            if existing_job is not None:
                existing_job.remove()
            scheduler.add_job(clean_chat_log_job, 'cron', hour='0', minute='5', id='clean_chat_log',
                              misfire_grace_time=300, max_instances=1)
        finally:
            rlock.un_lock('clean_chat_log_job')
