# coding=utf-8


import logging
import re
import traceback

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from common.utils.fork import ChildLink, Fork
from common.utils.split_model import get_split_model
from knowledge.models.knowledge import KnowledgeType, Document, Knowledge, Status
from knowledge.serializers.document import DocumentSerializers
from knowledge.serializers.paragraph import ParagraphSerializers

max_kb_error = logging.getLogger("max_kb_error")
max_kb = logging.getLogger("max_kb")


def get_save_handler(knowledge_id, selector):
    def handler(child_link: ChildLink, response: Fork.Response):
        if response.status == 200:
            try:
                document_name = child_link.tag.text if child_link.tag is not None and len(
                    child_link.tag.text.strip()) > 0 else child_link.url
                paragraphs = get_split_model('web.md').parse(response.content)
                DocumentSerializers.Create(
                    data={'knowledge_id': knowledge_id}
                ).save({
                    'name': document_name,
                    'paragraphs': paragraphs,
                    'meta': {'source_url': child_link.url, 'selector': selector},
                    'type': KnowledgeType.WEB
                }, with_valid=True)
            except Exception as e:
                logging.getLogger("max_kb_error").error(f'{str(e)}:{traceback.format_exc()}')

    return handler


def get_sync_handler(knowledge_id):
    knowledge = QuerySet(Knowledge).filter(id=knowledge_id).first()

    def handler(child_link: ChildLink, response: Fork.Response):
        if response.status == 200:
            try:

                document_name = child_link.tag.text if child_link.tag is not None and len(
                    child_link.tag.text.strip()) > 0 else child_link.url
                paragraphs = get_split_model('web.md').parse(response.content)
                first = QuerySet(Document).filter(meta__source_url=child_link.url.strip(), knowledge=knowledge).first()
                if first is not None:
                    # 如果存在,使用文档同步
                    DocumentSerializers.Sync(data={'document_id': first.id}).sync()
                else:
                    # 插入
                    DocumentSerializers.Create(
                        data={'knowledge_id': knowledge.id}
                    ).save({
                        'name': document_name,
                        'paragraphs': paragraphs,
                        'meta': {'source_url': child_link.url.strip(), 'selector': knowledge.meta.get('selector')},
                        'type': KnowledgeType.WEB
                    }, with_valid=True)
            except Exception as e:
                logging.getLogger("max_kb_error").error(f'{str(e)}:{traceback.format_exc()}')

    return handler


def get_sync_web_document_handler(knowledge_id):
    def handler(source_url: str, selector, response: Fork.Response):
        if response.status == 200:
            try:
                paragraphs = get_split_model('web.md').parse(response.content)
                # 插入
                DocumentSerializers.Create(data={'knowledge_id': knowledge_id}).save(
                    {'name': source_url[0:128], 'paragraphs': paragraphs,
                     'meta': {'source_url': source_url, 'selector': selector},
                     'type': KnowledgeType.WEB}, with_valid=True)
            except Exception as e:
                logging.getLogger("max_kb_error").error(f'{str(e)}:{traceback.format_exc()}')
        else:
            Document(name=source_url[0:128],
                     knowledge_id=knowledge_id,
                     meta={'source_url': source_url, 'selector': selector},
                     type=KnowledgeType.WEB,
                     char_length=0,
                     status=Status.error).save()

    return handler


def save_problem(knowledge_id, document_id, paragraph_id, problem):
    # print(f"knowledge_id: {knowledge_id}")
    # print(f"document_id: {document_id}")
    # print(f"paragraph_id: {paragraph_id}")
    # print(f"problem: {problem}")
    problem = re.sub(r"^\d+\.\s*", "", problem)
    pattern = r"<question>(.*?)</question>"
    match = re.search(pattern, problem)
    problem = match.group(1) if match else None
    if problem is None or len(problem) == 0:
        return
    try:
        ParagraphSerializers.Problem(
            data={
                "knowledge_id": knowledge_id,
                'document_id': document_id,
                'paragraph_id': paragraph_id
            }
        ).save(instance={"content": problem}, with_valid=True)
    except Exception as e:
        max_kb_error.error(_('Association problem failed {error}').format(error=str(e)))
