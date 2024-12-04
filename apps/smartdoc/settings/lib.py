# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： lib.py
    @date：2024/8/16 17:12
    @desc:
"""
import os
import shutil

from smartdoc.const import CONFIG, PROJECT_DIR

# celery相关配置
celery_data_dir = os.path.join(PROJECT_DIR, 'data', 'celery_task')
if not os.path.exists(celery_data_dir) or not os.path.isdir(celery_data_dir):
    os.makedirs(celery_data_dir)
broker_path = os.path.join(celery_data_dir, "celery_db.sqlite3")
backend_path = os.path.join(celery_data_dir, "celery_results.sqlite3")
# 使用sql_lite 当做broker 和 响应接收
CELERY_BROKER_URL = f'sqla+sqlite:///{broker_path}'
CELERY_result_backend = f'db+sqlite:///{backend_path}'
CELERY_timezone = CONFIG.TIME_ZONE
CELERY_ENABLE_UTC = False
CELERY_task_serializer = 'pickle'
CELERY_result_serializer = 'pickle'
CELERY_accept_content = ['json', 'pickle']
CELERY_RESULT_EXPIRES = 600
CELERY_WORKER_TASK_LOG_FORMAT = '%(asctime).19s %(message)s'
CELERY_WORKER_LOG_FORMAT = '%(asctime).19s %(message)s'
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_WORKER_REDIRECT_STDOUTS = True
CELERY_WORKER_REDIRECT_STDOUTS_LEVEL = "INFO"
CELERY_TASK_SOFT_TIME_LIMIT = 3600
CELERY_WORKER_CANCEL_LONG_RUNNING_TASKS_ON_CONNECTION_LOSS = True
CELERY_ACKS_LATE = True
celery_once_path = os.path.join(celery_data_dir, "celery_once")
try:
    if os.path.exists(celery_once_path) and os.path.isdir(celery_once_path):
        shutil.rmtree(celery_once_path)
except Exception as e:
    pass
CELERY_ONCE = {
    'backend': 'celery_once.backends.File',
    'settings': {'location': celery_once_path}
}
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_LOG_DIR = os.path.join(PROJECT_DIR, 'logs', 'celery')
