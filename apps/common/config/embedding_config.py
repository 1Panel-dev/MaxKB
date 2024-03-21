# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： embedding_config.py
    @date：2023/10/23 16:03
    @desc:
"""
from langchain_community.embeddings import HuggingFaceEmbeddings

from smartdoc.const import CONFIG


class EmbeddingModel:
    instance = None

    @staticmethod
    def get_embedding_model():
        """
        获取向量化模型
        :return:
        """
        if EmbeddingModel.instance is None:
            model_name = CONFIG.get('EMBEDDING_MODEL_NAME')
            cache_folder = CONFIG.get('EMBEDDING_MODEL_PATH')
            device = CONFIG.get('EMBEDDING_DEVICE')
            e = HuggingFaceEmbeddings(
                model_name=model_name,
                cache_folder=cache_folder,
                model_kwargs={'device': device})
            EmbeddingModel.instance = e
        return EmbeddingModel.instance


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
