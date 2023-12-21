# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： listener_manage.py
    @date：2023/10/20 14:01
    @desc:
"""
import logging

from blinker import signal
from django.db.models import QuerySet

from application.models import ChatRecord, Chat
from application.serializers.chat_message_serializers import ChatMessage
from common.event.common import poxy


class RecordChatMessageArgs:
    def __init__(self, index: int, chat_id: str, application_id: str, chat_message: ChatMessage):
        self.index = index
        self.chat_id = chat_id
        self.application_id = application_id
        self.chat_message = chat_message


class ListenerChatMessage:
    record_chat_message_signal = signal("record_chat_message")
    update_chat_message_token_signal = signal("update_chat_message_token")

    @staticmethod
    def record_chat_message(args: RecordChatMessageArgs):
        if not QuerySet(Chat).filter(id=args.chat_id).exists():
            Chat(id=args.chat_id, application_id=args.application_id, abstract=args.chat_message.problem).save()
        # 插入会话记录
        try:
            chat_record = ChatRecord(
                id=args.chat_message.id,
                chat_id=args.chat_id,
                dataset_id=args.chat_message.dataset_id,
                paragraph_id=args.chat_message.paragraph_id,
                source_id=args.chat_message.source_id,
                source_type=args.chat_message.source_type,
                problem_text=args.chat_message.problem,
                answer_text=args.chat_message.answer,
                index=args.index,
                message_tokens=args.chat_message.message_tokens,
                answer_tokens=args.chat_message.answer_token)
            chat_record.save()
        except Exception as e:
            print(e)

    @staticmethod
    @poxy
    def update_token(chat_message: ChatMessage):
        if chat_message.chat_model is not None:
            logging.getLogger("max_kb").info("开始更新token")
            message_token = chat_message.chat_model.get_num_tokens_from_messages(chat_message.chat_message)
            answer_token = chat_message.chat_model.get_num_tokens(chat_message.answer)
            # 修改token数量
            QuerySet(ChatRecord).filter(id=chat_message.id).update(
                **{'message_tokens': message_token, 'answer_tokens': answer_token})

    def run(self):
        # 记录会话
        ListenerChatMessage.record_chat_message_signal.connect(self.record_chat_message)
        ListenerChatMessage.update_chat_message_token_signal.connect(self.update_token)
