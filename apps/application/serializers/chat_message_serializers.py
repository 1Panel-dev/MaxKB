# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： chat_message_serializers.py
    @date：2023/11/14 13:51
    @desc:
"""
import json
import uuid
from typing import List

from django.db.models import QuerySet
from django.http import StreamingHttpResponse
from langchain.chat_models.base import BaseChatModel
from langchain.schema import HumanMessage
from rest_framework import serializers, status
from django.core.cache import cache
from common import event
from common.config.embedding_config import VectorStore, EmbeddingModel
from common.response import result
from dataset.models import Paragraph
from embedding.models import SourceType
from setting.models.model_management import Model

chat_cache = cache


class MessageManagement:
    @staticmethod
    def get_message(title: str, content: str, message: str):
        if content is None:
            return HumanMessage(content=message)
        return HumanMessage(content=(
            f'已知信息：{title}:{content} '
            '根据上述已知信息，请简洁和专业的来回答用户的问题。已知信息中的图片、链接地址和脚本语言请直接返回。如果无法从已知信息中得到答案，请说 “没有在知识库中查找到相关信息，建议咨询相关技术支持或参考官方文档进行操作” 或 “根据已知信息无法回答该问题，建议联系官方技术支持人员”，不允许在答案中添加编造成分，答案请使用中文。'
            f'问题是：{message}'))


class ChatMessage:
    def __init__(self, id: str, problem: str, title: str, paragraph: str, embedding_id: str, dataset_id: str,
                 document_id: str,
                 paragraph_id,
                 source_type: SourceType,
                 source_id: str,
                 answer: str,
                 message_tokens: int,
                 answer_token: int,
                 chat_model=None,
                 chat_message=None):
        self.id = id
        self.problem = problem
        self.title = title
        self.paragraph = paragraph
        self.embedding_id = embedding_id
        self.dataset_id = dataset_id
        self.document_id = document_id
        self.paragraph_id = paragraph_id
        self.source_type = source_type
        self.source_id = source_id
        self.answer = answer
        self.message_tokens = message_tokens
        self.answer_token = answer_token
        self.chat_model = chat_model
        self.chat_message = chat_message

    def get_chat_message(self):
        return MessageManagement.get_message(self.problem, self.paragraph, self.problem)


class ChatInfo:
    def __init__(self,
                 chat_id: str,
                 model: Model,
                 chat_model: BaseChatModel,
                 application_id: str | None,
                 dataset_id_list: List[str],
                 exclude_document_id_list: list[str],
                 dialogue_number: int):
        self.chat_id = chat_id
        self.application_id = application_id
        self.model = model
        self.chat_model = chat_model
        self.dataset_id_list = dataset_id_list
        self.exclude_document_id_list = exclude_document_id_list
        self.dialogue_number = dialogue_number
        self.chat_message_list: List[ChatMessage] = []

    def append_chat_message(self, chat_message: ChatMessage):
        self.chat_message_list.append(chat_message)
        if self.application_id is not None:
            # 插入数据库
            event.ListenerChatMessage.record_chat_message_signal.send(
                event.RecordChatMessageArgs(len(self.chat_message_list) - 1, self.chat_id, self.application_id,
                                            chat_message)
            )
            # 异步更新token
            event.ListenerChatMessage.update_chat_message_token_signal.send(chat_message)

    def get_context_message(self):
        start_index = len(self.chat_message_list) - self.dialogue_number
        return [self.chat_message_list[index].get_chat_message() for index in
                range(start_index if start_index > 0 else 0, len(self.chat_message_list))]


class ChatMessageSerializer(serializers.Serializer):
    chat_id = serializers.UUIDField(required=True)

    def chat(self, message):
        self.is_valid(raise_exception=True)
        chat_id = self.data.get('chat_id')
        chat_info: ChatInfo = chat_cache.get(chat_id)
        if chat_info is None:
            return result.Result(response_status=status.HTTP_404_NOT_FOUND, code=404, message="会话过期")

        chat_model = chat_info.chat_model
        vector = VectorStore.get_embedding_vector()
        # 向量库检索
        _value = vector.search(message, chat_info.dataset_id_list, chat_info.exclude_document_id_list,
                               [chat_message.embedding_id for chat_message in
                                (list(filter(lambda row: row.problem == message, chat_info.chat_message_list)))],
                               True,
                               EmbeddingModel.get_embedding_model())
        # 查询段落id详情
        paragraph = None
        if _value is not None:
            paragraph = QuerySet(Paragraph).get(id=_value.get('paragraph_id'))
            if paragraph is None:
                vector.delete_by_paragraph_id(_value.get('paragraph_id'))

        title, content = (None, None) if paragraph is None else (paragraph.title, paragraph.content)
        _id = str(uuid.uuid1())

        embedding_id, dataset_id, document_id, paragraph_id, source_type, source_id = (_value.get(
            'id'), _value.get(
            'dataset_id'), _value.get(
            'document_id'), _value.get(
            'paragraph_id'), _value.get(
            'source_type'), _value.get(
            'source_id')) if _value is not None else (None, None, None, None, None, None)

        if chat_model is None:
            def event_block_content(c: str):
                yield 'data: ' + json.dumps({'chat_id': chat_id, 'id': _id, 'operate': paragraph is not None,
                                             'is_end': True,
                                             'content': c if c is not None else '抱歉，根据已知信息无法回答这个问题，请重新描述您的问题或提供更多信息～'}) + "\n\n"
                chat_info.append_chat_message(
                    ChatMessage(_id, message, title, content, embedding_id, dataset_id, document_id,
                                paragraph_id,
                                source_type,
                                source_id,
                                c if c is not None else '抱歉，根据已知信息无法回答这个问题，请重新描述您的问题或提供更多信息～',
                                0,
                                0))
                # 重新设置缓存
                chat_cache.set(chat_id,
                               chat_info, timeout=60 * 30)

            r = StreamingHttpResponse(streaming_content=event_block_content(content),
                                      content_type='text/event-stream;charset=utf-8')

            r['Cache-Control'] = 'no-cache'
            return r
        # 获取上下文
        history_message = chat_info.get_context_message()

        # 构建会话请求问题
        chat_message = [*history_message, MessageManagement.get_message(title, content, message)]
        # 对话
        result_data = chat_model.stream(chat_message)

        def event_content(response):
            all_text = ''
            try:
                for chunk in response:
                    all_text += chunk.content
                    yield 'data: ' + json.dumps({'chat_id': chat_id, 'id': _id, 'operate': paragraph is not None,
                                                 'content': chunk.content, 'is_end': False}) + "\n\n"

                yield 'data: ' + json.dumps({'chat_id': chat_id, 'id': _id, 'operate': paragraph is not None,
                                             'content': '', 'is_end': True}) + "\n\n"
                chat_info.append_chat_message(
                    ChatMessage(_id, message, title, content, embedding_id, dataset_id, document_id,
                                paragraph_id,
                                source_type,
                                source_id, all_text,
                                0,
                                0,
                                chat_message=chat_message, chat_model=chat_model))
                # 重新设置缓存
                chat_cache.set(chat_id,
                               chat_info, timeout=60 * 30)
            except Exception as e:
                yield e

        r = StreamingHttpResponse(streaming_content=event_content(result_data),
                                  content_type='text/event-stream;charset=utf-8')

        r['Cache-Control'] = 'no-cache'
        return r
