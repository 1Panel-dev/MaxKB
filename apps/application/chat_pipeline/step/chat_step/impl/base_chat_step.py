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

from django.http import StreamingHttpResponse
from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage
from langchain.schema.messages import BaseMessageChunk, HumanMessage

from application.chat_pipeline.I_base_chat_pipeline import ParagraphPipelineModel
from application.chat_pipeline.pipeline_manage import PiplineManage
from application.chat_pipeline.step.chat_step.i_chat_step import IChatStep, PostResponseHandler


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
                  padding_problem_text: str = None):
    all_text = ''
    try:
        for chunk in response:
            all_text += chunk.content
            yield 'data: ' + json.dumps({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                                         'content': chunk.content, 'is_end': False}) + "\n\n"

        # 获取token
        request_token = chat_model.get_num_tokens_from_messages(message_list)
        response_token = chat_model.get_num_tokens(all_text)
        step.context['message_tokens'] = request_token
        step.context['answer_tokens'] = response_token
        current_time = time.time()
        step.context['answer_text'] = all_text
        step.context['run_time'] = current_time - step.context['start_time']
        manage.context['run_time'] = current_time - manage.context['start_time']
        manage.context['message_tokens'] = manage.context['message_tokens'] + request_token
        manage.context['answer_tokens'] = manage.context['answer_tokens'] + response_token
        post_response_handler.handler(chat_id, chat_record_id, paragraph_list, problem_text,
                                      all_text, manage, step, padding_problem_text)
        yield 'data: ' + json.dumps({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                                     'content': '', 'is_end': True}) + "\n\n"
    except Exception as e:
        logging.getLogger("max_kb_error").error(f'{str(e)}:{traceback.format_exc()}')
        yield 'data: ' + json.dumps({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                                     'content': '异常' + str(e), 'is_end': True}) + "\n\n"


class BaseChatStep(IChatStep):
    def execute(self, message_list: List[BaseMessage],
                chat_id,
                problem_text,
                post_response_handler: PostResponseHandler,
                chat_model: BaseChatModel = None,
                paragraph_list=None,
                manage: PiplineManage = None,
                padding_problem_text: str = None,
                **kwargs):
        # 调用模型
        if chat_model is None:
            chat_result = iter(
                [BaseMessageChunk(content=paragraph.title + "\n" + paragraph.content) for paragraph in paragraph_list])
        else:
            chat_result = chat_model.stream(message_list)

        chat_record_id = uuid.uuid1()
        r = StreamingHttpResponse(
            streaming_content=event_content(chat_result, chat_id, chat_record_id, paragraph_list,
                                            post_response_handler, manage, self, chat_model, message_list, problem_text,
                                            padding_problem_text),
            content_type='text/event-stream;charset=utf-8')

        r['Cache-Control'] = 'no-cache'
        return r

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
