# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： chat_message_serializers.py
    @date：2023/11/14 13:51
    @desc:
"""
import uuid
from typing import List
from uuid import UUID

from django.core.cache import caches
from django.db.models import QuerySet
from langchain.chat_models.base import BaseChatModel
from rest_framework import serializers

from application.chat_pipeline.pipeline_manage import PipelineManage
from application.chat_pipeline.step.chat_step.i_chat_step import PostResponseHandler
from application.chat_pipeline.step.chat_step.impl.base_chat_step import BaseChatStep
from application.chat_pipeline.step.generate_human_message_step.impl.base_generate_human_message_step import \
    BaseGenerateHumanMessageStep
from application.chat_pipeline.step.reset_problem_step.impl.base_reset_problem_step import BaseResetProblemStep
from application.chat_pipeline.step.search_dataset_step.impl.base_search_dataset_step import BaseSearchDatasetStep
from application.flow.i_step_node import WorkFlowPostHandler
from application.flow.workflow_manage import WorkflowManage, Flow
from application.models import ChatRecord, Chat, Application, ApplicationDatasetMapping, ApplicationTypeChoices, \
    WorkFlowVersion
from application.models.api_key_model import ApplicationPublicAccessClient, ApplicationAccessToken
from common.constants.authentication_type import AuthenticationType
from common.exception.app_exception import AppApiException, AppChatNumOutOfBoundsFailed
from common.util.field_message import ErrMessage
from common.util.split_model import flat_map
from dataset.models import Paragraph, Document
from setting.models import Model, Status

chat_cache = caches['chat_cache']


class ChatInfo:
    def __init__(self,
                 chat_id: str,
                 chat_model: BaseChatModel | None,
                 dataset_id_list: List[str],
                 exclude_document_id_list: list[str],
                 application: Application,
                 work_flow_version: WorkFlowVersion = None):
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
        self.work_flow_version = work_flow_version

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
            'stream': True,
            'search_mode': self.application.dataset_setting.get(
                'search_mode') if 'search_mode' in self.application.dataset_setting else 'embedding',
            'no_references_setting': self.application.dataset_setting.get(
                'no_references_setting') if 'no_references_setting' in self.application.dataset_setting else {
                'status': 'ai_questioning',
                'value': '{question}',
            },
            'user_id': self.application.user_id

        }

    def to_pipeline_manage_params(self, problem_text: str, post_response_handler: PostResponseHandler,
                                  exclude_paragraph_id_list, client_id: str, client_type, stream=True):
        params = self.to_base_pipeline_manage_params()
        return {**params, 'problem_text': problem_text, 'post_response_handler': post_response_handler,
                'exclude_paragraph_id_list': exclude_paragraph_id_list, 'stream': stream, 'client_id': client_id,
                'client_type': client_type}

    def append_chat_record(self, chat_record: ChatRecord, client_id=None):
        chat_record.problem_text = chat_record.problem_text[0:1024] if chat_record.problem_text is not None else ""
        # 存入缓存中
        self.chat_record_list.append(chat_record)
        if self.application.id is not None:
            # 插入数据库
            if not QuerySet(Chat).filter(id=self.chat_id).exists():
                Chat(id=self.chat_id, application_id=self.application.id, abstract=chat_record.problem_text,
                     client_id=client_id).save()
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
                    manage: PipelineManage,
                    step: BaseChatStep,
                    padding_problem_text: str = None,
                    client_id=None,
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
            chat_info.append_chat_record(chat_record, client_id)
            # 重新设置缓存
            chat_cache.set(chat_id,
                           chat_info, timeout=60 * 30)

    return PostHandler()


class ChatMessageSerializer(serializers.Serializer):
    chat_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char("对话id"))
    message = serializers.CharField(required=True, error_messages=ErrMessage.char("用户问题"))
    stream = serializers.BooleanField(required=True, error_messages=ErrMessage.char("是否流式回答"))
    re_chat = serializers.BooleanField(required=True, error_messages=ErrMessage.char("是否重新回答"))
    application_id = serializers.UUIDField(required=False, allow_null=True, error_messages=ErrMessage.uuid("应用id"))
    client_id = serializers.CharField(required=True, error_messages=ErrMessage.char("客户端id"))
    client_type = serializers.CharField(required=True, error_messages=ErrMessage.char("客户端类型"))

    def is_valid_application_workflow(self, *, raise_exception=False):
        self.is_valid_intraday_access_num()

    def is_valid_intraday_access_num(self):
        if self.data.get('client_type') == AuthenticationType.APPLICATION_ACCESS_TOKEN.value:
            access_client = QuerySet(ApplicationPublicAccessClient).filter(id=self.data.get('client_id')).first()
            if access_client is None:
                access_client = ApplicationPublicAccessClient(id=self.data.get('client_id'),
                                                              application_id=self.data.get('application_id'),
                                                              access_num=0,
                                                              intraday_access_num=0)
                access_client.save()

            application_access_token = QuerySet(ApplicationAccessToken).filter(
                application_id=self.data.get('application_id')).first()
            if application_access_token.access_num <= access_client.intraday_access_num:
                raise AppChatNumOutOfBoundsFailed(1002, "访问次数超过今日访问量")

    def is_valid_application_simple(self, *, chat_info: ChatInfo, raise_exception=False):
        self.is_valid_intraday_access_num()
        model = chat_info.application.model
        if model is None:
            return chat_info
        model = QuerySet(Model).filter(id=model.id).first()
        if model is None:
            return chat_info
        if model.status == Status.ERROR:
            raise AppApiException(500, "当前模型不可用")
        if model.status == Status.DOWNLOAD:
            raise AppApiException(500, "模型正在下载中,请稍后再发起对话")
        return chat_info

    def chat_simple(self, chat_info: ChatInfo):
        message = self.data.get('message')
        re_chat = self.data.get('re_chat')
        stream = self.data.get('stream')
        client_id = self.data.get('client_id')
        client_type = self.data.get('client_type')
        pipeline_manage_builder = PipelineManage.builder()
        # 如果开启了问题优化,则添加上问题优化步骤
        if chat_info.application.problem_optimization:
            pipeline_manage_builder.append_step(BaseResetProblemStep)
        # 构建流水线管理器
        pipeline_message = (pipeline_manage_builder.append_step(BaseSearchDatasetStep)
                            .append_step(BaseGenerateHumanMessageStep)
                            .append_step(BaseChatStep)
                            .build())
        exclude_paragraph_id_list = []
        # 相同问题是否需要排除已经查询到的段落
        if re_chat:
            paragraph_id_list = flat_map(
                [[paragraph.get('id') for paragraph in chat_record.details['search_step']['paragraph_list']] for
                 chat_record in chat_info.chat_record_list if
                 chat_record.problem_text == message and 'search_step' in chat_record.details and 'paragraph_list' in
                 chat_record.details['search_step']])
            exclude_paragraph_id_list = list(set(paragraph_id_list))
        # 构建运行参数
        params = chat_info.to_pipeline_manage_params(message, get_post_handler(chat_info), exclude_paragraph_id_list,
                                                     client_id, client_type, stream)
        # 运行流水线作业
        pipeline_message.run(params)
        return pipeline_message.context['chat_result']

    def chat_work_flow(self, chat_info: ChatInfo):
        message = self.data.get('message')
        re_chat = self.data.get('re_chat')
        stream = self.data.get('stream')
        client_id = self.data.get('client_id')
        client_type = self.data.get('client_type')
        user_id = chat_info.application.user_id
        work_flow_manage = WorkflowManage(Flow.new_instance(chat_info.work_flow_version.work_flow),
                                          {'history_chat_record': chat_info.chat_record_list, 'question': message,
                                           'chat_id': chat_info.chat_id, 'chat_record_id': str(uuid.uuid1()),
                                           'stream': stream,
                                           're_chat': re_chat,
                                           'user_id': user_id}, WorkFlowPostHandler(chat_info, client_id, client_type))
        r = work_flow_manage.run()
        return r

    def chat(self):
        super().is_valid(raise_exception=True)
        chat_info = self.get_chat_info()
        if chat_info.application.type == ApplicationTypeChoices.SIMPLE:
            self.is_valid_application_simple(raise_exception=True, chat_info=chat_info),
            return self.chat_simple(chat_info)
        else:
            self.is_valid_application_workflow(raise_exception=True)
            return self.chat_work_flow(chat_info)

    def get_chat_info(self):
        self.is_valid(raise_exception=True)
        chat_id = self.data.get('chat_id')
        chat_info: ChatInfo = chat_cache.get(chat_id)
        if chat_info is None:
            chat_info: ChatInfo = self.re_open_chat(chat_id)
            chat_cache.set(chat_id,
                           chat_info, timeout=60 * 30)
        return chat_info

    def re_open_chat(self, chat_id: str):
        chat = QuerySet(Chat).filter(id=chat_id).first()
        if chat is None:
            raise AppApiException(500, "会话不存在")
        application = QuerySet(Application).filter(id=chat.application_id).first()
        if application is None:
            raise AppApiException(500, "应用不存在")
        if application.type == ApplicationTypeChoices.SIMPLE:
            return self.re_open_chat_simple(chat_id, application)
        else:
            return self.re_open_chat_work_flow(chat_id, application)

    @staticmethod
    def re_open_chat_simple(chat_id, application):
        # 数据集id列表
        dataset_id_list = [str(row.dataset_id) for row in
                           QuerySet(ApplicationDatasetMapping).filter(
                               application_id=application.id)]

        # 需要排除的文档
        exclude_document_id_list = [str(document.id) for document in
                                    QuerySet(Document).filter(
                                        dataset_id__in=dataset_id_list,
                                        is_active=False)]
        return ChatInfo(chat_id, None, dataset_id_list, exclude_document_id_list, application)

    @staticmethod
    def re_open_chat_work_flow(chat_id, application):
        work_flow_version = QuerySet(WorkFlowVersion).filter(application_id=application.id).order_by(
            '-create_time')[0:1].first()
        if work_flow_version is None:
            raise AppApiException(500, "应用未发布,请发布后再使用")
        return ChatInfo(chat_id, None, [], [], application, work_flow_version)
