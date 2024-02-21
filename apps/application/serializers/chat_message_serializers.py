# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： chat_message_serializers.py
    @date：2023/11/14 13:51
    @desc:
"""
import json
from typing import List
from uuid import UUID

from django.core.cache import cache
from django.db.models import QuerySet
from langchain.chat_models.base import BaseChatModel
from rest_framework import serializers

from application.chat_pipeline.pipeline_manage import PiplineManage
from application.chat_pipeline.step.chat_step.i_chat_step import PostResponseHandler
from application.chat_pipeline.step.chat_step.impl.base_chat_step import BaseChatStep
from application.chat_pipeline.step.generate_human_message_step.impl.base_generate_human_message_step import \
    BaseGenerateHumanMessageStep
from application.chat_pipeline.step.reset_problem_step.impl.base_reset_problem_step import BaseResetProblemStep
from application.chat_pipeline.step.search_dataset_step.impl.base_search_dataset_step import BaseSearchDatasetStep
from application.models import ChatRecord, Chat, Application, ApplicationDatasetMapping
from common.exception.app_exception import AppApiException
from common.util.rsa_util import decrypt
from common.util.split_model import flat_map
from dataset.models import Paragraph, Document
from setting.models import Model
from setting.models_provider.constants.model_provider_constants import ModelProvideConstants

chat_cache = cache


class ChatInfo:
    def __init__(self,
                 chat_id: str,
                 chat_model: BaseChatModel,
                 dataset_id_list: List[str],
                 exclude_document_id_list: list[str],
                 application: Application):
        """
        :param chat_id:                     对话id
        :param chat_model:                  对话模型
        :param dataset_id_list:             数据集列表
        :param exclude_document_id_list:    排除的文档
        :param application:                 应用信息
        """
        self.chat_id = chat_id
        self.application = application
        self.chat_model = chat_model
        self.dataset_id_list = dataset_id_list
        self.exclude_document_id_list = exclude_document_id_list
        self.chat_record_list: List[ChatRecord] = []

    def to_base_pipeline_manage_params(self):
        dataset_setting = self.application.dataset_setting
        model_setting = self.application.model_setting
        return {
            'dataset_id_list': self.dataset_id_list,
            'exclude_document_id_list': self.exclude_document_id_list,
            'exclude_paragraph_id_list': [],
            'top_n': dataset_setting.get('top_n') if 'top_n' in dataset_setting else 3,
            'similarity': dataset_setting.get('similarity') if 'similarity' in dataset_setting else 0.6,
            'max_paragraph_char_number': dataset_setting.get(
                'max_paragraph_char_number') if 'max_paragraph_char_number' in dataset_setting else 5000,
            'history_chat_record': self.chat_record_list,
            'chat_id': self.chat_id,
            'dialogue_number': self.application.dialogue_number,
            'prompt': model_setting.get(
                'prompt') if 'prompt' in model_setting else Application.get_default_model_prompt(),
            'chat_model': self.chat_model,
            'model_id': self.application.model.id if self.application.model is not None else None,
            'problem_optimization': self.application.problem_optimization,
            'stream': True

        }

    def to_pipeline_manage_params(self, problem_text: str, post_response_handler: PostResponseHandler,
                                  exclude_paragraph_id_list, stream=True):
        params = self.to_base_pipeline_manage_params()
        return {**params, 'problem_text': problem_text, 'post_response_handler': post_response_handler,
                'exclude_paragraph_id_list': exclude_paragraph_id_list, 'stream': stream}

    def append_chat_record(self, chat_record: ChatRecord):
        # 存入缓存中
        self.chat_record_list.append(chat_record)
        if self.application.id is not None:
            # 插入数据库
            if not QuerySet(Chat).filter(id=self.chat_id).exists():
                Chat(id=self.chat_id, application_id=self.application.id, abstract=chat_record.problem_text).save()
            # 插入会话记录
            chat_record.save()


def get_post_handler(chat_info: ChatInfo):
    class PostHandler(PostResponseHandler):

        def handler(self,
                    chat_id: UUID,
                    chat_record_id,
                    paragraph_list: List[Paragraph],
                    problem_text: str,
                    answer_text,
                    manage: PiplineManage,
                    step: BaseChatStep,
                    padding_problem_text: str = None,
                    **kwargs):
            chat_record = ChatRecord(id=chat_record_id,
                                     chat_id=chat_id,
                                     problem_text=problem_text,
                                     answer_text=answer_text,
                                     details=manage.get_details(),
                                     message_tokens=manage.context['message_tokens'],
                                     answer_tokens=manage.context['answer_tokens'],
                                     run_time=manage.context['run_time'],
                                     index=len(chat_info.chat_record_list) + 1)
            chat_info.append_chat_record(chat_record)
            # 重新设置缓存
            chat_cache.set(chat_id,
                           chat_info, timeout=60 * 30)

    return PostHandler()


class ChatMessageSerializer(serializers.Serializer):
    chat_id = serializers.UUIDField(required=True)

    def chat(self, message, re_chat: bool, stream: bool):
        self.is_valid(raise_exception=True)
        chat_id = self.data.get('chat_id')
        chat_info: ChatInfo = chat_cache.get(chat_id)
        if chat_info is None:
            chat_info = self.re_open_chat(chat_id)
            chat_cache.set(chat_id,
                           chat_info, timeout=60 * 30)

        pipline_manage_builder = PiplineManage.builder()
        # 如果开启了问题优化,则添加上问题优化步骤
        if chat_info.application.problem_optimization:
            pipline_manage_builder.append_step(BaseResetProblemStep)
        # 构建流水线管理器
        pipline_message = (pipline_manage_builder.append_step(BaseSearchDatasetStep)
                           .append_step(BaseGenerateHumanMessageStep)
                           .append_step(BaseChatStep)
                           .build())
        exclude_paragraph_id_list = []
        # 相同问题是否需要排除已经查询到的段落
        if re_chat:
            paragraph_id_list = flat_map([row.paragraph_id_list for row in
                                          filter(lambda chat_record: chat_record == message,
                                                 chat_info.chat_record_list)])
            exclude_paragraph_id_list = list(set(paragraph_id_list))
        # 构建运行参数
        params = chat_info.to_pipeline_manage_params(message, get_post_handler(chat_info), exclude_paragraph_id_list,
                                                     stream)
        # 运行流水线作业
        pipline_message.run(params)
        return pipline_message.context['chat_result']

    @staticmethod
    def re_open_chat(chat_id: str):
        chat = QuerySet(Chat).filter(id=chat_id).first()
        if chat is None:
            raise AppApiException(500, "会话不存在")
        application = QuerySet(Application).filter(id=chat.application_id).first()
        if application is None:
            raise AppApiException(500, "应用不存在")
        model = QuerySet(Model).filter(id=application.model_id).first()
        chat_model = None
        if model is not None:
            # 对话模型
            chat_model = ModelProvideConstants[model.provider].value.get_model(model.model_type, model.model_name,
                                                                               json.loads(
                                                                                   decrypt(model.credential)),
                                                                               streaming=True)
        # 数据集id列表
        dataset_id_list = [str(row.dataset_id) for row in
                           QuerySet(ApplicationDatasetMapping).filter(
                               application_id=application.id)]

        # 需要排除的文档
        exclude_document_id_list = [str(document.id) for document in
                                    QuerySet(Document).filter(
                                        dataset_id__in=dataset_id_list,
                                        is_active=False)]
        return ChatInfo(chat_id, chat_model, dataset_id_list, exclude_document_id_list, application)
