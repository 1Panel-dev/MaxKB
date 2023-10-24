# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： pg_vector.py
    @date：2023/10/19 15:28
    @desc:
"""
import uuid
from typing import Dict, List

from django.db.models import QuerySet
from langchain.embeddings import HuggingFaceEmbeddings

from embedding.models import Embedding, SourceType
from embedding.vector.base_vector import BaseVectorStore


class PGVector(BaseVectorStore):

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
                              source_type=source_type,
                              )
        embedding.save()
        return True

    def _batch_save(self, text_list: List[Dict], embedding: HuggingFaceEmbeddings):
        texts = [row.get('text') for row in text_list]
        embeddings = embedding.embed_documents(texts)
        QuerySet(Embedding).bulk_create([Embedding(id=uuid.uuid1(),
                                                   document_id=text_list[index].get('document_id'),
                                                   paragraph_id=text_list[index].get('paragraph_id'),
                                                   dataset_id=text_list[index].get('dataset_id'),
                                                   is_active=text_list[index].get('is_active', True),
                                                   source_id=text_list[index].get('source_id'),
                                                   source_type=text_list[index].get('source_type'),
                                                   embedding=embeddings[index]) for index in
                                         range(0, len(text_list))]) if len(text_list) > 0 else None
        return True

    def search(self, query_text, dataset_id_list: list[str], is_active: bool, embedding: HuggingFaceEmbeddings):
        pass

    def update_by_source_id(self, source_id: str, instance: Dict):
        QuerySet(Embedding).filter(source_id=source_id).update(**instance)

    def update_by_paragraph_id(self, paragraph_id: str, instance: Dict):
        QuerySet(Embedding).filter(paragraph_id=paragraph_id).update(**instance)

    def delete_by_dataset_id(self, dataset_id: str):
        QuerySet(Embedding).filter(dataset_id=dataset_id).delete()

    def delete_by_document_id(self, document_id: str):
        QuerySet(Embedding).filter(document_id=document_id).delete()
        return True

    def delete_by_source_id(self, source_id: str, source_type: str):
        QuerySet(Embedding).filter(source_id=source_id, source_type=source_type).delete()
        return True

    def delete_by_paragraph_id(self, paragraph_id: str):
        QuerySet(Embedding).filter(paragraph_id=paragraph_id).delete()
