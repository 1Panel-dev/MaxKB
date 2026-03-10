# -*- coding: utf-8 -*-
#
import os

from dotenv import load_dotenv

from .conf import ConfigManager

__all__ = ['BASE_DIR', 'PROJECT_DIR', 'VERSION', 'CONFIG']

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join('/', 'opt', 'maxkb', 'logs')
PROJECT_DIR = os.path.dirname(BASE_DIR)
VERSION = '2.0.0'

# load environment variables from .env file
load_dotenv()
# 直接从 /opt/maxkb/conf 目录加载配置
CONFIG = ConfigManager.load_user_config(root_path=os.path.abspath('/opt/maxkb/conf'))

