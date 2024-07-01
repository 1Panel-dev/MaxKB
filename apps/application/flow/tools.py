# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： utils.py
    @date：2024/6/6 15:15
    @desc:
"""
import json
from typing import Iterator

from django.http import StreamingHttpResponse
from langchain_core.messages import BaseMessageChunk, BaseMessage

from application.flow.i_step_node import WorkFlowPostHandler
from common.response import result


def event_content(chat_id, chat_record_id, response, workflow,
                  write_context,
                  post_handler: WorkFlowPostHandler):
    """
    用于处理流式输出
    @param chat_id:         会话id
    @param chat_record_id:  对话记录id
    @param response:        响应数据
    @param workflow:        工作流管理器
    @param write_context    写入节点上下文
    @param post_handler:    后置处理器
    """
    answer = ''
    try:
        for chunk in response:
            answer += chunk.content
            yield 'data: ' + json.dumps({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                                         'content': chunk.content, 'is_end': False}, ensure_ascii=False) + "\n\n"
        write_context(answer, 200)
        post_handler.handler(chat_id, chat_record_id, answer, workflow)
        yield 'data: ' + json.dumps({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                                     'content': '', 'is_end': True}, ensure_ascii=False) + "\n\n"
    except Exception as e:
        answer = str(e)
        write_context(answer, 500)
        post_handler.handler(chat_id, chat_record_id, answer, workflow)
        yield 'data: ' + json.dumps({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                                     'content': answer, 'is_end': True}, ensure_ascii=False) + "\n\n"


def to_stream_response(chat_id, chat_record_id, response: Iterator[BaseMessageChunk], workflow, write_context,
                       post_handler):
    """
    将结果转换为服务流输出
    @param chat_id:        会话id
    @param chat_record_id: 对话记录id
    @param response:       响应数据
    @param workflow:       工作流管理器
    @param write_context   写入节点上下文
    @param post_handler:   后置处理器
    @return: 响应
    """
    r = StreamingHttpResponse(
        streaming_content=event_content(chat_id, chat_record_id, response, workflow, write_context, post_handler),
        content_type='text/event-stream;charset=utf-8',
        charset='utf-8')

    r['Cache-Control'] = 'no-cache'
    return r


def to_response(chat_id, chat_record_id, response: BaseMessage, workflow, write_context,
                post_handler: WorkFlowPostHandler):
    """
    将结果转换为服务输出

    @param chat_id:        会话id
    @param chat_record_id: 对话记录id
    @param response:       响应数据
    @param workflow:       工作流管理器
    @param write_context   写入节点上下文
    @param post_handler:   后置处理器
    @return: 响应
    """
    answer = response.content
    write_context(answer)
    post_handler.handler(chat_id, chat_record_id, answer, workflow)
    return result.success({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                           'content': answer, 'is_end': True})
