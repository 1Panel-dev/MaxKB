# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： embedding.py
    @date：2024/8/19 14:13
    @desc:
"""

import logging
import traceback
from typing import List

from celery_once import QueueOnce
from django.db.models import QuerySet

from common.config.embedding_config import ModelManage
from common.event import ListenerManagement, UpdateProblemArgs, UpdateEmbeddingDatasetIdArgs, \
    UpdateEmbeddingDocumentIdArgs
from dataset.models import Document
from ops import celery_app
from setting.models import Model
from setting.models_provider import get_model

max_kb_error = logging.getLogger("max_kb_error")
max_kb = logging.getLogger("max_kb")


def get_embedding_model(model_id):
    model = QuerySet(Model).filter(id=model_id).first()
    embedding_model = ModelManage.get_model(model_id,
                                            lambda _id: get_model(model))
    return embedding_model


@celery_app.task(base=QueueOnce, once={'keys': ['paragraph_id']}, name='celery:embedding_by_paragraph')
def embedding_by_paragraph(paragraph_id, model_id):
    embedding_model = get_embedding_model(model_id)
    ListenerManagement.embedding_by_paragraph(paragraph_id, embedding_model)


@celery_app.task(base=QueueOnce, once={'keys': ['paragraph_id_list']}, name='celery:embedding_by_paragraph_data_list')
def embedding_by_paragraph_data_list(data_list, paragraph_id_list, model_id):
    embedding_model = get_embedding_model(model_id)
    ListenerManagement.embedding_by_paragraph_data_list(data_list, paragraph_id_list, embedding_model)


@celery_app.task(base=QueueOnce, once={'keys': ['paragraph_id_list']}, name='celery:embedding_by_paragraph_list')
def embedding_by_paragraph_list(paragraph_id_list, model_id):
    embedding_model = get_embedding_model(model_id)
    ListenerManagement.embedding_by_paragraph_list(paragraph_id_list, embedding_model)


@celery_app.task(base=QueueOnce, once={'keys': ['document_id']}, name='celery:embedding_by_document')
def embedding_by_document(document_id, model_id):
    """
    向量化文档
    @param document_id: 文档id
    @param model_id 向量模型
    :return: None
    """
    embedding_model = get_embedding_model(model_id)
    ListenerManagement.embedding_by_document(document_id, embedding_model)


@celery_app.task(name='celery:embedding_by_document_list')
def embedding_by_document_list(document_id_list, model_id):
    """
    向量化文档
    @param document_id_list: 文档id列表
    @param model_id 向量模型
    :return: None
    """
    print(document_id_list)
    for document_id in document_id_list:
        embedding_by_document.delay(document_id, model_id)


@celery_app.task(base=QueueOnce, once={'keys': ['dataset_id']}, name='celery:embedding_by_dataset')
def embedding_by_dataset(dataset_id, model_id):
    """
          向量化知识库
          @param dataset_id: 知识库id
          @param model_id 向量模型
          :return: None
          """
    max_kb.info(f"开始--->向量化数据集:{dataset_id}")
    try:
        ListenerManagement.delete_embedding_by_dataset(dataset_id)
        document_list = QuerySet(Document).filter(dataset_id=dataset_id)
        max_kb.info(f"数据集文档:{[d.name for d in document_list]}")
        for document in document_list:
            try:
                embedding_by_document.delay(document.id, model_id)
            except Exception as e:
                pass
    except Exception as e:
        max_kb_error.error(f'向量化数据集:{dataset_id}出现错误{str(e)}{traceback.format_exc()}')
    finally:
        max_kb.info(f"结束--->向量化数据集:{dataset_id}")


def embedding_by_problem(args, model_id):
    """
    向量话问题
    @param args:    问题对象
    @param model_id: 模型id
    @return:
    """
    embedding_model = get_embedding_model(model_id)
    ListenerManagement.embedding_by_problem(args, embedding_model)


def delete_embedding_by_document(document_id):
    """
    删除指定文档id的向量
    @param document_id: 文档id
    @return: None
    """

    ListenerManagement.delete_embedding_by_document(document_id)


def delete_embedding_by_document_list(document_id_list: List[str]):
    """
    删除指定文档列表的向量数据
    @param document_id_list: 文档id列表
    @return: None
    """
    ListenerManagement.delete_embedding_by_document_list(document_id_list)


def delete_embedding_by_dataset(dataset_id):
    """
    删除指定数据集向量数据
    @param dataset_id: 数据集id
    @return: None
    """
    ListenerManagement.delete_embedding_by_dataset(dataset_id)


def delete_embedding_by_paragraph(paragraph_id):
    """
    删除指定段落的向量数据
    @param paragraph_id: 段落id
    @return: None
    """
    ListenerManagement.delete_embedding_by_paragraph(paragraph_id)


def delete_embedding_by_source(source_id):
    """
    删除指定资源id的向量数据
    @param source_id: 资源id
    @return: None
    """
    ListenerManagement.delete_embedding_by_source(source_id)


def disable_embedding_by_paragraph(paragraph_id):
    """
    禁用某个段落id的向量
    @param paragraph_id: 段落id
    @return: None
    """
    ListenerManagement.disable_embedding_by_paragraph(paragraph_id)


def enable_embedding_by_paragraph(paragraph_id):
    """
    开启某个段落id的向量数据
    @param paragraph_id: 段落id
    @return: None
    """
    ListenerManagement.enable_embedding_by_paragraph(paragraph_id)


def delete_embedding_by_source_ids(source_ids: List[str]):
    """
    删除向量根据source_id_list
    @param source_ids:
    @return:
    """
    ListenerManagement.delete_embedding_by_source_ids(source_ids)


def update_problem_embedding(problem_id: str, problem_content: str, model_id):
    """
    更新问题
    @param problem_id:
    @param problem_content:
    @param model_id:
    @return:
    """
    model = get_embedding_model(model_id)
    ListenerManagement.update_problem(UpdateProblemArgs(problem_id, problem_content, model))


def update_embedding_dataset_id(paragraph_id_list, target_dataset_id):
    """
    修改向量数据到指定知识库
    @param paragraph_id_list: 指定段落的向量数据
    @param target_dataset_id: 知识库id
    @return:
    """

    ListenerManagement.update_embedding_dataset_id(
        UpdateEmbeddingDatasetIdArgs(paragraph_id_list, target_dataset_id))


def delete_embedding_by_paragraph_ids(paragraph_ids: List[str]):
    """
    删除指定段落列表的向量数据
    @param paragraph_ids: 段落列表
    @return: None
    """
    ListenerManagement.delete_embedding_by_paragraph_ids(paragraph_ids)


def update_embedding_document_id(paragraph_id_list, target_document_id, target_dataset_id,
                                 target_embedding_model_id=None):
    target_embedding_model = get_embedding_model(
        target_embedding_model_id) if target_embedding_model_id is not None else None
    ListenerManagement.update_embedding_document_id(
        UpdateEmbeddingDocumentIdArgs(paragraph_id_list, target_document_id, target_dataset_id, target_embedding_model))


def delete_embedding_by_dataset_id_list(dataset_id_list):
    ListenerManagement.delete_embedding_by_dataset_id_list(dataset_id_list)
