# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： chat_message_serializers.py
    @date：2023/11/14 13:51
    @desc:
"""
import uuid
from datetime import datetime
from typing import List, Dict
from uuid import UUID

from django.core.cache import caches
from django.db.models import QuerySet
from rest_framework import serializers

from application.chat_pipeline.pipeline_manage import PipelineManage
from application.chat_pipeline.step.chat_step.i_chat_step import PostResponseHandler
from application.chat_pipeline.step.chat_step.impl.base_chat_step import BaseChatStep
from application.chat_pipeline.step.generate_human_message_step.impl.base_generate_human_message_step import \
    BaseGenerateHumanMessageStep
from application.chat_pipeline.step.reset_problem_step.impl.base_reset_problem_step import BaseResetProblemStep
from application.chat_pipeline.step.search_dataset_step.impl.base_search_dataset_step import BaseSearchDatasetStep
from application.flow.common import Answer
from application.flow.i_step_node import WorkFlowPostHandler
from application.flow.workflow_manage import WorkflowManage, Flow
from application.models import ChatRecord, Chat, Application, ApplicationDatasetMapping, ApplicationTypeChoices, \
    WorkFlowVersion
from application.models.api_key_model import ApplicationPublicAccessClient, ApplicationAccessToken
from common.constants.authentication_type import AuthenticationType
from common.exception.app_exception import AppChatNumOutOfBoundsFailed, ChatException
from common.handle.base_to_response import BaseToResponse
from common.handle.impl.response.openai_to_response import OpenaiToResponse
from common.handle.impl.response.system_to_response import SystemToResponse
from common.util.field_message import ErrMessage
from common.util.split_model import flat_map
from dataset.models import Paragraph, Document
from setting.models import Model, Status
from setting.models_provider import get_model_credential
from django.utils.translation import gettext_lazy as _

chat_cache = caches['chat_cache']


class ChatInfo:
    def __init__(self,
                 chat_id: str,
                 dataset_id_list: List[str],
                 exclude_document_id_list: list[str],
                 application: Application,
                 work_flow_version: WorkFlowVersion = None):
        """
        :param chat_id:                     对话id
        :param dataset_id_list:             数据集列表
        :param exclude_document_id_list:    排除的文档
        :param application:                 应用信息
        """
        self.chat_id = chat_id
        self.application = application
        self.dataset_id_list = dataset_id_list
        self.exclude_document_id_list = exclude_document_id_list
        self.chat_record_list: List[ChatRecord] = []
        self.work_flow_version = work_flow_version

    @staticmethod
    def get_no_references_setting(dataset_setting, model_setting):
        no_references_setting = dataset_setting.get(
            'no_references_setting', {
                'status': 'ai_questioning',
                'value': '{question}'})
        if no_references_setting.get('status') == 'ai_questioning':
            no_references_prompt = model_setting.get('no_references_prompt', '{question}')
            no_references_setting['value'] = no_references_prompt if len(no_references_prompt) > 0 else "{question}"
        return no_references_setting

    def to_base_pipeline_manage_params(self):
        dataset_setting = self.application.dataset_setting
        model_setting = self.application.model_setting
        model_id = self.application.model.id if self.application.model is not None else None
        model_params_setting = None
        if model_id is not None:
            model = QuerySet(Model).filter(id=model_id).first()
            credential = get_model_credential(model.provider, model.model_type, model.model_name)
            model_params_setting = credential.get_model_params_setting_form(model.model_name).get_default_form_data()
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
            'problem_optimization_prompt': self.application.problem_optimization_prompt if self.application.problem_optimization_prompt is not None and len(
                self.application.problem_optimization_prompt) > 0 else _(
                "() contains the user's question. Answer the guessed user's question based on the context ({question}) Requirement: Output a complete question and put it in the <data></data> tag"),
            'prompt': model_setting.get(
                'prompt') if 'prompt' in model_setting and len(model_setting.get(
                'prompt')) > 0 else Application.get_default_model_prompt(),
            'system': model_setting.get(
                'system', None),
            'model_id': model_id,
            'problem_optimization': self.application.problem_optimization,
            'stream': True,
            'model_setting': model_setting,
            'model_params_setting': model_params_setting if self.application.model_params_setting is None or len(
                self.application.model_params_setting.keys()) == 0 else self.application.model_params_setting,
            'search_mode': self.application.dataset_setting.get(
                'search_mode') if 'search_mode' in self.application.dataset_setting else 'embedding',
            'no_references_setting': self.get_no_references_setting(self.application.dataset_setting, model_setting),
            'user_id': self.application.user_id,
            'application_id': self.application.id
        }

    def to_pipeline_manage_params(self, problem_text: str, post_response_handler: PostResponseHandler,
                                  exclude_paragraph_id_list, client_id: str, client_type, stream=True, form_data=None):
        if form_data is None:
            form_data = {}
        params = self.to_base_pipeline_manage_params()
        return {**params, 'problem_text': problem_text, 'post_response_handler': post_response_handler,
                'exclude_paragraph_id_list': exclude_paragraph_id_list, 'stream': stream, 'client_id': client_id,
                'client_type': client_type, 'form_data': form_data}

    def append_chat_record(self, chat_record: ChatRecord, client_id=None, asker=None):
        chat_record.problem_text = chat_record.problem_text[0:10240] if chat_record.problem_text is not None else ""
        chat_record.answer_text = chat_record.answer_text[0:40960] if chat_record.problem_text is not None else ""
        is_save = True
        # 存入缓存中
        for index in range(len(self.chat_record_list)):
            record = self.chat_record_list[index]
            if record.id == chat_record.id:
                self.chat_record_list[index] = chat_record
                is_save = False
        if is_save:
            self.chat_record_list.append(chat_record)
        if self.application.id is not None:
            # 插入数据库
            if not QuerySet(Chat).filter(id=self.chat_id).exists():
                asker_dict = {'user_name': '游客'}
                if asker is not None:
                    if isinstance(asker, str):
                        asker_dict = {
                            'user_name': asker
                        }
                    elif isinstance(asker, dict):
                        asker_dict = asker

                Chat(id=self.chat_id, application_id=self.application.id, abstract=chat_record.problem_text[0:1024],
                     client_id=client_id, asker=asker_dict, update_time=datetime.now()).save()
            else:
                Chat.objects.filter(id=self.chat_id).update(update_time=datetime.now())
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
            answer_list = [[Answer(answer_text, 'ai-chat-node', 'ai-chat-node', 'ai-chat-node', {}, 'ai-chat-node',
                                   kwargs.get('reasoning_content', '')).to_dict()]]
            chat_record = ChatRecord(id=chat_record_id,
                                     chat_id=chat_id,
                                     problem_text=problem_text,
                                     answer_text=answer_text,
                                     details=manage.get_details(),
                                     message_tokens=manage.context['message_tokens'],
                                     answer_tokens=manage.context['answer_tokens'],
                                     answer_text_list=answer_list,
                                     run_time=manage.context['run_time'],
                                     index=len(chat_info.chat_record_list) + 1)
            asker = kwargs.get("asker", None)
            chat_info.append_chat_record(chat_record, client_id, asker=asker)
            # 重新设置缓存
            chat_cache.set(chat_id,
                           chat_info, timeout=60 * 30)

    return PostHandler()


class OpenAIMessage(serializers.Serializer):
    content = serializers.CharField(required=True, error_messages=ErrMessage.char(_('content')))
    role = serializers.CharField(required=True, error_messages=ErrMessage.char(_('Role')))


class OpenAIInstanceSerializer(serializers.Serializer):
    messages = serializers.ListField(child=OpenAIMessage())
    chat_id = serializers.UUIDField(required=False, error_messages=ErrMessage.char(_("Conversation ID")))
    re_chat = serializers.BooleanField(required=False, error_messages=ErrMessage.boolean(_("Regenerate")))
    stream = serializers.BooleanField(required=False, error_messages=ErrMessage.boolean(_("Streaming Output")))


class OpenAIChatSerializer(serializers.Serializer):
    application_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_("Application ID")))
    client_id = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Client id")))
    client_type = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Client Type")))

    @staticmethod
    def get_message(instance):
        return instance.get('messages')[-1].get('content')

    @staticmethod
    def generate_chat(chat_id, application_id, message, client_id, asker=None):
        if chat_id is None:
            chat_id = str(uuid.uuid1())
        chat = QuerySet(Chat).filter(id=chat_id).first()
        if chat is None:
            asker_dict = {'user_name': '游客'}
            if asker is not None:
                if isinstance(asker, str):
                    asker_dict = {
                        'user_name': asker
                    }
                elif isinstance(asker, dict):
                    asker_dict = asker
            Chat(id=chat_id, application_id=application_id, abstract=message[0:1024], client_id=client_id,
                 asker=asker_dict).save()
        return chat_id

    def chat(self, instance: Dict, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            OpenAIInstanceSerializer(data=instance).is_valid(raise_exception=True)
        chat_id = instance.get('chat_id')
        message = self.get_message(instance)
        re_chat = instance.get('re_chat', False)
        stream = instance.get('stream', False)
        application_id = self.data.get('application_id')
        client_id = self.data.get('client_id')
        client_type = self.data.get('client_type')
        chat_id = self.generate_chat(chat_id, application_id, message, client_id,
                                     asker=instance.get('form_data', {}).get("asker"))
        return ChatMessageSerializer(
            data={
                'chat_id': chat_id, 'message': message,
                're_chat': re_chat,
                'stream': stream,
                'application_id': application_id,
                'client_id': client_id,
                'client_type': client_type,
                'form_data': instance.get('form_data', {}),
                'image_list': instance.get('image_list', []),
                'document_list': instance.get('document_list', []),
                'audio_list': instance.get('audio_list', []),
                'other_list': instance.get('other_list', []),
            }
        ).chat(base_to_response=OpenaiToResponse())


class ChatMessageSerializer(serializers.Serializer):
    chat_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_("Conversation ID")))
    message = serializers.CharField(required=True, error_messages=ErrMessage.char(_("User Questions")))
    stream = serializers.BooleanField(required=True,
                                      error_messages=ErrMessage.char(_("Is the answer in streaming mode")))
    re_chat = serializers.BooleanField(required=True, error_messages=ErrMessage.char(_("Do you want to reply again")))
    chat_record_id = serializers.UUIDField(required=False, allow_null=True,
                                           error_messages=ErrMessage.uuid(_("Conversation record id")))

    node_id = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                    error_messages=ErrMessage.char(_("Node id")))

    runtime_node_id = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                            error_messages=ErrMessage.char(_("Runtime node id")))

    node_data = serializers.DictField(required=False, allow_null=True,
                                      error_messages=ErrMessage.char(_("Node parameters")))
    application_id = serializers.UUIDField(required=False, allow_null=True,
                                           error_messages=ErrMessage.uuid(_("Application ID")))
    client_id = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Client id")))
    client_type = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Client Type")))
    form_data = serializers.DictField(required=False, error_messages=ErrMessage.char(_("Global variables")))
    image_list = serializers.ListField(required=False, error_messages=ErrMessage.list(_("picture")))
    document_list = serializers.ListField(required=False, error_messages=ErrMessage.list(_("document")))
    audio_list = serializers.ListField(required=False, error_messages=ErrMessage.list(_("Audio")))
    other_list = serializers.ListField(required=False, error_messages=ErrMessage.list(_("Other")))
    child_node = serializers.DictField(required=False, allow_null=True,
                                       error_messages=ErrMessage.dict(_("Child Nodes")))

    def is_valid_application_workflow(self, *, raise_exception=False):
        self.is_valid_intraday_access_num()

    def is_valid_chat_id(self, chat_info: ChatInfo):
        if self.data.get('application_id') is not None and self.data.get('application_id') != str(
                chat_info.application.id):
            raise ChatException(500, _("Conversation does not exist"))

    def is_valid_intraday_access_num(self):
        if self.data.get('client_type') == AuthenticationType.APPLICATION_ACCESS_TOKEN.value:
            access_client = QuerySet(ApplicationPublicAccessClient).filter(client_id=self.data.get('client_id'),
                                                                           application_id=self.data.get(
                                                                               'application_id')).first()
            if access_client is None:
                access_client = ApplicationPublicAccessClient(client_id=self.data.get('client_id'),
                                                              application_id=self.data.get('application_id'),
                                                              access_num=0,
                                                              intraday_access_num=0)
                access_client.save()

            application_access_token = QuerySet(ApplicationAccessToken).filter(
                application_id=self.data.get('application_id')).first()
            if application_access_token.access_num <= access_client.intraday_access_num:
                raise AppChatNumOutOfBoundsFailed(1002, _("The number of visits exceeds today's visits"))

    def is_valid_application_simple(self, *, chat_info: ChatInfo, raise_exception=False):
        self.is_valid_intraday_access_num()
        model = chat_info.application.model
        if model is None:
            return chat_info
        model = QuerySet(Model).filter(id=model.id).first()
        if model is None:
            return chat_info
        if model.status == Status.ERROR:
            raise ChatException(500, _("The current model is not available"))
        if model.status == Status.DOWNLOAD:
            raise ChatException(500, _("The model is downloading, please try again later"))
        return chat_info

    def chat_simple(self, chat_info: ChatInfo, base_to_response):
        message = self.data.get('message')
        re_chat = self.data.get('re_chat')
        stream = self.data.get('stream')
        client_id = self.data.get('client_id')
        client_type = self.data.get('client_type')
        form_data = self.data.get("form_data")
        pipeline_manage_builder = PipelineManage.builder()
        # 如果开启了问题优化,则添加上问题优化步骤
        if chat_info.application.problem_optimization:
            pipeline_manage_builder.append_step(BaseResetProblemStep)
        # 构建流水线管理器
        pipeline_message = (pipeline_manage_builder.append_step(BaseSearchDatasetStep)
                            .append_step(BaseGenerateHumanMessageStep)
                            .append_step(BaseChatStep)
                            .add_base_to_response(base_to_response)
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
                                                     client_id, client_type, stream, form_data)
        # 运行流水线作业
        pipeline_message.run(params)
        return pipeline_message.context['chat_result']

    @staticmethod
    def get_chat_record(chat_info, chat_record_id):
        if chat_info is not None:
            chat_record_list = [chat_record for chat_record in chat_info.chat_record_list if
                                str(chat_record.id) == str(chat_record_id)]
            if chat_record_list is not None and len(chat_record_list):
                return chat_record_list[-1]
        chat_record = QuerySet(ChatRecord).filter(id=chat_record_id, chat_id=chat_info.chat_id).first()
        if chat_record is None:
            raise ChatException(500, _("Conversation record does not exist"))
        chat_record = QuerySet(ChatRecord).filter(id=chat_record_id).first()
        return chat_record

    def chat_work_flow(self, chat_info: ChatInfo, base_to_response):
        message = self.data.get('message')
        re_chat = self.data.get('re_chat')
        stream = self.data.get('stream')
        client_id = self.data.get('client_id')
        client_type = self.data.get('client_type')
        form_data = self.data.get('form_data')
        image_list = self.data.get('image_list')
        document_list = self.data.get('document_list')
        audio_list = self.data.get('audio_list')
        other_list = self.data.get('other_list')
        user_id = chat_info.application.user_id
        chat_record_id = self.data.get('chat_record_id')
        chat_record = None
        history_chat_record = chat_info.chat_record_list
        if chat_record_id is not None:
            chat_record = self.get_chat_record(chat_info, chat_record_id)
            history_chat_record = [r for r in chat_info.chat_record_list if str(r.id) != chat_record_id]
        work_flow_manage = WorkflowManage(Flow.new_instance(chat_info.work_flow_version.work_flow),
                                          {'history_chat_record': history_chat_record, 'question': message,
                                           'chat_id': chat_info.chat_id, 'chat_record_id': str(
                                              uuid.uuid1()) if chat_record is None else chat_record.id,
                                           'stream': stream,
                                           're_chat': re_chat,
                                           'client_id': client_id,
                                           'client_type': client_type,
                                           'user_id': user_id}, WorkFlowPostHandler(chat_info, client_id, client_type),
                                          base_to_response, form_data, image_list, document_list, audio_list, other_list,
                                          self.data.get('runtime_node_id'),
                                          self.data.get('node_data'), chat_record, self.data.get('child_node'))
        r = work_flow_manage.run()
        return r

    def chat(self, base_to_response: BaseToResponse = SystemToResponse()):
        super().is_valid(raise_exception=True)
        chat_info = self.get_chat_info()
        self.is_valid_chat_id(chat_info)
        if chat_info.application.type == ApplicationTypeChoices.SIMPLE:
            self.is_valid_application_simple(raise_exception=True, chat_info=chat_info),
            return self.chat_simple(chat_info, base_to_response)
        else:
            self.is_valid_application_workflow(raise_exception=True)
            return self.chat_work_flow(chat_info, base_to_response)

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
            raise ChatException(500, _("Conversation does not exist"))
        application = QuerySet(Application).filter(id=chat.application_id).first()
        if application is None:
            raise ChatException(500, _("Application does not exist"))
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
        chat_info = ChatInfo(chat_id, dataset_id_list, exclude_document_id_list, application)
        chat_record_list = list(QuerySet(ChatRecord).filter(chat_id=chat_id).order_by('-create_time')[0:5])
        chat_record_list.sort(key=lambda r: r.create_time)
        for chat_record in chat_record_list:
            chat_info.chat_record_list.append(chat_record)
        return chat_info

    @staticmethod
    def re_open_chat_work_flow(chat_id, application):
        work_flow_version = QuerySet(WorkFlowVersion).filter(application_id=application.id).order_by(
            '-create_time')[0:1].first()
        if work_flow_version is None:
            raise ChatException(500, _("The application has not been published. Please use it after publishing."))

        chat_info = ChatInfo(chat_id, [], [], application, work_flow_version)
        chat_record_list = list(QuerySet(ChatRecord).filter(chat_id=chat_id).order_by('-create_time')[0:5])
        chat_record_list.sort(key=lambda r: r.create_time)
        for chat_record in chat_record_list:
            chat_info.chat_record_list.append(chat_record)
        return chat_info
