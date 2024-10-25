# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： sync.py
    @date：2024/8/20 21:37
    @desc:
"""

import logging
import traceback
from typing import List

from celery_once import QueueOnce

from common.util.fork import ForkManage, Fork
from dataset.task.tools import get_save_handler, get_sync_web_document_handler, get_sync_handler

from ops import celery_app

max_kb_error = logging.getLogger("max_kb_error")
max_kb = logging.getLogger("max_kb")


@celery_app.task(base=QueueOnce, once={'keys': ['dataset_id']}, name='celery:sync_web_dataset')
def sync_web_dataset(dataset_id: str, url: str, selector: str):
    try:
        max_kb.info(f"开始--->开始同步web知识库:{dataset_id}")
        ForkManage(url, selector.split(" ") if selector is not None else []).fork(2, set(),
                                                                                  get_save_handler(dataset_id,
                                                                                                   selector))
        max_kb.info(f"结束--->结束同步web知识库:{dataset_id}")
    except Exception as e:
        max_kb_error.error(f'同步web知识库:{dataset_id}出现错误{str(e)}{traceback.format_exc()}')


@celery_app.task(base=QueueOnce, once={'keys': ['dataset_id']}, name='celery:sync_web_dataset')
def sync_replace_web_dataset(dataset_id: str, url: str, selector: str):
    try:
        max_kb.info(f"开始--->开始同步web知识库:{dataset_id}")
        ForkManage(url, selector.split(" ") if selector is not None else []).fork(2, set(),
                                                                                  get_sync_handler(dataset_id
                                                                                                   ))
        max_kb.info(f"结束--->结束同步web知识库:{dataset_id}")
    except Exception as e:
        max_kb_error.error(f'同步web知识库:{dataset_id}出现错误{str(e)}{traceback.format_exc()}')


@celery_app.task(name='celery:sync_web_document')
def sync_web_document(dataset_id, source_url_list: List[str], selector: str):
    handler = get_sync_web_document_handler(dataset_id)
    for source_url in source_url_list:
        result = Fork(base_fork_url=source_url, selector_list=selector.split(' ')).fork()
        handler(source_url, selector, result)
