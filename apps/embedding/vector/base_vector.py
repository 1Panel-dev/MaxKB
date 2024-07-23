# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_vector.py
    @date：2023/10/18 19:16
    @desc:
"""
import threading
from abc import ABC, abstractmethod
from functools import reduce
from typing import List, Dict

from langchain_core.embeddings import Embeddings

from common.chunk import text_to_chunk
from common.util.common import sub_array
from embedding.models import SourceType, SearchMode

lock = threading.Lock()


def chunk_data(data: Dict):
    if str(data.get('source_type')) == SourceType.PARAGRAPH.value:
        text = data.get('text')
        chunk_list = text_to_chunk(text)
        return [{**data, 'text': chunk} for chunk in chunk_list]
    return [data]


def chunk_data_list(data_list: List[Dict]):
    result = [chunk_data(data) for data in data_list]
    return reduce(lambda x, y: [*x, *y], result, [])


class BaseVectorStore(ABC):
    vector_exists = False

    @abstractmethod
    def vector_is_create(self) -> bool:
        """
        判断向量库是否创建
        :return: 是否创建向量库
        """
        pass

    @abstractmethod
    def vector_create(self):
        """
        创建 向量库
        :return:
        """
        pass

    def save_pre_handler(self):
        """
        插入前置处理器 主要是判断向量库是否创建
        :return: True
        """
        if not BaseVectorStore.vector_exists:
            if not self.vector_is_create():
                self.vector_create()
                BaseVectorStore.vector_exists = True
        return True

    def save(self, text, source_type: SourceType, dataset_id: str, document_id: str, paragraph_id: str, source_id: str,
             is_active: bool,
             embedding: Embeddings):
        """
        插入向量数据
        :param source_id:  资源id
        :param dataset_id: 知识库id
        :param text: 文本
        :param source_type: 资源类型
        :param document_id: 文档id
        :param is_active:   是否禁用
        :param embedding:   向量化处理器
        :param paragraph_id 段落id
        :return:  bool
        """
        self.save_pre_handler()
        data = {'document_id': document_id, 'paragraph_id': paragraph_id, 'dataset_id': dataset_id,
                'is_active': is_active, 'source_id': source_id, 'source_type': source_type, 'text': text}
        chunk_list = chunk_data(data)
        result = sub_array(chunk_list)
        for child_array in result:
            self._batch_save(child_array, embedding)

    def batch_save(self, data_list: List[Dict], embedding: Embeddings):
        # 获取锁
        lock.acquire()
        try:
            """
            批量插入
            :param data_list: 数据列表
            :param embedding: 向量化处理器
            :return: bool
            """
            self.save_pre_handler()
            chunk_list = chunk_data_list(data_list)
            result = sub_array(chunk_list)
            for child_array in result:
                self._batch_save(child_array, embedding)
        finally:
            # 释放锁
            lock.release()
        return True

    @abstractmethod
    def _save(self, text, source_type: SourceType, dataset_id: str, document_id: str, paragraph_id: str, source_id: str,
              is_active: bool,
              embedding: Embeddings):
        pass

    @abstractmethod
    def _batch_save(self, text_list: List[Dict], embedding: Embeddings):
        pass

    def search(self, query_text, dataset_id_list: list[str], exclude_document_id_list: list[str],
               exclude_paragraph_list: list[str],
               is_active: bool,
               embedding: Embeddings):
        if dataset_id_list is None or len(dataset_id_list) == 0:
            return []
        embedding_query = embedding.embed_query(query_text)
        result = self.query(embedding_query, dataset_id_list, exclude_document_id_list, exclude_paragraph_list,
                            is_active, 1, 0.65)
        return result[0]

    @abstractmethod
    def query(self, query_text: str, query_embedding: List[float], dataset_id_list: list[str],
              exclude_document_id_list: list[str],
              exclude_paragraph_list: list[str], is_active: bool, top_n: int, similarity: float,
              search_mode: SearchMode):
        pass

    @abstractmethod
    def hit_test(self, query_text, dataset_id: list[str], exclude_document_id_list: list[str], top_number: int,
                 similarity: float,
                 search_mode: SearchMode,
                 embedding: Embeddings):
        pass

    @abstractmethod
    def update_by_paragraph_id(self, paragraph_id: str, instance: Dict):
        pass

    @abstractmethod
    def update_by_paragraph_ids(self, paragraph_ids: str, instance: Dict):
        pass

    @abstractmethod
    def update_by_source_id(self, source_id: str, instance: Dict):
        pass

    @abstractmethod
    def update_by_source_ids(self, source_ids: List[str], instance: Dict):
        pass

    @abstractmethod
    def delete_by_dataset_id(self, dataset_id: str):
        pass

    @abstractmethod
    def delete_by_document_id(self, document_id: str):
        pass

    @abstractmethod
    def delete_bu_document_id_list(self, document_id_list: List[str]):
        pass

    @abstractmethod
    def delete_by_dataset_id_list(self, dataset_id_list: List[str]):
        pass

    @abstractmethod
    def delete_by_source_id(self, source_id: str, source_type: str):
        pass

    @abstractmethod
    def delete_by_source_ids(self, source_ids: List[str], source_type: str):
        pass

    @abstractmethod
    def delete_by_paragraph_id(self, paragraph_id: str):
        pass

    @abstractmethod
    def delete_by_paragraph_ids(self, paragraph_ids: List[str]):
        pass
