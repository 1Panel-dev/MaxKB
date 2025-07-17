"""
WSGI config for maxkb project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maxkb.settings')

application = get_wsgi_application()



def post_handler():
    from common.database_model_manage.database_model_manage import DatabaseModelManage
    from common import job
    from common import event

    event.run()
    job.run()
    DatabaseModelManage.init()

# 仅在web中启动定时任务，local_model celery 不需要
if os.environ.get('ENABLE_SCHEDULER') == '1':
    post_handler()


