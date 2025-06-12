# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_chat_record.py
    @date：2025/6/10 15:10
    @desc:
"""
import uuid
from functools import reduce
from typing import Dict

from django.db import transaction
from django.db.models import QuerySet
from rest_framework import serializers
from rest_framework.utils.formatting import lazy_format

from application.models import ChatRecord, ApplicationAccessToken
from application.serializers.common import ChatInfo
from common.db.search import page_search
from common.exception.app_exception import AppApiException
from common.utils.common import post
from knowledge.models import Paragraph, Document, Problem, ProblemParagraphMapping

from django.utils.translation import gettext_lazy as _, gettext

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
    workspace_id = serializers.CharField(required=False, label=_("Workspace ID"))
    application_id = serializers.UUIDField(required=True, label=_("Application ID"))
    chat_record_id = serializers.UUIDField(required=True, label=_("Conversation record id"))

    def is_valid(self, *, debug=False, raise_exception=False):
        super().is_valid(raise_exception=True)
        application_access_token = QuerySet(ApplicationAccessToken).filter(
            application_id=self.data.get('application_id')).first()
        if application_access_token is None:
            raise AppApiException(500, gettext('Application authentication information does not exist'))
        if not application_access_token.show_source and not debug:
            raise AppApiException(500, gettext('Displaying knowledge sources is not enabled'))

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
        return ApplicationChatRecordQuerySerializers.reset_chat_record(chat_record)


class ApplicationChatRecordQuerySerializers(serializers.Serializer):
    application_id = serializers.UUIDField(required=True, label=_("Application ID"))
    chat_id = serializers.UUIDField(required=True, label=_("Chat ID"))
    order_asc = serializers.BooleanField(required=False, allow_null=True, label=_("Is it in order"))

    def list(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        QuerySet(ChatRecord).filter(chat_id=self.data.get('chat_id'))
        order_by = 'create_time' if self.data.get('order_asc') is None or self.data.get(
            'order_asc') else '-create_time'
        return [ChatRecordSerializerModel(chat_record).data for chat_record in
                QuerySet(ChatRecord).filter(chat_id=self.data.get('chat_id')).order_by(order_by)]

    @staticmethod
    def reset_chat_record(chat_record):
        knowledge_list = []
        paragraph_list = []

        if 'search_step' in chat_record.details and chat_record.details.get('search_step').get(
                'paragraph_list') is not None:
            paragraph_list = chat_record.details.get('search_step').get(
                'paragraph_list')
            knowledge_list = [{'id': dataset_id, 'name': name} for dataset_id, name in reduce(lambda x, y: {**x, **y},
                                                                                              [{row.get(
                                                                                                  'knowledge_id'): row.get(
                                                                                                  "knowledge_name")} for
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

        return {
            **ChatRecordSerializerModel(chat_record).data,
            'padding_problem_text': chat_record.details.get('problem_padding').get(
                'padding_problem_text') if 'problem_padding' in chat_record.details else None,
            'knowledge_list': knowledge_list,
            'paragraph_list': paragraph_list,
            'execution_details': [chat_record.details[key] for key in chat_record.details]
        }

    def page(self, current_page: int, page_size: int, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        order_by = '-create_time' if self.data.get('order_asc') is None or self.data.get(
            'order_asc') else 'create_time'
        page = page_search(current_page, page_size,
                           QuerySet(ChatRecord).filter(chat_id=self.data.get('chat_id')).order_by(order_by),
                           post_records_handler=lambda chat_record: self.reset_chat_record(chat_record))
        return page


class ParagraphModel(serializers.ModelSerializer):
    class Meta:
        model = Paragraph
        fields = "__all__"


class ChatRecordImproveSerializer(serializers.Serializer):
    chat_id = serializers.UUIDField(required=True, label=_("Conversation ID"))

    chat_record_id = serializers.UUIDField(required=True,
                                           label=_("Conversation record id"))

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
    knowledge_id = serializers.UUIDField(required=True, label=_("Knowledge base id"))
    document_id = serializers.UUIDField(required=True, label=_("Document id"))
    chat_ids = serializers.ListSerializer(child=serializers.UUIDField(), required=True,
                                          label=_("Conversation ID"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        if not Document.objects.filter(id=self.data['document_id'], knowledge_id=self.data['knowledge_id']).exists():
            raise AppApiException(500, gettext("The document id is incorrect"))

    @staticmethod
    def post_embedding_paragraph(paragraph_ids, knowledge_id):
        model_id = get_embedding_model_id_by_knowledge_id(knowledge_id)
        embedding_by_paragraph_list(paragraph_ids, model_id)

    @post(post_function=post_embedding_paragraph)
    @transaction.atomic
    def post_improve(self, instance: Dict):
        ApplicationChatRecordAddKnowledgeSerializer(data=instance).is_valid(raise_exception=True)

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
                id=uuid.uuid1(),
                document_id=document_id,
                content=chat_record.answer_text,
                knowledge_id=knowledge_id,
                title=chat_record.problem_text
            )
            problem, _ = Problem.objects.get_or_create(content=chat_record.problem_text, knowledge_id=knowledge_id)
            problem_paragraph_mapping = ProblemParagraphMapping(
                id=uuid.uuid1(),
                knowledge_id=knowledge_id,
                document_id=document_id,
                problem_id=problem.id,
                paragraph_id=paragraph.id
            )
            paragraphs.append(paragraph)
            paragraph_ids.append(paragraph.id)
            problem_paragraph_mappings.append(problem_paragraph_mapping)
            chat_record.improve_paragraph_id_list.append(paragraph.id)

        # 批量保存段落和问题映射
        Paragraph.objects.bulk_create(paragraphs)
        ProblemParagraphMapping.objects.bulk_create(problem_paragraph_mappings)

        # 批量保存聊天记录
        ChatRecord.objects.bulk_update(chat_record_list, ['improve_paragraph_id_list'])
        update_document_char_length(document_id)

        return paragraph_ids, knowledge_id


class ApplicationChatRecordImproveSerializer(serializers.Serializer):
    chat_id = serializers.UUIDField(required=True, label=_("Conversation ID"))

    chat_record_id = serializers.UUIDField(required=True,
                                           label=_("Conversation record id"))

    knowledge_id = serializers.UUIDField(required=True, label=_("Knowledge base id"))

    document_id = serializers.UUIDField(required=True, label=_("Document id"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
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
    def improve(self, instance: Dict, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        ApplicationChatRecordImproveInstanceSerializer(data=instance).is_valid(raise_exception=True)
        chat_record_id = self.data.get('chat_record_id')
        chat_id = self.data.get('chat_id')
        chat_record = QuerySet(ChatRecord).filter(id=chat_record_id, chat_id=chat_id).first()
        if chat_record is None:
            raise AppApiException(500, gettext('Conversation record does not exist'))

        document_id = self.data.get("document_id")
        knowledge_id = self.data.get("knowledge_id")
        paragraph = Paragraph(id=uuid.uuid1(),
                              document_id=document_id,
                              content=instance.get("content"),
                              knowledge_id=knowledge_id,
                              title=instance.get("title") if 'title' in instance else '')
        problem_text = instance.get('problem_text') if instance.get(
            'problem_text') is not None else chat_record.problem_text
        problem, _ = QuerySet(Problem).get_or_create(content=problem_text, knowledge_id=knowledge_id)
        problem_paragraph_mapping = ProblemParagraphMapping(id=uuid.uuid1(), knowledge_id=knowledge_id,
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
        return ChatRecordSerializerModel(chat_record).data, paragraph.id, knowledge_id

    class Operate(serializers.Serializer):
        chat_id = serializers.UUIDField(required=True, label=_("Conversation ID"))

        chat_record_id = serializers.UUIDField(required=True,
                                               label=_("Conversation record id"))

        knowledge_id = serializers.UUIDField(required=True, label=_("Knowledge base id"))

        document_id = serializers.UUIDField(required=True, label=_("Document id"))

        paragraph_id = serializers.UUIDField(required=True, label=_("Paragraph id"))

        workspace_id = serializers.CharField(required=True, label=_("Workspace ID"))

        def delete(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
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
