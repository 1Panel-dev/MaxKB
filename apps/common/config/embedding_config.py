# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： embedding_config.py
    @date：2023/10/23 16:03
    @desc:
"""
import time

from common.cache.mem_cache import MemCache


class EmbeddingModelManage:
    cache = MemCache('model', {})
    up_clear_time = time.time()

    @staticmethod
    def get_model(_id, get_model):
        model_instance = EmbeddingModelManage.cache.get(_id)
        if model_instance is None:
            model_instance = get_model(_id)
            EmbeddingModelManage.cache.set(_id, model_instance, timeout=60 * 30)
            return model_instance
        # 续期
        EmbeddingModelManage.cache.touch(_id, timeout=60 * 30)
        EmbeddingModelManage.clear_timeout_cache()
        return model_instance

    @staticmethod
    def clear_timeout_cache():
        if time.time() - EmbeddingModelManage.up_clear_time > 60:
            EmbeddingModelManage.cache.clear_timeout_data()


class VectorStore:
    from embedding.vector.pg_vector import PGVector
    from embedding.vector.base_vector import BaseVectorStore
    instance_map = {
        'pg_vector': PGVector,
    }
    instance = None

    @staticmethod
    def get_embedding_vector() -> BaseVectorStore:
        from embedding.vector.pg_vector import PGVector
        if VectorStore.instance is None:
            from smartdoc.const import CONFIG
            vector_store_class = VectorStore.instance_map.get(CONFIG.get("VECTOR_STORE_NAME"),
                                                              PGVector)
            VectorStore.instance = vector_store_class()
        return VectorStore.instance
