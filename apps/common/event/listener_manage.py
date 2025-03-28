# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： listener_manage.py
    @date：2023/10/20 14:01
    @desc:
"""
import logging
import os
import threading
import datetime
import traceback
from typing import List

import django.db.models
from django.db.models import QuerySet
from django.db.models.functions import Substr, Reverse
from langchain_core.embeddings import Embeddings

from common.config.embedding_config import VectorStore
from common.db.search import native_search, get_dynamics_model, native_update
from common.util.file_util import get_file_content
from common.util.lock import try_lock, un_lock
from common.util.page_utils import page_desc
from dataset.models import Paragraph, Status, Document, ProblemParagraphMapping, TaskType, State
from embedding.models import SourceType, SearchMode
from smartdoc.conf import PROJECT_DIR
from django.utils.translation import gettext_lazy as _

max_kb_error = logging.getLogger(__file__)
max_kb = logging.getLogger(__file__)
lock = threading.Lock()


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
            max_kb_error.error(_('Query vector data: {paragraph_id_list} error {error} {traceback}').format(
                paragraph_id_list=paragraph_id_list, error=str(e), traceback=traceback.format_exc()))

    @staticmethod
    def embedding_by_paragraph_data_list(data_list, paragraph_id_list, embedding_model: Embeddings):
        max_kb.info(_('Start--->Embedding paragraph: {paragraph_id_list}').format(paragraph_id_list=paragraph_id_list))
        status = Status.success
        try:
            # 删除段落
            VectorStore.get_embedding_vector().delete_by_paragraph_ids(paragraph_id_list)

            def is_save_function():
                return QuerySet(Paragraph).filter(id__in=paragraph_id_list).exists()

            # 批量向量化
            VectorStore.get_embedding_vector().batch_save(data_list, embedding_model, is_save_function)
        except Exception as e:
            max_kb_error.error(_('Vectorized paragraph: {paragraph_id_list} error {error} {traceback}').format(
                paragraph_id_list=paragraph_id_list, error=str(e), traceback=traceback.format_exc()))
            status = Status.error
        finally:
            QuerySet(Paragraph).filter(id__in=paragraph_id_list).update(**{'status': status})
            max_kb.info(
                _('End--->Embedding paragraph: {paragraph_id_list}').format(paragraph_id_list=paragraph_id_list))

    @staticmethod
    def embedding_by_paragraph(paragraph_id, embedding_model: Embeddings):
        """
        向量化段落 根据段落id
        @param paragraph_id:    段落id
        @param embedding_model:  向量模型
        """
        max_kb.info(_('Start--->Embedding paragraph: {paragraph_id}').format(paragraph_id=paragraph_id))
        # 更新到开始状态
        ListenerManagement.update_status(QuerySet(Paragraph).filter(id=paragraph_id), TaskType.EMBEDDING, State.STARTED)
        try:
            data_list = native_search(
                {'problem': QuerySet(get_dynamics_model({'paragraph.id': django.db.models.CharField()})).filter(
                    **{'paragraph.id': paragraph_id}),
                    'paragraph': QuerySet(Paragraph).filter(id=paragraph_id)},
                select_string=get_file_content(
                    os.path.join(PROJECT_DIR, "apps", "common", 'sql', 'list_embedding_text.sql')))
            # 删除段落
            VectorStore.get_embedding_vector().delete_by_paragraph_id(paragraph_id)

            def is_the_task_interrupted():
                _paragraph = QuerySet(Paragraph).filter(id=paragraph_id).first()
                if _paragraph is None or Status(_paragraph.status)[TaskType.EMBEDDING] == State.REVOKE:
                    return True
                return False

            # 批量向量化
            VectorStore.get_embedding_vector().batch_save(data_list, embedding_model, is_the_task_interrupted)
            # 更新到开始状态
            ListenerManagement.update_status(QuerySet(Paragraph).filter(id=paragraph_id), TaskType.EMBEDDING,
                                             State.SUCCESS)
        except Exception as e:
            max_kb_error.error(_('Vectorized paragraph: {paragraph_id} error {error} {traceback}').format(
                paragraph_id=paragraph_id, error=str(e), traceback=traceback.format_exc()))
            ListenerManagement.update_status(QuerySet(Paragraph).filter(id=paragraph_id), TaskType.EMBEDDING,
                                             State.FAILURE)
        finally:
            max_kb.info(_('End--->Embedding paragraph: {paragraph_id}').format(paragraph_id=paragraph_id))

    @staticmethod
    def embedding_by_data_list(data_list: List, embedding_model: Embeddings):
        # 批量向量化
        VectorStore.get_embedding_vector().batch_save(data_list, embedding_model, lambda: True)

    @staticmethod
    def get_embedding_paragraph_apply(embedding_model, is_the_task_interrupted, post_apply=lambda: None):
        def embedding_paragraph_apply(paragraph_list):
            for paragraph in paragraph_list:
                if is_the_task_interrupted():
                    break
                ListenerManagement.embedding_by_paragraph(str(paragraph.get('id')), embedding_model)
            post_apply()

        return embedding_paragraph_apply

    @staticmethod
    def get_aggregation_document_status(document_id):
        def aggregation_document_status():
            pass
            sql = get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'update_document_status_meta.sql'))
            native_update({'document_custom_sql': QuerySet(Document).filter(id=document_id)}, sql, with_table_name=True)

        return aggregation_document_status

    @staticmethod
    def get_aggregation_document_status_by_dataset_id(dataset_id):
        def aggregation_document_status():
            sql = get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'update_document_status_meta.sql'))
            native_update({'document_custom_sql': QuerySet(Document).filter(dataset_id=dataset_id)}, sql,
                          with_table_name=True)

        return aggregation_document_status

    @staticmethod
    def get_aggregation_document_status_by_query_set(queryset):
        def aggregation_document_status():
            sql = get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'update_document_status_meta.sql'))
            native_update({'document_custom_sql': queryset}, sql, with_table_name=True)

        return aggregation_document_status

    @staticmethod
    def post_update_document_status(document_id, task_type: TaskType):
        _document = QuerySet(Document).filter(id=document_id).first()

        status = Status(_document.status)
        if status[task_type] == State.REVOKE:
            status[task_type] = State.REVOKED
        else:
            status[task_type] = State.SUCCESS
        for item in _document.status_meta.get('aggs', []):
            agg_status = item.get('status')
            agg_count = item.get('count')
            if Status(agg_status)[task_type] == State.FAILURE and agg_count > 0:
                status[task_type] = State.FAILURE
        ListenerManagement.update_status(QuerySet(Document).filter(id=document_id), task_type, status[task_type])

        ListenerManagement.update_status(QuerySet(Paragraph).annotate(
            reversed_status=Reverse('status'),
            task_type_status=Substr('reversed_status', task_type.value,
                                    task_type.value),
        ).filter(task_type_status=State.REVOKE.value).filter(document_id=document_id).values('id'),
                                         task_type,
                                         State.REVOKED)

    @staticmethod
    def update_status(query_set: QuerySet, taskType: TaskType, state: State):
        exec_sql = get_file_content(
            os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'update_paragraph_status.sql'))
        bit_number = len(TaskType)
        up_index = taskType.value - 1
        next_index = taskType.value + 1
        current_index = taskType.value
        status_number = state.value
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') + '+00'
        params_dict = {'${bit_number}': bit_number, '${up_index}': up_index,
                       '${status_number}': status_number, '${next_index}': next_index,
                       '${table_name}': query_set.model._meta.db_table, '${current_index}': current_index,
                       '${current_time}': current_time}
        for key in params_dict:
            _value_ = params_dict[key]
            exec_sql = exec_sql.replace(key, str(_value_))
        lock.acquire()
        try:
            native_update(query_set, exec_sql)
        finally:
            lock.release()

    @staticmethod
    def embedding_by_document(document_id, embedding_model: Embeddings, state_list=None):
        """
        向量化文档
        @param state_list:
        @param document_id: 文档id
        @param embedding_model 向量模型
        :return: None
        """
        if state_list is None:
            state_list = [State.PENDING, State.SUCCESS, State.FAILURE, State.REVOKE, State.REVOKED]
        if not try_lock('embedding' + str(document_id)):
            return
        try:
            def is_the_task_interrupted():
                document = QuerySet(Document).filter(id=document_id).first()
                if document is None or Status(document.status)[TaskType.EMBEDDING] == State.REVOKE:
                    return True
                return False

            if is_the_task_interrupted():
                return
            max_kb.info(_('Start--->Embedding document: {document_id}').format(document_id=document_id)
                        )
            # 批量修改状态为PADDING
            ListenerManagement.update_status(QuerySet(Document).filter(id=document_id), TaskType.EMBEDDING,
                                             State.STARTED)


            # 根据段落进行向量化处理
            page_desc(QuerySet(Paragraph)
                      .annotate(
                reversed_status=Reverse('status'),
                task_type_status=Substr('reversed_status', TaskType.EMBEDDING.value,
                                        1),
            ).filter(task_type_status__in=state_list, document_id=document_id)
                      .values('id'), 5,
                      ListenerManagement.get_embedding_paragraph_apply(embedding_model, is_the_task_interrupted,
                                                                       ListenerManagement.get_aggregation_document_status(
                                                                           document_id)),
                      is_the_task_interrupted)
        except Exception as e:
            max_kb_error.error(_('Vectorized document: {document_id} error {error} {traceback}').format(
                document_id=document_id, error=str(e), traceback=traceback.format_exc()))
        finally:
            ListenerManagement.post_update_document_status(document_id, TaskType.EMBEDDING)
            ListenerManagement.get_aggregation_document_status(document_id)()
            max_kb.info(_('End--->Embedding document: {document_id}').format(document_id=document_id))
            un_lock('embedding' + str(document_id))

    @staticmethod
    def embedding_by_dataset(dataset_id, embedding_model: Embeddings):
        """
        向量化知识库
        @param dataset_id: 知识库id
        @param embedding_model 向量模型
        :return: None
        """
        max_kb.info(_('Start--->Embedding dataset: {dataset_id}').format(dataset_id=dataset_id))
        try:
            ListenerManagement.delete_embedding_by_dataset(dataset_id)
            document_list = QuerySet(Document).filter(dataset_id=dataset_id)
            max_kb.info(_('Start--->Embedding document: {document_list}').format(document_list=document_list))
            for document in document_list:
                ListenerManagement.embedding_by_document(document.id, embedding_model=embedding_model)
        except Exception as e:
            max_kb_error.error(_('Vectorized dataset: {dataset_id} error {error} {traceback}').format(
                dataset_id=dataset_id, error=str(e), traceback=traceback.format_exc()))
        finally:
            max_kb.info(_('End--->Embedding dataset: {dataset_id}').format(dataset_id=dataset_id))

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
