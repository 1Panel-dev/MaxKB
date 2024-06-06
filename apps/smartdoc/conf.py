# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""
配置分类：
1. Django使用的配置文件，写到settings中
2. 程序需要, 用户不需要更改的写到settings中
3. 程序需要, 用户需要更改的写到本config中
"""
import errno
import logging
import os
import re
from importlib import import_module
from urllib.parse import urljoin, urlparse

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)
logger = logging.getLogger('smartdoc.conf')


def import_string(dotted_path):
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError as err:
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as err:
        raise ImportError(
            'Module "%s" does not define a "%s" attribute/class' %
            (module_path, class_name)) from err


def is_absolute_uri(uri):
    """ 判断一个uri是否是绝对地址 """
    if not isinstance(uri, str):
        return False

    result = re.match(r'^http[s]?://.*', uri)
    if result is None:
        return False

    return True


def build_absolute_uri(base, uri):
    """ 构建绝对uri地址 """
    if uri is None:
        return base

    if isinstance(uri, int):
        uri = str(uri)

    if not isinstance(uri, str):
        return base

    if is_absolute_uri(uri):
        return uri

    parsed_base = urlparse(base)
    url = "{}://{}".format(parsed_base.scheme, parsed_base.netloc)
    path = '{}/{}/'.format(parsed_base.path.strip('/'), uri.strip('/'))
    return urljoin(url, path)


class DoesNotExist(Exception):
    pass


class Config(dict):
    defaults = {
        # 数据库相关配置
        "DB_HOST": "127.0.0.1",
        "DB_PORT": 5432,
        "DB_USER": "root",
        "DB_PASSWORD": "Password123@postgres",
        "DB_ENGINE": "django.db.backends.postgresql_psycopg2",
        # 向量模型
        "EMBEDDING_MODEL_NAME": "shibing624/text2vec-base-chinese",
        "EMBEDDING_DEVICE": "cpu",
        "EMBEDDING_MODEL_PATH": os.path.join(PROJECT_DIR, 'models'),
        # 向量库配置
        "VECTOR_STORE_NAME": 'pg_vector',
        "DEBUG": False

    }

    def get_debug(self) -> bool:
        return self.get('DEBUG') if 'DEBUG' in self else True

    def get_time_zone(self) -> str:
        return self.get('TIME_ZONE') if 'TIME_ZONE' in self else 'Asia/Shanghai'

    def get_db_setting(self) -> dict:
        return {
            "NAME": self.get('DB_NAME'),
            "HOST": self.get('DB_HOST'),
            "PORT": self.get('DB_PORT'),
            "USER": self.get('DB_USER'),
            "PASSWORD": self.get('DB_PASSWORD'),
            "ENGINE": self.get('DB_ENGINE')
        }

    def __init__(self, *args):
        super().__init__(*args)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, dict.__repr__(self))

    def __getitem__(self, item):
        return self.get(item)

    def __getattr__(self, item):
        return self.get(item)


class ConfigManager:
    config_class = Config

    def __init__(self, root_path=None):
        self.root_path = root_path
        self.config = self.config_class()
        for key in self.config_class.defaults:
            self.config[key] = self.config_class.defaults[key]

    def from_mapping(self, *mapping, **kwargs):
        """Updates the config like :meth:`update` ignoring items with non-upper
        keys.

        .. versionadded:: 0.11
        """
        mappings = []
        if len(mapping) == 1:
            if hasattr(mapping[0], 'items'):
                mappings.append(mapping[0].items())
            else:
                mappings.append(mapping[0])
        elif len(mapping) > 1:
            raise TypeError(
                'expected at most 1 positional argument, got %d' % len(mapping)
            )
        mappings.append(kwargs.items())
        for mapping in mappings:
            for (key, value) in mapping:
                if key.isupper():
                    self.config[key] = value
        return True

    def from_yaml(self, filename, silent=False):
        if self.root_path:
            filename = os.path.join(self.root_path, filename)
        try:
            with open(filename, 'rt', encoding='utf8') as f:
                obj = yaml.safe_load(f)
        except IOError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise
        if obj:
            return self.from_mapping(obj)
        return True

    def load_from_yml(self):
        for i in ['config_example.yml', 'config.yaml', 'config.yml']:
            if not os.path.isfile(os.path.join(self.root_path, i)):
                continue
            loaded = self.from_yaml(i)
            if loaded:
                return True
        msg = f"""

                   Error: No config file found.

                   You can run `cp config_example.yml {self.root_path}/config.yml`, and edit it.

                   """
        raise ImportError(msg)

    def load_from_env(self):
        keys = os.environ.keys()
        config = {key.replace('MAXKB_', ''): os.environ.get(key) for key in keys if key.startswith('MAXKB_')}
        if len(config.keys()) <= 1:
            msg = f"""

                             Error: No config env found.

                             Please set environment variables
                                MAXKB_CONFIG_TYPE: 配置文件读取方式 FILE: 使用配置文件配置  ENV: 使用ENV配置
                                MAXKB_DB_NAME: 数据库名称
                                MAXKB_DB_HOST: 数据库主机
                                MAXKB_DB_PORT: 数据库端口
                                MAXKB_DB_USER: 数据库用户名
                                MAXKB_DB_PASSWORD: 数据库密码
                                MAXKB_EMBEDDING_MODEL_PATH: 向量模型目录
                                MAXKB_EMBEDDING_MODEL_NAME: 向量模型名称
                             """
            raise ImportError(msg)
        self.from_mapping(config)
        return True

    @classmethod
    def load_user_config(cls, root_path=None, config_class=None):
        config_class = config_class or Config
        cls.config_class = config_class
        if not root_path:
            root_path = PROJECT_DIR
        manager = cls(root_path=root_path)
        config_type = os.environ.get('MAXKB_CONFIG_TYPE')
        if config_type is None or config_type != 'ENV':
            manager.load_from_yml()
        else:
            manager.load_from_env()
        config = manager.config
        return config
