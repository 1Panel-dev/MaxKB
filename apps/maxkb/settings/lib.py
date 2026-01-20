# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： lib.py
    @date：2024/8/16 17:12
    @desc:
"""
import os

from redis.sentinel import Sentinel

from maxkb.const import CONFIG, PROJECT_DIR, LOG_DIR

# celery相关配置
celery_data_dir = os.path.join(PROJECT_DIR, 'data', 'celery_task')
if not os.path.exists(celery_data_dir) or not os.path.isdir(celery_data_dir):
    os.makedirs(celery_data_dir, 0o700, exist_ok=True)
    os.chmod(os.path.dirname(celery_data_dir), 0o700)
# Celery using redis as broker
redis_celery_once_db = CONFIG.get("REDIS_DB")
redis_celery_db = CONFIG.get('REDIS_DB')
CELERY_BROKER_URL_FORMAT = '%(protocol)s://:%(password)s@%(host)s:%(port)s/%(db)s'
if CONFIG.get('REDIS_SENTINEL_MASTER') and CONFIG.get('REDIS_SENTINEL_SENTINELS'):
    sentinels_str = CONFIG.get('REDIS_SENTINEL_SENTINELS')
    sentinels = [
        (host.strip(), int(port))
        for hostport in sentinels_str.split(',')
        for host, port in [hostport.strip().split(':')]
    ]
    CELERY_BROKER_URL = ';'.join([CELERY_BROKER_URL_FORMAT % {
        'protocol': 'sentinel', 'password': CONFIG.get('REDIS_PASSWORD'),
        'host': item[0], 'port': item[1], 'db': redis_celery_db
    } for item in sentinels])
    SENTINEL_OPTIONS = {
        'master_name': CONFIG.get('REDIS_SENTINEL_MASTER'),
    }
    CELERY_BROKER_TRANSPORT_OPTIONS = CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS = SENTINEL_OPTIONS

    # celery-once 哨兵模式配置
    sentinel = Sentinel(
        sentinels,
        socket_timeout=5,
        password=CONFIG.get('REDIS_SENTINEL_PASSWORD', CONFIG.get('REDIS_PASSWORD'))
    )
    master_host, master_port = sentinel.discover_master(CONFIG.get('REDIS_SENTINEL_MASTER'))
    celery_once_settings = {
        'url': f"redis://:{CONFIG.get('REDIS_PASSWORD')}@{master_host}:{master_port}/{redis_celery_once_db}",
        'master_name': CONFIG.get('REDIS_SENTINEL_MASTER'),
        'password': CONFIG.get('REDIS_PASSWORD'),
        'db': redis_celery_once_db,
    }
else:
    CELERY_BROKER_URL = CELERY_BROKER_URL_FORMAT % {
        'protocol': 'redis',
        'password': CONFIG.get('REDIS_PASSWORD'),
        'host': CONFIG.get('REDIS_HOST'),
        'port': CONFIG.get('REDIS_PORT'),
        'db': redis_celery_db
    }
    # celery-once 常规模式配置
    celery_once_settings = {
        'url': CELERY_BROKER_URL_FORMAT % {
            'protocol': 'redis',
            'password': CONFIG.get('REDIS_PASSWORD'),
            'host': CONFIG.get('REDIS_HOST'),
            'port': CONFIG.get('REDIS_PORT'),
            'db': redis_celery_once_db,
        }
    }
CELERY_result_backend = CELERY_BROKER_URL
CELERY_timezone = CONFIG.get_time_zone()
CELERY_ENABLE_UTC = False
CELERY_task_serializer = 'hmac_signed_serializer'
CELERY_result_serializer = 'hmac_signed_serializer'
CELERY_accept_content = ['json', 'hmac_signed_serializer']
CELERY_RESULT_EXPIRES = 600
CELERY_WORKER_TASK_LOG_FORMAT = '%(asctime).19s %(message)s'
CELERY_WORKER_LOG_FORMAT = '%(asctime).19s %(message)s'
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_WORKER_REDIRECT_STDOUTS = True
CELERY_WORKER_REDIRECT_STDOUTS_LEVEL = "INFO"
CELERY_TASK_SOFT_TIME_LIMIT = 3600
CELERY_WORKER_CANCEL_LONG_RUNNING_TASKS_ON_CONNECTION_LOSS = True
# celery-once 配置
celery_once_settings['default_timeout'] = 3600  # 锁的默认超时时间（秒）
CELERY_ONCE = {
    'backend': 'celery_once.backends.Redis',
    'settings': celery_once_settings
}
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_LOG_DIR = os.path.join(LOG_DIR, 'celery')
