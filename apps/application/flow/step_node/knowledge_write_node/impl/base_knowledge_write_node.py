# coding=utf-8
"""
    @project: MaxKB
    @Author：niu
    @file： base_knowledge_write_node.py
    @date：2025/11/13 11:19
    @desc:
"""
from functools import reduce
from typing import Dict, List
import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.db.models.aggregates import Max

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from application.flow.i_step_node import NodeResult
from application.flow.step_node.knowledge_write_node.i_knowledge_write_node import IKnowledgeWriteNode
from common.chunk import text_to_chunk
from common.utils.common import bulk_create_in_batches
from knowledge.models import Document, KnowledgeType, Paragraph, File, FileSourceType, Problem, ProblemParagraphMapping
from knowledge.serializers.common import ProblemParagraphObject, ProblemParagraphManage
from knowledge.serializers.document import DocumentSerializers


class ParagraphInstanceSerializer(serializers.Serializer):
    content = serializers.CharField(required=True, label=_('content'), max_length=102400, min_length=1, allow_null=True,
                                    allow_blank=True)
    title = serializers.CharField(required=False, max_length=256, label=_('section title'), allow_null=True,
                                  allow_blank=True)
    problem_list = serializers.ListField(required=False, child=serializers.CharField(required=False, allow_blank=True))
    is_active = serializers.BooleanField(required=False, label=_('Is active'))
    chunks = serializers.ListField(required=False, child=serializers.CharField(required=True))


class KnowledgeWriteParamSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, label=_('document name'), max_length=128, min_length=1,
                                 source=_('document name'))
    meta = serializers.DictField(required=False)
    paragraphs = ParagraphInstanceSerializer(required=False, many=True, allow_null=True)
    source_file_id = serializers.UUIDField(required=False, allow_null=True)


def convert_uuid_to_str(obj):
    if isinstance(obj, dict):
        return {k: convert_uuid_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_uuid_to_str(i) for i in obj]
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    else:
        return obj

def link_file(source_file_id, document_id):
    if source_file_id is None:
        return
    source_file = QuerySet(File).filter(id=source_file_id).first()
    if source_file:
        file_content = source_file.get_bytes()

        new_file = File(
            id=uuid.uuid7(),
            file_name=source_file.file_name,
            file_size=source_file.file_size,
            source_type=FileSourceType.DOCUMENT,
            source_id=document_id,  # 更新为当前知识库ID
            meta=source_file.meta.copy() if source_file.meta else {}
        )

        # 保存文件内容和元数据
        new_file.save(file_content)

def get_paragraph_problem_model(knowledge_id: str, document_id: str, instance: Dict):
    paragraph = Paragraph(
        id=uuid.uuid7(),
        document_id=document_id,
        content=instance.get("content"),
        knowledge_id=knowledge_id,
        title=instance.get("title") if 'title' in instance else '',
        chunks = instance.get('chunks') if 'chunks' in instance else text_to_chunk(instance.get("content")),
    )

    problem_paragraph_object_list = [ProblemParagraphObject(
        knowledge_id, document_id, str(paragraph.id), problem
    ) for problem in (instance.get('problem_list') if 'problem_list' in instance else [])]

    return {
        'paragraph': paragraph,
        'problem_paragraph_object_list': problem_paragraph_object_list,
    }


def get_paragraph_model(document_model, paragraph_list: List):
    knowledge_id = document_model.knowledge_id
    paragraph_model_dict_list = [
        get_paragraph_problem_model(knowledge_id, document_model.id, paragraph)
        for paragraph in paragraph_list
    ]

    paragraph_model_list = []
    problem_paragraph_object_list = []
    for paragraphs in paragraph_model_dict_list:
        paragraph = paragraphs.get('paragraph')
        for problem_model in paragraphs.get('problem_paragraph_object_list'):
            problem_paragraph_object_list.append(problem_model)
        paragraph_model_list.append(paragraph)

    return {
        'document': document_model,
        'paragraph_model_list': paragraph_model_list,
        'problem_paragraph_object_list': problem_paragraph_object_list,
    }


def get_document_paragraph_model(knowledge_id: str, instance: Dict):
    source_meta = {'source_file_id': instance.get("source_file_id")} if instance.get("source_file_id") else {}
    meta = {**instance.get('meta'), **source_meta} if instance.get('meta') is not None else source_meta
    meta = {**convert_uuid_to_str(meta), 'allow_download': True}

    document_model = Document(
        **{
            'knowledge_id': knowledge_id,
            'id': uuid.uuid7(),
            'name': instance.get('name'),
            'char_length': reduce(
                lambda x, y: x + y,
                [len(p.get('content')) for p in instance.get('paragraphs', [])],
                0),
            'meta': meta,
            'type': instance.get('type') if instance.get('type') is not None else KnowledgeType.WORKFLOW
        }
    )

    return get_paragraph_model(
        document_model,
        instance.get('paragraphs') if 'paragraphs' in instance else []
    )


class BaseKnowledgeWriteNode(IKnowledgeWriteNode):

    def save_context(self, details, workflow_manage):
        pass

    def save(self, document_list):
        serializer = KnowledgeWriteParamSerializer(data=document_list, many=True)
        serializer.is_valid(raise_exception=True)
        document_list = serializer.data

        knowledge_id = self.workflow_params.get("knowledge_id")
        workspace_id = self.workflow_params.get("workspace_id")

        document_model_list = []
        paragraph_model_list = []
        problem_paragraph_object_list = []

        for document in document_list:
            document_paragraph_dict_model = get_document_paragraph_model(
                knowledge_id,
                document
            )
            document_instance = document_paragraph_dict_model.get('document')
            link_file(document.get("source_file_id"), document_instance.id)
            document_model_list.append(document_instance)
            for paragraph in document_paragraph_dict_model.get("paragraph_model_list"):
                paragraph_model_list.append(paragraph)
            for problem_paragraph_object in document_paragraph_dict_model.get("problem_paragraph_object_list"):
                problem_paragraph_object_list.append(problem_paragraph_object)

        problem_model_list, problem_paragraph_mapping_list = (
            ProblemParagraphManage(problem_paragraph_object_list, knowledge_id).to_problem_model_list()
        )

        QuerySet(Document).bulk_create(document_model_list) if len(document_model_list) > 0 else None

        if len(paragraph_model_list) > 0:
            for document in document_model_list:
                max_position = Paragraph.objects.filter(document_id=document.id).aggregate(
                    max_position=Max('position')
                )['max_position'] or 0
                sub_list = [p for p in paragraph_model_list if p.document_id == document.id]
                for i, paragraph in enumerate(sub_list):
                    paragraph.position = max_position + i + 1
                QuerySet(Paragraph).bulk_create(sub_list if len(sub_list) > 0 else [])

        bulk_create_in_batches(Problem, problem_model_list, batch_size=1000)

        bulk_create_in_batches(ProblemParagraphMapping, problem_paragraph_mapping_list, batch_size=1000)

        return document_model_list, knowledge_id, workspace_id

    @staticmethod
    def post_embedding(document_model_list, knowledge_id, workspace_id):
        for document in document_model_list:
            DocumentSerializers.Operate(data={
                'knowledge_id': knowledge_id,
                'document_id': document.id,
                'workspace_id': workspace_id
            }).refresh()

    def execute(self, documents, **kwargs) -> NodeResult:

        document_model_list, knowledge_id, workspace_id = self.save(documents)
        self.post_embedding(document_model_list, knowledge_id, workspace_id)

        write_content_list = [{
            "name": document.get("name"),
            "paragraphs": [{
                "title": p.get("title"),
                "content": p.get("content"),
            } for p in document.get("paragraphs")[0:5]]
        } for document in documents]

        return NodeResult({'write_content': write_content_list}, {})

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'write_content': self.context.get("write_content"),
            'status': self.status,
            'err_message': self.err_message
        }
