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

from application.models.api_key_model import ApplicationPublicAccessClient

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


def client_access_num_reset_job():
    logging.getLogger("max_kb").info('开始重置access_num')
    QuerySet(ApplicationPublicAccessClient).update(intraday_access_num=0)
    logging.getLogger("max_kb").info('结束重置access_num')


def run():
    scheduler.start()
    access_num_reset = scheduler.get_job(job_id='access_num_reset')
    if access_num_reset is not None:
        access_num_reset.remove()
    scheduler.add_job(client_access_num_reset_job, 'cron', hour='0', minute='0', second='0',
                      id='access_num_reset')
