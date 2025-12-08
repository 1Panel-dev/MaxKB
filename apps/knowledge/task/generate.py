import traceback

from celery_once import QueueOnce
from django.db.models import QuerySet
from django.db.models.functions import Reverse, Substr
from django.utils.translation import gettext_lazy as _
from langchain_core.messages import HumanMessage

from common.config.embedding_config import ModelManage
from common.event.listener_manage import ListenerManagement
from common.utils.logger import maxkb_logger
from common.utils.page_utils import page, page_desc
from knowledge.models import Paragraph, Document, Status, TaskType, State
from knowledge.task.handler import save_problem
from models_provider.models import Model
from models_provider.tools import get_model
from ops import celery_app


def get_llm_model(model_id, model_params_setting=None):
    model = QuerySet(Model).filter(id=model_id).first()
    return ModelManage.get_model(model_id, lambda _id: get_model(model, **(model_params_setting or {})))


def generate_problem_by_paragraph(paragraph, llm_model, prompt):
    try:
        ListenerManagement.update_status(QuerySet(Paragraph).filter(id=paragraph.id), TaskType.GENERATE_PROBLEM,
                                         State.STARTED)
        res = llm_model.invoke(
            [HumanMessage(content=prompt.replace('{data}', paragraph.content).replace('{title}', paragraph.title))])
        if (res.content is None) or (len(res.content) == 0):
            return
        problems = res.content.split('\n')
        for problem in problems:
            save_problem(paragraph.knowledge_id, paragraph.document_id, paragraph.id, problem)
        ListenerManagement.update_status(QuerySet(Paragraph).filter(id=paragraph.id), TaskType.GENERATE_PROBLEM,
                                         State.SUCCESS)
    except Exception as e:
        ListenerManagement.update_status(QuerySet(Paragraph).filter(id=paragraph.id), TaskType.GENERATE_PROBLEM,
                                         State.FAILURE)


def get_generate_problem(llm_model, prompt, post_apply=lambda: None, is_the_task_interrupted=lambda: False):
    def generate_problem(paragraph_list):
        for paragraph in paragraph_list:
            if is_the_task_interrupted():
                return
            generate_problem_by_paragraph(paragraph, llm_model, prompt)
            post_apply()

    return generate_problem


def get_is_the_task_interrupted(document_id):
    def is_the_task_interrupted():
        document = QuerySet(Document).filter(id=document_id).first()
        if document is None or Status(document.status)[TaskType.GENERATE_PROBLEM] == State.REVOKE:
            return True
        return False

    return is_the_task_interrupted


@celery_app.task(base=QueueOnce, once={'keys': ['knowledge_id']},
                 name='celery:generate_related_by_knowledge')
def generate_related_by_knowledge_id(knowledge_id, model_id, model_params_setting, prompt, state_list=None):
    document_list = QuerySet(Document).filter(knowledge_id=knowledge_id)
    for document in document_list:
        try:
            generate_related_by_document_id.delay(document.id, model_id, model_params_setting, prompt, state_list)
        except Exception as e:
            pass


@celery_app.task(base=QueueOnce, once={'keys': ['document_id']},
                 name='celery:generate_related_by_document')
def generate_related_by_document_id(document_id, model_id, model_params_setting, prompt, state_list=None):
    if state_list is None:
        state_list = [State.PENDING.value, State.STARTED.value, State.SUCCESS.value, State.FAILURE.value,
                      State.REVOKE.value,
                      State.REVOKED.value, State.IGNORED.value]
    try:
        is_the_task_interrupted = get_is_the_task_interrupted(document_id)
        if is_the_task_interrupted():
            return
        ListenerManagement.update_status(QuerySet(Document).filter(id=document_id),
                                         TaskType.GENERATE_PROBLEM,
                                         State.STARTED)
        llm_model = get_llm_model(model_id, model_params_setting)

        # 生成问题函数
        generate_problem = get_generate_problem(llm_model, prompt,
                                                ListenerManagement.get_aggregation_document_status(
                                                    document_id), is_the_task_interrupted)
        query_set = QuerySet(Paragraph).annotate(
            reversed_status=Reverse('status'),
            task_type_status=Substr('reversed_status', TaskType.GENERATE_PROBLEM.value,
                                    1),
        ).filter(task_type_status__in=state_list, document_id=document_id)
        page_desc(query_set, 10, generate_problem, is_the_task_interrupted)
    except Exception as e:
        maxkb_logger.error(f'根据文档生成问题:{document_id}出现错误{str(e)}{traceback.format_exc()}')
        maxkb_logger.error(_('Generate issue based on document: {document_id} error {error}{traceback}').format(
            document_id=document_id, error=str(e), traceback=traceback.format_exc()))
    finally:
        ListenerManagement.post_update_document_status(document_id, TaskType.GENERATE_PROBLEM)
        maxkb_logger.info(_('End--->Generate problem: {document_id}').format(document_id=document_id))


@celery_app.task(base=QueueOnce, once={'keys': ['paragraph_id_list']},
                 name='celery:generate_related_by_paragraph_list')
def generate_related_by_paragraph_id_list(document_id, paragraph_id_list, model_id, model_params_setting, prompt):
    try:
        is_the_task_interrupted = get_is_the_task_interrupted(document_id)
        if is_the_task_interrupted():
            ListenerManagement.update_status(QuerySet(Document).filter(id=document_id),
                                             TaskType.GENERATE_PROBLEM,
                                             State.REVOKED)
            return
        ListenerManagement.update_status(QuerySet(Document).filter(id=document_id),
                                         TaskType.GENERATE_PROBLEM,
                                         State.STARTED)
        llm_model = get_llm_model(model_id, model_params_setting)
        # 生成问题函数
        generate_problem = get_generate_problem(llm_model, prompt, ListenerManagement.get_aggregation_document_status(
            document_id))

        def is_the_task_interrupted():
            document = QuerySet(Document).filter(id=document_id).first()
            if document is None or Status(document.status)[TaskType.GENERATE_PROBLEM] == State.REVOKE:
                return True
            return False

        page(QuerySet(Paragraph).filter(id__in=paragraph_id_list), 10, generate_problem, is_the_task_interrupted)
    finally:
        ListenerManagement.post_update_document_status(document_id, TaskType.GENERATE_PROBLEM)
