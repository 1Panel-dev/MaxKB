# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： tools.py
    @date：2024/8/20 21:48
    @desc:
"""

import logging
import traceback

from common.util.fork import ChildLink, Fork
from common.util.split_model import get_split_model
from dataset.models import Type, Document, Status

max_kb_error = logging.getLogger("max_kb_error")
max_kb = logging.getLogger("max_kb")


def get_save_handler(dataset_id, selector):
    from dataset.serializers.document_serializers import DocumentSerializers

    def handler(child_link: ChildLink, response: Fork.Response):
        if response.status == 200:
            try:
                document_name = child_link.tag.text if child_link.tag is not None and len(
                    child_link.tag.text.strip()) > 0 else child_link.url
                paragraphs = get_split_model('web.md').parse(response.content)
                DocumentSerializers.Create(data={'dataset_id': dataset_id}).save(
                    {'name': document_name, 'paragraphs': paragraphs,
                     'meta': {'source_url': child_link.url, 'selector': selector},
                     'type': Type.web}, with_valid=True)
            except Exception as e:
                logging.getLogger("max_kb_error").error(f'{str(e)}:{traceback.format_exc()}')

    return handler


def get_sync_web_document_handler(dataset_id):
    from dataset.serializers.document_serializers import DocumentSerializers

    def handler(source_url: str, selector, response: Fork.Response):
        if response.status == 200:
            try:
                paragraphs = get_split_model('web.md').parse(response.content)
                # 插入
                DocumentSerializers.Create(data={'dataset_id': dataset_id}).save(
                    {'name': source_url[0:128], 'paragraphs': paragraphs,
                     'meta': {'source_url': source_url, 'selector': selector},
                     'type': Type.web}, with_valid=True)
            except Exception as e:
                logging.getLogger("max_kb_error").error(f'{str(e)}:{traceback.format_exc()}')
        else:
            Document(name=source_url[0:128],
                     dataset_id=dataset_id,
                     meta={'source_url': source_url, 'selector': selector},
                     type=Type.web,
                     char_length=0,
                     status=Status.error).save()

    return handler
