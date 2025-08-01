# -*- coding: utf-8 -*-
#
import os

from ..const import PROJECT_DIR, CONFIG, LOG_DIR

MAX_KB_LOG_FILE = os.path.join(LOG_DIR, 'maxkb.log')
DRF_EXCEPTION_LOG_FILE = os.path.join(LOG_DIR, 'drf_exception.log')
UNEXPECTED_EXCEPTION_LOG_FILE = os.path.join(LOG_DIR, 'unexpected_exception.log')
LOG_LEVEL = CONFIG.get_log_level()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'main': {
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'format': '%(asctime)s [%(module)s %(levelname)s] %(message)s',
        },
        'exception': {
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'format': '\n%(asctime)s [%(levelname)s] %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'syslog': {
            'format': 'maxkb: %(message)s'
        },
        'msg': {
            'format': '%(message)s'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'main'
        },
        'file': {
            'encoding': 'utf8',
            'level': 'DEBUG',
            'class': 'common.utils.logger.DailyTimedRotatingFileHandler',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'formatter': 'main',
            'filename': MAX_KB_LOG_FILE,
        },
        'drf_exception': {
            'encoding': 'utf8',
            'level': 'DEBUG',
            'class': 'common.utils.logger.DailyTimedRotatingFileHandler',
            'formatter': 'exception',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'filename': DRF_EXCEPTION_LOG_FILE,
        },
        'unexpected_exception': {
            'encoding': 'utf8',
            'level': 'DEBUG',
            'class': 'common.utils.logger.DailyTimedRotatingFileHandler',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'formatter': 'exception',
            'filename': UNEXPECTED_EXCEPTION_LOG_FILE,
        },
        'syslog': {
            'level': 'INFO',
            'class': 'logging.NullHandler',
            'formatter': 'syslog'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': False,
            'level': LOG_LEVEL,
        },
        'django.request': {
            'handlers': ['console', 'file', 'syslog'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'sqlalchemy': {
            'handlers': ['console', 'file', 'syslog'],
            'level': "ERROR",
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console', 'file', 'syslog'],
            'propagate': False,
            'level': LOG_LEVEL,
        },
        'django.server': {
            'handlers': ['console', 'file', 'syslog'],
            'level': 'ERROR',
            'propagate': False,
        },
        'max_kb': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'common.event': {
            'handlers': ['console', 'file'],
            'level': "DEBUG",
            'propagate': False,
        },
    }
}

SYSLOG_ENABLE = CONFIG.SYSLOG_ENABLE

if not os.path.isdir(LOG_DIR):
    os.makedirs(LOG_DIR, mode=0o755)
