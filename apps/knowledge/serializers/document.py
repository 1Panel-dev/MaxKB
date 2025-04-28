import os
from functools import reduce
from typing import Dict, List

import uuid_utils.compat as uuid
from celery_once import AlreadyQueued
from django.db import transaction
from django.db.models import QuerySet, Model
from django.db.models.functions import Substr, Reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.db.search import native_search
from common.event import ListenerManagement
from common.exception.app_exception import AppApiException
from common.utils.common import post, get_file_content
from knowledge.models import Knowledge, Paragraph, Problem, Document, KnowledgeType, ProblemParagraphMapping, State, \
    TaskType
from knowledge.serializers.common import ProblemParagraphManage
from knowledge.serializers.paragraph import ParagraphSerializers, ParagraphInstanceSerializer
from knowledge.task import embedding_by_document
from maxkb.const import PROJECT_DIR


class DocumentInstanceSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, label=_('document name'), max_length=128, min_length=1)
    paragraphs = ParagraphInstanceSerializer(required=False, many=True, allow_null=True)


class DocumentCreateRequest(serializers.Serializer):
    name = serializers.CharField(required=True, label=_('knowledge name'), max_length=64, min_length=1)
    desc = serializers.CharField(required=True, label=_('knowledge description'), max_length=256, min_length=1)
    embedding_model_id = serializers.UUIDField(required=True, label=_('embedding model'))
    documents = DocumentInstanceSerializer(required=False, many=True)


class DocumentSerializers(serializers.Serializer):
    class Operate(serializers.Serializer):
        document_id = serializers.UUIDField(required=True, label=_('document id'))
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            document_id = self.data.get('document_id')
            if not QuerySet(Document).filter(id=document_id).exists():
                raise AppApiException(500, _('document id not exist'))

        def one(self, with_valid=False):
            if with_valid:
                self.is_valid(raise_exception=True)
            query_set = QuerySet(model=Document)
            query_set = query_set.filter(**{'id': self.data.get("document_id")})
            return native_search({
                'document_custom_sql': query_set,
                'order_by_query': QuerySet(Document).order_by('-create_time', 'id')
            }, select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "knowledge", 'sql', 'list_document.sql')), with_search_one=True)

        def refresh(self, state_list=None, with_valid=True):
            if state_list is None:
                state_list = [State.PENDING.value, State.STARTED.value, State.SUCCESS.value, State.FAILURE.value,
                              State.REVOKE.value,
                              State.REVOKED.value, State.IGNORED.value]
            if with_valid:
                self.is_valid(raise_exception=True)
            knowledge = QuerySet(Knowledge).filter(id=self.data.get('knowledge_id')).first()
            embedding_model_id = knowledge.embedding_model_id
            knowledge_user_id = knowledge.user_id
            embedding_model = QuerySet(Model).filter(id=embedding_model_id).first()
            if embedding_model is None:
                raise AppApiException(500, _('Model does not exist'))
            if embedding_model.permission_type == 'PRIVATE' and knowledge_user_id != embedding_model.user_id:
                raise AppApiException(500, _('No permission to use this model') + f"{embedding_model.name}")
            document_id = self.data.get("document_id")
            ListenerManagement.update_status(QuerySet(Document).filter(id=document_id), TaskType.EMBEDDING,
                                             State.PENDING)
            ListenerManagement.update_status(QuerySet(Paragraph).annotate(
                reversed_status=Reverse('status'),
                task_type_status=Substr('reversed_status', TaskType.EMBEDDING.value, 1),
            ).filter(task_type_status__in=state_list, document_id=document_id).values('id'),
                                             TaskType.EMBEDDING, State.PENDING)
            ListenerManagement.get_aggregation_document_status(document_id)()

            try:
                embedding_by_document.delay(document_id, embedding_model_id, state_list)
            except AlreadyQueued as e:
                raise AppApiException(500, _('The task is being executed, please do not send it repeatedly.'))

    class Create(serializers.Serializer):
        knowledge_id = serializers.UUIDField(required=True, label=_('document id'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if not QuerySet(Knowledge).filter(id=self.data.get('knowledge_id')).exists():
                raise AppApiException(10000, _('knowledge id not exist'))
            return True

        @staticmethod
        def post_embedding(result, document_id, knowledge_id):
            DocumentSerializers.Operate(
                data={'knowledge_id': knowledge_id, 'document_id': document_id}).refresh()
            return result

        @post(post_function=post_embedding)
        @transaction.atomic
        def save(self, instance: Dict, with_valid=False, **kwargs):
            if with_valid:
                DocumentCreateRequest(data=instance).is_valid(raise_exception=True)
                self.is_valid(raise_exception=True)
            knowledge_id = self.data.get('knowledge_id')
            document_paragraph_model = self.get_document_paragraph_model(knowledge_id, instance)

            document_model = document_paragraph_model.get('document')
            paragraph_model_list = document_paragraph_model.get('paragraph_model_list')
            problem_paragraph_object_list = document_paragraph_model.get('problem_paragraph_object_list')
            problem_model_list, problem_paragraph_mapping_list = (
                ProblemParagraphManage(problem_paragraph_object_list, knowledge_id).to_problem_model_list())
            # 插入文档
            document_model.save()
            # 批量插入段落
            QuerySet(Paragraph).bulk_create(paragraph_model_list) if len(paragraph_model_list) > 0 else None
            # 批量插入问题
            QuerySet(Problem).bulk_create(problem_model_list) if len(problem_model_list) > 0 else None
            # 批量插入关联问题
            QuerySet(ProblemParagraphMapping).bulk_create(problem_paragraph_mapping_list) if len(
                problem_paragraph_mapping_list) > 0 else None
            document_id = str(document_model.id)
            return (DocumentSerializers.Operate(
                data={'knowledge_id': knowledge_id, 'document_id': document_id}
            ).one(with_valid=True), document_id, knowledge_id)

        @staticmethod
        def get_paragraph_model(document_model, paragraph_list: List):
            knowledge_id = document_model.knowledge_id
            paragraph_model_dict_list = [
                ParagraphSerializers.Create(
                    data={
                        'knowledge_id': knowledge_id, 'document_id': str(document_model.id)
                    }).get_paragraph_problem_model(knowledge_id, document_model.id, paragraph)
                for paragraph in paragraph_list]

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
                'problem_paragraph_object_list': problem_paragraph_object_list
            }

        @staticmethod
        def get_document_paragraph_model(knowledge_id, instance: Dict):
            document_model = Document(
                **{
                    'knowledge_id': knowledge_id,
                    'id': uuid.uuid7(),
                    'name': instance.get('name'),
                    'char_length': reduce(lambda x, y: x + y,
                                          [len(p.get('content')) for p in instance.get('paragraphs', [])],
                                          0),
                    'meta': instance.get('meta') if instance.get('meta') is not None else {},
                    'type': instance.get('type') if instance.get('type') is not None else KnowledgeType.BASE
                })

            return DocumentSerializers.Create.get_paragraph_model(document_model,
                                                                  instance.get('paragraphs') if
                                                                  'paragraphs' in instance else [])
