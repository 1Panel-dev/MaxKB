import logging
from math import ceil

from celery_once import QueueOnce
from django.db.models import QuerySet
from langchain_core.messages import HumanMessage

from common.config.embedding_config import ModelManage
from dataset.models import Paragraph, Document, Status
from dataset.task.tools import save_problem
from ops import celery_app
from setting.models import Model
from setting.models_provider import get_model

max_kb_error = logging.getLogger("max_kb_error")
max_kb = logging.getLogger("max_kb")


def get_llm_model(model_id):
    model = QuerySet(Model).filter(id=model_id).first()
    return ModelManage.get_model(model_id, lambda _id: get_model(model))


@celery_app.task(base=QueueOnce, once={'keys': ['document_id']},
                 name='celery:generate_related_by_document')
def generate_related_by_document_id(document_id, model_id, prompt):
    llm_model = get_llm_model(model_id)
    offset = 0
    page_size = 10
    QuerySet(Document).filter(id=document_id).update(status=Status.generating)

    count = QuerySet(Paragraph).filter(document_id=document_id).count()
    for i in range(0, ceil(count / page_size)):
        paragraph_list = QuerySet(Paragraph).filter(document_id=document_id).all()[offset:offset + page_size]
        offset += page_size
        for paragraph in paragraph_list:
            res = llm_model.invoke([HumanMessage(content=prompt.replace('{data}', paragraph.content))])
            if (res.content is None) or (len(res.content) == 0):
                continue
            problems = res.content.split('\n')
            for problem in problems:
                save_problem(paragraph.dataset_id, paragraph.document_id, paragraph.id, problem)

    QuerySet(Document).filter(id=document_id).update(status=Status.success)



@celery_app.task(base=QueueOnce, once={'keys': ['paragraph_id_list']},
                 name='celery:generate_related_by_paragraph_list')
def generate_related_by_paragraph_id_list(paragraph_id_list, model_id, prompt):
    llm_model = get_llm_model(model_id)
    offset = 0
    page_size = 10
    count = QuerySet(Paragraph).filter(id__in=paragraph_id_list).count()
    for i in range(0, ceil(count / page_size)):
        paragraph_list = QuerySet(Paragraph).filter(id__in=paragraph_id_list).all()[offset:offset + page_size]
        offset += page_size
        for paragraph in paragraph_list:
            res = llm_model.invoke([HumanMessage(content=prompt.replace('{data}', paragraph.content))])
            if (res.content is None) or (len(res.content) == 0):
                continue
            problems = res.content.split('\n')
            for problem in problems:
                save_problem(paragraph.dataset_id, paragraph.document_id, paragraph.id, problem)
