# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： chat_serializers.py
    @date：2023/11/14 9:59
    @desc:
"""
import datetime
import json
import os
import uuid
from functools import reduce
from typing import Dict, List

from django.core.cache import cache
from django.db import transaction
from django.db.models import QuerySet
from rest_framework import serializers

from application.models import Chat, Application, ApplicationDatasetMapping, VoteChoices, ChatRecord
from application.serializers.application_serializers import ModelDatasetAssociation, DatasetSettingSerializer, \
    ModelSettingSerializer
from application.serializers.chat_message_serializers import ChatInfo
from common.db.search import native_search, native_page_search, page_search
from common.event import ListenerManagement
from common.exception.app_exception import AppApiException
from common.util.file_util import get_file_content
from common.util.lock import try_lock, un_lock
from common.util.rsa_util import decrypt
from common.util.split_model import flat_map
from dataset.models import Document, Problem, Paragraph
from setting.models import Model
from setting.models_provider.constants.model_provider_constants import ModelProvideConstants
from smartdoc.conf import PROJECT_DIR

chat_cache = cache


class ChatSerializers(serializers.Serializer):
    class Operate(serializers.Serializer):
        chat_id = serializers.UUIDField(required=True)
        application_id = serializers.UUIDField(required=True)

        def delete(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            QuerySet(Chat).filter(id=self.data.get('chat_id'), application_id=self.data.get('application_id')).delete()
            return True

    class Query(serializers.Serializer):
        abstract = serializers.CharField(required=False)
        history_day = serializers.IntegerField(required=True)
        user_id = serializers.UUIDField(required=True)
        application_id = serializers.UUIDField(required=True)

        def get_end_time(self):
            history_day = self.data.get('history_day')
            return datetime.datetime.now() - datetime.timedelta(days=history_day)

        def get_query_set(self):
            end_time = self.get_end_time()
            query_dict = {'application_id': self.data.get("application_id"), 'create_time__gte': end_time}
            if 'abstract' in self.data and self.data.get('abstract') is not None:
                query_dict['abstract'] = self.data.get('abstract')
            return QuerySet(Chat).filter(**query_dict).order_by("-create_time")

        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return native_search(self.get_query_set(), select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "application", 'sql', 'list_application_chat.sql')),
                                 with_table_name=True)

        def page(self, current_page: int, page_size: int, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return native_page_search(current_page, page_size, self.get_query_set(), select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "application", 'sql', 'list_application_chat.sql')),
                                      with_table_name=True)

    class OpenChat(serializers.Serializer):
        user_id = serializers.UUIDField(required=True)

        application_id = serializers.UUIDField(required=True)

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            user_id = self.data.get('user_id')
            application_id = self.data.get('application_id')
            if not QuerySet(Application).filter(id=application_id, user_id=user_id).exists():
                raise AppApiException(500, '应用不存在')

        def open(self):
            self.is_valid(raise_exception=True)
            application_id = self.data.get('application_id')
            application = QuerySet(Application).get(id=application_id)
            model = QuerySet(Model).filter(id=application.model_id).first()
            dataset_id_list = [str(row.dataset_id) for row in
                               QuerySet(ApplicationDatasetMapping).filter(
                                   application_id=application_id)]
            chat_model = None
            if model is not None:
                chat_model = ModelProvideConstants[model.provider].value.get_model(model.model_type, model.model_name,
                                                                                   json.loads(
                                                                                       decrypt(model.credential)),
                                                                                   streaming=True)

            chat_id = str(uuid.uuid1())
            chat_cache.set(chat_id,
                           ChatInfo(chat_id, chat_model, dataset_id_list,
                                    [str(document.id) for document in
                                     QuerySet(Document).filter(
                                         dataset_id__in=dataset_id_list,
                                         is_active=False)],
                                    application), timeout=60 * 30)
            return chat_id

    class OpenTempChat(serializers.Serializer):
        user_id = serializers.UUIDField(required=True)

        model_id = serializers.UUIDField(required=True)

        multiple_rounds_dialogue = serializers.BooleanField(required=True)

        dataset_id_list = serializers.ListSerializer(required=False, child=serializers.UUIDField(required=True))
        # 数据集相关设置
        dataset_setting = DatasetSettingSerializer(required=True)
        # 模型相关设置
        model_setting = ModelSettingSerializer(required=True)
        # 问题补全
        problem_optimization = serializers.BooleanField(required=True)

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            ModelDatasetAssociation(
                data={'user_id': self.data.get('user_id'), 'model_id': self.data.get('model_id'),
                      'dataset_id_list': self.data.get('dataset_id_list')}).is_valid()

        def open(self):
            self.is_valid(raise_exception=True)
            chat_id = str(uuid.uuid1())
            model = QuerySet(Model).filter(user_id=self.data.get('user_id'), id=self.data.get('model_id')).first()
            if model is None:
                raise AppApiException(500, "模型不存在")
            dataset_id_list = self.data.get('dataset_id_list')
            chat_model = ModelProvideConstants[model.provider].value.get_model(model.model_type, model.model_name,
                                                                               json.loads(
                                                                                   decrypt(model.credential)),
                                                                               streaming=True)
            application = Application(id=None, dialogue_number=3, model=model,
                                      dataset_setting=self.data.get('dataset_setting'),
                                      model_setting=self.data.get('model_setting'),
                                      problem_optimization=self.data.get('problem_optimization'))
            chat_cache.set(chat_id,
                           ChatInfo(chat_id, chat_model, dataset_id_list,
                                    [str(document.id) for document in
                                     QuerySet(Document).filter(
                                         dataset_id__in=dataset_id_list,
                                         is_active=False)],
                                    application), timeout=60 * 30)
            return chat_id


class ChatRecordSerializerModel(serializers.ModelSerializer):
    class Meta:
        model = ChatRecord
        fields = ['id', 'chat_id', 'vote_status', 'problem_text', 'answer_text',
                  'message_tokens', 'answer_tokens', 'const', 'improve_paragraph_id_list', 'run_time', 'index',
                  'create_time', 'update_time']


class ChatRecordSerializer(serializers.Serializer):
    class Operate(serializers.Serializer):
        chat_id = serializers.UUIDField(required=True)

        chat_record_id = serializers.UUIDField(required=True)

        def get_chat_record(self):
            chat_record_id = self.data.get('chat_record_id')
            chat_id = self.data.get('chat_id')
            chat_info: ChatInfo = chat_cache.get(chat_id)
            chat_record_list = [chat_record for chat_record in chat_info.chat_record_list if
                                chat_record.id == uuid.UUID(chat_record_id)]
            if chat_record_list is not None and len(chat_record_list):
                return chat_record_list[-1]
            return QuerySet(ChatRecord).filter(id=chat_record_id, chat_id=chat_id).first()

        def one(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            chat_record = self.get_chat_record()
            if chat_record is None:
                raise AppApiException(500, "对话不存在")
            dataset_list = []
            paragraph_list = []
            if len(chat_record.paragraph_id_list) > 0:
                paragraph_list = native_search(QuerySet(Paragraph).filter(id__in=chat_record.paragraph_id_list),
                                               get_file_content(
                                                   os.path.join(PROJECT_DIR, "apps", "application", 'sql',
                                                                'list_dataset_paragraph_by_paragraph_id.sql')),
                                               with_table_name=True)
                dataset_list = [{'id': dataset_id, 'name': name} for dataset_id, name in reduce(lambda x, y: {**x, **y},
                                                                                                [{row.get(
                                                                                                    'dataset_id'): row.get(
                                                                                                    "dataset_name")} for
                                                                                                    row in
                                                                                                    paragraph_list],
                                                                                                {}).items()]

            return {
                **ChatRecordSerializerModel(chat_record).data,
                'padding_problem_text':  chat_record.details.get('problem_padding').get(
                    'padding_problem_text') if 'problem_padding' in chat_record.details else None,
                'dataset_list': dataset_list,
                'paragraph_list': paragraph_list}

    class Query(serializers.Serializer):
        application_id = serializers.UUIDField(required=True)
        chat_id = serializers.UUIDField(required=True)

        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            QuerySet(ChatRecord).filter(chat_id=self.data.get('chat_id'))
            return [ChatRecordSerializerModel(chat_record).data for chat_record in
                    QuerySet(ChatRecord).filter(chat_id=self.data.get('chat_id'))]

        def reset_chat_record_list(self, chat_record_list: List[ChatRecord]):
            paragraph_id_list = flat_map([chat_record.paragraph_id_list for chat_record in chat_record_list])
            # 去重
            paragraph_id_list = list(set(paragraph_id_list))
            paragraph_list = self.search_paragraph(paragraph_id_list)
            return [self.reset_chat_record(chat_record, paragraph_list) for chat_record in chat_record_list]

        @staticmethod
        def search_paragraph(paragraph_id_list: List[str]):
            paragraph_list = []
            if len(paragraph_id_list) > 0:
                paragraph_list = native_search(QuerySet(Paragraph).filter(id__in=paragraph_id_list),
                                               get_file_content(
                                                   os.path.join(PROJECT_DIR, "apps", "application", 'sql',
                                                                'list_dataset_paragraph_by_paragraph_id.sql')),
                                               with_table_name=True)
            return paragraph_list

        @staticmethod
        def reset_chat_record(chat_record, all_paragraph_list):
            paragraph_list = list(
                filter(
                    lambda paragraph: chat_record.paragraph_id_list.__contains__(uuid.UUID(str(paragraph.get('id')))),
                    all_paragraph_list))
            dataset_list = [{'id': dataset_id, 'name': name} for dataset_id, name in reduce(lambda x, y: {**x, **y},
                                                                                            [{row.get(
                                                                                                'dataset_id'): row.get(
                                                                                                "dataset_name")} for
                                                                                                row in
                                                                                                paragraph_list],
                                                                                            {}).items()]
            return {
                **ChatRecordSerializerModel(chat_record).data,
                'padding_problem_text': chat_record.details.get('problem_padding').get(
                    'padding_problem_text') if 'problem_padding' in chat_record.details else None,
                'dataset_list': dataset_list,
                'paragraph_list': paragraph_list
            }

        def page(self, current_page: int, page_size: int, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            page = page_search(current_page, page_size,
                               QuerySet(ChatRecord).filter(chat_id=self.data.get('chat_id')).order_by("index"),
                               post_records_handler=lambda chat_record: chat_record)
            records = page.get('records')
            page['records'] = self.reset_chat_record_list(records)
            return page

    class Vote(serializers.Serializer):
        chat_id = serializers.UUIDField(required=True)

        chat_record_id = serializers.UUIDField(required=True)

        vote_status = serializers.ChoiceField(choices=VoteChoices.choices)

        @transaction.atomic
        def vote(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            if not try_lock(self.data.get('chat_record_id')):
                raise AppApiException(500, "正在对当前会话纪要进行投票中,请勿重复发送请求")
            try:
                chat_record_details_model = QuerySet(ChatRecord).get(id=self.data.get('chat_record_id'),
                                                                     chat_id=self.data.get('chat_id'))
                if chat_record_details_model is None:
                    raise AppApiException(500, "不存在的对话 chat_record_id")
                vote_status = self.data.get("vote_status")
                if chat_record_details_model.vote_status == VoteChoices.UN_VOTE:
                    if vote_status == VoteChoices.STAR:
                        # 点赞
                        chat_record_details_model.vote_status = VoteChoices.STAR

                    if vote_status == VoteChoices.TRAMPLE:
                        # 点踩
                        chat_record_details_model.vote_status = VoteChoices.TRAMPLE
                    chat_record_details_model.save()
                else:
                    if vote_status == VoteChoices.UN_VOTE:
                        # 取消点赞
                        chat_record_details_model.vote_status = VoteChoices.UN_VOTE
                        chat_record_details_model.save()
                    else:
                        raise AppApiException(500, "已经投票过,请先取消后再进行投票")
            finally:
                un_lock(self.data.get('chat_record_id'))
            return True

    class ImproveSerializer(serializers.Serializer):
        title = serializers.CharField(required=False)
        content = serializers.CharField(required=True)

    class ParagraphModel(serializers.ModelSerializer):
        class Meta:
            model = Paragraph
            fields = "__all__"

    class ChatRecordImprove(serializers.Serializer):
        chat_id = serializers.UUIDField(required=True)

        chat_record_id = serializers.UUIDField(required=True)

        def get(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            chat_record_id = self.data.get('chat_record_id')
            chat_id = self.data.get('chat_id')
            chat_record = QuerySet(ChatRecord).filter(id=chat_record_id, chat_id=chat_id).first()
            if chat_record is None:
                raise AppApiException(500, '不存在的对话记录')
            if chat_record.improve_paragraph_id_list is None or len(chat_record.improve_paragraph_id_list) == 0:
                return []

            paragraph_model_list = QuerySet(Paragraph).filter(id__in=chat_record.improve_paragraph_id_list)
            if len(paragraph_model_list) < len(chat_record.improve_paragraph_id_list):
                paragraph_model_id_list = [str(p.id) for p in paragraph_model_list]
                chat_record.improve_paragraph_id_list = list(
                    filter(lambda p_id: paragraph_model_id_list.__contains__(p_id),
                           chat_record.improve_paragraph_id_list))
                chat_record.save()
            return [ChatRecordSerializer.ParagraphModel(p).data for p in paragraph_model_list]

    class Improve(serializers.Serializer):
        chat_id = serializers.UUIDField(required=True)

        chat_record_id = serializers.UUIDField(required=True)

        dataset_id = serializers.UUIDField(required=True)

        document_id = serializers.UUIDField(required=True)

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if not QuerySet(Document).filter(id=self.data.get('document_id'),
                                             dataset_id=self.data.get('dataset_id')).exists():
                raise AppApiException(500, "文档id不正确")

        @transaction.atomic
        def improve(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            ChatRecordSerializer.ImproveSerializer(data=instance).is_valid(raise_exception=True)
            chat_record_id = self.data.get('chat_record_id')
            chat_id = self.data.get('chat_id')
            chat_record = QuerySet(ChatRecord).filter(id=chat_record_id, chat_id=chat_id).first()
            if chat_record is None:
                raise AppApiException(500, '不存在的对话记录')

            document_id = self.data.get("document_id")
            dataset_id = self.data.get("dataset_id")
            paragraph = Paragraph(id=uuid.uuid1(),
                                  document_id=document_id,
                                  content=instance.get("content"),
                                  dataset_id=dataset_id,
                                  title=instance.get("title") if 'title' in instance else '')

            problem = Problem(id=uuid.uuid1(), content=chat_record.problem_text, paragraph_id=paragraph.id,
                              document_id=document_id, dataset_id=dataset_id)
            # 插入问题
            problem.save()
            # 插入段落
            paragraph.save()
            chat_record.improve_paragraph_id_list.append(paragraph.id)
            # 添加标注
            chat_record.save()
            ListenerManagement.embedding_by_paragraph_signal.send(paragraph.id)
            return ChatRecordSerializerModel(chat_record).data
