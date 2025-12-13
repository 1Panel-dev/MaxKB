# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： sync.py
    @date：2024/8/20 21:37
    @desc:
"""

import traceback
from typing import List

from celery_once import QueueOnce
from django.utils.translation import gettext_lazy as _

from common.utils.fork import ForkManage, Fork
from common.utils.logger import maxkb_logger
from ops import celery_app




@celery_app.task(base=QueueOnce, once={'keys': ['knowledge_id']}, name='celery:sync_web_knowledge')
def sync_web_knowledge(knowledge_id: str, url: str, selector: str):
    from knowledge.task.handler import get_save_handler

    try:
        maxkb_logger.info(
            _('Start--->Start synchronization web knowledge base:{knowledge_id}').format(knowledge_id=knowledge_id))
        ForkManage(url, selector.split(" ") if selector is not None else []).fork(2, set(),
                                                                                  get_save_handler(knowledge_id,
                                                                                                   selector))

        maxkb_logger.info(_('End--->End synchronization web knowledge base:{knowledge_id}').format(knowledge_id=knowledge_id))
    except Exception as e:
        maxkb_logger.error(_('Synchronize web knowledge base:{knowledge_id} error{error}{traceback}').format(
            knowledge_id=knowledge_id, error=str(e), traceback=traceback.format_exc()))


@celery_app.task(base=QueueOnce, once={'keys': ['knowledge_id']}, name='celery:sync_replace_web_knowledge')
def sync_replace_web_knowledge(knowledge_id: str, url: str, selector: str):
    from knowledge.task.handler import get_sync_handler

    try:
        maxkb_logger.info(
            _('Start--->Start synchronization web knowledge base:{knowledge_id}').format(knowledge_id=knowledge_id))
        ForkManage(url, selector.split(" ") if selector is not None else []).fork(2, set(),
                                                                                  get_sync_handler(knowledge_id
                                                                                                   ))
        maxkb_logger.info(_('End--->End synchronization web knowledge base:{knowledge_id}').format(knowledge_id=knowledge_id))
    except Exception as e:
        maxkb_logger.error(_('Synchronize web knowledge base:{knowledge_id} error{error}{traceback}').format(
            knowledge_id=knowledge_id, error=str(e), traceback=traceback.format_exc()))


@celery_app.task(name='celery:sync_web_document')
def sync_web_document(knowledge_id, source_url_list: List[str], selector: str):
    from knowledge.task.handler import get_sync_web_document_handler

    handler = get_sync_web_document_handler(knowledge_id)
    for source_url in source_url_list:
        try:
            result = Fork(base_fork_url=source_url, selector_list=selector.split(' ')).fork()
            handler(source_url, selector, result)
        except Exception as e:
            pass
