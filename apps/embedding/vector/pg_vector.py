# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： pg_vector.py
    @date：2023/10/19 15:28
    @desc:
"""
import json
import os
import uuid
from abc import ABC, abstractmethod
from typing import Dict, List

from django.db.models import QuerySet
from langchain_core.embeddings import Embeddings

from common.db.search import generate_sql_by_query_dict
from common.db.sql_execute import select_list
from common.util.file_util import get_file_content
from common.util.ts_vecto_util import to_ts_vector, to_query
from embedding.models import Embedding, SourceType, SearchMode
from embedding.vector.base_vector import BaseVectorStore
from smartdoc.conf import PROJECT_DIR


class PGVector(BaseVectorStore):

    def delete_by_source_ids(self, source_ids: List[str], source_type: str):
        QuerySet(Embedding).filter(source_id__in=source_ids, source_type=source_type).delete()

    def update_by_source_ids(self, source_ids: List[str], instance: Dict):
        QuerySet(Embedding).filter(source_id__in=source_ids).update(**instance)

    def vector_is_create(self) -> bool:
        # 项目启动默认是创建好的 不需要再创建
        return True

    def vector_create(self):
        return True

    def _save(self, text, source_type: SourceType, dataset_id: str, document_id: str, paragraph_id: str, source_id: str,
              is_active: bool,
              embedding: Embeddings):
        text_embedding = embedding.embed_query(text)
        embedding = Embedding(id=uuid.uuid1(),
                              dataset_id=dataset_id,
                              document_id=document_id,
                              is_active=is_active,
                              paragraph_id=paragraph_id,
                              source_id=source_id,
                              embedding=text_embedding,
                              source_type=source_type,
                              search_vector=to_ts_vector(text))
        embedding.save()
        return True

    def _batch_save(self, text_list: List[Dict], embedding: Embeddings):
        texts = [row.get('text') for row in text_list]
        embeddings = embedding.embed_documents(texts)
        embedding_list = [Embedding(id=uuid.uuid1(),
                                    document_id=text_list[index].get('document_id'),
                                    paragraph_id=text_list[index].get('paragraph_id'),
                                    dataset_id=text_list[index].get('dataset_id'),
                                    is_active=text_list[index].get('is_active', True),
                                    source_id=text_list[index].get('source_id'),
                                    source_type=text_list[index].get('source_type'),
                                    embedding=embeddings[index],
                                    search_vector=to_ts_vector(text_list[index]['text'])) for index in
                          range(0, len(text_list))]
        QuerySet(Embedding).bulk_create(embedding_list) if len(embedding_list) > 0 else None
        return True

    def hit_test(self, query_text, dataset_id_list: list[str], exclude_document_id_list: list[str], top_number: int,
                 similarity: float,
                 search_mode: SearchMode,
                 embedding: Embeddings):
        if dataset_id_list is None or len(dataset_id_list) == 0:
            return []
        exclude_dict = {}
        embedding_query = embedding.embed_query(query_text)
        query_set = QuerySet(Embedding).filter(dataset_id__in=dataset_id_list, is_active=True)
        if exclude_document_id_list is not None and len(exclude_document_id_list) > 0:
            exclude_dict.__setitem__('document_id__in', exclude_document_id_list)
        query_set = query_set.exclude(**exclude_dict)
        for search_handle in search_handle_list:
            if search_handle.support(search_mode):
                return search_handle.handle(query_set, query_text, embedding_query, top_number, similarity, search_mode)

    def query(self, query_text: str, query_embedding: List[float], dataset_id_list: list[str],
              exclude_document_id_list: list[str],
              exclude_paragraph_list: list[str], is_active: bool, top_n: int, similarity: float,
              search_mode: SearchMode):
        exclude_dict = {}
        if dataset_id_list is None or len(dataset_id_list) == 0:
            return []
        query_set = QuerySet(Embedding).filter(dataset_id__in=dataset_id_list, is_active=is_active)
        if exclude_document_id_list is not None and len(exclude_document_id_list) > 0:
            query_set = query_set.exclude(document_id__in=exclude_document_id_list)
        if exclude_paragraph_list is not None and len(exclude_paragraph_list) > 0:
            query_set = query_set.exclude(paragraph_id__in=exclude_paragraph_list)
        query_set = query_set.exclude(**exclude_dict)
        for search_handle in search_handle_list:
            if search_handle.support(search_mode):
                return search_handle.handle(query_set, query_text, query_embedding, top_n, similarity, search_mode)

    def update_by_source_id(self, source_id: str, instance: Dict):
        QuerySet(Embedding).filter(source_id=source_id).update(**instance)

    def update_by_paragraph_id(self, paragraph_id: str, instance: Dict):
        QuerySet(Embedding).filter(paragraph_id=paragraph_id).update(**instance)

    def update_by_paragraph_ids(self, paragraph_id: str, instance: Dict):
        QuerySet(Embedding).filter(paragraph_id__in=paragraph_id).update(**instance)

    def delete_by_dataset_id(self, dataset_id: str):
        QuerySet(Embedding).filter(dataset_id=dataset_id).delete()

    def delete_by_dataset_id_list(self, dataset_id_list: List[str]):
        QuerySet(Embedding).filter(dataset_id__in=dataset_id_list).delete()

    def delete_by_document_id(self, document_id: str):
        QuerySet(Embedding).filter(document_id=document_id).delete()
        return True

    def delete_bu_document_id_list(self, document_id_list: List[str]):
        return QuerySet(Embedding).filter(document_id__in=document_id_list).delete()

    def delete_by_source_id(self, source_id: str, source_type: str):
        QuerySet(Embedding).filter(source_id=source_id, source_type=source_type).delete()
        return True

    def delete_by_paragraph_id(self, paragraph_id: str):
        QuerySet(Embedding).filter(paragraph_id=paragraph_id).delete()

    def delete_by_paragraph_ids(self, paragraph_ids: List[str]):
        QuerySet(Embedding).filter(paragraph_id__in=paragraph_ids).delete()


class ISearch(ABC):
    @abstractmethod
    def support(self, search_mode: SearchMode):
        pass

    @abstractmethod
    def handle(self, query_set, query_text, query_embedding, top_number: int,
               similarity: float, search_mode: SearchMode):
        pass


class EmbeddingSearch(ISearch):
    def handle(self,
               query_set,
               query_text,
               query_embedding,
               top_number: int,
               similarity: float,
               search_mode: SearchMode):
        exec_sql, exec_params = generate_sql_by_query_dict({'embedding_query': query_set},
                                                           select_string=get_file_content(
                                                               os.path.join(PROJECT_DIR, "apps", "embedding", 'sql',
                                                                            'embedding_search.sql')),
                                                           with_table_name=True)
        embedding_model = select_list(exec_sql,
                                      [json.dumps(query_embedding), *exec_params, similarity, top_number])
        return embedding_model

    def support(self, search_mode: SearchMode):
        return search_mode.value == SearchMode.embedding.value


class KeywordsSearch(ISearch):
    def handle(self,
               query_set,
               query_text,
               query_embedding,
               top_number: int,
               similarity: float,
               search_mode: SearchMode):
        exec_sql, exec_params = generate_sql_by_query_dict({'keywords_query': query_set},
                                                           select_string=get_file_content(
                                                               os.path.join(PROJECT_DIR, "apps", "embedding", 'sql',
                                                                            'keywords_search.sql')),
                                                           with_table_name=True)
        embedding_model = select_list(exec_sql,
                                      [to_query(query_text), *exec_params, similarity, top_number])
        return embedding_model

    def support(self, search_mode: SearchMode):
        return search_mode.value == SearchMode.keywords.value


class BlendSearch(ISearch):
    def handle(self,
               query_set,
               query_text,
               query_embedding,
               top_number: int,
               similarity: float,
               search_mode: SearchMode):
        exec_sql, exec_params = generate_sql_by_query_dict({'embedding_query': query_set},
                                                           select_string=get_file_content(
                                                               os.path.join(PROJECT_DIR, "apps", "embedding", 'sql',
                                                                            'blend_search.sql')),
                                                           with_table_name=True)
        embedding_model = select_list(exec_sql,
                                      [json.dumps(query_embedding), to_query(query_text), *exec_params, similarity,
                                       top_number])
        return embedding_model

    def support(self, search_mode: SearchMode):
        return search_mode.value == SearchMode.blend.value


search_handle_list = [EmbeddingSearch(), KeywordsSearch(), BlendSearch()]
