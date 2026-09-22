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
import json

from common.cache.mem_cache import MemCache
from common.utils.rsa_util import rsa_long_decrypt

_lock = threading.Lock()
locks = {}


class ModelManage:
    cache = MemCache("model", {})
    # 按 model_id 缓存的解密凭据与模型行，避免每次调用重复 RSA 解密 / 重复查库。
    # 二者在模型更新/删除时通过 delete_key(_id) 一并失效，保证改 key 立即生效。
    credential_cache = MemCache("model_credential", {})
    model_cache = MemCache("model_row", {})
    up_clear_time = time.time()

    @staticmethod
    def get_decrypted_credential(model_id, credential):
        """返回解密后的凭据 dict；结果按 model_id 缓存，改 key 时由 delete_key 清除。"""
        cached = ModelManage.credential_cache.get(model_id)
        if cached is not None:
            return cached
        decrypted = json.loads(rsa_long_decrypt(credential))
        ModelManage.credential_cache.set(model_id, decrypted, timeout=60 * 60 * 8)
        return decrypted

    @staticmethod
    def get_model_row(_id):
        return ModelManage.model_cache.get(_id)

    @staticmethod
    def set_model_row(_id, model):
        ModelManage.model_cache.set(_id, model, timeout=60 * 60 * 8)

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
        for cache in (ModelManage.cache, ModelManage.credential_cache, ModelManage.model_cache):
            if cache.has_key(_id):
                cache.delete(_id)


class VectorStore:
    from knowledge.vector.pg_vector import PGVector
    from knowledge.vector.base_vector import BaseVectorStore

    instance_map = {
        "pg_vector": PGVector,
    }
    instance = None

    @staticmethod
    def get_embedding_vector() -> BaseVectorStore:
        from knowledge.vector.pg_vector import PGVector

        if VectorStore.instance is None:
            from maxkb.const import CONFIG

            vector_store_class = VectorStore.instance_map.get(CONFIG.get("VECTOR_STORE_NAME"), PGVector)
            VectorStore.instance = vector_store_class()
        return VectorStore.instance
