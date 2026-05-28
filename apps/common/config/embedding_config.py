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
    from knowledge.vector.qdrant_store import QdrantVectorStore
    from knowledge.vector.base_vector import BaseVectorStore
    instance_map = {
        'pg_vector': PGVector,
        'qdrant': QdrantVectorStore,
    }
    instance = None
    _qdrant_instance = None

    @staticmethod
    def get_embedding_vector(knowledge_id=None) -> BaseVectorStore:
        from knowledge.vector.pg_vector import PGVector
        from maxkb.const import CONFIG

        # Per-knowledge vector store selection
        if knowledge_id is not None:
            store_type = VectorStore._get_knowledge_store_type(knowledge_id)
            if store_type == 'qdrant':
                if VectorStore._qdrant_instance is None:
                    VectorStore._qdrant_instance = VectorStore.instance_map['qdrant']()
                return VectorStore._qdrant_instance

        # Global default
        if VectorStore.instance is None:
            vector_store_class = VectorStore.instance_map.get(
                CONFIG.get("VECTOR_STORE_NAME"), PGVector
            )
            VectorStore.instance = vector_store_class()
        return VectorStore.instance

    @staticmethod
    def _get_knowledge_store_type(knowledge_id: str) -> str:
        """Look up the vector_store_type for a given knowledge base."""
        try:
            from knowledge.models import Knowledge
            from django.db.models import QuerySet
            knowledge = QuerySet(Knowledge).filter(id=knowledge_id).first()
            if knowledge and hasattr(knowledge, 'vector_store_type'):
                return knowledge.vector_store_type
        except Exception:
            pass
        from maxkb.const import CONFIG
        return CONFIG.get("VECTOR_STORE_NAME", "pg_vector")
