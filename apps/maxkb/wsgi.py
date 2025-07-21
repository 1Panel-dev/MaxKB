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
    from common import event

    event.run()
    DatabaseModelManage.init()


def post_scheduler_handler():
    from common import job

    job.run()

# 启动后处理函数
post_handler()

# 仅在scheduler中启动定时任务，dev local_model celery 不需要
if os.environ.get('ENABLE_SCHEDULER') == '1':
    post_scheduler_handler()
