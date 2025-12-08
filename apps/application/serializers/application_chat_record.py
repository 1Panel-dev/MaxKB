# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_chat_record.py
    @date：2025/6/10 15:10
    @desc:
"""
from functools import reduce
from typing import Dict

import uuid_utils.compat as uuid
from django.db import transaction
from django.db.models import QuerySet
from django.db.models.aggregates import Max, Min
from django.utils.translation import gettext_lazy as _, gettext
from rest_framework import serializers
from rest_framework.utils.formatting import lazy_format

from application.models import ChatRecord, ApplicationAccessToken, Application
from application.serializers.application_chat import ChatCountSerializer
from application.serializers.common import ChatInfo
from common.auth.authentication import get_is_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants, ViewPermission, CompareConstants
from common.db.search import page_search
from common.exception.app_exception import AppApiException, AppUnauthorizedFailed
from common.utils.common import post
from knowledge.models import Paragraph, Document, Problem, ProblemParagraphMapping, Knowledge
from knowledge.serializers.common import get_embedding_model_id_by_knowledge_id, update_document_char_length
from knowledge.serializers.paragraph import ParagraphSerializers
from knowledge.task.embedding import embedding_by_paragraph, embedding_by_paragraph_list


class ChatRecordSerializerModel(serializers.ModelSerializer):
    class Meta:
        model = ChatRecord
        fields = ['id', 'chat_id', 'vote_status', 'problem_text', 'answer_text',
                  'message_tokens', 'answer_tokens', 'const', 'improve_paragraph_id_list', 'run_time', 'index',
                  'answer_text_list',
                  'create_time', 'update_time']


class ChatRecordOperateSerializer(serializers.Serializer):
    chat_id = serializers.UUIDField(required=True, label=_("Conversation ID"))
    workspace_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Workspace ID"))
    application_id = serializers.UUIDField(required=True, label=_("Application ID"))
    chat_record_id = serializers.UUIDField(required=True, label=_("Conversation record id"))

    def is_valid(self, *, debug=False, raise_exception=False):
        super().is_valid(raise_exception=True)
        workspace_id = self.data.get('workspace_id')
        query_set = QuerySet(Application).filter(id=self.data.get('application_id'))
        if workspace_id:
            query_set = query_set.filter(workspace_id=workspace_id)
        if not query_set.exists():
            raise AppApiException(500, _('Application id does not exist'))
        application_access_token = QuerySet(ApplicationAccessToken).filter(
            application_id=self.data.get('application_id')).first()
        if application_access_token is None:
            raise AppApiException(500, gettext('Application authentication information does not exist'))

    def get_chat_record(self):
        chat_record_id = self.data.get('chat_record_id')
        chat_id = self.data.get('chat_id')
        chat_info: ChatInfo = ChatInfo.get_cache(chat_id)
        if chat_info is not None:
            chat_record_list = [chat_record for chat_record in chat_info.chat_record_list if
                                str(chat_record.id) == str(chat_record_id)]
            if chat_record_list is not None and len(chat_record_list):
                return chat_record_list[-1]
        return QuerySet(ChatRecord).filter(id=chat_record_id, chat_id=chat_id).first()

    def one(self, debug):
        self.is_valid(debug=debug, raise_exception=True)
        chat_record = self.get_chat_record()
        if chat_record is None:
            raise AppApiException(500, gettext("Conversation does not exist"))
        application_access_token = QuerySet(ApplicationAccessToken).filter(
            application_id=self.data.get('application_id')).first()
        show_source = False
        show_exec = False
        if application_access_token is not None:
            show_exec = application_access_token.show_exec
            show_source = application_access_token.show_source
        return ApplicationChatRecordQuerySerializers.reset_chat_record(
            chat_record, True if debug else show_source, True if debug else show_exec)


class ApplicationChatRecordQuerySerializers(serializers.Serializer):
    workspace_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Workspace ID"))
    application_id = serializers.UUIDField(required=True, label=_("Application ID"))
    chat_id = serializers.UUIDField(required=True, label=_("Chat ID"))
    order_asc = serializers.BooleanField(required=False, allow_null=True, label=_("Is it in order"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        workspace_id = self.data.get('workspace_id')
        query_set = QuerySet(Application).filter(id=self.data.get('application_id'))
        if workspace_id:
            query_set = query_set.filter(workspace_id=workspace_id)
        if not query_set.exists():
            raise AppApiException(500, _('Application id does not exist'))

    def list(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        QuerySet(ChatRecord).filter(chat_id=self.data.get('chat_id'))
        order_by = 'create_time' if self.data.get('order_asc') is None or self.data.get(
            'order_asc') else '-create_time'
        return [ChatRecordSerializerModel(chat_record).data for chat_record in
                QuerySet(ChatRecord).filter(chat_id=self.data.get('chat_id')).order_by(order_by)]

    @staticmethod
    def get_loop_workflow_node(details):
        result = []
        for item in details.values():
            if item.get('type') == 'loop-node':
                for loop_item in item.get('loop_node_data') or []:
                    for inner_item in loop_item.values():
                        result.append(inner_item)
        return result

    @staticmethod
    def reset_chat_record(chat_record, show_source, show_exec):
        knowledge_list = []
        paragraph_list = []
        if 'search_step' in chat_record.details and chat_record.details.get('search_step').get(
                'paragraph_list') is not None:
            paragraph_list = chat_record.details.get('search_step').get(
                'paragraph_list')

        for item in [*chat_record.details.values(),
                     *ApplicationChatRecordQuerySerializers.get_loop_workflow_node(chat_record.details)]:
            if item.get('type') == 'search-knowledge-node' and item.get('show_knowledge', False):
                paragraph_list = paragraph_list + (item.get(
                    'paragraph_list') or [])

            if item.get('type') == 'reranker-node' and item.get('show_knowledge', False):
                paragraph_list = paragraph_list + [rl.get('metadata') for rl in (item.get('result_list') or []) if
                                                   'document_id' in (rl.get('metadata') or {}) and 'knowledge_id' in (
                                                           rl.get(
                                                               'metadata') or {})]
        paragraph_list = list({p.get('id'): p for p in paragraph_list}.values())
        knowledge_list = knowledge_list + [{'id': knowledge_id, **knowledge} for knowledge_id, knowledge in
                                           reduce(lambda x, y: {**x, **y},
                                                  [{row.get(
                                                      'knowledge_id'): {'knowledge_name': row.get(
                                                      "knowledge_name"),
                                                      'knowledge_type': row.get('knowledge_type')}} for
                                                      row in
                                                      paragraph_list],
                                                  {}).items()]

        if len(chat_record.improve_paragraph_id_list) > 0:
            paragraph_model_list = QuerySet(Paragraph).filter(id__in=chat_record.improve_paragraph_id_list)
            if len(paragraph_model_list) < len(chat_record.improve_paragraph_id_list):
                paragraph_model_id_list = [str(p.id) for p in paragraph_model_list]
                chat_record.improve_paragraph_id_list = list(
                    filter(lambda p_id: paragraph_model_id_list.__contains__(p_id),
                           chat_record.improve_paragraph_id_list))
                chat_record.save()
        show_source_dict = {'knowledge_list': knowledge_list,
                            'paragraph_list': paragraph_list, }
        show_exec_dict = {'execution_details': [chat_record.details[key] for key in chat_record.details if
                                                (True if show_exec else chat_record.details[key].get(
                                                    'type') == 'start-node')]}
        return {
            **ChatRecordSerializerModel(chat_record).data,
            'padding_problem_text': chat_record.details.get('problem_padding').get(
                'padding_problem_text') if 'problem_padding' in chat_record.details else None,
            **(show_source_dict if show_source else {}),
            **(show_exec_dict if show_exec else show_exec_dict)
        }

    def page(self, current_page: int, page_size: int, with_valid=True, show_source=None, show_exec=None):
        if with_valid:
            self.is_valid(raise_exception=True)
        order_by = '-create_time' if self.data.get('order_asc') is None or self.data.get(
            'order_asc') else 'create_time'
        if show_source is None:
            show_source = True
        if show_exec is None:
            show_exec = True
        page = page_search(current_page, page_size,
                           QuerySet(ChatRecord).filter(chat_id=self.data.get('chat_id')).order_by(order_by),
                           post_records_handler=lambda chat_record: self.reset_chat_record(chat_record, show_source,
                                                                                           show_exec))
        return page


class ParagraphModel(serializers.ModelSerializer):
    class Meta:
        model = Paragraph
        fields = "__all__"


class ChatRecordImproveSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Workspace ID"))

    application_id = serializers.UUIDField(required=True, label=_("Application ID"))

    chat_id = serializers.UUIDField(required=True, label=_("Conversation ID"))

    chat_record_id = serializers.UUIDField(required=True,
                                           label=_("Conversation record id"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        workspace_id = self.data.get('workspace_id')
        query_set = QuerySet(Application).filter(id=self.data.get('application_id'))
        if workspace_id:
            query_set = query_set.filter(workspace_id=workspace_id)
        if not query_set.exists():
            raise AppApiException(500, _('Application id does not exist'))

    def get(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        chat_record_id = self.data.get('chat_record_id')
        chat_id = self.data.get('chat_id')
        chat_record = QuerySet(ChatRecord).filter(id=chat_record_id, chat_id=chat_id).first()
        if chat_record is None:
            raise AppApiException(500, gettext('Conversation record does not exist'))
        if chat_record.improve_paragraph_id_list is None or len(chat_record.improve_paragraph_id_list) == 0:
            return []

        paragraph_model_list = QuerySet(Paragraph).filter(id__in=chat_record.improve_paragraph_id_list)
        if len(paragraph_model_list) < len(chat_record.improve_paragraph_id_list):
            paragraph_model_id_list = [str(p.id) for p in paragraph_model_list]
            chat_record.improve_paragraph_id_list = list(
                filter(lambda p_id: paragraph_model_id_list.__contains__(p_id),
                       chat_record.improve_paragraph_id_list))
            chat_record.save()
        return [ParagraphModel(p).data for p in paragraph_model_list]


class ApplicationChatRecordImproveInstanceSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, max_length=256, allow_null=True, allow_blank=True,
                                  label=_("Section title"))
    content = serializers.CharField(required=True, label=_("Paragraph content"))

    problem_text = serializers.CharField(required=False, max_length=256, allow_null=True, allow_blank=True,
                                         label=_("question"))


class ApplicationChatRecordAddKnowledgeSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Workspace ID"))
    application_id = serializers.UUIDField(required=True, label=_("Application ID"))
    knowledge_id = serializers.UUIDField(required=True, label=_("Knowledge base id"))
    document_id = serializers.UUIDField(required=True, label=_("Document id"))
    chat_ids = serializers.ListSerializer(child=serializers.UUIDField(), required=True,
                                          label=_("Conversation ID"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        workspace_id = self.data.get('workspace_id')
        query_set = QuerySet(Application).filter(id=self.data.get('application_id'))
        if workspace_id:
            query_set = query_set.filter(workspace_id=workspace_id)
        if not query_set.exists():
            raise AppApiException(500, _('Application id does not exist'))
        if not Document.objects.filter(id=self.data['document_id'], knowledge_id=self.data['knowledge_id']).exists():
            raise AppApiException(500, gettext("The document id is incorrect"))

    @staticmethod
    def post_embedding_paragraph(paragraph_ids, knowledge_id):
        model_id = get_embedding_model_id_by_knowledge_id(knowledge_id)
        embedding_by_paragraph_list(paragraph_ids, model_id)

    @post(post_function=post_embedding_paragraph)
    @transaction.atomic
    def post_improve(self, instance: Dict, request=None, scope='WORKSPACE', with_valid=True):
        if with_valid:
            ApplicationChatRecordAddKnowledgeSerializer(data=instance).is_valid(raise_exception=True)
        self.is_valid(raise_exception=True)
        if scope == 'WORKSPACE':
            is_permission = get_is_permissions(request=request, workspace_id=self.data.get('workspace_id'),
                                               knowledge_id=self.data.get("knowledge_id"))(
                PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_knowledge_permission(),
                PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_permission_workspace_manage_role(),
                RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
                ViewPermission([RoleConstants.USER.get_workspace_role()],
                               [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                               CompareConstants.AND),
            )
        else:
            is_permission = get_is_permissions(request=request, workspace_id=self.data.get('workspace_id'),
                                               knowledge_id=self.data.get("knowledge_id"))(
                PermissionConstants.RESOURCE_KNOWLEDGE_DOCUMENT_EDIT, RoleConstants.ADMIN
            )
        if not is_permission:
            raise AppUnauthorizedFailed(403, gettext('No permission to access'))

        chat_ids = instance['chat_ids']
        document_id = instance['document_id']
        knowledge_id = instance['knowledge_id']

        # 获取所有聊天记录
        chat_record_list = list(ChatRecord.objects.filter(chat_id__in=chat_ids))
        if len(chat_record_list) < len(chat_ids):
            raise AppApiException(500, gettext("Conversation records that do not exist"))

        # 批量创建段落和问题映射
        paragraphs = []
        paragraph_ids = []
        problem_paragraph_mappings = []
        for chat_record in chat_record_list:
            paragraph = Paragraph(
                id=uuid.uuid7(),
                document_id=document_id,
                content=chat_record.answer_text,
                knowledge_id=knowledge_id,
                title=chat_record.problem_text
            )
            problem, _ = Problem.objects.get_or_create(content=chat_record.problem_text, knowledge_id=knowledge_id)
            problem_paragraph_mapping = ProblemParagraphMapping(
                id=uuid.uuid7(),
                knowledge_id=knowledge_id,
                document_id=document_id,
                problem_id=problem.id,
                paragraph_id=paragraph.id
            )
            paragraphs.append(paragraph)
            paragraph_ids.append(paragraph.id)
            problem_paragraph_mappings.append(problem_paragraph_mapping)
            chat_record.improve_paragraph_id_list.append(paragraph.id)

        # 处理段落位置
        self.prepend_paragraphs(document_id, paragraphs)

        # 批量创建新段落和问题映射
        Paragraph.objects.bulk_create(paragraphs)
        ProblemParagraphMapping.objects.bulk_create(problem_paragraph_mappings)

        # 批量保存聊天记录
        ChatRecord.objects.bulk_update(chat_record_list, ['improve_paragraph_id_list'])
        update_document_char_length(document_id)
        for chat_id in chat_ids:
            ChatCountSerializer(data={'chat_id': chat_id}).update_chat()

        return paragraph_ids, knowledge_id

    @staticmethod
    def prepend_paragraphs(document_id, paragraphs):
        # 获取所有现有段落
        existing_paragraphs = list(Paragraph.objects.filter(
            document_id=document_id
        ).order_by('position'))

        # 计算新段落数量
        new_count = len(paragraphs)

        # 如果已有段落，需要重新调整所有段落的位置
        if existing_paragraphs:
            # 为现有段落重新分配位置，从新段落数量+1开始
            for i, existing_paragraph in enumerate(existing_paragraphs):
                existing_paragraph.position = new_count + i + 1

            # 批量更新现有段落位置
            if existing_paragraphs:
                Paragraph.objects.bulk_update(existing_paragraphs, ['position'])

        # 为新段落分配位置，从1开始
        for i, paragraph in enumerate(paragraphs):
            paragraph.position = i + 1


class ApplicationChatRecordImproveSerializer(serializers.Serializer):
    chat_id = serializers.UUIDField(required=True, label=_("Conversation ID"))

    chat_record_id = serializers.UUIDField(required=True,
                                           label=_("Conversation record id"))

    knowledge_id = serializers.UUIDField(required=True, label=_("Knowledge base id"))

    document_id = serializers.UUIDField(required=True, label=_("Document id"))
    application_id = serializers.UUIDField(required=True, label=_("Application id"))

    workspace_id = serializers.CharField(required=True, label=_("Workspace ID"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        workspace_id = self.data.get('workspace_id')
        query_set = QuerySet(Application).filter(id=self.data.get('application_id'))
        if workspace_id:
            query_set = query_set.filter(workspace_id=workspace_id)
        if not query_set.exists():
            raise AppApiException(500, _('Application id does not exist'))

        query_set = QuerySet(Knowledge).filter(id=self.data.get('knowledge_id'))
        if workspace_id:
            query_set = query_set.filter(workspace_id=workspace_id)
        if not query_set.exists():
            raise AppApiException(500, _('Knowledge id does not exist'))

        if not QuerySet(Document).filter(id=self.data.get('document_id'),
                                         knowledge_id=self.data.get('knowledge_id')).exists():
            raise AppApiException(500, gettext("The document id is incorrect"))

    @staticmethod
    def post_embedding_paragraph(chat_record, paragraph_id, knowledge_id):
        model_id = get_embedding_model_id_by_knowledge_id(knowledge_id)
        # 发送向量化事件
        embedding_by_paragraph(paragraph_id, model_id)
        return chat_record

    @post(post_function=post_embedding_paragraph)
    @transaction.atomic
    def improve(self, instance: Dict, request=None, scope='WORKSPACE', with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        if scope == 'WORKSPACE':
            is_permission = get_is_permissions(request, workspace_id=self.data.get('workspace_id'),
                                               knowledge_id=self.data.get("knowledge_id"))(
                PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_knowledge_permission(),
                PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_permission_workspace_manage_role(),
                RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
                ViewPermission([RoleConstants.USER.get_workspace_role()],
                               [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                               CompareConstants.AND),
            )
        else:
            is_permission = get_is_permissions(request, workspace_id=self.data.get('workspace_id'),
                                               knowledge_id=self.data.get("knowledge_id"))(
                PermissionConstants.RESOURCE_KNOWLEDGE_DOCUMENT_EDIT, RoleConstants.ADMIN
            )
        if not is_permission:
            raise AppUnauthorizedFailed(403, gettext('No permission to access'))
        ApplicationChatRecordImproveInstanceSerializer(data=instance).is_valid(raise_exception=True)
        chat_record_id = self.data.get('chat_record_id')
        chat_id = self.data.get('chat_id')
        chat_record = QuerySet(ChatRecord).filter(id=chat_record_id, chat_id=chat_id).first()
        if chat_record is None:
            raise AppApiException(500, gettext('Conversation record does not exist'))

        document_id = self.data.get("document_id")
        knowledge_id = self.data.get("knowledge_id")
        max_position = Paragraph.objects.filter(document_id=document_id).aggregate(
            max_position=Max('position')
        )['max_position'] or 0
        paragraph = Paragraph(
            id=uuid.uuid7(),
            document_id=document_id,
            content=instance.get("content"),
            knowledge_id=knowledge_id,
            title=instance.get("title") if 'title' in instance else '',
            position=max_position + 1
        )
        problem_text = instance.get('problem_text') if instance.get(
            'problem_text') is not None else chat_record.problem_text
        problem, _ = QuerySet(Problem).get_or_create(content=problem_text, knowledge_id=knowledge_id)
        problem_paragraph_mapping = ProblemParagraphMapping(id=uuid.uuid7(), knowledge_id=knowledge_id,
                                                            document_id=document_id,
                                                            problem_id=problem.id,
                                                            paragraph_id=paragraph.id)
        # 插入段落
        paragraph.save()
        # 插入关联问题
        problem_paragraph_mapping.save()
        chat_record.improve_paragraph_id_list.append(paragraph.id)
        update_document_char_length(document_id)
        # 添加标注
        chat_record.save()
        ChatCountSerializer(data={'chat_id': chat_id}).update_chat()
        return ChatRecordSerializerModel(chat_record).data, paragraph.id, knowledge_id

    class Operate(serializers.Serializer):
        chat_id = serializers.UUIDField(required=True, label=_("Conversation ID"))

        chat_record_id = serializers.UUIDField(required=True,
                                               label=_("Conversation record id"))

        knowledge_id = serializers.UUIDField(required=True, label=_("Knowledge base id"))

        document_id = serializers.UUIDField(required=True, label=_("Document id"))

        paragraph_id = serializers.UUIDField(required=True, label=_("Paragraph id"))

        workspace_id = serializers.CharField(required=True, label=_("Workspace ID"))

        def delete(self, request=None, scope='WORKSPACE', with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                if scope == 'WORKSPACE':
                    is_permission = get_is_permissions(request=request, workspace_id=self.data.get('workspace_id'),
                                                       knowledge_id=self.data.get("knowledge_id"))(
                        PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_knowledge_permission(),
                        PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT.get_workspace_permission_workspace_manage_role(),
                        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
                        ViewPermission([RoleConstants.USER.get_workspace_role()],
                                       [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                                       CompareConstants.AND),
                    )
                else:
                    is_permission = get_is_permissions(request=request, workspace_id=self.data.get('workspace_id'),
                                                       knowledge_id=self.data.get("knowledge_id"))(
                        PermissionConstants.RESOURCE_KNOWLEDGE_DOCUMENT_EDIT, RoleConstants.ADMIN
                    )

                if not is_permission:
                    raise AppUnauthorizedFailed(403, gettext('No permission to access'))

            workspace_id = self.data.get('workspace_id')
            chat_record_id = self.data.get('chat_record_id')
            chat_id = self.data.get('chat_id')
            knowledge_id = self.data.get('knowledge_id')
            document_id = self.data.get('document_id')
            paragraph_id = self.data.get('paragraph_id')
            chat_record = QuerySet(ChatRecord).filter(id=chat_record_id, chat_id=chat_id).first()
            if chat_record is None:
                raise AppApiException(500, gettext('Conversation record does not exist'))
            if not chat_record.improve_paragraph_id_list.__contains__(uuid.UUID(paragraph_id)):
                message = lazy_format(
                    gettext(
                        'The paragraph id is wrong. The current conversation record does not exist. [{paragraph_id}] paragraph id'),
                    paragraph_id=paragraph_id)
                raise AppApiException(500, message.__str__())
            chat_record.improve_paragraph_id_list = [row for row in chat_record.improve_paragraph_id_list if
                                                     str(row) != paragraph_id]
            chat_record.save()
            o = ParagraphSerializers.Operate(
                data={"workspace_id": workspace_id, "knowledge_id": knowledge_id, 'document_id': document_id,
                      "paragraph_id": paragraph_id})
            o.is_valid(raise_exception=True)
            o.delete()
            return True
