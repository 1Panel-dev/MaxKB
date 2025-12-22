# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： common_serializers.py
    @date：2023/11/17 11:00
    @desc:
"""
import os
import re
import zipfile
from typing import List

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.tools import save_workflow_mapping
from common.config.embedding_config import ModelManage
from common.db.search import native_search
from common.db.sql_execute import sql_execute, update_execute
from common.exception.app_exception import AppApiException
from common.utils.common import get_file_content
from common.utils.fork import Fork
from common.utils.logger import maxkb_logger
from knowledge.models import Document, KnowledgeWorkflow, KnowledgeWorkflowVersion, KnowledgeType
from knowledge.models import Paragraph, Problem, ProblemParagraphMapping, Knowledge, File
from maxkb.conf import PROJECT_DIR
from models_provider.tools import get_model, get_model_default_params
from system_manage.models.resource_mapping import ResourceMapping, ResourceType


class MetaSerializer(serializers.Serializer):
    class WebMeta(serializers.Serializer):
        source_url = serializers.CharField(required=True, label=_('source url'))
        selector = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('selector'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            source_url = self.data.get('source_url')
            response = Fork(source_url, []).fork()
            if response.status == 500:
                raise AppApiException(500, _('URL error, cannot parse [{source_url}]').format(source_url=source_url))

    class BaseMeta(serializers.Serializer):
        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)


class BatchSerializer(serializers.Serializer):
    id_list = serializers.ListField(required=True, child=serializers.UUIDField(required=True), label=_('id list'))

    def is_valid(self, *, model=None, raise_exception=False):
        super().is_valid(raise_exception=True)
        if model is not None:
            id_list = self.data.get('id_list')
            model_list = QuerySet(model).filter(id__in=id_list)
            if len(model_list) != len(id_list):
                model_id_list = [str(m.id) for m in model_list]
                error_id_list = list(filter(lambda row_id: not model_id_list.__contains__(row_id), id_list))
                raise AppApiException(500, _('The following id does not exist: {error_id_list}').format(
                    error_id_list=error_id_list))


class ProblemParagraphObject:
    def __init__(self, knowledge_id: str, document_id: str, paragraph_id: str, problem_content: str):
        self.knowledge_id = knowledge_id
        self.document_id = document_id
        self.paragraph_id = paragraph_id
        self.problem_content = problem_content


class GenerateRelatedSerializer(serializers.Serializer):
    model_id = serializers.UUIDField(required=True, label=_('Model id'))
    prompt = serializers.CharField(required=True, label=_('Prompt word'))
    state_list = serializers.ListField(required=False, child=serializers.CharField(required=True),
                                       label=_("state list"))


class ProblemParagraphManage:
    def __init__(self, problem_paragraph_object_list: List[ProblemParagraphObject], knowledge_id):
        self.knowledge_id = knowledge_id
        self.problem_paragraph_object_list = problem_paragraph_object_list

    def to_problem_model_list(self):
        problem_list = [item.problem_content for item in self.problem_paragraph_object_list]
        exists_problem_list = []
        if len(self.problem_paragraph_object_list) > 0:
            # 查询到已存在的问题列表
            exists_problem_list = QuerySet(Problem).filter(knowledge_id=self.knowledge_id,
                                                           content__in=problem_list).all()
        problem_content_dict = {}
        problem_model_list = [
            or_get(
                exists_problem_list,
                problemParagraphObject.problem_content,
                problemParagraphObject.knowledge_id,
                problemParagraphObject.document_id,
                problemParagraphObject.paragraph_id, problem_content_dict
            ) for problemParagraphObject in self.problem_paragraph_object_list]

        problem_paragraph_mapping_list = [
            ProblemParagraphMapping(
                id=uuid.uuid7(),
                document_id=document_id,
                problem_id=problem_model.id,
                paragraph_id=paragraph_id,
                knowledge_id=self.knowledge_id
            ) for problem_model, document_id, paragraph_id in problem_model_list]

        result = [
            problem_model for problem_model, is_create in problem_content_dict.values() if is_create
        ], problem_paragraph_mapping_list
        return result


def get_embedding_model_by_knowledge_id_list(knowledge_id_list: List):
    knowledge_list = QuerySet(Knowledge).filter(id__in=knowledge_id_list)
    if len(set([knowledge.embedding_model_id for knowledge in knowledge_list])) > 1:
        raise Exception(_('The knowledge base is inconsistent with the vector model'))
    if len(knowledge_list) == 0:
        raise Exception(_('Knowledge base setting error, please reset the knowledge base'))

    default_params = get_model_default_params(knowledge_list[0].embedding_model)

    return ModelManage.get_model(
        str(knowledge_list[0].embedding_model_id),
        lambda _id: get_model(knowledge_list[0].embedding_model, **{**default_params})
    )


def get_embedding_model_by_knowledge_id(knowledge_id: str):
    knowledge = QuerySet(Knowledge).select_related('embedding_model').filter(id=knowledge_id).first()

    default_params = get_model_default_params(knowledge.embedding_model)

    return ModelManage.get_model(str(knowledge.embedding_model_id),
                                 lambda _id: get_model(knowledge.embedding_model, **{**default_params}))


def get_embedding_model_by_knowledge(knowledge):
    default_params = get_model_default_params(knowledge.embedding_model)

    return ModelManage.get_model(str(knowledge.embedding_model_id),
                                 lambda _id: get_model(knowledge.embedding_model, **{**default_params}))


def get_embedding_model_id_by_knowledge_id(knowledge_id):
    knowledge = QuerySet(Knowledge).select_related('embedding_model').filter(id=knowledge_id).first()
    return str(knowledge.embedding_model_id)


def get_embedding_model_id_by_knowledge_id_list(knowledge_id_list: List):
    knowledge_list = QuerySet(Knowledge).filter(id__in=knowledge_id_list)
    if len(set([knowledge.embedding_model_id for knowledge in knowledge_list])) > 1:
        raise Exception(_('The knowledge base is inconsistent with the vector model'))
    if len(knowledge_list) == 0:
        raise Exception(_('Knowledge base setting error, please reset the knowledge base'))
    return str(knowledge_list[0].embedding_model_id)


def zip_dir(zip_path, output=None):
    output = output or os.path.basename(zip_path) + '.zip'
    zip = zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(zip_path):
        relative_root = '' if root == zip_path else root.replace(zip_path, '') + os.sep
        for filename in files:
            zip.write(os.path.join(root, filename), relative_root + filename)
    zip.close()


def is_valid_uuid(s):
    try:
        uuid.UUID(s)
        return True
    except ValueError:
        return False


def write_image(zip_path: str, image_list: List[str]):
    for image in image_list:
        search = re.search("\(.*\)", image)
        if search:
            text = search.group()
            if text.startswith('(./oss/file/'):
                r = text.replace('(./oss/file/', '').replace(')', '')
                r = r.strip().split(" ")[0]
                if not is_valid_uuid(r):
                    break
                file = QuerySet(File).filter(id=r).first()
                if file is None:
                    break
                zip_inner_path = os.path.join('oss', 'file', r)
                file_path = os.path.join(zip_path, zip_inner_path)
                if not os.path.exists(os.path.dirname(file_path)):
                    os.makedirs(os.path.dirname(file_path))
                with open(os.path.join(zip_path, file_path), 'wb') as f:
                    f.write(file.get_bytes())


def update_document_char_length(document_id: str):
    update_execute(get_file_content(
        os.path.join(PROJECT_DIR, "apps", "knowledge", 'sql', 'update_document_char_length.sql')),
        (document_id, document_id))


def list_paragraph(paragraph_list: List[str]):
    if paragraph_list is None or len(paragraph_list) == 0:
        return []
    return native_search(QuerySet(Paragraph).filter(id__in=paragraph_list), get_file_content(
        os.path.join(PROJECT_DIR, "apps", "knowledge", 'sql', 'list_paragraph.sql')))


def or_get(exists_problem_list, content, knowledge_id, document_id, paragraph_id, problem_content_dict):
    if content in problem_content_dict:
        return problem_content_dict.get(content)[0], document_id, paragraph_id
    exists = [row for row in exists_problem_list if row.content == content]
    if len(exists) > 0:
        problem_content_dict[content] = exists[0], False
        return exists[0], document_id, paragraph_id
    else:
        problem = Problem(id=uuid.uuid7(), content=content, knowledge_id=knowledge_id)
        problem_content_dict[content] = problem, True
        return problem, document_id, paragraph_id


def get_knowledge_operation_object(knowledge_id: str):
    knowledge_model = QuerySet(model=Knowledge).filter(id=knowledge_id).first()
    if knowledge_model is not None:
        return {
            "name": knowledge_model.name,
            "desc": knowledge_model.desc,
            "type": knowledge_model.type,
            "create_time": knowledge_model.create_time,
            "update_time": knowledge_model.update_time
        }
    return {}


def create_knowledge_index(knowledge_id=None, document_id=None):
    if knowledge_id is None and document_id is None:
        raise AppApiException(500, _('Knowledge ID or Document ID must be provided'))

    if knowledge_id is not None:
        k_id = knowledge_id
    else:
        document = QuerySet(Document).filter(id=document_id).first()
        k_id = document.knowledge_id

    sql = f"SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'embedding' AND indexname = 'embedding_hnsw_idx_{k_id}'"
    index = sql_execute(sql, [])
    if not index:
        sql = f"SELECT vector_dims(embedding) AS dims FROM embedding WHERE knowledge_id = '{k_id}' LIMIT 1"
        result = sql_execute(sql, [])
        if len(result) == 0:
            return
        dims = result[0]['dims']
        sql = f"""CREATE INDEX "embedding_hnsw_idx_{k_id}" ON embedding USING hnsw ((embedding::vector({dims})) vector_cosine_ops) WHERE knowledge_id = '{k_id}'"""
        update_execute(sql, [])
        maxkb_logger.info(f'Created index for knowledge ID: {k_id}')


def drop_knowledge_index(knowledge_id=None, document_id=None):
    if knowledge_id is None and document_id is None:
        raise AppApiException(500, _('Knowledge ID or Document ID must be provided'))

    if knowledge_id is not None:
        k_id = knowledge_id
    else:
        document = QuerySet(Document).filter(id=document_id).first()
        k_id = document.knowledge_id

    sql = f"SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'embedding' AND indexname = 'embedding_hnsw_idx_{k_id}'"
    index = sql_execute(sql, [])
    if index:
        sql = f'DROP INDEX "embedding_hnsw_idx_{k_id}"'
        update_execute(sql, [])
        maxkb_logger.info(f'Dropped index for knowledge ID: {k_id}')


def update_resource_mapping_by_knowledge(knowledge_id: str):
    knowledge = QuerySet(Knowledge).filter(id=knowledge_id).first()
    if knowledge.type == KnowledgeType.WORKFLOW:
        knowledge_workflow_version = QuerySet(KnowledgeWorkflowVersion).filter(
            knowledge_id=knowledge_id).order_by(
            '-create_time')[0:1].first()
        if knowledge_workflow_version:
            other = ResourceMapping(source_type=ResourceType.KNOWLEDGE, target_type=ResourceType.MODEL,
                                    source_id=knowledge.id,
                                    target_id=knowledge.embedding_model_id)
            save_workflow_mapping(knowledge_workflow_version.work_flow, ResourceType.KNOWLEDGE,
                                  str(knowledge_id), [other])
            return

    QuerySet(ResourceMapping).filter(source_type=ResourceType.KNOWLEDGE,
                                     source_id=knowledge.id).delete()
    ResourceMapping(source_type=ResourceType.KNOWLEDGE, target_type=ResourceType.MODEL,
                    source_id=knowledge.id,
                    target_id=knowledge.embedding_model_id).save()
