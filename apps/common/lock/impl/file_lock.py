# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： file_lock.py
    @date：2024/8/20 10:48
    @desc:
"""
import errno
import hashlib
import os
import time

import six

from common.lock.base_lock import BaseLock
from smartdoc.const import PROJECT_DIR


def key_to_lock_name(key):
    """
    Combine part of a key with its hash to prevent very long filenames
    """
    MAX_LENGTH = 50
    key_hash = hashlib.md5(six.b(key)).hexdigest()
    lock_name = key[:MAX_LENGTH - len(key_hash) - 1] + '_' + key_hash
    return lock_name


class FileLock(BaseLock):
    """
     File locking backend.
     """

    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        self.location = settings.get('location')
        if self.location is None:
            self.location = os.path.join(PROJECT_DIR, 'data', 'lock')
        try:
            os.makedirs(self.location)
        except OSError as error:
            # Directory exists?
            if error.errno != errno.EEXIST:
                # Re-raise unexpected OSError
                raise

    def _get_lock_path(self, key):
        lock_name = key_to_lock_name(key)
        return os.path.join(self.location, lock_name)

    def try_lock(self, key, timeout):
        lock_path = self._get_lock_path(key)
        try:
            # 创建锁文件,如果没创建成功则拿不到
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL)
        except OSError as error:
            if error.errno == errno.EEXIST:
                # File already exists, check its modification time
                mtime = os.path.getmtime(lock_path)
                ttl = mtime + timeout - time.time()
                if ttl > 0:
                    return False
                else:
                    # 如果超时时间已到,直接上锁成功继续执行
                    os.utime(lock_path, None)
                    return True
            else:
                return False
        else:
            os.close(fd)
            return True

    def un_lock(self, key):
        lock_path = self._get_lock_path(key)
        os.remove(lock_path)
