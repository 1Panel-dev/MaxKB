from functools import reduce
from typing import Dict

import uuid_utils.compat as uuid
from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.exception.app_exception import AppApiException
from common.utils.common import valid_license, post
from knowledge.models import Knowledge, KnowledgeScope, KnowledgeType, Document, Paragraph, Problem, \
    ProblemParagraphMapping
from knowledge.serializers.common import ProblemParagraphManage, get_embedding_model_id_by_knowledge_id
from knowledge.serializers.document import DocumentSerializers
from knowledge.task import sync_web_knowledge, embedding_by_knowledge


class KnowledgeModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Knowledge
        fields = ['id', 'name', 'desc', 'meta', 'folder_id', 'type', 'workspace_id', 'create_time', 'update_time']


class KnowledgeBaseCreateRequest(serializers.Serializer):
    name = serializers.CharField(required=True, label=_('knowledge name'))
    folder_id = serializers.CharField(required=True, label=_('folder id'))
    desc = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('knowledge description'))
    embedding = serializers.CharField(required=True, label=_('knowledge embedding'))


class KnowledgeWebCreateRequest(serializers.Serializer):
    name = serializers.CharField(required=True, label=_('knowledge name'))
    folder_id = serializers.CharField(required=True, label=_('folder id'))
    desc = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('knowledge description'))
    embedding = serializers.CharField(required=True, label=_('knowledge embedding'))
    source_url = serializers.CharField(required=True, label=_('source url'))
    selector = serializers.CharField(required=True, label=_('knowledge selector'))


class KnowledgeSerializer(serializers.Serializer):
    class Create(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_('user id'))
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))

        @staticmethod
        def post_embedding_knowledge(document_list, knowledge_id):
            # todo 发送向量化事件
            model_id = get_embedding_model_id_by_knowledge_id(knowledge_id)
            embedding_by_knowledge.delay(knowledge_id, model_id)
            return document_list

        @valid_license(model=Knowledge, count=50,
                       message=_(
                           'The community version supports up to 50 knowledge bases. If you need more knowledge bases, please contact us (https://fit2cloud.com/).'))
        @post(post_function=post_embedding_knowledge)
        @transaction.atomic
        def save_base(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                KnowledgeBaseCreateRequest(data=instance).is_valid(raise_exception=True)
            if QuerySet(Knowledge).filter(workspace_id=self.data.get('workspace_id'),
                                          name=instance.get('name')).exists():
                raise AppApiException(500, _('Knowledge base name duplicate!'))

            knowledge_id = uuid.uuid7()
            knowledge = Knowledge(
                id=knowledge_id,
                name=instance.get('name'),
                workspace_id=self.data.get('workspace_id'),
                desc=instance.get('desc'),
                type=instance.get('type', KnowledgeType.BASE),
                user_id=self.data.get('user_id'),
                scope=KnowledgeScope.WORKSPACE,
                folder_id=instance.get('folder_id', 'root'),
                embedding_model_id=instance.get('embedding'),
                meta=instance.get('meta', {}),
            )

            document_model_list = []
            paragraph_model_list = []
            problem_paragraph_object_list = []
            # 插入文档
            for document in instance.get('documents') if 'documents' in instance else []:
                document_paragraph_dict_model = DocumentSerializers.Create.get_document_paragraph_model(knowledge_id,
                                                                                                        document)
                document_model_list.append(document_paragraph_dict_model.get('document'))
                for paragraph in document_paragraph_dict_model.get('paragraph_model_list'):
                    paragraph_model_list.append(paragraph)
                for problem_paragraph_object in document_paragraph_dict_model.get('problem_paragraph_object_list'):
                    problem_paragraph_object_list.append(problem_paragraph_object)

            problem_model_list, problem_paragraph_mapping_list = (
                ProblemParagraphManage(problem_paragraph_object_list, knowledge_id)
                .to_problem_model_list())
            # 插入知识库
            knowledge.save()
            # 插入文档
            QuerySet(Document).bulk_create(document_model_list) if len(document_model_list) > 0 else None
            # 批量插入段落
            QuerySet(Paragraph).bulk_create(paragraph_model_list) if len(paragraph_model_list) > 0 else None
            # 批量插入问题
            QuerySet(Problem).bulk_create(problem_model_list) if len(problem_model_list) > 0 else None
            # 批量插入关联问题
            QuerySet(ProblemParagraphMapping).bulk_create(problem_paragraph_mapping_list) if len(
                problem_paragraph_mapping_list) > 0 else None

            return {
                **KnowledgeModelSerializer(knowledge).data,
                'user_id': self.data.get('user_id'),
                'document_list': document_model_list,
                "document_count": len(document_model_list),
                "char_length": reduce(lambda x, y: x + y, [d.char_length for d in document_model_list], 0)
            }, knowledge_id

        def save_web(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                KnowledgeWebCreateRequest(data=instance).is_valid(raise_exception=True)

            if QuerySet(Knowledge).filter(workspace_id=self.data.get('workspace_id'),
                                          name=instance.get('name')).exists():
                raise AppApiException(500, _('Knowledge base name duplicate!'))

            knowledge_id = uuid.uuid7()
            knowledge = Knowledge(
                id=knowledge_id,
                name=instance.get('name'),
                desc=instance.get('desc'),
                user_id=self.data.get('user_id'),
                type=instance.get('type', KnowledgeType.WEB),
                scope=KnowledgeScope.WORKSPACE,
                folder_id=instance.get('folder_id', 'root'),
                embedding_model_id=instance.get('embedding'),
                meta={
                    'source_url': instance.get('source_url'),
                    'selector': instance.get('selector'),
                    'embedding_model_id': instance.get('embedding')
                },
            )
            knowledge.save()
            sync_web_knowledge.delay(str(knowledge_id), instance.get('source_url'), instance.get('selector'))
            return {**KnowledgeModelSerializer(knowledge).data, 'document_list': []}


class KnowledgeTreeSerializer(serializers.Serializer):
    def get_knowledge_list(self, param):
        pass
