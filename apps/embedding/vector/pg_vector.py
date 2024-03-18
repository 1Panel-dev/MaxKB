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
from typing import Dict, List

from django.contrib.postgres.search import SearchVector
from django.db.models import QuerySet
from langchain_community.embeddings import HuggingFaceEmbeddings

from common.config.embedding_config import EmbeddingModel
from common.db.search import native_search, generate_sql_by_query_dict
from common.db.sql_execute import select_one, select_list
from common.util.file_util import get_file_content
from embedding.models import Embedding, SourceType
from embedding.vector.base_vector import BaseVectorStore
from smartdoc.conf import PROJECT_DIR


class PGVector(BaseVectorStore):

    def delete_by_source_ids(self, source_ids: List[str], source_type: str):
        QuerySet(Embedding).filter(source_id__in=source_ids, source_type=source_type).delete()

    def update_by_source_ids(self, source_ids: List[str], instance: Dict):
        QuerySet(Embedding).filter(source_id__in=source_ids).update(**instance)

    def embed_documents(self, text_list: List[str]):
        embedding = EmbeddingModel.get_embedding_model()
        return embedding.embed_documents(text_list)

    def embed_query(self, text: str):
        embedding = EmbeddingModel.get_embedding_model()
        return embedding.embed_query(text)

    def vector_is_create(self) -> bool:
        # 项目启动默认是创建好的 不需要再创建
        return True

    def vector_create(self):
        return True

    def _save(self, text, source_type: SourceType, dataset_id: str, document_id: str, paragraph_id: str, source_id: str,
              is_active: bool,
              embedding: HuggingFaceEmbeddings):
        text_embedding = embedding.embed_query(text)
        embedding = Embedding(id=uuid.uuid1(),
                              dataset_id=dataset_id,
                              document_id=document_id,
                              is_active=is_active,
                              paragraph_id=paragraph_id,
                              source_id=source_id,
                              embedding=text_embedding,
                              source_type=source_type)
        embedding.save()
        return True

    def _batch_save(self, text_list: List[Dict], embedding: HuggingFaceEmbeddings):
        texts = [row.get('text') for row in text_list]
        embeddings = embedding.embed_documents(texts)
        embedding_list = [Embedding(id=uuid.uuid1(),
                                    document_id=text_list[index].get('document_id'),
                                    paragraph_id=text_list[index].get('paragraph_id'),
                                    dataset_id=text_list[index].get('dataset_id'),
                                    is_active=text_list[index].get('is_active', True),
                                    source_id=text_list[index].get('source_id'),
                                    source_type=text_list[index].get('source_type'),
                                    embedding=embeddings[index]) for index in
                          range(0, len(text_list))]
        QuerySet(Embedding).bulk_create(embedding_list) if len(embedding_list) > 0 else None
        return True

    def hit_test(self, query_text, dataset_id_list: list[str], exclude_document_id_list: list[str], top_number: int,
                 similarity: float,
                 embedding: HuggingFaceEmbeddings):
        if dataset_id_list is None or len(dataset_id_list) == 0:
            return []
        exclude_dict = {}
        embedding_query = embedding.embed_query(query_text)
        query_set = QuerySet(Embedding).filter(dataset_id__in=dataset_id_list, is_active=True)
        if exclude_document_id_list is not None and len(exclude_document_id_list) > 0:
            exclude_dict.__setitem__('document_id__in', exclude_document_id_list)
        query_set = query_set.exclude(**exclude_dict)
        exec_sql, exec_params = generate_sql_by_query_dict({'embedding_query': query_set},
                                                           select_string=get_file_content(
                                                               os.path.join(PROJECT_DIR, "apps", "embedding", 'sql',
                                                                            'hit_test.sql')),
                                                           with_table_name=True)
        embedding_model = select_list(exec_sql,
                                      [json.dumps(embedding_query), *exec_params, similarity, top_number])
        return embedding_model

    def query(self, query_embedding: List[float], dataset_id_list: list[str], exclude_document_id_list: list[str],
              exclude_paragraph_list: list[str], is_active: bool, top_n: int, similarity: float):
        exclude_dict = {}
        if dataset_id_list is None or len(dataset_id_list) == 0:
            return []
        query_set = QuerySet(Embedding).filter(dataset_id__in=dataset_id_list, is_active=is_active)
        if exclude_document_id_list is not None and len(exclude_document_id_list) > 0:
            exclude_dict.__setitem__('document_id__in', exclude_document_id_list)
        if exclude_paragraph_list is not None and len(exclude_paragraph_list) > 0:
            exclude_dict.__setitem__('paragraph_id__in', exclude_paragraph_list)
        query_set = query_set.exclude(**exclude_dict)
        exec_sql, exec_params = generate_sql_by_query_dict({'embedding_query': query_set},
                                                           select_string=get_file_content(
                                                               os.path.join(PROJECT_DIR, "apps", "embedding", 'sql',
                                                                            'embedding_search.sql')),
                                                           with_table_name=True)
        embedding_model = select_list(exec_sql,
                                      [json.dumps(query_embedding), *exec_params, similarity, top_n])
        return embedding_model

    def update_by_source_id(self, source_id: str, instance: Dict):
        QuerySet(Embedding).filter(source_id=source_id).update(**instance)

    def update_by_paragraph_id(self, paragraph_id: str, instance: Dict):
        QuerySet(Embedding).filter(paragraph_id=paragraph_id).update(**instance)

    def delete_by_dataset_id(self, dataset_id: str):
        QuerySet(Embedding).filter(dataset_id=dataset_id).delete()

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
