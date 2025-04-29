import os
from functools import reduce
from typing import Dict

import uuid_utils.compat as uuid
from django.db import transaction, models
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.db.search import native_search, get_dynamics_model, native_page_search
from common.db.sql_execute import select_list
from common.exception.app_exception import AppApiException
from common.utils.common import valid_license, post, get_file_content
from knowledge.models import Knowledge, KnowledgeScope, KnowledgeType, Document, Paragraph, Problem, \
    ProblemParagraphMapping, ApplicationKnowledgeMapping
from knowledge.serializers.common import ProblemParagraphManage, get_embedding_model_id_by_knowledge_id, MetaSerializer
from knowledge.serializers.document import DocumentSerializers
from knowledge.task import sync_web_knowledge, embedding_by_knowledge, delete_embedding_by_knowledge
from maxkb.conf import PROJECT_DIR


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


class KnowledgeEditRequest(serializers.Serializer):
    name = serializers.CharField(required=False, max_length=64, min_length=1, label=_('knowledge name'))
    desc = serializers.CharField(required=False, max_length=256, min_length=1, label=_('knowledge description'))
    meta = serializers.DictField(required=False)
    application_id_list = serializers.ListSerializer(
        required=False,
        child=serializers.UUIDField(required=True, label=_('application id')),
        label=_('application id list')
    )

    @staticmethod
    def get_knowledge_meta_valid_map():
        knowledge_meta_valid_map = {
            KnowledgeType.BASE: MetaSerializer.BaseMeta,
            KnowledgeType.WEB: MetaSerializer.WebMeta
        }
        return knowledge_meta_valid_map

    def is_valid(self, *, knowledge: Knowledge = None):
        super().is_valid(raise_exception=True)
        if 'meta' in self.data and self.data.get('meta') is not None:
            knowledge_meta_valid_map = self.get_knowledge_meta_valid_map()
            valid_class = knowledge_meta_valid_map.get(knowledge.type)
            valid_class(data=self.data.get('meta')).is_valid(raise_exception=True)


class KnowledgeSerializer(serializers.Serializer):
    class Query(serializers.Serializer):
        workspace_id = serializers.CharField(required=True)
        folder_id = serializers.CharField(required=True)
        name = serializers.CharField(required=False, label=_('knowledge name'), allow_null=True, allow_blank=True,
                                     max_length=64, min_length=1)
        desc = serializers.CharField(required=False, label=_('knowledge description'), allow_null=True,
                                     allow_blank=True, max_length=256, min_length=1)
        user_id = serializers.UUIDField(required=False, label=_('user id'), allow_null=True)

        def get_query_set(self):
            workspace_id = self.data.get("workspace_id")
            query_set_dict = {}
            query_set = QuerySet(model=get_dynamics_model({
                'temp.name': models.CharField(),
                'temp.desc': models.CharField(),
                "document_temp.char_length": models.IntegerField(),
                'temp.create_time': models.DateTimeField(),
                'temp.user_id': models.CharField(),
                'temp.workspace_id': models.CharField(),
                'temp.folder_id': models.CharField(),
                'temp.id': models.CharField()
            }))
            if "desc" in self.data and self.data.get('desc') is not None:
                query_set = query_set.filter(**{'temp.desc__icontains': self.data.get("desc")})
            if "name" in self.data and self.data.get('name') is not None:
                query_set = query_set.filter(**{'temp.name__icontains': self.data.get("name")})
            if "user_id" in self.data and self.data.get('user_id') is not None:
                query_set = query_set.filter(**{'temp.user_id': self.data.get("user_id")})
            if "workspace_id" in self.data and self.data.get('workspace_id') is not None:
                query_set = query_set.filter(**{'temp.workspace_id': self.data.get("workspace_id")})
            if "folder_id" in self.data and self.data.get('folder_id') is not None:
                query_set = query_set.filter(**{'temp.folder_id': self.data.get("folder_id")})
            query_set = query_set.order_by("-temp.create_time", "temp.id")
            query_set_dict['default_sql'] = query_set

            query_set_dict['knowledge_custom_sql'] = QuerySet(model=get_dynamics_model({
                'knowledge.workspace_id': models.CharField(),
            })).filter(**{'knowledge.workspace_id': workspace_id})

            return query_set_dict

        def page(self, current_page: int, page_size: int):
            self.is_valid(raise_exception=True)
            return native_page_search(
                current_page,
                page_size,
                self.get_query_set(),
                select_string=get_file_content(
                    os.path.join(PROJECT_DIR, "apps", "knowledge", 'sql', 'list_knowledge.sql')
                ),
                post_records_handler=lambda r: r
            )

        def list(self):
            self.is_valid(raise_exception=True)
            return native_search(
                self.get_query_set(),
                select_string=get_file_content(
                    os.path.join(PROJECT_DIR, "apps", "knowledge", 'sql', 'list_knowledge.sql')
                )
            )

    class Operate(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_('user id'))
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))

        def list_application(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            knowledge = QuerySet(Knowledge).get(id=self.data.get("knowledge_id"))
            return select_list(
                get_file_content(
                    os.path.join(PROJECT_DIR, "apps", "knowledge", 'sql', 'list_knowledge_application.sql')
                ),
                [
                    self.data.get('user_id') if self.data.get('user_id') == str(knowledge.user_id) else None,
                    knowledge.user_id,
                    self.data.get('user_id')
                ]
            )

        def one(self):
            self.is_valid()
            query_set_dict = {
                'default_sql': QuerySet(
                    model=get_dynamics_model({'temp.id': models.UUIDField()})
                ).filter(**{'temp.id': self.data.get("knowledge_id")}),
                'knowledge_custom_sql': QuerySet(
                    model=get_dynamics_model({'knowledge.user_id': models.CharField()})
                ).filter(**{'knowledge.user_id': self.data.get("user_id")}),
            }
            # todo 这里需要优化
            # all_application_list = [str(adm.get('id')) for adm in self.list_application(with_valid=False)]
            all_application_list = []
            return {
                **native_search(query_set_dict, select_string=get_file_content(
                    os.path.join(PROJECT_DIR, "apps", "knowledge", 'sql', 'list_knowledge.sql')), with_search_one=True),
                'application_id_list': list(filter(
                    lambda application_id: all_application_list.__contains__(application_id),
                    [
                        str(
                            application_knowledge_mapping.application_id
                        ) for application_knowledge_mapping in
                        QuerySet(ApplicationKnowledgeMapping).filter(knowledge_id=self.data.get('knowledge_id'))
                    ]
                ))
            }

        @transaction.atomic
        def edit(self, instance: Dict):
            self.is_valid()
            if QuerySet(Knowledge).filter(
                    workspace_id=self.data.get('workspace_id'),
                    name=instance.get('name')
            ).exclude(id=self.data.get('knowledge_id')).exists():
                raise AppApiException(500, _('Knowledge base name duplicate!'))
            knowledge = QuerySet(Knowledge).get(id=self.data.get("knowledge_id"))
            KnowledgeEditRequest(data=instance).is_valid(knowledge=knowledge)
            if 'embedding_model_id' in instance:
                knowledge.embedding_model_id = instance.get('embedding_model_id')
            if "name" in instance:
                knowledge.name = instance.get("name")
            if 'desc' in instance:
                knowledge.desc = instance.get("desc")
            if 'meta' in instance:
                knowledge.meta = instance.get('meta')
            if 'application_id_list' in instance and instance.get('application_id_list') is not None:
                application_id_list = instance.get('application_id_list')
                # 当前用户可修改关联的知识库列表
                application_knowledge_id_list = [
                    str(knowledge_dict.get('id')) for knowledge_dict in self.list_application(with_valid=False)
                ]
                for knowledge_id in application_id_list:
                    if not application_knowledge_id_list.__contains__(knowledge_id):
                        raise AppApiException(
                            500,
                            _(
                                'Unknown application id {knowledge_id}, cannot be associated'
                            ).format(knowledge_id=knowledge_id)
                        )

                QuerySet(ApplicationKnowledgeMapping).filter(
                    application_id__in=application_knowledge_id_list,
                    knowledge_id=self.data.get("knowledge_id")
                ).delete()
                # 插入
                QuerySet(ApplicationKnowledgeMapping).bulk_create([
                    ApplicationKnowledgeMapping(
                        application_id=application_id, knowledge_id=self.data.get('knowledge_id')
                    ) for application_id in application_id_list
                ]) if len(application_id_list) > 0 else None

            knowledge.save()
            return self.one()

        @transaction.atomic
        def delete(self):
            self.is_valid()
            knowledge = QuerySet(Knowledge).get(id=self.data.get("knowledge_id"))
            QuerySet(Document).filter(knowledge=knowledge).delete()
            QuerySet(ProblemParagraphMapping).filter(knowledge=knowledge).delete()
            QuerySet(Paragraph).filter(knowledge=knowledge).delete()
            QuerySet(Problem).filter(knowledge=knowledge).delete()
            knowledge.delete()
            delete_embedding_by_knowledge(self.data.get('knowledge_id'))
            return True

    class Create(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_('user id'))
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))

        @staticmethod
        def post_embedding_knowledge(document_list, knowledge_id):
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
            QuerySet(ProblemParagraphMapping).bulk_create(
                problem_paragraph_mapping_list
            ) if len(problem_paragraph_mapping_list) > 0 else None

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
