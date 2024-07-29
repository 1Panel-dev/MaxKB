# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_chat_step.py
    @date：2024/1/9 18:25
    @desc: 对话step Base实现
"""
import json
import logging
import time
import traceback
import uuid
from typing import List

from django.db.models import QuerySet
from django.http import StreamingHttpResponse
from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage
from langchain.schema.messages import HumanMessage, AIMessage
from langchain_core.messages import AIMessageChunk

from application.chat_pipeline.I_base_chat_pipeline import ParagraphPipelineModel
from application.chat_pipeline.pipeline_manage import PipelineManage
from application.chat_pipeline.step.chat_step.i_chat_step import IChatStep, PostResponseHandler
from application.models.api_key_model import ApplicationPublicAccessClient
from common.constants.authentication_type import AuthenticationType
from common.response import result
from setting.models_provider.tools import get_model_instance_by_model_user_id


def add_access_num(client_id=None, client_type=None):
    if client_type == AuthenticationType.APPLICATION_ACCESS_TOKEN.value:
        application_public_access_client = QuerySet(ApplicationPublicAccessClient).filter(id=client_id).first()
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
                  client_id=None, client_type=None,
                  is_ai_chat: bool = None):
    all_text = ''
    try:
        for chunk in response:
            all_text += chunk.content
            yield 'data: ' + json.dumps({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                                         'content': chunk.content, 'is_end': False}) + "\n\n"

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
                                      all_text, manage, step, padding_problem_text, client_id)
        yield 'data: ' + json.dumps({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                                     'content': '', 'is_end': True}) + "\n\n"
        add_access_num(client_id, client_type)
    except Exception as e:
        logging.getLogger("max_kb_error").error(f'{str(e)}:{traceback.format_exc()}')
        all_text = '异常' + str(e)
        write_context(step, manage, 0, 0, all_text)
        post_response_handler.handler(chat_id, chat_record_id, paragraph_list, problem_text,
                                      all_text, manage, step, padding_problem_text, client_id)
        add_access_num(client_id, client_type)
        yield 'data: ' + json.dumps({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                                     'content': all_text, 'is_end': True}) + "\n\n"


class BaseChatStep(IChatStep):
    def execute(self, message_list: List[BaseMessage],
                chat_id,
                problem_text,
                post_response_handler: PostResponseHandler,
                model_id: str = None,
                user_id: str = None,
                paragraph_list=None,
                manage: PipelineManage = None,
                padding_problem_text: str = None,
                stream: bool = True,
                client_id=None, client_type=None,
                no_references_setting=None,
                **kwargs):
        chat_model = get_model_instance_by_model_user_id(model_id, user_id) if model_id is not None else None
        if stream:
            return self.execute_stream(message_list, chat_id, problem_text, post_response_handler, chat_model,
                                       paragraph_list,
                                       manage, padding_problem_text, client_id, client_type, no_references_setting)
        else:
            return self.execute_block(message_list, chat_id, problem_text, post_response_handler, chat_model,
                                      paragraph_list,
                                      manage, padding_problem_text, client_id, client_type, no_references_setting)

    def get_details(self, manage, **kwargs):
        return {
            'step_type': 'chat_step',
            'run_time': self.context['run_time'],
            'model_id': str(manage.context['model_id']),
            'message_list': self.reset_message_list(self.context['step_args'].get('message_list'),
                                                    self.context['answer_text']),
            'message_tokens': self.context['message_tokens'],
            'answer_tokens': self.context['answer_tokens'],
            'cost': 0,
        }

    @staticmethod
    def reset_message_list(message_list: List[BaseMessage], answer_text):
        result = [{'role': 'user' if isinstance(message, HumanMessage) else 'ai', 'content': message.content} for
                  message
                  in
                  message_list]
        result.append({'role': 'ai', 'content': answer_text})
        return result

    @staticmethod
    def get_stream_result(message_list: List[BaseMessage],
                          chat_model: BaseChatModel = None,
                          paragraph_list=None,
                          no_references_setting=None,
                          problem_text=None):
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
            return iter([AIMessageChunk('抱歉，没有配置 AI 模型，无法优化引用分段，请先去应用中设置 AI 模型。')]), False
        else:
            return chat_model.stream(message_list), True

    def execute_stream(self, message_list: List[BaseMessage],
                       chat_id,
                       problem_text,
                       post_response_handler: PostResponseHandler,
                       chat_model: BaseChatModel = None,
                       paragraph_list=None,
                       manage: PipelineManage = None,
                       padding_problem_text: str = None,
                       client_id=None, client_type=None,
                       no_references_setting=None):
        chat_result, is_ai_chat = self.get_stream_result(message_list, chat_model, paragraph_list,
                                                         no_references_setting, problem_text)
        chat_record_id = uuid.uuid1()
        r = StreamingHttpResponse(
            streaming_content=event_content(chat_result, chat_id, chat_record_id, paragraph_list,
                                            post_response_handler, manage, self, chat_model, message_list, problem_text,
                                            padding_problem_text, client_id, client_type, is_ai_chat),
            content_type='text/event-stream;charset=utf-8')

        r['Cache-Control'] = 'no-cache'
        return r

    @staticmethod
    def get_block_result(message_list: List[BaseMessage],
                         chat_model: BaseChatModel = None,
                         paragraph_list=None,
                         no_references_setting=None,
                         problem_text=None):
        if paragraph_list is None:
            paragraph_list = []

        directly_return_chunk_list = [AIMessage(content=paragraph.content)
                                      for paragraph in paragraph_list if
                                      paragraph.hit_handling_method == 'directly_return']
        if directly_return_chunk_list is not None and len(directly_return_chunk_list) > 0:
            return directly_return_chunk_list[0], False
        elif len(paragraph_list) == 0 and no_references_setting.get(
                'status') == 'designated_answer':
            return AIMessage(no_references_setting.get('value').replace('{question}', problem_text)), False
        if chat_model is None:
            return AIMessage('抱歉，没有配置 AI 模型，无法优化引用分段，请先去应用中设置 AI 模型。'), False
        else:
            return chat_model.invoke(message_list), True

    def execute_block(self, message_list: List[BaseMessage],
                      chat_id,
                      problem_text,
                      post_response_handler: PostResponseHandler,
                      chat_model: BaseChatModel = None,
                      paragraph_list=None,
                      manage: PipelineManage = None,
                      padding_problem_text: str = None,
                      client_id=None, client_type=None, no_references_setting=None):
        chat_record_id = uuid.uuid1()
        # 调用模型
        try:
            chat_result, is_ai_chat = self.get_block_result(message_list, chat_model, paragraph_list,
                                                            no_references_setting, problem_text)
            if is_ai_chat:
                request_token = chat_model.get_num_tokens_from_messages(message_list)
                response_token = chat_model.get_num_tokens(chat_result.content)
            else:
                request_token = 0
                response_token = 0
            write_context(self, manage, request_token, response_token, chat_result.content)
            post_response_handler.handler(chat_id, chat_record_id, paragraph_list, problem_text,
                                          chat_result.content, manage, self, padding_problem_text, client_id)
            add_access_num(client_id, client_type)
            return result.success({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                                   'content': chat_result.content, 'is_end': True})
        except Exception as e:
            all_text = '异常' + str(e)
            write_context(self, manage, 0, 0, all_text)
            post_response_handler.handler(chat_id, chat_record_id, paragraph_list, problem_text,
                                          all_text, manage, self, padding_problem_text, client_id)
            add_access_num(client_id, client_type)
            return result.success({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                                   'content': all_text, 'is_end': True})
