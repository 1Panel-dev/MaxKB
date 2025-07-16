# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： client_access_num_job.py
    @date：2024/3/14 11:56
    @desc:
"""
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from django.db.models import QuerySet
from django_apscheduler.jobstores import DjangoJobStore

from application.models import ApplicationChatUserStats
from common.utils.lock import try_lock, un_lock, lock
from common.utils.logger import maxkb_logger

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


def client_access_num_reset_job():
    client_access_num_reset_job_lock()


@lock(lock_key="access_num_reset_execute", timeout=30)
def client_access_num_reset_job_lock():
    from django.utils.translation import gettext_lazy as _
    maxkb_logger.info(_('start reset access_num'))
    QuerySet(ApplicationChatUserStats).update(intraday_access_num=0)
    maxkb_logger.info(_('end reset access_num'))


def run():
    if try_lock('access_num_reset', 30 * 30):
        try:
            scheduler.start()
            access_num_reset = scheduler.get_job(job_id='access_num_reset')
            if access_num_reset is not None:
                access_num_reset.remove()
            scheduler.add_job(client_access_num_reset_job, 'cron', hour='0', minute='0', second='0',
                              id='access_num_reset')
        finally:
            un_lock('access_num_reset')
