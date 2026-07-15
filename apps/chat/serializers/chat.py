# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： chat.py
    @date：2025/6/9 11:23
    @desc:
"""
import json
import os
from gettext import gettext
from typing import List, Dict

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from rest_framework import serializers

from application.chat_pipeline.pipeline_manage import PipelineManage
from application.chat_pipeline.step.chat_step.i_chat_step import PostResponseHandler
from application.chat_pipeline.step.chat_step.impl.base_chat_step import BaseChatStep
from application.chat_pipeline.step.generate_human_message_step.impl.base_generate_human_message_step import \
    BaseGenerateHumanMessageStep
from application.chat_pipeline.step.reset_problem_step.impl.base_reset_problem_step import BaseResetProblemStep
from application.chat_pipeline.step.search_dataset_step.impl.base_search_dataset_step import BaseSearchDatasetStep
from application.flow.common import Answer
from application.flow.tools import to_stream_response_simple
from application.workflow.common import WorkflowType, new_instance
from application.workflow.workflow_manage import WorkflowManage, CallBack
from application.workflow.nodes import get_start_node
from application.workflow.message.struct.text_content import TextContent
from application.workflow.message.struct.reasoning_content import ReasoningContent
from application.workflow.message.struct.tool_content import ToolContent
from application.workflow.message.struct.form_content import FormContent
from application.models import Application, ApplicationTypeChoices, \
    ChatUserType, ApplicationChatUserStats, ApplicationAccessToken, ChatRecord, Chat, ApplicationVersion
from application.serializers.application import ApplicationOperateSerializer
from application.serializers.common import ChatInfo
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.exception.app_exception import AppApiException, AppChatNumOutOfBoundsFailed, ChatException
from common.handle.base_to_response import BaseToResponse
from common.handle.impl.response.openai_to_response import OpenaiToResponse
from common.handle.impl.response.system_to_response import SystemToResponse
from common.utils.common import flat_map, get_file_content, is_valid_uuid
from knowledge.models import Document, Paragraph
from maxkb.conf import PROJECT_DIR
from models_provider.models import Model, Status
from models_provider.tools import get_model_instance_by_model_workspace_id
from system_manage.models.resource_mapping import ResourceMapping


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
                                     index=len(chat_info.chat_record_list) + 1,
                                     ip_address=chat_info.ip_address,
                                     source=chat_info.source
                                     )
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


SYSTEM_ROLE = get_file_content(os.path.join(PROJECT_DIR, "apps", "chat", 'template', 'generate_prompt_system'))


class PromptGenerateSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=False, label=_('Workspace ID'))
    model_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Model"))
    application_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Application"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        workspace_id = self.data.get('workspace_id')
        query_set = QuerySet(Application).filter(id=self.data.get('application_id'))
        if workspace_id:
            query_set = query_set.filter(workspace_id=workspace_id)
        application = query_set.first()
        if application is None:
            raise AppApiException(500, _('Application id does not exist'))
        return application

    def generate_prompt(self, instance: dict):
        application = self.is_valid(raise_exception=True)
        GeneratePromptSerializers(data=instance).is_valid(raise_exception=True)
        workspace_id = self.data.get('workspace_id')
        model_id = self.data.get('model_id')
        prompt = instance.get('prompt')
        messages = instance.get('messages')

        message = messages[-1]['content']
        q = prompt.replace("{userInput}", message)

        messages[-1]['content'] = q
        SUPPORTED_MODEL_TYPES = ["LLM", "IMAGE"]
        model_exist = QuerySet(Model).filter(
            id=model_id,
            model_type__in=SUPPORTED_MODEL_TYPES
        ).exists()
        if not model_exist:
            raise Exception(_("Model does not exists or is not an LLM model"))

        def process():
            model = get_model_instance_by_model_workspace_id(model_id=model_id, workspace_id=workspace_id,
                                                             **application.model_params_setting)
            try:
                for r in model.stream([SystemMessage(content=SYSTEM_ROLE),
                                       *[HumanMessage(content=m.get('content')) if m.get(
                                           'role') == 'user' else AIMessage(
                                           content=m.get('content')) for m in messages]]):
                    yield 'data: ' + json.dumps({'content': r.content}) + '\n\n'
            except Exception as e:
                yield 'data: ' + json.dumps({'error': str(e)}) + '\n\n'

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
    ip_address = serializers.CharField(required=False, label=_("IP Address"))
    source = serializers.JSONField(required=False, label=_("Source"))

    @staticmethod
    def get_message(instance):
        return instance.get('messages')[-1].get('content')

    @staticmethod
    def generate_chat(chat_id, application_id, message, chat_user_id, chat_user_type, ip_address, source):
        if chat_id is None:
            chat_id = str(uuid.uuid1())
            chat_info = ChatInfo(chat_id, chat_user_id, chat_user_type, ip_address, source, [], [],
                                 application_id)
            chat_info.set_cache()
        else:
            chat_info = ChatInfo.get_cache(chat_id)
            if chat_info is None:
                open_chat = ChatSerializers(data={
                    'chat_id': chat_id,
                    'chat_user_id': chat_user_id,
                    'chat_user_type': chat_user_type,
                    'application_id': application_id,
                    'ip_address': ip_address,
                    'source': source,
                })
                open_chat.is_valid(raise_exception=True)
                chat_info = open_chat.re_open_chat(chat_id)
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
        ip_address = self.data.get('ip_address')
        source = self.data.get('source')
        chat_id = self.generate_chat(chat_id, application_id, message, chat_user_id, chat_user_type, ip_address, source)
        return ChatSerializers(
            data={
                'chat_id': chat_id,
                'chat_user_id': chat_user_id,
                'chat_user_type': chat_user_type,
                'application_id': application_id,
                'ip_address': ip_address,
                'source': source,
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
    ip_address = serializers.CharField(required=False, label=_("IP Address"), allow_null=True, allow_blank=True)
    source = serializers.JSONField(required=False, label=_("Source"))

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
        ip_address = self.data.get('ip_address')
        source = self.data.get('source')
        form_data = instance.get("form_data")
        chat_record_id = instance.get('chat_record_id')
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
                                                     chat_user_id, chat_user_type, ip_address, source, stream,
                                                     form_data)
        if chat_record_id:
            params['chat_record_id'] = chat_record_id
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
                if not is_valid_uuid(chat_record_id):
                    raise ChatException(500, _("Conversation record does not exist"))
        chat_record = QuerySet(ChatRecord).filter(id=chat_record_id).first()
        return chat_record

    def chat_work_flow(self, chat_info: ChatInfo, instance: dict, base_to_response):
        import queue

        message = instance.get('message')
        re_chat = instance.get('re_chat')
        stream = instance.get('stream')
        chat_user_id = self.data.get("chat_user_id")
        chat_user_type = self.data.get('chat_user_type')
        ip_address = self.data.get('ip_address')
        source = self.data.get('source')
        form_data = instance.get('form_data')
        image_list = instance.get('image_list')
        video_list = instance.get('video_list')
        document_list = instance.get('document_list')
        audio_list = instance.get('audio_list')
        other_list = instance.get('other_list')
        workspace_id = chat_info.application.workspace_id
        chat_record_id = instance.get('chat_record_id')
        position = instance.get('position')
        chunk_id = instance.get('chunk_id')
        debug = self.data.get('debug', False)
        history_chat_record = chat_info.chat_record_list
        if chat_record_id is not None:
            chat_record = self.get_chat_record(chat_info, chat_record_id)
            if chat_record:
                history_chat_record = [r for r in chat_info.chat_record_list if str(r.id) != chat_record_id]

        work_flow = chat_info.application.work_flow
        workflow = new_instance(work_flow, WorkflowType.APPLICATION)

        chat_record_id_str = str(uuid.uuid7()) if chat_record_id is None else str(chat_record_id)

        parameters = {
            'history_chat_record': history_chat_record,
            'question': message,
            'chat_id': chat_info.chat_id,
            'chat_record_id': chat_record_id_str,
            'stream': stream,
            're_chat': re_chat,
            'chat_user_id': chat_user_id,
            'chat_user_type': chat_user_type,
            'ip_address': ip_address,
            'source': source,
            'workspace_id': workspace_id,
            'debug': debug,
            'chat_user': chat_info.get_chat_user(),
            'chat_user_group': chat_info.get_chat_user_group(),
            'application_id': str(chat_info.application_id),
            'form_data': form_data or {},
            'position': position,
            'chunk_id': chunk_id,
            'image_list': image_list or [],
            'document_list': document_list or [],
            'audio_list': audio_list or [],
            'video_list': video_list or [],
            'other_list': other_list or [],
        }

        result_queue = queue.Queue()
        answer_text = ''
        reasoning_text = ''

        def on_next(wf_manage, content):
            nonlocal answer_text, reasoning_text
            if isinstance(content, TextContent):
                answer_text += content.content
                result_queue.put(('chunk', {
                    'content': [{
                        'id': content.id,
                        'type': 'TEXT',
                        'content': content.content,
                    }]
                }))
            elif isinstance(content, ReasoningContent):
                reasoning_text += content.content
                result_queue.put(('chunk', {
                    'content': [{
                        'id': content.id,
                        'type': 'REASONING',
                        'content': content.content,
                        'status': content.status.value if content.status else None,
                    }]
                }))
            elif isinstance(content, ToolContent):
                result_queue.put(('chunk', {
                    'content': [{
                        'id': content.id,
                        'type': 'TOOL',
                        'content': content.content,
                        'arguments': content.arguments,
                        'result': content.result,
                        'status': content.status.value if content.status else None,
                    }]
                }))
            elif isinstance(content, FormContent):
                def position_to_dict(pos):
                    if pos is None:
                        return None
                    return {
                        'id': pos.id,
                        'index': pos.index,
                        'children': position_to_dict(pos.children)
                    }

                result_queue.put(('chunk', {
                    'content': [{
                        'id': content.id,
                        'type': 'FORM',
                        'form_field_list': content.form_field_list,
                        'form_content_format': content.form_content_format,
                        'is_submit': content.is_submit,
                        'form_data': content.form_data,
                        'status': content.status.value if content.status else None,
                        'position': position_to_dict(content.position),
                        'chat_record_id': chat_record_id_str,
                    }]
                }))

        def on_complete(wf_manage, error):
            if error:
                result_queue.put(('error', error))
            else:
                self._save_chat_record(chat_info, chat_info.chat_id, chat_record_id_str,
                                       message, answer_text, reasoning_text, wf_manage)
            result_queue.put(('done', None))

        call_back = CallBack(on_next, on_complete)

        def get_start_node_fn(wf, wm):
            return get_start_node(wf, wm, WorkflowType.APPLICATION, position)

        # 判断是否是 Form 提交（有 position 和 chat_record_id）
        if position and chat_record_id:
            # 从历史 context 恢复
            work_flow_manage = WorkflowManage.from_context(
                chat_record_id=chat_record_id,
                workflow=workflow,
                parameters=parameters,
                workflow_type=WorkflowType.APPLICATION,
                call_back=call_back,
                get_start_node=get_start_node_fn
            )
            if work_flow_manage is None:
                # 恢复失败，回退到正常流程
                work_flow_manage = WorkflowManage(workflow, parameters, WorkflowType.APPLICATION,
                                                  call_back, get_start_node_fn)
        else:
            # 正常创建新的 WorkflowManage
            work_flow_manage = WorkflowManage(workflow, parameters, WorkflowType.APPLICATION,
                                              call_back, get_start_node_fn)

        work_flow_manage.start_node.workflow_manage = work_flow_manage

        chat_info.set_chat(message)

        if stream:
            def generate():
                work_flow_manage.run()
                while True:
                    msg_type, data = result_queue.get()
                    if msg_type == 'done':
                        yield 'data: [DONE]\n\n'
                        break
                    if msg_type == 'error':
                        yield 'data: ' + json.dumps({
                            'chat_id': str(chat_info.chat_id),
                            'chat_record_id': chat_record_id_str,
                            'content': [{'type': 'FAILURE', 'content': str(data)}]
                        }, ensure_ascii=False) + '\n\n'
                        yield 'data: [DONE]\n\n'
                        break
                    if msg_type == 'chunk':
                        data['chat_id'] = str(chat_info.chat_id)
                        data['chat_record_id'] = chat_record_id_str
                        yield 'data: ' + json.dumps(data, ensure_ascii=False) + '\n\n'

            return to_stream_response_simple(generate())
        else:
            work_flow_manage.run()
            while True:
                msg_type, data = result_queue.get()
                if msg_type == 'done':
                    break
                if msg_type == 'error':
                    raise data
            return base_to_response.to_block_response(
                chat_info.chat_id, chat_record_id_str, answer_text, True, 0, 0)

    def _save_chat_record(self, chat_info, chat_id, chat_record_id, question, answer,
                          reasoning_content, wf_manage):
        context = wf_manage.context
        message_tokens = sum(
            v.get('message_tokens', 0) for v in context.values() if isinstance(v, dict) and 'message_tokens' in v)
        answer_tokens = sum(
            v.get('answer_tokens', 0) for v in context.values() if isinstance(v, dict) and 'answer_tokens' in v)

        answer_text_list = [[Answer(answer, 'ai-chat-node', 'ai-chat-node', 'ai-chat-node', {},
                                    'ai-chat-node', reasoning_content).to_dict()]]

        chat_record = ChatRecord(
            id=chat_record_id,
            chat_id=chat_id,
            problem_text=question,
            answer_text=answer,
            details={},
            message_tokens=message_tokens,
            answer_tokens=answer_tokens,
            answer_text_list=answer_text_list,
            run_time=0,
            index=len(chat_info.chat_record_list) + 1,
            ip_address=chat_info.ip_address,
            source=chat_info.source,
            workflow_context=dict(context) if context else None
        )
        chat_info.append_chat_record(chat_record)
        chat_info.set_cache()

    def is_valid_chat_user(self):
        chat_user_id = self.data.get('chat_user_id')
        application_id = self.data.get('application_id')
        chat_user_type = self.data.get('chat_user_type')
        is_auth_chat_user = DatabaseModelManage.get_model("is_auth_chat_user")
        application_access_token = QuerySet(ApplicationAccessToken).filter(application_id=application_id).first()
        if application_access_token and application_access_token.authentication and application_access_token.authentication_value.get(
                'type') == 'login':
            if chat_user_type == ChatUserType.ANONYMOUS_USER.value:
                raise ChatException(500, _("The chat user is not authorized."))
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
        if not self.data.get('debug'):
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
        knowledge_id_list = [str(row.target_id) for row in
                             QuerySet(ResourceMapping).filter(source_id=str(application.id),
                                                              source_type='APPLICATION',
                                                              target_type='KNOWLEDGE')]

        # 需要排除的文档
        exclude_document_id_list = [str(document.id) for document in
                                    QuerySet(Document).filter(
                                        knowledge_id__in=knowledge_id_list,
                                        is_active=False)]
        chat_info = ChatInfo(chat_id, self.data.get('chat_user_id'), self.data.get('chat_user_type'),
                             self.data.get('ip_address'),
                             self.data.get('source'), knowledge_id_list,
                             exclude_document_id_list, application.id)
        chat_record_list = list(QuerySet(ChatRecord).filter(chat_id=chat_id).order_by('-create_time')[0:5])
        chat_record_list.sort(key=lambda r: r.create_time)
        for chat_record in chat_record_list:
            chat_info.chat_record_list.append(chat_record)
        return chat_info

    def re_open_chat_work_flow(self, chat_id, application):
        chat_info = ChatInfo(chat_id, self.data.get('chat_user_id'), self.data.get('chat_user_type'),
                             self.data.get('ip_address'),
                             self.data.get('source'), [], [],
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
    ip_address = serializers.CharField(required=False, label=_("IP Address"))
    source = serializers.JSONField(required=False, label=_("Source"))

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
        ip_address = self.data.get("ip_address")
        source = self.data.get("source")
        debug = self.data.get("debug")
        chat_id = str(uuid.uuid7())
        ChatInfo(chat_id, chat_user_id, chat_user_type, ip_address, source, [],
                 [],
                 application_id, debug).set_cache()
        return chat_id

    def open_simple(self, application):
        application_id = self.data.get('application_id')
        chat_user_id = self.data.get("chat_user_id")
        chat_user_type = self.data.get("chat_user_type")
        ip_address = self.data.get("ip_address")
        source = self.data.get("source")
        debug = self.data.get("debug")
        knowledge_id_list = [str(row.target_id) for row in
                             QuerySet(ResourceMapping).filter(source_id=str(application_id),
                                                              source_type='APPLICATION',
                                                              target_type='KNOWLEDGE')]

        chat_id = str(uuid.uuid7())
        ChatInfo(chat_id, chat_user_id, chat_user_type, ip_address, source, knowledge_id_list,
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
