# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： chat.py
    @date：2025/6/9 11:23
    @desc:
"""
import json
from gettext import gettext
from typing import List, Dict

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from langchain_core.messages import HumanMessage, AIMessage
from rest_framework import serializers

from application.chat_pipeline.pipeline_manage import PipelineManage
from application.chat_pipeline.step.chat_step.i_chat_step import PostResponseHandler
from application.chat_pipeline.step.chat_step.impl.base_chat_step import BaseChatStep
from application.chat_pipeline.step.generate_human_message_step.impl.base_generate_human_message_step import \
    BaseGenerateHumanMessageStep
from application.chat_pipeline.step.reset_problem_step.impl.base_reset_problem_step import BaseResetProblemStep
from application.chat_pipeline.step.search_dataset_step.impl.base_search_dataset_step import BaseSearchDatasetStep
from application.flow.common import Answer, Workflow
from application.flow.i_step_node import WorkFlowPostHandler
from application.flow.tools import to_stream_response_simple
from application.flow.workflow_manage import WorkflowManage
from application.models import Application, ApplicationTypeChoices, ApplicationKnowledgeMapping, \
    ChatUserType, ApplicationChatUserStats, ApplicationAccessToken, ChatRecord, Chat, ApplicationVersion
from application.serializers.application import ApplicationOperateSerializer
from application.serializers.common import ChatInfo
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.exception.app_exception import AppApiException, AppChatNumOutOfBoundsFailed, ChatException
from common.handle.base_to_response import BaseToResponse
from common.handle.impl.response.openai_to_response import OpenaiToResponse
from common.handle.impl.response.system_to_response import SystemToResponse
from common.utils.common import flat_map
from knowledge.models import Document, Paragraph
from models_provider.models import Model, Status
from models_provider.tools import get_model_instance_by_model_workspace_id


class ChatMessagesSerializers(serializers.Serializer):
    role = serializers.CharField(required=True, label=_("Role"))
    content = serializers.CharField(required=True, label=_("Content"))


class GeneratePromptSerializers(serializers.Serializer):
    prompt = serializers.CharField(required=True, label=_("Prompt template"))
    messages = serializers.ListSerializer(child=ChatMessagesSerializers(), required=True, label=_("Chat context"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        messages = self.data.get("messages")

        if len(messages) > 30:
            raise AppApiException(400, _("Too many messages"))

        for index in range(len(messages)):
            role = messages[index].get('role')
            if role == 'ai' and index % 2 != 1:
                raise AppApiException(400, _("Authentication failed. Please verify that the parameters are correct."))
            if role == 'user' and index % 2 != 0:
                raise AppApiException(400, _("Authentication failed. Please verify that the parameters are correct."))
            if role not in ['user', 'ai']:
                raise AppApiException(400, _("Authentication failed. Please verify that the parameters are correct."))

class ChatMessageSerializers(serializers.Serializer):
    message = serializers.CharField(required=True, label=_("User Questions"))
    stream = serializers.BooleanField(required=True,
                                      label=_("Is the answer in streaming mode"))
    re_chat = serializers.BooleanField(required=True, label=_("Do you want to reply again"))
    chat_record_id = serializers.UUIDField(required=False, allow_null=True,
                                           label=_("Conversation record id"))

    node_id = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                    label=_("Node id"))

    runtime_node_id = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                            label=_("Runtime node id"))

    node_data = serializers.DictField(required=False, allow_null=True,
                                      label=_("Node parameters"))

    form_data = serializers.DictField(required=False, label=_("Global variables"))
    image_list = serializers.ListField(required=False, label=_("picture"))
    document_list = serializers.ListField(required=False, label=_("document"))
    audio_list = serializers.ListField(required=False, label=_("Audio"))
    other_list = serializers.ListField(required=False, label=_("Other"))
    child_node = serializers.DictField(required=False, allow_null=True,
                                       label=_("Child Nodes"))


def get_post_handler(chat_info: ChatInfo):
    class PostHandler(PostResponseHandler):

        def handler(self,
                    chat_id,
                    chat_record_id,
                    paragraph_list: List[Paragraph],
                    problem_text: str,
                    answer_text,
                    manage: PipelineManage,
                    step: BaseChatStep,
                    padding_problem_text: str = None,
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
            chat_info.append_chat_record(chat_record)
            # 重新设置缓存
            chat_info.set_cache()

    return PostHandler()


class DebugChatSerializers(serializers.Serializer):
    chat_id = serializers.UUIDField(required=True, label=_("Conversation ID"))

    def chat(self, instance: dict, base_to_response: BaseToResponse = SystemToResponse()):
        self.is_valid(raise_exception=True)
        chat_id = self.data.get('chat_id')
        chat_info: ChatInfo = ChatInfo.get_cache(chat_id)
        application = QuerySet(Application).filter(id=chat_info.application_id).first()
        chat_info.application = application
        return ChatSerializers(data={
            'chat_id': chat_id, "chat_user_id": chat_info.chat_user_id,
            "chat_user_type": chat_info.chat_user_type,
            "application_id": chat_info.application.id, "debug": True
        }).chat(instance, base_to_response)


class PromptGenerateSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=False, label=_('Workspace ID'))
    model_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Model"))
    application_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Application"))

    def generate_prompt(self, instance: dict, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            GeneratePromptSerializers(data=instance).is_valid(raise_exception=True)
        workspace_id = self.data.get('workspace_id')
        model_id = self.data.get('model_id')
        prompt = instance.get('prompt')
        messages = instance.get('messages')

        message = messages[-1]['content']
        q = prompt.replace("{userInput}", message)
        messages[-1]['content'] = q

        model_exist = QuerySet(Model).filter(workspace_id=workspace_id,
                                             id=model_id,
                                             model_type = "LLM"
                                             ).exists()
        if not model_exist:
            raise Exception(_("Model does not exists or is not an LLM model"))

        def process():
            model = get_model_instance_by_model_workspace_id(model_id=model_id, workspace_id=workspace_id)

            for r in model.stream([HumanMessage(content=m.get('content')) if m.get('role') == 'user' else AIMessage(
                    content=m.get('content')) for m in messages]):
                yield 'data: ' + json.dumps({'content': r.content}) + '\n\n'

        return to_stream_response_simple(process())


class OpenAIMessage(serializers.Serializer):
    content = serializers.CharField(required=True, label=_('content'))
    role = serializers.CharField(required=True, label=_('Role'))


class OpenAIInstanceSerializer(serializers.Serializer):
    messages = serializers.ListField(child=OpenAIMessage())
    chat_id = serializers.UUIDField(required=False, label=_("Conversation ID"))
    re_chat = serializers.BooleanField(required=False, label=_("Regenerate"))
    stream = serializers.BooleanField(required=False, label=_("Streaming Output"))


class OpenAIChatSerializer(serializers.Serializer):
    application_id = serializers.UUIDField(required=True, label=_("Application ID"))
    chat_user_id = serializers.CharField(required=True, label=_("Client id"))
    chat_user_type = serializers.CharField(required=True, label=_("Client Type"))

    @staticmethod
    def get_message(instance):
        return instance.get('messages')[-1].get('content')

    @staticmethod
    def generate_chat(chat_id, application_id, message, chat_user_id, chat_user_type):
        if chat_id is None:
            chat_id = str(uuid.uuid1())
        chat_info = ChatInfo(chat_id, chat_user_id, chat_user_type, [], [],
                             application_id)
        chat_info.set_cache()
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
        chat_user_id = self.data.get('chat_user_id')
        chat_user_type = self.data.get('chat_user_type')
        chat_id = self.generate_chat(chat_id, application_id, message, chat_user_id, chat_user_type)
        return ChatSerializers(
            data={
                'chat_id': chat_id,
                'chat_user_id': chat_user_id,
                'chat_user_type': chat_user_type,
                'application_id': application_id
            }
        ).chat({'message': message,
                're_chat': re_chat,
                'stream': stream,
                'form_data': instance.get('form_data', {}),
                'image_list': instance.get('image_list', []),
                'document_list': instance.get('document_list', []),
                'audio_list': instance.get('audio_list', []),
                'other_list': instance.get('other_list', [])},
               base_to_response=OpenaiToResponse())


class ChatSerializers(serializers.Serializer):
    chat_id = serializers.UUIDField(required=True, label=_("Conversation ID"))
    chat_user_id = serializers.CharField(required=True, label=_("Client id"))
    chat_user_type = serializers.CharField(required=True, label=_("Client Type"))
    application_id = serializers.UUIDField(required=True, allow_null=True,
                                           label=_("Application ID"))
    debug = serializers.BooleanField(required=False, label=_("Debug"))

    def is_valid_application_workflow(self, *, raise_exception=False):
        self.is_valid_intraday_access_num()

    def is_valid_chat_id(self, chat_info: ChatInfo):
        if self.data.get('application_id') is not None and self.data.get('application_id') != str(
                chat_info.application_id):
            raise ChatException(500, _("Conversation does not exist"))

    def is_valid_intraday_access_num(self):
        if not self.data.get('debug') and [ChatUserType.ANONYMOUS_USER.value,
                                           ChatUserType.CHAT_USER.value].__contains__(
            self.data.get('chat_user_type')):
            access_client = QuerySet(ApplicationChatUserStats).filter(chat_user_id=self.data.get('chat_user_id'),
                                                                      application_id=self.data.get(
                                                                          'application_id')).first()
            if access_client is None:
                access_client = ApplicationChatUserStats(chat_user_id=self.data.get('chat_user_id'),
                                                         chat_user_type=self.data.get('chat_user_type'),
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
        model_id = chat_info.application.model_id
        if model_id is None:
            return chat_info
        model = QuerySet(Model).filter(id=model_id).first()
        if model is None:
            return chat_info
        if model.status == Status.ERROR:
            raise ChatException(500, _("The current model is not available"))
        if model.status == Status.DOWNLOAD:
            raise ChatException(500, _("The model is downloading, please try again later"))
        return chat_info

    def chat_simple(self, chat_info: ChatInfo, instance, base_to_response):
        message = instance.get('message')
        re_chat = instance.get('re_chat')
        stream = instance.get('stream')
        chat_user_id = self.data.get('chat_user_id')
        chat_user_type = self.data.get('chat_user_type')
        form_data = instance.get("form_data")
        pipeline_manage_builder = PipelineManage.builder()
        # 如果开启了问题优化,则添加上问题优化步骤
        if chat_info.application.problem_optimization:
            pipeline_manage_builder.append_step(BaseResetProblemStep)
        # 构建流水线管理器
        pipeline_message = (pipeline_manage_builder.append_step(BaseSearchDatasetStep)
                            .append_step(BaseGenerateHumanMessageStep)
                            .append_step(BaseChatStep)
                            .add_base_to_response(base_to_response)
                            .add_debug(self.data.get('debug', False))
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
                                                     chat_user_id, chat_user_type, stream, form_data)
        chat_info.set_chat(message)
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

    def chat_work_flow(self, chat_info: ChatInfo, instance: dict, base_to_response):
        message = instance.get('message')
        re_chat = instance.get('re_chat')
        stream = instance.get('stream')
        chat_user_id = self.data.get("chat_user_id")
        chat_user_type = self.data.get('chat_user_type')
        form_data = instance.get('form_data')
        image_list = instance.get('image_list')
        document_list = instance.get('document_list')
        audio_list = instance.get('audio_list')
        other_list = instance.get('other_list')
        workspace_id = chat_info.application.workspace_id
        chat_record_id = instance.get('chat_record_id')
        debug = self.data.get('debug', False)
        chat_record = None
        history_chat_record = chat_info.chat_record_list
        if chat_record_id is not None:
            chat_record = self.get_chat_record(chat_info, chat_record_id)
            history_chat_record = [r for r in chat_info.chat_record_list if str(r.id) != chat_record_id]
        work_flow = chat_info.application.work_flow
        work_flow_manage = WorkflowManage(Workflow.new_instance(work_flow),
                                          {'history_chat_record': history_chat_record, 'question': message,
                                           'chat_id': chat_info.chat_id, 'chat_record_id': str(
                                              uuid.uuid7()) if chat_record is None else chat_record.id,
                                           'stream': stream,
                                           're_chat': re_chat,
                                           'chat_user_id': chat_user_id,
                                           'chat_user_type': chat_user_type,
                                           'workspace_id': workspace_id,
                                           'debug': debug,
                                           'chat_user': chat_info.get_chat_user(),
                                           'application_id': str(chat_info.application_id)},
                                          WorkFlowPostHandler(chat_info),
                                          base_to_response, form_data, image_list, document_list, audio_list,
                                          other_list,
                                          instance.get('runtime_node_id'),
                                          instance.get('node_data'), chat_record, instance.get('child_node'))
        chat_info.set_chat(message)
        r = work_flow_manage.run()
        return r

    def is_valid_chat_user(self):
        chat_user_id = self.data.get('chat_user_id')
        application_id = self.data.get('application_id')
        chat_user_type = self.data.get('chat_user_type')
        is_auth_chat_user = DatabaseModelManage.get_model("is_auth_chat_user")
        application_access_token = QuerySet(ApplicationAccessToken).filter(application_id=application_id).first()
        if application_access_token and application_access_token.authentication and application_access_token.authentication_value.get(
                'type') == 'login':
            if chat_user_type == ChatUserType.CHAT_USER.value and is_auth_chat_user:
                is_auth = is_auth_chat_user(chat_user_id, application_id)
                if not is_auth:
                    raise ChatException(500, _("The chat user is not authorized."))

    def chat(self, instance: dict, base_to_response: BaseToResponse = SystemToResponse()):
        super().is_valid(raise_exception=True)
        ChatMessageSerializers(data=instance).is_valid(raise_exception=True)
        chat_info = self.get_chat_info()
        chat_info.get_application()
        chat_info.get_chat_user(asker=(instance.get('form_data') or {}).get('asker'))
        self.is_valid_chat_id(chat_info)
        self.is_valid_chat_user()
        if chat_info.application.type == ApplicationTypeChoices.SIMPLE:
            self.is_valid_application_simple(raise_exception=True, chat_info=chat_info)
            return self.chat_simple(chat_info, instance, base_to_response)
        else:
            self.is_valid_application_workflow(raise_exception=True)
            return self.chat_work_flow(chat_info, instance, base_to_response)

    def get_chat_info(self):
        self.is_valid(raise_exception=True)
        chat_id = self.data.get('chat_id')
        chat_info: ChatInfo = ChatInfo.get_cache(chat_id)
        if chat_info is None:
            chat_info: ChatInfo = self.re_open_chat(chat_id)
            chat_info.set_cache()
        return chat_info

    def re_open_chat(self, chat_id: str):
        chat = QuerySet(Chat).filter(id=chat_id).first()
        if chat is None:
            raise ChatException(500, _("Conversation does not exist"))
        application = QuerySet(Application).filter(id=chat.application_id).first()
        if application is None:
            raise ChatException(500, _("Application does not exist"))
        application_version = QuerySet(ApplicationVersion).filter(application_id=application.id).order_by(
            '-create_time')[0:1].first()
        if application_version is None:
            raise ChatException(500, _("The application has not been published. Please use it after publishing."))
        if application.type == ApplicationTypeChoices.SIMPLE:
            return self.re_open_chat_simple(chat_id, application)
        else:
            return self.re_open_chat_work_flow(chat_id, application)

    def re_open_chat_simple(self, chat_id, application):
        # 数据集id列表
        knowledge_id_list = [str(row.knowledge_id) for row in
                             QuerySet(ApplicationKnowledgeMapping).filter(
                                 application_id=application.id)]

        # 需要排除的文档
        exclude_document_id_list = [str(document.id) for document in
                                    QuerySet(Document).filter(
                                        knowledge_id__in=knowledge_id_list,
                                        is_active=False)]
        chat_info = ChatInfo(chat_id, self.data.get('chat_user_id'), self.data.get('chat_user_type'), knowledge_id_list,
                             exclude_document_id_list, application.id)
        chat_record_list = list(QuerySet(ChatRecord).filter(chat_id=chat_id).order_by('-create_time')[0:5])
        chat_record_list.sort(key=lambda r: r.create_time)
        for chat_record in chat_record_list:
            chat_info.chat_record_list.append(chat_record)
        return chat_info

    def re_open_chat_work_flow(self, chat_id, application):
        chat_info = ChatInfo(chat_id, self.data.get('chat_user_id'), self.data.get('chat_user_type'), [], [],
                             application.id)
        chat_record_list = list(QuerySet(ChatRecord).filter(chat_id=chat_id).order_by('-create_time')[0:5])
        chat_record_list.sort(key=lambda r: r.create_time)
        for chat_record in chat_record_list:
            chat_info.chat_record_list.append(chat_record)
        return chat_info


class OpenChatSerializers(serializers.Serializer):
    workspace_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Workspace ID"))
    application_id = serializers.UUIDField(required=True)
    chat_user_id = serializers.CharField(required=True, label=_("Client id"))
    chat_user_type = serializers.CharField(required=True, label=_("Client Type"))
    debug = serializers.BooleanField(required=True, label=_("Debug"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        workspace_id = self.data.get('workspace_id')
        application_id = self.data.get('application_id')
        query_set = QuerySet(Application).filter(id=application_id)
        if workspace_id:
            query_set = query_set.filter(workspace_id=workspace_id)
        if not query_set.exists():
            raise AppApiException(500, gettext('Application does not exist'))

    def open(self):
        self.is_valid(raise_exception=True)
        application_id = self.data.get('application_id')
        application = QuerySet(Application).get(id=application_id)
        debug = self.data.get("debug")
        if not debug:
            application_version = QuerySet(ApplicationVersion).filter(application_id=application_id).order_by(
                '-create_time')[0:1].first()
            if application_version is None:
                raise AppApiException(500,
                                      _("The application has not been published. Please use it after publishing."))
        if application.type == ApplicationTypeChoices.SIMPLE:
            return self.open_simple(application)
        else:
            return self.open_work_flow(application)

    def open_work_flow(self, application):
        self.is_valid(raise_exception=True)
        application_id = self.data.get('application_id')
        chat_user_id = self.data.get("chat_user_id")
        chat_user_type = self.data.get("chat_user_type")
        debug = self.data.get("debug")
        chat_id = str(uuid.uuid7())
        ChatInfo(chat_id, chat_user_id, chat_user_type, [],
                 [],
                 application_id, debug).set_cache()
        return chat_id

    def open_simple(self, application):
        application_id = self.data.get('application_id')
        chat_user_id = self.data.get("chat_user_id")
        chat_user_type = self.data.get("chat_user_type")
        debug = self.data.get("debug")
        knowledge_id_list = [str(row.knowledge_id) for row in
                             QuerySet(ApplicationKnowledgeMapping).filter(
                                 application_id=application_id)]
        chat_id = str(uuid.uuid7())
        ChatInfo(chat_id, chat_user_id, chat_user_type, knowledge_id_list,
                 [str(document.id) for document in
                  QuerySet(Document).filter(
                      knowledge_id__in=knowledge_id_list,
                      is_active=False)],
                 application_id,
                 debug=debug).set_cache()
        return chat_id


class TextToSpeechSerializers(serializers.Serializer):
    application_id = serializers.UUIDField(required=True, label=_("Application ID"))

    def text_to_speech(self, instance):
        self.is_valid(raise_exception=True)
        application_id = self.data.get('application_id')
        application = QuerySet(Application).filter(id=application_id).first()
        return ApplicationOperateSerializer(
            data={'application_id': application_id,
                  'user_id': application.user_id}).text_to_speech(instance, False)


class SpeechToTextSerializers(serializers.Serializer):
    application_id = serializers.UUIDField(required=True, label=_("Application ID"))

    def speech_to_text(self, instance):
        self.is_valid(raise_exception=True)
        application_id = self.data.get('application_id')
        application = QuerySet(Application).filter(id=application_id).first()
        return ApplicationOperateSerializer(
            data={'application_id': application_id,
                  'user_id': application.user_id}).speech_to_text(instance, False)
