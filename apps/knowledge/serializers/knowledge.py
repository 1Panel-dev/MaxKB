import io
import logging
import os
import re
import traceback
from functools import reduce
from tempfile import TemporaryDirectory
from typing import Dict, List

import uuid_utils.compat as uuid
from celery_once import AlreadyQueued
from django.core import validators
from django.db import transaction, models
from django.db.models import QuerySet
from django.db.models.functions import Reverse, Substr
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import ApplicationKnowledgeMapping
from common.config.embedding_config import VectorStore
from common.db.search import native_search, get_dynamics_model, native_page_search
from common.db.sql_execute import select_list
from common.event import ListenerManagement
from common.exception.app_exception import AppApiException
from common.utils.common import valid_license, post, get_file_content, parse_image
from common.utils.fork import Fork, ChildLink
from common.utils.split_model import get_split_model
from knowledge.models import Knowledge, KnowledgeScope, KnowledgeType, Document, Paragraph, Problem, \
    ProblemParagraphMapping, TaskType, State, SearchMode, KnowledgeFolder
from knowledge.serializers.common import ProblemParagraphManage, get_embedding_model_id_by_knowledge_id, MetaSerializer, \
    GenerateRelatedSerializer, get_embedding_model_by_knowledge_id, list_paragraph, write_image, zip_dir
from knowledge.serializers.document import DocumentSerializers
from knowledge.task.embedding import embedding_by_knowledge, delete_embedding_by_knowledge
from knowledge.task.generate import generate_related_by_knowledge_id
from knowledge.task.sync import sync_web_knowledge, sync_replace_web_knowledge
from maxkb.conf import PROJECT_DIR
from models_provider.models import Model


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


class HitTestSerializer(serializers.Serializer):
    query_text = serializers.CharField(required=True, label=_('query text'))
    top_number = serializers.IntegerField(required=True, max_value=10000, min_value=1, label=_("top number"))
    similarity = serializers.FloatField(required=True, max_value=2, min_value=0, label=_('similarity'))
    search_mode = serializers.CharField(required=True, label=_('search mode'), validators=[
        validators.RegexValidator(regex=re.compile("^embedding|keywords|blend$"),
                                  message=_('The type only supports embedding|keywords|blend'), code=500)
    ])


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
            folder_query_set = QuerySet(KnowledgeFolder)

            if "desc" in self.data and self.data.get('desc') is not None:
                query_set = query_set.filter(**{'temp.desc__icontains': self.data.get("desc")})
                folder_query_set = folder_query_set.filter(**{'desc__icontains': self.data.get("desc")})
            if "name" in self.data and self.data.get('name') is not None:
                query_set = query_set.filter(**{'temp.name__icontains': self.data.get("name")})
                folder_query_set = folder_query_set.filter(**{'name__icontains': self.data.get("name")})
            if "user_id" in self.data and self.data.get('user_id') is not None:
                query_set = query_set.filter(**{'temp.user_id': self.data.get("user_id")})
                folder_query_set = folder_query_set.filter(**{'user_id': self.data.get("user_id")})
            if "workspace_id" in self.data and self.data.get('workspace_id') is not None:
                query_set = query_set.filter(**{'temp.workspace_id': self.data.get("workspace_id")})
                folder_query_set = folder_query_set.filter(**{'workspace_id': self.data.get("workspace_id")})
            if "folder_id" in self.data and self.data.get('folder_id') is not None:
                query_set = query_set.filter(**{'temp.folder_id': self.data.get("folder_id")})
                folder_query_set = folder_query_set.filter(**{'parent_id': self.data.get("folder_id")})
            query_set = query_set.order_by("-temp.create_time", "temp.id")
            query_set_dict['default_sql'] = query_set

            query_set_dict['knowledge_custom_sql'] = QuerySet(model=get_dynamics_model({
                'knowledge.workspace_id': models.CharField(),
            })).filter(**{'knowledge.workspace_id': workspace_id})
            query_set_dict['folder_query_set'] = folder_query_set
            return query_set_dict

        def page(self, current_page: int, page_size: int):
            self.is_valid(raise_exception=True)

            folder_id = self.data.get('folder_id', 'root')
            root = KnowledgeFolder.objects.filter(id=folder_id).first()
            if not root:
                raise serializers.ValidationError(_('Folder not found'))

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

        @transaction.atomic
        def embedding(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            knowledge_id = self.data.get('knowledge_id')
            knowledge = QuerySet(Knowledge).filter(id=knowledge_id).first()
            embedding_model_id = knowledge.embedding_model_id
            embedding_model = QuerySet(Model).filter(id=embedding_model_id).first()
            if embedding_model is None:
                raise AppApiException(500, _('Model does not exist'))
            ListenerManagement.update_status(
                QuerySet(Document).filter(knowledge_id=self.data.get('knowledge_id')),
                TaskType.EMBEDDING,
                State.PENDING
            )
            ListenerManagement.update_status(
                QuerySet(Paragraph).filter(knowledge_id=self.data.get('knowledge_id')),
                TaskType.EMBEDDING,
                State.PENDING
            )
            ListenerManagement.get_aggregation_document_status_by_knowledge_id(self.data.get('knowledge_id'))()
            embedding_model_id = get_embedding_model_id_by_knowledge_id(self.data.get('knowledge_id'))
            try:
                embedding_by_knowledge.delay(knowledge_id, embedding_model_id)
            except AlreadyQueued as e:
                raise AppApiException(500, _('Failed to send the vectorization task, please try again later!'))

        def generate_related(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                GenerateRelatedSerializer(data=instance).is_valid(raise_exception=True)
            knowledge_id = self.data.get('knowledge_id')
            model_id = instance.get("model_id")
            prompt = instance.get("prompt")
            state_list = instance.get('state_list')
            ListenerManagement.update_status(
                QuerySet(Document).filter(knowledge_id=knowledge_id),
                TaskType.GENERATE_PROBLEM,
                State.PENDING
            )
            ListenerManagement.update_status(
                QuerySet(Paragraph).annotate(
                    reversed_status=Reverse('status'),
                    task_type_status=Substr('reversed_status', TaskType.GENERATE_PROBLEM.value, 1),
                ).filter(
                    task_type_status__in=state_list, knowledge_id=knowledge_id
                ).values('id'),
                TaskType.GENERATE_PROBLEM,
                State.PENDING
            )
            ListenerManagement.get_aggregation_document_status_by_knowledge_id(knowledge_id)()
            try:
                generate_related_by_knowledge_id.delay(knowledge_id, model_id, prompt, state_list)
            except AlreadyQueued as e:
                raise AppApiException(500, _('Failed to send the vectorization task, please try again later!'))

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
        
        def export_excel(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            document_list = QuerySet(Document).filter(knowledge_id=self.data.get('id'))
            paragraph_list = native_search(QuerySet(Paragraph).filter(knowledge_id=self.data.get("id")), get_file_content(
                os.path.join(PROJECT_DIR, "apps", "knowledge", 'sql', 'list_paragraph_document_name.sql')))
            problem_mapping_list = native_search(
                QuerySet(ProblemParagraphMapping).filter(knowledge_id=self.data.get("id")), get_file_content(
                    os.path.join(PROJECT_DIR, "apps", "knowledge", 'sql', 'list_problem_mapping.sql')),
                with_table_name=True)
            data_dict, document_dict = DocumentSerializers.Operate.merge_problem(paragraph_list, problem_mapping_list,
                                                                                 document_list)
            workbook = DocumentSerializers.Operate.get_workbook(data_dict, document_dict)
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="knowledge.xlsx"'
            workbook.save(response)
            return response

        def export_zip(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            document_list = QuerySet(Document).filter(knowledge_id=self.data.get('id'))
            paragraph_list = native_search(QuerySet(Paragraph).filter(knowledge_id=self.data.get("id")), get_file_content(
                os.path.join(PROJECT_DIR, "apps", "knowledge", 'sql', 'list_paragraph_document_name.sql')))
            problem_mapping_list = native_search(
                QuerySet(ProblemParagraphMapping).filter(knowledge_id=self.data.get("id")), get_file_content(
                    os.path.join(PROJECT_DIR, "apps", "knowledge", 'sql', 'list_problem_mapping.sql')),
                with_table_name=True)
            data_dict, document_dict = DocumentSerializers.Operate.merge_problem(paragraph_list, problem_mapping_list,
                                                                                 document_list)
            res = [parse_image(paragraph.get('content')) for paragraph in paragraph_list]

            workbook = DocumentSerializers.Operate.get_workbook(data_dict, document_dict)
            response = HttpResponse(content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="archive.zip"'
            zip_buffer = io.BytesIO()
            with TemporaryDirectory() as tempdir:
                knowledge_file = os.path.join(tempdir, 'knowledge.xlsx')
                workbook.save(knowledge_file)
                for r in res:
                    write_image(tempdir, r)
                zip_dir(tempdir, zip_buffer)
            response.write(zip_buffer.getvalue())
            return response

        @staticmethod
        def merge_problem(paragraph_list: List[Dict], problem_mapping_list: List[Dict]):
            result = {}
            document_dict = {}

            for paragraph in paragraph_list:
                problem_list = [problem_mapping.get('content') for problem_mapping in problem_mapping_list if
                                problem_mapping.get('paragraph_id') == paragraph.get('id')]
                document_sheet = result.get(paragraph.get('document_id'))
                d = document_dict.get(paragraph.get('document_name'))
                if d is None:
                    document_dict[paragraph.get('document_name')] = {paragraph.get('document_id')}
                else:
                    d.add(paragraph.get('document_id'))

                if document_sheet is None:
                    result[paragraph.get('document_id')] = [[paragraph.get('title'), paragraph.get('content'),
                                                             '\n'.join(problem_list)]]
                else:
                    document_sheet.append([paragraph.get('title'), paragraph.get('content'), '\n'.join(problem_list)])
            result_document_dict = {}
            for d_name in document_dict:
                for index, d_id in enumerate(document_dict.get(d_name)):
                    result_document_dict[d_id] = d_name if index == 0 else d_name + str(index)
            return result, result_document_dict

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

    class SyncWeb(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        knowledge_id = serializers.CharField(required=True, label=_('knowledge id'))
        user_id = serializers.UUIDField(required=False, label=_('user id'))
        sync_type = serializers.CharField(required=True, label=_('sync type'), validators=[
            validators.RegexValidator(regex=re.compile("^replace|complete$"),
                                      message=_('The synchronization type only supports:replace|complete'), code=500)])

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            first = QuerySet(Knowledge).filter(id=self.data.get("knowledge_id")).first()
            if first is None:
                raise AppApiException(300, _('id does not exist'))
            if first.type != KnowledgeType.WEB:
                raise AppApiException(500, _('Synchronization is only supported for web site types'))

        def sync(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            sync_type = self.data.get('sync_type')
            knowledge_id = self.data.get('knowledge_id')
            knowledge = QuerySet(Knowledge).get(id=knowledge_id)
            self.__getattribute__(sync_type + '_sync')(knowledge)
            return True

        @staticmethod
        def get_sync_handler(knowledge):
            def handler(child_link: ChildLink, response: Fork.Response):
                if response.status == 200:
                    try:
                        document_name = child_link.tag.text if child_link.tag is not None and len(
                            child_link.tag.text.strip()) > 0 else child_link.url
                        paragraphs = get_split_model('web.md').parse(response.content)
                        print(child_link.url.strip())
                        first = QuerySet(Document).filter(
                            meta__source_url=child_link.url.strip(),
                            knowledge=knowledge
                        ).first()
                        if first is not None:
                            # 如果存在,使用文档同步
                            DocumentSerializers.Sync(data={'document_id': first.id}).sync()
                        else:
                            # 插入
                            DocumentSerializers.Create(data={'knowledge_id': knowledge.id}).save(
                                {'name': document_name, 'paragraphs': paragraphs,
                                 'meta': {'source_url': child_link.url.strip(),
                                          'selector': knowledge.meta.get('selector')},
                                 'type': Knowledge.WEB}, with_valid=True)
                    except Exception as e:
                        logging.getLogger("max_kb_error").error(f'{str(e)}:{traceback.format_exc()}')

            return handler

        def replace_sync(self, knowledge):
            """
            替换同步
            :return:
            """
            url = knowledge.meta.get('source_url')
            selector = knowledge.meta.get('selector') if 'selector' in knowledge.meta else None
            sync_replace_web_knowledge.delay(str(knowledge.id), url, selector)

        def complete_sync(self, knowledge):
            """
            完整同步  删掉当前数据集下所有的文档,再进行同步
            :return:
            """
            # 删除关联问题
            QuerySet(ProblemParagraphMapping).filter(knowledge=knowledge).delete()
            # 删除文档
            QuerySet(Document).filter(knowledge=knowledge).delete()
            # 删除段落
            QuerySet(Paragraph).filter(knowledge=knowledge).delete()
            # 删除向量
            delete_embedding_by_knowledge(self.data.get('knowledge_id'))
            # 同步
            self.replace_sync(knowledge)

    class HitTest(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        knowledge_id = serializers.UUIDField(required=True, label=_("id"))
        user_id = serializers.UUIDField(required=False, label=_('user id'))
        query_text = serializers.CharField(required=True, label=_('query text'))
        top_number = serializers.IntegerField(required=True, max_value=10000, min_value=1, label=_("top number"))
        similarity = serializers.FloatField(required=True, max_value=2, min_value=0, label=_('similarity'))
        search_mode = serializers.CharField(required=True, label=_('search mode'), validators=[
            validators.RegexValidator(regex=re.compile("^embedding|keywords|blend$"),
                                      message=_('The type only supports embedding|keywords|blend'), code=500)
        ])

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            if not QuerySet(Knowledge).filter(id=self.data.get("knowledge_id")).exists():
                raise AppApiException(300, _('id does not exist'))

        def hit_test(self):
            self.is_valid()
            vector = VectorStore.get_embedding_vector()
            exclude_document_id_list = [
                str(
                    document.id
                ) for document in QuerySet(Document).filter(knowledge_id=self.data.get('knowledge_id'), is_active=False)
            ]
            model = get_embedding_model_by_knowledge_id(self.data.get('knowledge_id'))
            # 向量库检索
            hit_list = vector.hit_test(
                self.data.get('query_text'),
                [self.data.get('knowledge_id')],
                exclude_document_id_list,
                self.data.get('top_number'),
                self.data.get('similarity'),
                SearchMode(self.data.get('search_mode')),
                model
            )
            hit_dict = reduce(lambda x, y: {**x, **y}, [{hit.get('paragraph_id'): hit} for hit in hit_list], {})
            p_list = list_paragraph([h.get('paragraph_id') for h in hit_list])
            return [
                {
                    **p,
                    'similarity': hit_dict.get(p.get('id')).get('similarity'),
                    'comprehensive_score': hit_dict.get(p.get('id')).get('comprehensive_score')
                } for p in p_list
            ]
