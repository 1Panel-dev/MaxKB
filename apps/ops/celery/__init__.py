# -*- coding: utf-8 -*-

import os

from celery import Celery
from kombu import Exchange, Queue
from celery.app.log import Logging
from smartdoc import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartdoc.settings')
from .heatbeat import *

app = Celery('MaxKB')

configs = {k: v for k, v in settings.__dict__.items() if k.startswith('CELERY')}
# Using a string here means the worker will not have to
# pickle the object when using Windows.
# app.config_from_object('django.conf:settings', namespace='CELERY')

configs["CELERY_QUEUES"] = [
    Queue("celery", Exchange("celery"), routing_key="celery"),
]

app.namespace = 'CELERY'
app.conf.update(configs)
app.autodiscover_tasks(lambda: [app_config.split('.')[0] for app_config in settings.INSTALLED_APPS])
log = Logging(app)
