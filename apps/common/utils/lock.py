# coding=utf-8
"""
    @project: qabot
    @Author：虎
    @file： lock.py
    @date：2023/9/11 11:45
    @desc:
"""
from functools import wraps

import uuid_utils.compat as uuid
from django.core.cache import caches
from django_redis import get_redis_connection

memory_cache = caches['default']

class RedisLock():
    def __init__(self):
        self.lock_value = None

    def try_lock(self, key: str, timeout=None):
        """
        获取锁
        :param key:    获取锁 key
        :param timeout 超时时间
        :return: 是否获取到锁
        """
        redis_client = get_redis_connection("default")
        if timeout is None:
            timeout = 3600  # 默认超时时间为3600秒
        self.lock_value = str(uuid.uuid7())
        return redis_client.set(key, self.lock_value, nx=True, ex=timeout)


    def un_lock(self, key: str):
        """
        解锁
        :param key: 解锁 key
        :return: 是否解锁成功
        """
        redis_client = get_redis_connection("default")
        unlock_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
        redis_client.eval(unlock_script, 1, key, self.lock_value)


def lock(lock_key, timeout=None):
    """
    给一个函数上锁
    @param lock_key: 上锁key 字符串|函数  函数返回值为字符串
    @param timeout:  超时时间
    :return: 装饰器函数 当前装饰器主要限制一个key只能一个线程去调用 相同key只能阻塞等待上一个任务执行完毕 不同key不需要等待

    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = lock_key(*args, **kwargs) if callable(lock_key) else lock_key
            rlock = RedisLock()
            if not rlock.try_lock(key, timeout):
                # 获取锁失败，可自定义异常或返回
                return None
            try:
                return func(*args, **kwargs)
            finally:
                rlock.un_lock(key)

        return wrapper

    return decorator
