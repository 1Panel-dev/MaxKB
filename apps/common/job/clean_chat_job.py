# coding=utf-8

import datetime

from django.db import transaction
from django.db.models import CharField, Q, Max
from django.db.models.functions import Cast
from django.utils import timezone

from application.models import Application, Chat, ChatRecord, ApplicationChatUserStats
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


def delete_orphan_chats(orphan_chat_ids):
    if not orphan_chat_ids:
        maxkb_logger.info('[clean_chat_log] delete_orphan_chats skipped, orphan_chat_ids is empty')
        return

    maxkb_logger.info(f'[clean_chat_log] start delete_orphan_chats, orphan_chat_count={len(orphan_chat_ids)}')
    orphan_chats = list(Chat.objects.filter(id__in=orphan_chat_ids))
    maxkb_logger.info(f'[clean_chat_log] loaded orphan chats, count={len(orphan_chats)}')

    # 按 (application_id, chat_user_id) 收集孤儿会话的用户，
    # 仅当该用户在该应用下不再有其它会话时才删除其访问统计，避免误删其他应用或仍活跃用户的统计
    app_user_ids = {}
    for chat in orphan_chats:
        if chat.chat_user_id:
            chat_user_id = str(chat.chat_user_id)
            app_user_ids.setdefault(chat.application_id, set()).add(chat_user_id)

    if app_user_ids:
        all_user_ids = set()
        for user_ids in app_user_ids.values():
            all_user_ids.update(user_ids)

        remaining_keys = Chat.objects.filter(
            application_id__in=app_user_ids.keys(),
            chat_user_id__in=all_user_ids,
        ).exclude(id__in=orphan_chat_ids).values_list('application_id', 'chat_user_id').distinct()

        remaining_app_user_ids = {}
        for app_id, user_id in remaining_keys:
            remaining_app_user_ids.setdefault(app_id, set()).add(user_id)

        for app_id, user_ids in app_user_ids.items():
            user_ids_to_delete = user_ids - remaining_app_user_ids.get(app_id, set())
            if user_ids_to_delete:
                maxkb_logger.info(
                    f'[clean_chat_log] delete application_chat_user_stats, '
                    f'application_id={app_id}, chat_user_count={len(user_ids_to_delete)}'
                )
                ApplicationChatUserStats.objects.annotate(
                    chat_user_id_str=Cast('chat_user_id', output_field=CharField(max_length=128))
                ).filter(
                    application_id=app_id,
                    chat_user_id_str__in=user_ids_to_delete,
                ).delete()

    deleted_chat_count, _ = Chat.objects.filter(id__in=orphan_chat_ids).delete()
    maxkb_logger.info(f'[clean_chat_log] delete orphan chats, count={deleted_chat_count}')


def clean_method(query_conditions, clean_log=True):
    batch_size = 500
    maxkb_logger.info(f'[clean_chat_log] start clean_method, clean_log={clean_log}, batch_size={batch_size}')
    while True:
        with transaction.atomic():
            chat_records = ChatRecord.objects.filter(query_conditions).select_related('chat').only('id', 'chat_id',
                                                                                                   'create_time')[
                           :batch_size]
            if not chat_records:
                maxkb_logger.info('[clean_chat_log] no more chat_records, break batch loop')
                break
            chat_record_ids = [record.id for record in chat_records]
            chat_ids = {record.chat_id for record in chat_records}
            maxkb_logger.info(
                f'[clean_chat_log] fetch batch chat_records, '
                f'chat_record_count={len(chat_record_ids)}, chat_count={len(chat_ids)}'
            )

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
                maxkb_logger.info(f'[clean_chat_log] delete chat_records, count={deleted_count}')

                from django.db.models import Count
                updated_counts = ChatRecord.objects.filter(chat_id__in=chat_ids) \
                    .values('chat_id') \
                    .annotate(count=Count('id'))

                count_map = {item['chat_id']: item['count'] for item in updated_counts}
                maxkb_logger.info(f'[clean_chat_log] remaining chat_record count_map={count_map}')

                for chat_id in chat_ids:
                    count = count_map.get(chat_id, 0)  # 如果没有记录则为0
                    Chat.objects.filter(id=chat_id).update(chat_record_count=count)

                # 删除已经没有关联 ChatRecord 的 Chat
                orphan_chat_ids = [chat_id for chat_id in chat_ids if count_map.get(chat_id, 0) == 0]
                maxkb_logger.info(
                    f'[clean_chat_log] orphan_chat_ids_count={len(orphan_chat_ids)}, '
                    f'orphan_chat_ids={orphan_chat_ids}'
                )
                delete_orphan_chats(orphan_chat_ids)
            File.objects.filter(loid__in=[file.loid for file in files_to_delete]).delete()

            if deleted_count < batch_size:
                break

    if clean_log:
        maxkb_logger.info('[clean_chat_log] start final orphan chat cleanup')
        orphan_chat_ids = list(
            Chat.objects.filter(chatrecord__isnull=True).values_list('id', flat=True)
        )
        maxkb_logger.info(f'[clean_chat_log] final orphan_chat_count={len(orphan_chat_ids)}')
        delete_orphan_chats(orphan_chat_ids)


def run():
    rlock = RedisLock()
    if rlock.try_lock('clean_chat_log_job', 30 * 30):
        try:
            maxkb_logger.debug('get lock clean_chat_log_job')

            existing_job = scheduler.get_job(job_id='clean_chat_log')
            if existing_job is not None:
                existing_job.remove()
            scheduler.add_job(clean_chat_log_job, 'interval', minutes=5, id='clean_chat_log',
                              misfire_grace_time=300, max_instances=1)
        finally:
            rlock.un_lock('clean_chat_log_job')
