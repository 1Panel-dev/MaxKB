# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： conf.py
    @date：2025/4/11 16:58
    @desc:
"""
import errno
import logging
import os

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)
logger = logging.getLogger('smartdoc.conf')


class Config(dict):
    defaults = {
        # 数据库相关配置
        "DB_HOST": "127.0.0.1",
        "DB_PORT": 5432,
        "DB_USER": "root",
        "DB_PASSWORD": "Password123@postgres",
        "DB_ENGINE": "dj_db_conn_pool.backends.postgresql",
        "DB_MAX_OVERFLOW": 80,
        # 语言
        'LANGUAGE_CODE': 'zh-CN',
        "DEBUG": False,
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
            "ENGINE": self.get('DB_ENGINE'),
            "POOL_OPTIONS": {
                "POOL_SIZE": 20,
                "MAX_OVERFLOW": int(self.get('DB_MAX_OVERFLOW'))
            }
        }

    @staticmethod
    def get_cache_setting():
        return {
            'default': {
                'BACKEND': 'diskcache.DjangoCache',
                'LOCATION': f'{PROJECT_DIR}/data/cache'
            },
        }

    def get_language_code(self):
        return self.get('LANGUAGE_CODE', 'zh-CN')

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
        if len(config.keys()) <= 0:
            msg = f"""

                             Error: No config env found.

                             Please set environment variables
                                MAXKB_CONFIG_TYPE: 配置文件读取方式 FILE: 使用配置文件配置  ENV: 使用ENV配置
                                MAXKB_DB_NAME: 数据库名称
                                MAXKB_DB_HOST: 数据库主机
                                MAXKB_DB_PORT: 数据库端口
                                MAXKB_DB_USER: 数据库用户名
                                MAXKB_DB_PASSWORD: 数据库密码
                                
                                MAXKB_REDIS_HOST:缓存数据库主机
                                MAXKB_REDIS_PORT:缓存数据库端口
                                MAXKB_REDIS_PASSWORD:缓存数据库密码
                                MAXKB_REDIS_DB:缓存数据库
                                MAXKB_REDIS_MAX_CONNECTIONS:缓存数据库最大连接数
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
