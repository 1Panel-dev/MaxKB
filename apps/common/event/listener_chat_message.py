# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： listener_manage.py
    @date：2023/10/20 14:01
    @desc:
"""

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

    @staticmethod
    @poxy
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

    def run(self):
        # 记录会话
        ListenerChatMessage.record_chat_message_signal.connect(self.record_chat_message)
