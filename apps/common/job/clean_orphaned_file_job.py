# coding=utf-8

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from django.db.models import Q
from django_apscheduler.jobstores import DjangoJobStore

from application.models import Chat
from common.lock.impl.file_lock import FileLock
from dataset.models import File

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")
lock = FileLock()


def clean_debug_file():
    logging.getLogger("max_kb").info('开始清理没有关联会话的上传文件')
    existing_chat_ids = set(Chat.objects.values_list('id', flat=True))
    # UUID to str
    existing_chat_ids = [str(chat_id) for chat_id in existing_chat_ids]
    print(existing_chat_ids)
    # 查找引用的不存在的 chat_id 并删除相关记录
    deleted_count, _ = File.objects.filter(~Q(meta__chat_id__in=existing_chat_ids)).delete()

    logging.getLogger("max_kb").info(f'结束清理没有关联会话的上传文件: {deleted_count}')


def run():
    if lock.try_lock('clean_orphaned_file_job', 30 * 30):
        try:
            scheduler.start()
            clean_orphaned_file = scheduler.get_job(job_id='clean_orphaned_file')
            if clean_orphaned_file is not None:
                clean_orphaned_file.remove()
            scheduler.add_job(clean_debug_file, 'cron', hour='2', minute='0', second='0',
                              id='clean_orphaned_file')
        finally:
            lock.un_lock('clean_orphaned_file_job')
