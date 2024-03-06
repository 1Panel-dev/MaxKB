# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： mem_cache.py
    @date：2024/3/6 11:20
    @desc:
"""
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.cache.backends.locmem import LocMemCache


class MemCache(LocMemCache):
    def __init__(self, name, params):
        super().__init__(name, params)

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        key = self.make_and_validate_key(key, version=version)
        pickled = value
        with self._lock:
            self._set(key, pickled, timeout)

    def get(self, key, default=None, version=None):
        key = self.make_and_validate_key(key, version=version)
        with self._lock:
            if self._has_expired(key):
                self._delete(key)
                return default
            pickled = self._cache[key]
            self._cache.move_to_end(key, last=False)
        return pickled
