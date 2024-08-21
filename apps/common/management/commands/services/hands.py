import logging
import os
import sys

from smartdoc.const import CONFIG, PROJECT_DIR

try:
    from apps.smartdoc import const

    __version__ = const.VERSION
except ImportError as e:
    print("Not found __version__: {}".format(e))
    print("Python is: ")
    logging.info(sys.executable)
    __version__ = 'Unknown'
    sys.exit(1)

HTTP_HOST = '0.0.0.0'
HTTP_PORT = CONFIG.HTTP_LISTEN_PORT or 8080
DEBUG = CONFIG.DEBUG or False

LOG_DIR = os.path.join(PROJECT_DIR, 'data', 'logs')
APPS_DIR = os.path.join(PROJECT_DIR, 'apps')
TMP_DIR = os.path.join(PROJECT_DIR, 'tmp')
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)
