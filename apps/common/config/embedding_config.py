# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： embedding_config.py
    @date：2023/10/23 16:03
    @desc:
"""

import threading
import time

from common.cache.mem_cache import MemCache

_lock = threading.Lock()
locks = {}


class ModelManage:
    cache = MemCache('model', {})
    up_clear_time = time.time()

    @staticmethod
    def _get_lock(_id):
        lock = locks.get(_id)
        if lock is None:
            with _lock:
                lock = locks.get(_id)
                if lock is None:
                    lock = threading.Lock()
                    locks[_id] = lock

        return lock

    @staticmethod
    def get_model(_id, get_model):
        model_instance = ModelManage.cache.get(_id)
        if model_instance is None:
            lock = ModelManage._get_lock(_id)
            with lock:
                model_instance = ModelManage.cache.get(_id)
                if model_instance is None:
                    model_instance = get_model(_id)
                    ModelManage.cache.set(_id, model_instance, timeout=60 * 60 * 8)
        else:
            if model_instance.is_cache_model():
                ModelManage.cache.touch(_id, timeout=60 * 60 * 8)
            else:
                model_instance = get_model(_id)
                ModelManage.cache.set(_id, model_instance, timeout=60 * 60 * 8)
        ModelManage.clear_timeout_cache()
        return model_instance

    @staticmethod
    def clear_timeout_cache():
        if time.time() - ModelManage.up_clear_time > 60 * 60:
            threading.Thread(target=lambda: ModelManage.cache.clear_timeout_data()).start()
            ModelManage.up_clear_time = time.time()

    @staticmethod
    def delete_key(_id):
        if ModelManage.cache.has_key(_id):
            ModelManage.cache.delete(_id)


class VectorStore:
    from knowledge.vector.pg_vector import PGVector
    from knowledge.vector.base_vector import BaseVectorStore
    instance_map = {
        'pg_vector': PGVector,
    }
    instance = None

    @staticmethod
    def get_embedding_vector() -> BaseVectorStore:
        from knowledge.vector.pg_vector import PGVector
        if VectorStore.instance is None:
            from maxkb.const import CONFIG
            vector_store_class = VectorStore.instance_map.get(CONFIG.get("VECTOR_STORE_NAME"),
                                                              PGVector)
            VectorStore.instance = vector_store_class()
        return VectorStore.instance
