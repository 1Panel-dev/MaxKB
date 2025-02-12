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


class Reasoning:
    def __init__(self, reasoning_content_start, reasoning_content_end):
        self.content = ""
        self.reasoning_content = ""
        self.all_content = ""
        self.reasoning_content_start_tag = reasoning_content_start
        self.reasoning_content_end_tag = reasoning_content_end
        self.reasoning_content_start_tag_len = len(
            reasoning_content_start) if reasoning_content_start is not None else 0
        self.reasoning_content_end_tag_len = len(reasoning_content_end) if reasoning_content_end is not None else 0
        self.reasoning_content_end_tag_prefix = reasoning_content_end[
            0] if self.reasoning_content_end_tag_len > 0 else ''
        self.reasoning_content_is_start = False
        self.reasoning_content_is_end = False
        self.reasoning_content_chunk = ""

    def get_end_reasoning_content(self):
        if not self.reasoning_content_is_start and not self.reasoning_content_is_end:
            r = {'content': self.all_content, 'reasoning_content': ''}
            self.reasoning_content_chunk = ""
            return r
        if self.reasoning_content_is_start and not self.reasoning_content_is_end:
            r = {'content': '', 'reasoning_content': self.reasoning_content_chunk}
            self.reasoning_content_chunk = ""
            return r
        return {'content': '', 'reasoning_content': ''}

    def get_reasoning_content(self, chunk):
        # 如果没有开始思考过程标签那么就全是结果
        if self.reasoning_content_start_tag is None or len(self.reasoning_content_start_tag) == 0:
            self.content += chunk.content
            return {'content': chunk.content, 'reasoning_content': ''}
        # 如果没有结束思考过程标签那么就全部是思考过程
        if self.reasoning_content_end_tag is None or len(self.reasoning_content_end_tag) == 0:
            return {'content': '', 'reasoning_content': chunk.content}
        self.all_content += chunk.content
        if not self.reasoning_content_is_start and len(self.all_content) >= self.reasoning_content_start_tag_len:
            if self.all_content.startswith(self.reasoning_content_start_tag):
                self.reasoning_content_is_start = True
                self.reasoning_content_chunk = self.all_content[self.reasoning_content_start_tag_len:]
            else:
                if not self.reasoning_content_is_end:
                    self.reasoning_content_is_end = True
                    self.content += self.all_content
                    return {'content': self.all_content, 'reasoning_content': ''}
        else:
            if self.reasoning_content_is_start:
                self.reasoning_content_chunk += chunk.content
        reasoning_content_end_tag_prefix_index = self.reasoning_content_chunk.find(
            self.reasoning_content_end_tag_prefix)
        if self.reasoning_content_is_end:
            self.content += chunk.content
            return {'content': chunk.content, 'reasoning_content': ''}
        # 是否包含结束
        if reasoning_content_end_tag_prefix_index > -1:
            if len(self.reasoning_content_chunk) - reasoning_content_end_tag_prefix_index >= self.reasoning_content_end_tag_len:
                reasoning_content_end_tag_index = self.reasoning_content_chunk.find(self.reasoning_content_end_tag)
                if reasoning_content_end_tag_index > -1:
                    reasoning_content_chunk = self.reasoning_content_chunk[0:reasoning_content_end_tag_index]
                    content_chunk = self.reasoning_content_chunk[
                                    reasoning_content_end_tag_index + self.reasoning_content_end_tag_len:]
                    self.reasoning_content += reasoning_content_chunk
                    self.content += content_chunk
                    self.reasoning_content_chunk = ""
                    self.reasoning_content_is_end = True
                    return {'content': content_chunk, 'reasoning_content': reasoning_content_chunk}
                else:
                    reasoning_content_chunk = self.reasoning_content_chunk[0:reasoning_content_end_tag_prefix_index + 1]
                    self.reasoning_content_chunk = self.reasoning_content_chunk.replace(reasoning_content_chunk, '')
                    self.reasoning_content += reasoning_content_chunk
                    return {'content': '', 'reasoning_content': reasoning_content_chunk}
            else:
                return {'content': '', 'reasoning_content': ''}

        else:
            if self.reasoning_content_is_end:
                self.content += chunk.content
                return {'content': chunk.content, 'reasoning_content': ''}
            else:
                # aaa
                result = {'content': '', 'reasoning_content': self.reasoning_content_chunk}
                self.reasoning_content += self.reasoning_content_chunk
                self.reasoning_content_chunk = ""
                return result


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


def to_response_simple(chat_id, chat_record_id, response: BaseMessage, workflow,
                       post_handler: WorkFlowPostHandler):
    answer = response.content
    post_handler.handler(chat_id, chat_record_id, answer, workflow)
    return result.success({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                           'content': answer, 'is_end': True})


def to_stream_response_simple(stream_event):
    r = StreamingHttpResponse(
        streaming_content=stream_event,
        content_type='text/event-stream;charset=utf-8',
        charset='utf-8')

    r['Cache-Control'] = 'no-cache'
    return r
