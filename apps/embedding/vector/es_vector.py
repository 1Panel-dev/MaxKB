# coding=utf-8
"""
    @project: maxkb
    @Author：ilxch@163.com
    @file： es_vector.py
    @date：2024/09/04 15:28
    @desc: ES数据库操作API
"""
import uuid
from abc import ABC, abstractmethod
from typing import Dict, List
from langchain_core.embeddings import Embeddings
from common.util.ts_vecto_util import to_ts_vector, to_query
from embedding.models import Embedding, SourceType, SearchMode
from embedding.vector.base_vector import BaseVectorStore
from elasticsearch import helpers


class ESVector(BaseVectorStore):
    def __init__(self, es_connection, index_name):
        self.es = es_connection
        self.index_name = index_name

    def search(self, body: Dict, size: int):
        return self.es.search(index=self.index_name, body=body, size=size)

    def searchembed(self, query: Dict, vector: List[float], size, similarity):
        return self.es.search(index=self.index_name, body={
            "min_score": similarity,
            "size": size,
            "query": query,
            "knn": {
                "field": "embedding",
                "query_vector": vector,
                "k": size,
                "num_candidates": 2 * size  # 默认为2倍size
            },
            "_source": ["paragraph_id"]  # 添加这一行
        })

    def delete_by_query(self, query):
        return self.es.search(index=self.index_name, body=query)

    def bulk(self, documents: List[Dict]):
        actions = [
            {
                "_index": self.index_name,
                "_id": document.get('id'),
                "_source": document
            }
            for document in documents
        ]
        return helpers.bulk(self.es, actions)

    def delete_by_source_ids(self, source_ids: List[str], source_type: str):
        if len(source_ids) == 0:
            return
        return self.delete_by_query(query={
            "query": {
                "terms": {
                    "_id": source_ids
                }
            }
        })

    def update_by_source_ids(self, source_ids: List[str], instance: Dict):
        return self.bulk(source_ids, instance)

    def vector_is_create(self) -> bool:
        return self.es.indices.exists(index=self.index_name)

    def vector_create(self):
        return self.es.indices.create(index=self.index_name, ignore=400)

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
        res = self.es.index(index=self.index_name, body=embedding.to_dict())
        print("res---->" + str(res))
        return True

    def _batch_save(self, text_list: List[Dict], embedding: Embeddings, is_save_function):
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
                          range(0, len(texts))]
        if is_save_function():
            embeddings = [embedding.to_dict() for embedding in embedding_list]
            self.bulk(embeddings)
        return True

    def update_by_source_id(self, source_id: str, instance: Dict):
        self.es.update(index=self.index_name, id=source_id, body={"doc": instance})

    def update_by_paragraph_id(self, paragraph_id: str, instance: Dict):
        self.es.update(index=self.index_name, id=paragraph_id, body={"doc": instance})

    def update_by_paragraph_ids(self, paragraph_ids: List[str], instance: Dict):
        for paragraph_id in paragraph_ids:
            self.es.update(index=self.index_name, id=paragraph_id, body={"doc": instance})

    def delete_by_dataset_id(self, dataset_id: str):
        self.es.delete_by_query(index=self.index_name, body={"query": {"match": {"dataset_id": dataset_id}}})

    def delete_by_dataset_id_list(self, dataset_id_list: List[str]):
        self.delete_by_query(body={"query": {"terms": {"dataset_id": dataset_id_list}}})

    def delete_by_document_id(self, document_id: str):
        self.delete_by_query(query={
            "query": {
                "match": {
                    "document_id.keyword": document_id
                }
            }
        })
        return True

    def delete_by_document_id_list(self, document_id_list: List[str]):
        if len(document_id_list) == 0:
            return True
        self.delete_by_query(query={
            "query": {
                "match": {
                    "document_id.keyword": document_id_list
                }
            }
        })
        return True

    def delete_by_source_id(self, source_id: str, source_type: str):
        self.delete_by_query(query={"query": {
            "bool": {"must": [{"match": {"source_id.keyword": source_id}}, {"match": {"source_type": source_type}}]}
        }})
        return True

    def delete_by_paragraph_id(self, paragraph_id: str):
        self.delete_by_query(query={
            "query": {
                "match": {
                    "paragraph_id.keyword": paragraph_id
                }
            }
        })

    def delete_by_paragraph_ids(self, paragraph_ids: List[str]):
        self.delete_by_query(query={
            "query": {
                "terms": {
                    "paragraph_id.keyword": paragraph_ids
                }
            }
        })

    def hit_test(self, query_text, dataset_id_list: list[str], exclude_document_id_list: list[str], top_number: int,
                 similarity: float,
                 search_mode: SearchMode,
                 embedding: Embeddings):
        if dataset_id_list is None or len(dataset_id_list) == 0:
            return []
        embedding_query = embedding.embed_query(query_text)
        filter_query = {
            "bool": {
                "filter": [
                    {"term": {"is_active": True}},
                    {"terms": {"dataset_id.keyword": [str(uuid) for uuid in dataset_id_list]}},
                    {"bool": {"must_not": [
                        {"terms": {"document_id.keyword": [str(uuid) for uuid in exclude_document_id_list]}}]}}
                ]
            }
        }
        for search_handle in search_handle_list:
            if search_handle.support(search_mode, self):
                return search_handle.handle(filter_query, query_text, embedding_query, top_number, similarity,
                                            search_mode)

    def query(self, query_text: str, query_embedding: List[float], dataset_id_list: list[str],
              exclude_document_id_list: list[str],
              exclude_paragraph_list: list[str], is_active: bool, top_n: int, similarity: float,
              search_mode: SearchMode):
        if dataset_id_list is None or len(dataset_id_list) == 0:
            return []
        filter_query = {
            "bool": {
                "filter": [
                    {"term": {"is_active": "true"}},
                    {"term": {"dataset_id.keyword": [str(uuid) for uuid in dataset_id_list]}},
                    {"bool": {"must_not": [
                        {"terms": {"document_id.keyword": [str(uuid) for uuid in exclude_document_id_list]}}]}},
                    {"bool": {"must_not": [
                        {"terms": {"paragraph_id.keyword": [str(uuid) for uuid in exclude_paragraph_list]}}]}}
                ]
            }
        }
        for search_handle in search_handle_list:
            if search_handle.support(search_mode):
                return search_handle.handle(filter_query, query_text, query_embedding, top_n, similarity, search_mode)


class ISearch(ABC):
    @abstractmethod
    def support(self, search_mode: SearchMode, esVector: ESVector):
        pass

    @abstractmethod
    def handle(self, filter_query: Dict, query_text: str, query_embedding: List[float], top_number: int,
               similarity: float, search_mode: SearchMode):
        pass


# 向量检索
class EmbeddingSearch(ISearch):
    def __init__(self):
        self.esVector = None

    def handle(self,
               filter_query,
               query_text,
               query_embedding,
               top_number: int,
               similarity: float,
               search_mode: SearchMode):
        result = self.esVector.searchembed(query=filter_query, vector=query_embedding, size=top_number,
                                           similarity=similarity)
        hits = result['hits']['hits']
        return [{'paragraph_id': uuid.UUID(hit['_source']['paragraph_id']),
                 'similarity': hit['_score'],
                 'comprehensive_score': hit['_source'].get('_score', 0)}
                for hit in hits]

    def support(self, search_mode: SearchMode, esVector: ESVector):
        self.esVector = esVector
        return search_mode.value == SearchMode.embedding.value


# 关键词检索
class KeywordsSearch(ISearch):
    def __init__(self):
        self.esVector = None

    def handle(self,
               filter_query,
               query_text,
               query_embedding,
               top_number: int,
               similarity: float,
               search_mode: SearchMode):
        filter_query['bool']['must'] = {"multi_match": {
            "query": to_query(query_text),
            "fields": ["search_vector"]
        }}
        result = self.esVector.search(body={
            "query": filter_query
        }, size=top_number)
        hits = [hit for hit in result['hits']['hits'] if hit['_score'] > similarity]
        return [{'paragraph_id': uuid.UUID(hit['_source']['paragraph_id']),
                 'similarity': hit['_score'],
                 'comprehensive_score': hit['_source'].get('_score', 0)}
                for hit in hits]

    def support(self, search_mode: SearchMode, esVector: ESVector):
        self.esVector = esVector
        return search_mode.value == SearchMode.keywords.value


# 混合检索
class BlendSearch(ISearch):
    def __init__(self):
        self.esVector = None

    def handle(self,
               filter_query,
               query_text,
               query_embedding,
               top_number: int,
               similarity: float,
               search_mode: SearchMode):
        knn_filter = filter_query
        filter_query['bool']['must'] = {"multi_match": {
            "query": to_query(query_text),
            "fields": ["search_vector"]
        }}
        result = self.esVector.search(body={
            "min_score": similarity,
            "query": filter_query,
            "knn": {
                "field": "embedding",
                "query_vector": query_embedding,
                "k": top_number,
                "num_candidates": 2 * top_number,  # 默认为2倍size
                "filter": knn_filter
            },
            "_source": ["paragraph_id"]  # 添加这一行
        }, size=top_number)

        hits = [hit for hit in result['hits']['hits'] if hit['_score'] > similarity]

        return [{'paragraph_id': uuid.UUID(hit['_source']['paragraph_id']),
                 'similarity': hit['_score'],
                 'comprehensive_score': hit['_source'].get('_score', 0)}
                for hit in hits]

    def support(self, search_mode: SearchMode, esVector: ESVector):
        self.esVector = esVector
        return search_mode.value == SearchMode.blend.value

search_handle_list = [EmbeddingSearch(), KeywordsSearch(), BlendSearch()]
