# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_chat_step.py
    @date：2024/1/9 18:25
    @desc: 对话step Base实现
"""
import json
import time
import traceback
from typing import List

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.http import StreamingHttpResponse
from django.utils.translation import gettext as _
from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage
from langchain.schema.messages import HumanMessage, AIMessage
from langchain_core.messages import AIMessageChunk, SystemMessage
from rest_framework import status

from application.chat_pipeline.I_base_chat_pipeline import ParagraphPipelineModel
from application.chat_pipeline.pipeline_manage import PipelineManage
from application.chat_pipeline.step.chat_step.i_chat_step import IChatStep, PostResponseHandler
from application.flow.tools import Reasoning, mcp_response_generator
from application.models import ApplicationChatUserStats, ChatUserType, Application, ApplicationApiKey, \
    ApplicationAccessToken
from common.exception.app_exception import AppApiException
from common.utils.logger import maxkb_logger
from common.utils.rsa_util import rsa_long_decrypt
from common.utils.tool_code import ToolExecutor
from models_provider.tools import get_model_instance_by_model_workspace_id
from tools.models import Tool


def add_access_num(chat_user_id=None, chat_user_type=None, application_id=None):
    if [ChatUserType.ANONYMOUS_USER.value, ChatUserType.CHAT_USER.value].__contains__(
            chat_user_type) and application_id is not None:
        application_public_access_client = (QuerySet(ApplicationChatUserStats).filter(chat_user_id=chat_user_id,
                                                                                      chat_user_type=chat_user_type,
                                                                                      application_id=application_id)
                                            .first())
        if application_public_access_client is not None:
            application_public_access_client.access_num = application_public_access_client.access_num + 1
            application_public_access_client.intraday_access_num = application_public_access_client.intraday_access_num + 1
            application_public_access_client.save()


def write_context(step, manage, request_token, response_token, all_text):
    step.context['message_tokens'] = request_token
    step.context['answer_tokens'] = response_token
    current_time = time.time()
    step.context['answer_text'] = all_text
    step.context['run_time'] = current_time - step.context['start_time']
    manage.context['run_time'] = current_time - manage.context['start_time']
    manage.context['message_tokens'] = manage.context['message_tokens'] + request_token
    manage.context['answer_tokens'] = manage.context['answer_tokens'] + response_token


def event_content(response,
                  chat_id,
                  chat_record_id,
                  paragraph_list: List[ParagraphPipelineModel],
                  post_response_handler: PostResponseHandler,
                  manage,
                  step,
                  chat_model,
                  message_list: List[BaseMessage],
                  problem_text: str,
                  padding_problem_text: str = None,
                  chat_user_id=None, chat_user_type=None,
                  is_ai_chat: bool = None,
                  model_setting=None):
    if model_setting is None:
        model_setting = {}
    reasoning_content_enable = model_setting.get('reasoning_content_enable', False)
    reasoning_content_start = model_setting.get('reasoning_content_start', '<think>')
    reasoning_content_end = model_setting.get('reasoning_content_end', '</think>')
    reasoning = Reasoning(reasoning_content_start,
                          reasoning_content_end)
    all_text = ''
    reasoning_content = ''
    try:
        response_reasoning_content = False
        for chunk in response:
            reasoning_chunk = reasoning.get_reasoning_content(chunk)
            content_chunk = reasoning_chunk.get('content')
            if 'reasoning_content' in chunk.additional_kwargs:
                response_reasoning_content = True
                reasoning_content_chunk = chunk.additional_kwargs.get('reasoning_content', '')
            else:
                reasoning_content_chunk = reasoning_chunk.get('reasoning_content')
            content_chunk = reasoning._normalize_content(content_chunk)
            all_text += content_chunk
            if reasoning_content_chunk is None:
                reasoning_content_chunk = ''
            reasoning_content += reasoning_content_chunk
            yield manage.get_base_to_response().to_stream_chunk_response(chat_id, str(chat_record_id), 'ai-chat-node',
                                                                         [], content_chunk,
                                                                         False,
                                                                         0, 0, {'node_is_end': False,
                                                                                'view_type': 'many_view',
                                                                                'node_type': 'ai-chat-node',
                                                                                'real_node_id': 'ai-chat-node',
                                                                                'reasoning_content': reasoning_content_chunk if reasoning_content_enable else ''})
        reasoning_chunk = reasoning.get_end_reasoning_content()
        all_text += reasoning_chunk.get('content')
        reasoning_content_chunk = ""
        if not response_reasoning_content:
            reasoning_content_chunk = reasoning_chunk.get(
                'reasoning_content')
        yield manage.get_base_to_response().to_stream_chunk_response(chat_id, str(chat_record_id), 'ai-chat-node',
                                                                     [], reasoning_chunk.get('content'),
                                                                     False,
                                                                     0, 0, {'node_is_end': False,
                                                                            'view_type': 'many_view',
                                                                            'node_type': 'ai-chat-node',
                                                                            'real_node_id': 'ai-chat-node',
                                                                            'reasoning_content'
                                                                            : reasoning_content_chunk if reasoning_content_enable else ''})
        # 获取token
        if is_ai_chat:
            try:
                request_token = chat_model.get_num_tokens_from_messages(message_list)
                response_token = chat_model.get_num_tokens(all_text)
            except Exception as e:
                request_token = 0
                response_token = 0
        else:
            request_token = 0
            response_token = 0
        write_context(step, manage, request_token, response_token, all_text)
        post_response_handler.handler(chat_id, chat_record_id, paragraph_list, problem_text,
                                      all_text, manage, step, padding_problem_text,
                                      reasoning_content=reasoning_content if reasoning_content_enable else '')
        yield manage.get_base_to_response().to_stream_chunk_response(chat_id, str(chat_record_id), 'ai-chat-node',
                                                                     [], '', True,
                                                                     request_token, response_token,
                                                                     {'node_is_end': True, 'view_type': 'many_view',
                                                                      'node_type': 'ai-chat-node'})
        if not manage.debug:
            add_access_num(chat_user_id, chat_user_type, manage.context.get('application_id'))
    except Exception as e:
        maxkb_logger.error(f'{str(e)}:{traceback.format_exc()}')
        all_text = 'Exception:' + str(e)
        write_context(step, manage, 0, 0, all_text)
        post_response_handler.handler(chat_id, chat_record_id, paragraph_list, problem_text,
                                      all_text, manage, step, padding_problem_text, reasoning_content='')
        if not manage.debug:
            add_access_num(chat_user_id, chat_user_type, manage.context.get('application_id'))
        yield manage.get_base_to_response().to_stream_chunk_response(chat_id, str(chat_record_id), 'ai-chat-node',
                                                                     [], all_text,
                                                                     False,
                                                                     0, 0, {'node_is_end': False,
                                                                            'view_type': 'many_view',
                                                                            'node_type': 'ai-chat-node',
                                                                            'real_node_id': 'ai-chat-node',
                                                                            'reasoning_content': ''})


class BaseChatStep(IChatStep):
    def execute(self, message_list: List[BaseMessage],
                chat_id,
                problem_text,
                post_response_handler: PostResponseHandler,
                model_id: str = None,
                workspace_id: str = None,
                paragraph_list=None,
                manage: PipelineManage = None,
                padding_problem_text: str = None,
                stream: bool = True,
                chat_user_id=None, chat_user_type=None,
                no_references_setting=None,
                model_params_setting=None,
                model_setting=None,
                mcp_tool_ids=None,
                mcp_servers='',
                mcp_source="referencing",
                tool_ids=None,
                application_ids=None,
                mcp_output_enable=True,
                **kwargs):
        chat_model = get_model_instance_by_model_workspace_id(model_id, workspace_id,
                                                              **model_params_setting) if model_id is not None else None
        if stream:
            return self.execute_stream(message_list, chat_id, problem_text, post_response_handler, chat_model,
                                       paragraph_list,
                                       manage, padding_problem_text, chat_user_id, chat_user_type,
                                       no_references_setting,
                                       model_setting,
                                       mcp_tool_ids, mcp_servers, mcp_source, tool_ids,
                                       application_ids,
                                       mcp_output_enable)
        else:
            return self.execute_block(message_list, chat_id, problem_text, post_response_handler, chat_model,
                                      paragraph_list,
                                      manage, padding_problem_text, chat_user_id, chat_user_type, no_references_setting,
                                      model_setting,
                                      mcp_tool_ids, mcp_servers, mcp_source, tool_ids,
                                      application_ids,
                                      mcp_output_enable)

    def get_details(self, manage, **kwargs):
        return {
            'status': self.status,
            'err_message': self.err_message,
            'step_type': 'chat_step',
            'run_time': self.context.get('run_time') or 0,
            'model_id': str(manage.context['model_id']),
            'message_list': self.reset_message_list(self.context['step_args'].get('message_list'),
                                                    self.context['answer_text']),
            'message_tokens': self.context['message_tokens'],
            'answer_tokens': self.context['answer_tokens'],
            'cost': 0,
        }

    @staticmethod
    def reset_message_list(message_list: List[BaseMessage], answer_text):
        result = [{'role': 'user' if isinstance(message, HumanMessage) else (
            'system' if isinstance(message, SystemMessage) else 'ai'), 'content': message.content} for
                  message
                  in
                  message_list]
        result.append({'role': 'ai', 'content': answer_text})
        return result

    def _handle_mcp_request(self, mcp_source, mcp_servers, mcp_tool_ids, tool_ids,
                            application_ids, mcp_output_enable, chat_model, message_list):

        mcp_servers_config = {}

        # 迁移过来mcp_source是None
        if mcp_source is None:
            mcp_source = 'custom'
        # 兼容老数据
        if not mcp_tool_ids:
            mcp_tool_ids = []
        if mcp_source == 'custom' and mcp_servers and '"stdio"' not in mcp_servers:
            mcp_servers_config = json.loads(mcp_servers)
        elif mcp_tool_ids:
            mcp_tools = QuerySet(Tool).filter(id__in=mcp_tool_ids).values()
            for mcp_tool in mcp_tools:
                if mcp_tool and mcp_tool['is_active']:
                    mcp_servers_config = {**mcp_servers_config, **json.loads(mcp_tool['code'])}

        if tool_ids and len(tool_ids) > 0:  # 如果有工具ID，则将其转换为MCP
            self.context['tool_ids'] = tool_ids
            for tool_id in tool_ids:
                tool = QuerySet(Tool).filter(id=tool_id).first()
                if tool is None or tool.is_active is False:
                    continue
                executor = ToolExecutor()
                if tool.init_params is not None:
                    params = json.loads(rsa_long_decrypt(tool.init_params))
                else:
                    params = {}
                tool_config = executor.get_tool_mcp_config(tool.code, params, tool.name, tool.desc)

                mcp_servers_config[str(tool.id)] = tool_config

        if application_ids and len(application_ids) > 0:
            self.context['application_ids'] = application_ids
            for application_id in application_ids:
                app = QuerySet(Application).filter(id=application_id, is_publish=True).first()
                if app is None:
                    continue
                app_key = QuerySet(ApplicationApiKey).filter(application_id=application_id, is_active=True).first()
                if app_key is not None:
                    api_key = app_key.secret_key
                    application_access_token = QuerySet(ApplicationAccessToken).filter(
                        application_id=app_key.application_id
                    ).first()
                    if application_access_token is not None and application_access_token.authentication:
                        raise AppApiException(
                            500,
                            _('Agent 【{name}】 access token authentication is not supported for agent tool').format(
                                name=app.name)
                        )
                else:
                    raise AppApiException(
                        500,
                        _('Agent Key is required for agent tool 【{name}】').format(name=app.name)
                    )
                executor = ToolExecutor()
                app_config = executor.get_app_mcp_config(api_key)
                mcp_servers_config[app.name] = app_config

        if len(mcp_servers_config) > 0:
            return mcp_response_generator(chat_model, message_list, json.dumps(mcp_servers_config), mcp_output_enable)

        return None

    def get_stream_result(self, message_list: List[BaseMessage],
                          chat_model: BaseChatModel = None,
                          paragraph_list=None,
                          no_references_setting=None,
                          problem_text=None,
                          mcp_tool_ids=None,
                          mcp_servers='',
                          mcp_source="referencing",
                          tool_ids=None,
                          application_ids=None,
                          mcp_output_enable=True):
        if paragraph_list is None:
            paragraph_list = []
        directly_return_chunk_list = [AIMessageChunk(content=paragraph.content)
                                      for paragraph in paragraph_list if (
                                              paragraph.hit_handling_method == 'directly_return' and paragraph.similarity >= paragraph.directly_return_similarity)]
        if directly_return_chunk_list is not None and len(directly_return_chunk_list) > 0:
            return iter(directly_return_chunk_list), False
        elif len(paragraph_list) == 0 and no_references_setting.get(
                'status') == 'designated_answer':
            return iter(
                [AIMessageChunk(content=no_references_setting.get('value').replace('{question}', problem_text))]), False
        if chat_model is None:
            return iter([AIMessageChunk(
                _('Sorry, the AI model is not configured. Please go to the application to set up the AI model first.'))]), False
        else:
            # 处理 MCP 请求
            mcp_result = self._handle_mcp_request(
                mcp_source, mcp_servers, mcp_tool_ids, tool_ids,
                application_ids, mcp_output_enable, chat_model,
                message_list,
            )
            if mcp_result:
                return mcp_result, True
            return chat_model.stream(message_list), True

    def execute_stream(self, message_list: List[BaseMessage],
                       chat_id,
                       problem_text,
                       post_response_handler: PostResponseHandler,
                       chat_model: BaseChatModel = None,
                       paragraph_list=None,
                       manage: PipelineManage = None,
                       padding_problem_text: str = None,
                       chat_user_id=None, chat_user_type=None,
                       no_references_setting=None,
                       model_setting=None,
                       mcp_tool_ids=None,
                       mcp_servers='',
                       mcp_source="referencing",
                       tool_ids=None,
                       application_ids=None,
                       mcp_output_enable=True):
        chat_result, is_ai_chat = self.get_stream_result(message_list, chat_model, paragraph_list,
                                                         no_references_setting, problem_text, mcp_tool_ids,
                                                         mcp_servers, mcp_source, tool_ids,
                                                         application_ids,
                                                         mcp_output_enable)
        chat_record_id = self.context.get('step_args', {}).get('chat_record_id') if self.context.get('step_args',
                                                                                                     {}).get(
            'chat_record_id') else uuid.uuid7()
        r = StreamingHttpResponse(
            streaming_content=event_content(chat_result, chat_id, chat_record_id, paragraph_list,
                                            post_response_handler, manage, self, chat_model, message_list, problem_text,
                                            padding_problem_text, chat_user_id, chat_user_type, is_ai_chat,
                                            model_setting),
            content_type='text/event-stream;charset=utf-8')

        r['Cache-Control'] = 'no-cache'
        return r

    def get_block_result(self, message_list: List[BaseMessage],
                         chat_model: BaseChatModel = None,
                         paragraph_list=None,
                         no_references_setting=None,
                         problem_text=None,
                         mcp_tool_ids=None,
                         mcp_servers='',
                         mcp_source="referencing",
                         tool_ids=None,
                         application_ids=None,
                         mcp_output_enable=True
                         ):
        if paragraph_list is None:
            paragraph_list = []
        directly_return_chunk_list = [AIMessageChunk(content=paragraph.content)
                                      for paragraph in paragraph_list if (
                                              paragraph.hit_handling_method == 'directly_return' and paragraph.similarity >= paragraph.directly_return_similarity)]
        if directly_return_chunk_list is not None and len(directly_return_chunk_list) > 0:
            return directly_return_chunk_list[0], False
        elif len(paragraph_list) == 0 and no_references_setting.get(
                'status') == 'designated_answer':
            return AIMessage(no_references_setting.get('value').replace('{question}', problem_text)), False
        if chat_model is None:
            return AIMessage(
                _('Sorry, the AI model is not configured. Please go to the application to set up the AI model first.')), False
        else:
            # 处理 MCP 请求
            mcp_result = self._handle_mcp_request(
                mcp_source, mcp_servers, mcp_tool_ids, tool_ids,
                application_ids, mcp_output_enable,
                chat_model, message_list,
            )
            if mcp_result:
                return mcp_result, True
            return chat_model.invoke(message_list), True

    def execute_block(self, message_list: List[BaseMessage],
                      chat_id,
                      problem_text,
                      post_response_handler: PostResponseHandler,
                      chat_model: BaseChatModel = None,
                      paragraph_list=None,
                      manage: PipelineManage = None,
                      padding_problem_text: str = None,
                      chat_user_id=None, chat_user_type=None, no_references_setting=None,
                      model_setting=None,
                      mcp_tool_ids=None,
                      mcp_servers='',
                      mcp_source="referencing",
                      tool_ids=None,
                      application_ids=None,
                      mcp_output_enable=True):
        reasoning_content_enable = model_setting.get('reasoning_content_enable', False)
        reasoning_content_start = model_setting.get('reasoning_content_start', '<think>')
        reasoning_content_end = model_setting.get('reasoning_content_end', '</think>')
        reasoning = Reasoning(reasoning_content_start,
                              reasoning_content_end)
        chat_record_id = uuid.uuid7()
        # 调用模型
        try:
            chat_result, is_ai_chat = self.get_block_result(message_list, chat_model, paragraph_list,
                                                            no_references_setting, problem_text,
                                                            mcp_tool_ids, mcp_servers, mcp_source,
                                                            tool_ids, application_ids,
                                                            mcp_output_enable)
            if is_ai_chat:
                request_token = chat_model.get_num_tokens_from_messages(message_list)
                response_token = chat_model.get_num_tokens(chat_result.content)
            else:
                request_token = 0
                response_token = 0
            write_context(self, manage, request_token, response_token, chat_result.content)
            reasoning_result = reasoning.get_reasoning_content(chat_result)
            reasoning_result_end = reasoning.get_end_reasoning_content()
            content = reasoning_result.get('content') + reasoning_result_end.get('content')
            if 'reasoning_content' in chat_result.response_metadata:
                reasoning_content = (chat_result.response_metadata.get('reasoning_content', '') or '')
            else:
                reasoning_content = (reasoning_result.get('reasoning_content') or "") + (reasoning_result_end.get(
                    'reasoning_content') or "")
            post_response_handler.handler(chat_id, chat_record_id, paragraph_list, problem_text,
                                          content, manage, self, padding_problem_text,
                                          reasoning_content=reasoning_content)
            if not manage.debug:
                add_access_num(chat_user_id, chat_user_type, manage.context.get('application_id'))
            return manage.get_base_to_response().to_block_response(str(chat_id), str(chat_record_id),
                                                                   content, True,
                                                                   request_token, response_token,
                                                                   {
                                                                       'reasoning_content': reasoning_content if reasoning_content_enable else '',
                                                                       'answer_list': [{
                                                                           'content': content,
                                                                           'reasoning_content': reasoning_content if reasoning_content_enable else ''
                                                                       }]})
        except Exception as e:
            all_text = 'Exception:' + str(e)
            write_context(self, manage, 0, 0, all_text)
            post_response_handler.handler(chat_id, chat_record_id, paragraph_list, problem_text,
                                          all_text, manage, self, padding_problem_text, reasoning_content='')
            if not manage.debug:
                add_access_num(chat_user_id, chat_user_type, manage.context.get('application_id'))
            return manage.get_base_to_response().to_block_response(str(chat_id), str(chat_record_id), all_text, True, 0,
                                                                   0, _status=status.HTTP_500_INTERNAL_SERVER_ERROR)
