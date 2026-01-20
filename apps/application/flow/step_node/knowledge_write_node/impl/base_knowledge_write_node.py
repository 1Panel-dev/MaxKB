# coding=utf-8
"""
    @project: MaxKB
    @Author：niu
    @file： base_knowledge_write_node.py
    @date：2025/11/13 11:19
    @desc:
"""
from functools import reduce
from typing import Dict, List, Any
import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.db.models.aggregates import Max

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from application.flow.i_step_node import NodeResult
from application.flow.step_node.knowledge_write_node.i_knowledge_write_node import IKnowledgeWriteNode
from common.chunk import text_to_chunk
from common.utils.common import bulk_create_in_batches, filter_special_character
from knowledge.models import Document, KnowledgeType, Paragraph, File, FileSourceType, Problem, ProblemParagraphMapping, \
    Tag, DocumentTag
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


class TagInstanceSerializer(serializers.Serializer):
    key = serializers.CharField(required=True, max_length=64, label=_('Tag Key'))
    value = serializers.CharField(required=True, max_length=128, label=_('Tag Value'))


class KnowledgeWriteParamSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, label=_('document name'), max_length=128, min_length=1,
                                 source=_('document name'))
    meta = serializers.DictField(required=False)
    tags = serializers.ListField(required=False, label=_('Tags'), child=TagInstanceSerializer())
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
        content=filter_special_character(instance.get("content")),
        knowledge_id=knowledge_id,
        title=instance.get("title") if 'title' in instance else '',
        chunks=[filter_special_character(c) for c in (instance.get('chunks') if 'chunks' in instance else text_to_chunk(
            instance.get("content")))],
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


def save_knowledge_tags(knowledge_id: str, tags: List[Dict[str, Any]]):
    existed_tags_dict = {
        (key, value): str(tag_id)
        for key, value, tag_id in QuerySet(Tag).filter(knowledge_id=knowledge_id).values_list("key", "value", "id")
    }

    tag_model_list = []
    new_tag_dict = {}
    for tag in tags:
        key = tag.get("key")
        value = tag.get("value")

        if (key, value) not in existed_tags_dict:
            tag_model = Tag(
                id=uuid.uuid7(),
                knowledge_id=knowledge_id,
                key=key,
                value=value
            )
            tag_model_list.append(tag_model)
            new_tag_dict[(key, value)] = str(tag_model.id)

    if tag_model_list:
        Tag.objects.bulk_create(tag_model_list)

    all_tag_dict = {**existed_tags_dict, **new_tag_dict}

    return all_tag_dict, new_tag_dict


def batch_add_document_tag(document_tag_map: Dict[str, List[str]]):
    """
    批量添加文档-标签关联
    document_tag_map: {document_id: [tag_id1, tag_id2, ...]}
    """
    all_document_ids = list(document_tag_map.keys())
    all_tag_ids = list(set(tag_id for tag_ids in document_tag_map.values() for tag_id in tag_ids))

    # 查询已存在的文档-标签关联
    existed_relations = set(
        QuerySet(DocumentTag).filter(
            document_id__in=all_document_ids,
            tag_id__in=all_tag_ids
        ).values_list('document_id', 'tag_id')
    )

    new_relations = [
        DocumentTag(
            id=uuid.uuid7(),
            document_id=doc_id,
            tag_id=tag_id,
        )
        for doc_id, tag_ids in document_tag_map.items()
        for tag_id in tag_ids
        if (doc_id, tag_id) not in existed_relations
    ]

    if new_relations:
        QuerySet(DocumentTag).bulk_create(new_relations)


class BaseKnowledgeWriteNode(IKnowledgeWriteNode):

    def save_context(self, details, workflow_manage):
        self.context['exception_message'] = details.get('err_message')

    def save(self, document_list):
        serializer = KnowledgeWriteParamSerializer(data=document_list, many=True)
        serializer.is_valid(raise_exception=True)
        document_list = serializer.data

        knowledge_id = self.workflow_params.get("knowledge_id")
        workspace_id = self.workflow_params.get("workspace_id")

        document_model_list = []
        paragraph_model_list = []
        problem_paragraph_object_list = []
        # 所有标签
        knowledge_tag_list = []
        # 文档标签映射关系
        document_tags_map = {}
        knowledge_tag_dict = {}

        for document in document_list:
            document_paragraph_dict_model = get_document_paragraph_model(
                knowledge_id,
                document
            )
            document_instance = document_paragraph_dict_model.get('document')
            link_file(document.get("source_file_id"), document_instance.id)
            document_model_list.append(document_instance)
            # 收集标签
            single_document_tag_list = document.get("tags", [])
            # 去重传入的标签
            for tag in single_document_tag_list:
                tag_key = (tag['key'], tag['value'])
                if tag_key not in knowledge_tag_dict:
                    knowledge_tag_dict[tag_key] = tag

            if single_document_tag_list:
                document_tags_map[str(document_instance.id)] = single_document_tag_list

            for paragraph in document_paragraph_dict_model.get("paragraph_model_list"):
                paragraph_model_list.append(paragraph)
            for problem_paragraph_object in document_paragraph_dict_model.get("problem_paragraph_object_list"):
                problem_paragraph_object_list.append(problem_paragraph_object)
        knowledge_tag_list = list(knowledge_tag_dict.values())
        # 保存所有文档中含有的标签到知识库
        if knowledge_tag_list:
            all_tag_dict, new_tag_dict = save_knowledge_tags(knowledge_id, knowledge_tag_list)
            # 构建文档-标签ID映射
            document_tag_id_map = {}
            # 为每个文档添加其对应的标签
            for doc_id, doc_tags in document_tags_map.items():
                doc_tag_ids = [
                    all_tag_dict[(tag.get("key"), tag.get("value"))]
                    for tag in doc_tags
                    if (tag.get("key"), tag.get("value")) in all_tag_dict
                ]
                if doc_tag_ids:
                    document_tag_id_map[doc_id] = doc_tag_ids
            if document_tag_id_map:
                batch_add_document_tag(document_tag_id_map)

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
            'err_message': self.err_message,
            'enableException': self.node.properties.get('enableException'),
        }
