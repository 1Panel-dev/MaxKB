# coding=utf-8
"""
    @project: qabot
    @Author：虎
    @file： file_cache.py
    @date：2023/9/11 15:58
    @desc: 文件缓存
"""
import datetime
import math
import os
import time

from diskcache import Cache
from django.core.cache.backends.base import BaseCache


class FileCache(BaseCache):
    def __init__(self, dir, params):
        super().__init__(params)
        self._dir = os.path.abspath(dir)
        self._createdir()
        self.cache = Cache(self._dir)

    def _createdir(self):
        old_umask = os.umask(0o077)
        try:
            os.makedirs(self._dir, 0o700, exist_ok=True)
        finally:
            os.umask(old_umask)

    def add(self, key, value, timeout=None, version=None):
        expire = timeout if isinstance(timeout, int) or isinstance(timeout,
                                                                   float) or timeout is None else timeout.total_seconds()
        return self.cache.add(self.get_key(key, version), value=value, expire=expire)

    def set(self, key, value, timeout=None, version=None):
        expire = timeout if isinstance(timeout, int) or isinstance(timeout,
                                                                   float) or timeout is None else timeout.total_seconds()
        return self.cache.set(self.get_key(key, version), value=value, expire=expire)

    def get(self, key, default=None, version=None):
        return self.cache.get(self.get_key(key, version), default=default)

    @staticmethod
    def get_key(key, version):
        if version is None:
            return f"default:{key}"
        return f"{version}:{key}"

    def delete(self, key, version=None):
        return self.cache.delete(self.get_key(key, version))

    def touch(self, key, timeout=None, version=None):
        expire = timeout if isinstance(timeout, int) or isinstance(timeout,
                                                                   float) else timeout.total_seconds()

        return self.cache.touch(self.get_key(key, version), expire=expire)

    def ttl(self, key, version=None):
        """
        获取key的剩余时间
        :param key: key
        :return:  剩余时间
        @param version:
        """
        value, expire_time = self.cache.get(self.get_key(key, version), expire_time=True)
        if value is None:
            return None
        return datetime.timedelta(seconds=math.ceil(expire_time - time.time()))

    def clear_by_application_id(self, application_id):
        delete_keys = []
        for key in self.cache.iterkeys():
            value = self.cache.get(key)
            if (hasattr(value,
                        'application') and value.application is not None and value.application.id is not None and
                    str(
                        value.application.id) == application_id):
                delete_keys.append(key)
        for key in delete_keys:
            self.cache.delete(key)

    def clear_timeout_data(self):
        for key in self.cache.iterkeys():
            self.get(key)
