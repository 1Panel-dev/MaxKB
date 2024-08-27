# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： listener_manage.py
    @date：2023/10/20 14:01
    @desc:
"""
import datetime
import logging
import os
import traceback
from typing import List

import django.db.models
from django.db.models import QuerySet
from langchain_core.embeddings import Embeddings

from common.config.embedding_config import VectorStore
from common.db.search import native_search, get_dynamics_model
from common.event.common import embedding_poxy
from common.util.file_util import get_file_content
from common.util.lock import try_lock, un_lock
from dataset.models import Paragraph, Status, Document, ProblemParagraphMapping
from embedding.models import SourceType, SearchMode
from smartdoc.conf import PROJECT_DIR

max_kb_error = logging.getLogger(__file__)
max_kb = logging.getLogger(__file__)


class SyncWebDatasetArgs:
    def __init__(self, lock_key: str, url: str, selector: str, handler):
        self.lock_key = lock_key
        self.url = url
        self.selector = selector
        self.handler = handler


class SyncWebDocumentArgs:
    def __init__(self, source_url_list: List[str], selector: str, handler):
        self.source_url_list = source_url_list
        self.selector = selector
        self.handler = handler


class UpdateProblemArgs:
    def __init__(self, problem_id: str, problem_content: str, embedding_model: Embeddings):
        self.problem_id = problem_id
        self.problem_content = problem_content
        self.embedding_model = embedding_model


class UpdateEmbeddingDatasetIdArgs:
    def __init__(self, paragraph_id_list: List[str], target_dataset_id: str):
        self.paragraph_id_list = paragraph_id_list
        self.target_dataset_id = target_dataset_id


class UpdateEmbeddingDocumentIdArgs:
    def __init__(self, paragraph_id_list: List[str], target_document_id: str, target_dataset_id: str,
                 target_embedding_model: Embeddings = None):
        self.paragraph_id_list = paragraph_id_list
        self.target_document_id = target_document_id
        self.target_dataset_id = target_dataset_id
        self.target_embedding_model = target_embedding_model


class ListenerManagement:

    @staticmethod
    def embedding_by_problem(args, embedding_model: Embeddings):
        VectorStore.get_embedding_vector().save(**args, embedding=embedding_model)

    @staticmethod
    def embedding_by_paragraph_list(paragraph_id_list, embedding_model: Embeddings):
        try:
            data_list = native_search(
                {'problem': QuerySet(get_dynamics_model({'paragraph.id': django.db.models.CharField()})).filter(
                    **{'paragraph.id__in': paragraph_id_list}),
                    'paragraph': QuerySet(Paragraph).filter(id__in=paragraph_id_list)},
                select_string=get_file_content(
                    os.path.join(PROJECT_DIR, "apps", "common", 'sql', 'list_embedding_text.sql')))
            ListenerManagement.embedding_by_paragraph_data_list(data_list, paragraph_id_list=paragraph_id_list,
                                                                embedding_model=embedding_model)
        except Exception as e:
            max_kb_error.error(f'查询向量数据:{paragraph_id_list}出现错误{str(e)}{traceback.format_exc()}')

    @staticmethod
    def embedding_by_paragraph_data_list(data_list, paragraph_id_list, embedding_model: Embeddings):
        max_kb.info(f'开始--->向量化段落:{paragraph_id_list}')
        status = Status.success
        try:
            # 删除段落
            VectorStore.get_embedding_vector().delete_by_paragraph_ids(paragraph_id_list)

            def is_save_function():
                return QuerySet(Paragraph).filter(id__in=paragraph_id_list).exists()

            # 批量向量化
            VectorStore.get_embedding_vector().batch_save(data_list, embedding_model, is_save_function)
        except Exception as e:
            max_kb_error.error(f'向量化段落:{paragraph_id_list}出现错误{str(e)}{traceback.format_exc()}')
            status = Status.error
        finally:
            QuerySet(Paragraph).filter(id__in=paragraph_id_list).update(**{'status': status})
            max_kb.info(f'结束--->向量化段落:{paragraph_id_list}')

    @staticmethod
    def embedding_by_paragraph(paragraph_id, embedding_model: Embeddings):
        """
        向量化段落 根据段落id
        @param paragraph_id:    段落id
        @param embedding_model:  向量模型
        """
        max_kb.info(f"开始--->向量化段落:{paragraph_id}")
        status = Status.success
        try:
            data_list = native_search(
                {'problem': QuerySet(get_dynamics_model({'paragraph.id': django.db.models.CharField()})).filter(
                    **{'paragraph.id': paragraph_id}),
                    'paragraph': QuerySet(Paragraph).filter(id=paragraph_id)},
                select_string=get_file_content(
                    os.path.join(PROJECT_DIR, "apps", "common", 'sql', 'list_embedding_text.sql')))
            # 删除段落
            VectorStore.get_embedding_vector().delete_by_paragraph_id(paragraph_id)

            def is_save_function():
                return QuerySet(Paragraph).filter(id=paragraph_id).exists()

            # 批量向量化
            VectorStore.get_embedding_vector().batch_save(data_list, embedding_model, is_save_function)
        except Exception as e:
            max_kb_error.error(f'向量化段落:{paragraph_id}出现错误{str(e)}{traceback.format_exc()}')
            status = Status.error
        finally:
            QuerySet(Paragraph).filter(id=paragraph_id).update(**{'status': status})
            max_kb.info(f'结束--->向量化段落:{paragraph_id}')

    @staticmethod
    def embedding_by_document(document_id, embedding_model: Embeddings):
        """
        向量化文档
        @param document_id: 文档id
        @param embedding_model 向量模型
        :return: None
        """
        if not try_lock('embedding' + str(document_id)):
            return
        max_kb.info(f"开始--->向量化文档:{document_id}")
        QuerySet(Document).filter(id=document_id).update(**{'status': Status.embedding})
        QuerySet(Paragraph).filter(document_id=document_id).update(**{'status': Status.embedding})
        status = Status.success
        try:
            data_list = native_search(
                {'problem': QuerySet(
                    get_dynamics_model({'paragraph.document_id': django.db.models.CharField()})).filter(
                    **{'paragraph.document_id': document_id}),
                    'paragraph': QuerySet(Paragraph).filter(document_id=document_id)},
                select_string=get_file_content(
                    os.path.join(PROJECT_DIR, "apps", "common", 'sql', 'list_embedding_text.sql')))
            # 删除文档向量数据
            VectorStore.get_embedding_vector().delete_by_document_id(document_id)

            def is_save_function():
                return QuerySet(Document).filter(id=document_id).exists()

            # 批量向量化
            VectorStore.get_embedding_vector().batch_save(data_list, embedding_model, is_save_function)
        except Exception as e:
            max_kb_error.error(f'向量化文档:{document_id}出现错误{str(e)}{traceback.format_exc()}')
            status = Status.error
        finally:
            # 修改状态
            QuerySet(Document).filter(id=document_id).update(
                **{'status': status, 'update_time': datetime.datetime.now()})
            QuerySet(Paragraph).filter(document_id=document_id).update(**{'status': status})
            max_kb.info(f"结束--->向量化文档:{document_id}")
            un_lock('embedding' + str(document_id))

    @staticmethod
    def embedding_by_dataset(dataset_id, embedding_model: Embeddings):
        """
        向量化知识库
        @param dataset_id: 知识库id
        @param embedding_model 向量模型
        :return: None
        """
        max_kb.info(f"开始--->向量化数据集:{dataset_id}")
        try:
            ListenerManagement.delete_embedding_by_dataset(dataset_id)
            document_list = QuerySet(Document).filter(dataset_id=dataset_id)
            max_kb.info(f"数据集文档:{[d.name for d in document_list]}")
            for document in document_list:
                ListenerManagement.embedding_by_document(document.id, embedding_model=embedding_model)
        except Exception as e:
            max_kb_error.error(f'向量化数据集:{dataset_id}出现错误{str(e)}{traceback.format_exc()}')
        finally:
            max_kb.info(f"结束--->向量化数据集:{dataset_id}")

    @staticmethod
    def delete_embedding_by_document(document_id):
        VectorStore.get_embedding_vector().delete_by_document_id(document_id)

    @staticmethod
    def delete_embedding_by_document_list(document_id_list: List[str]):
        VectorStore.get_embedding_vector().delete_by_document_id_list(document_id_list)

    @staticmethod
    def delete_embedding_by_dataset(dataset_id):
        VectorStore.get_embedding_vector().delete_by_dataset_id(dataset_id)

    @staticmethod
    def delete_embedding_by_paragraph(paragraph_id):
        VectorStore.get_embedding_vector().delete_by_paragraph_id(paragraph_id)

    @staticmethod
    def delete_embedding_by_source(source_id):
        VectorStore.get_embedding_vector().delete_by_source_id(source_id, SourceType.PROBLEM)

    @staticmethod
    def disable_embedding_by_paragraph(paragraph_id):
        VectorStore.get_embedding_vector().update_by_paragraph_id(paragraph_id, {'is_active': False})

    @staticmethod
    def enable_embedding_by_paragraph(paragraph_id):
        VectorStore.get_embedding_vector().update_by_paragraph_id(paragraph_id, {'is_active': True})

    @staticmethod
    def update_problem(args: UpdateProblemArgs):
        problem_paragraph_mapping_list = QuerySet(ProblemParagraphMapping).filter(problem_id=args.problem_id)
        embed_value = args.embedding_model.embed_query(args.problem_content)
        VectorStore.get_embedding_vector().update_by_source_ids([v.id for v in problem_paragraph_mapping_list],
                                                                {'embedding': embed_value})

    @staticmethod
    def update_embedding_dataset_id(args: UpdateEmbeddingDatasetIdArgs):
        VectorStore.get_embedding_vector().update_by_paragraph_ids(args.paragraph_id_list,
                                                                   {'dataset_id': args.target_dataset_id})

    @staticmethod
    def update_embedding_document_id(args: UpdateEmbeddingDocumentIdArgs):
        if args.target_embedding_model is None:
            VectorStore.get_embedding_vector().update_by_paragraph_ids(args.paragraph_id_list,
                                                                       {'document_id': args.target_document_id,
                                                                        'dataset_id': args.target_dataset_id})
        else:
            ListenerManagement.embedding_by_paragraph_list(args.paragraph_id_list,
                                                           embedding_model=args.target_embedding_model)

    @staticmethod
    def delete_embedding_by_source_ids(source_ids: List[str]):
        VectorStore.get_embedding_vector().delete_by_source_ids(source_ids, SourceType.PROBLEM)

    @staticmethod
    def delete_embedding_by_paragraph_ids(paragraph_ids: List[str]):
        VectorStore.get_embedding_vector().delete_by_paragraph_ids(paragraph_ids)

    @staticmethod
    def delete_embedding_by_dataset_id_list(source_ids: List[str]):
        VectorStore.get_embedding_vector().delete_by_dataset_id_list(source_ids)

    @staticmethod
    def hit_test(query_text, dataset_id: list[str], exclude_document_id_list: list[str], top_number: int,
                 similarity: float,
                 search_mode: SearchMode,
                 embedding: Embeddings):
        return VectorStore.get_embedding_vector().hit_test(query_text, dataset_id, exclude_document_id_list, top_number,
                                                           similarity, search_mode, embedding)
