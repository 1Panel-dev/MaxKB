# -*- coding: utf-8 -*-

import os

from celery import Celery
from kombu import Exchange, Queue
from maxkb import settings
from .heartbeat import *
from .hmac_signed_serializer import register_hmac_signed_serializer

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maxkb.settings')

register_hmac_signed_serializer()

app = Celery('MaxKB')

configs = {k: v for k, v in settings.__dict__.items() if k.startswith('CELERY')}
configs['worker_concurrency'] = 5
# Using a string here means the worker will not have to
# pickle the object when using Windows.
# app.config_from_object('django.conf:settings', namespace='CELERY')

configs["task_queues"] = [
    Queue("celery", Exchange("celery"), routing_key="celery"),
    Queue("model", Exchange("model"), routing_key="model")
]
app.namespace = 'CELERY'
app.conf.update(
    {key.replace('CELERY_', '') if key.replace('CELERY_', '').lower() == key.replace('CELERY_',
                                                                                     '') else key: configs.get(
        key) for
        key
        in configs.keys()})
app.autodiscover_tasks(lambda: [app_config.split('.')[0] for app_config in settings.INSTALLED_APPS])
