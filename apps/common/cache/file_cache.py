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
from django.core.cache.backends.base import DEFAULT_TIMEOUT, BaseCache


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

    def add(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        expire = timeout if isinstance(timeout, int) or isinstance(timeout,
                                                                   float) else timeout.total_seconds()
        return self.cache.add(key, value=value, expire=expire)

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        expire = timeout if isinstance(timeout, int) or isinstance(timeout,
                                                                   float) else timeout.total_seconds()
        return self.cache.set(key, value=value, expire=expire)

    def get(self, key, default=None, version=None):
        return self.cache.get(key, default=default)

    def delete(self, key, version=None):
        return self.cache.delete(key)

    def touch(self, key, timeout=DEFAULT_TIMEOUT, version=None):
        expire = timeout if isinstance(timeout, int) or isinstance(timeout,
                                                                   float) else timeout.total_seconds()

        return self.cache.touch(key, expire=expire)

    def ttl(self, key):
        """
        获取key的剩余时间
        :param key: key
        :return:  剩余时间
        """
        value, expire_time = self.cache.get(key, expire_time=True)
        if value is None:
            return None
        return datetime.timedelta(seconds=math.ceil(expire_time - time.time()))
