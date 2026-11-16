# coding=utf-8
from contextlib import contextmanager
from unittest.mock import patch

from django.test import SimpleTestCase
from django.urls import resolve

from chat.serializers.chat_record import HistoricalConversationRecordSerializer
from common.exception.app_exception import AppApiException

CHAT_ID = "0b1d5a02-6f5b-4d1e-9a4e-6a3c1a1a1a1a"
RECORD_ID = "0b1d5a02-6f5b-4d1e-9a4e-6a3c1a1a1a1c"
DATA = {
    "chat_id": CHAT_ID,
    "application_id": "0b1d5a02-6f5b-4d1e-9a4e-6a3c1a1a1a1b",
    "chat_user_id": "0b1d5a02-6f5b-4d1e-9a4e-6a3c1a1a1a1d",
}


@contextmanager
def patched_truncate(chat_exists=True):
    """隔离 DB：会话归属、记录查询、历史缓存与统计全部打桩，只测截断的编排。"""
    with (
        patch("chat.serializers.chat_record.QuerySet") as query_set,
        patch("chat.serializers.chat_record.ChatHistory") as chat_history,
        patch("chat.serializers.chat_record.ChatCountSerializer") as chat_count,
    ):
        query_set.return_value.filter.return_value.exists.return_value = chat_exists
        yield query_set, chat_history, chat_count


class ChatRecordTruncateTests(SimpleTestCase):
    def test_truncate_deletes_record_and_later_records(self):
        """按原记录的创建时间删除该记录及之后的记录，并让历史缓存失效、刷新会话统计。"""
        with patched_truncate() as (query_set, chat_history, chat_count):
            record = query_set.return_value.filter.return_value.first.return_value

            self.assertTrue(HistoricalConversationRecordSerializer(data=DATA).truncate(RECORD_ID))

            _ownership, lookup, delete_filter = query_set.return_value.filter.call_args_list
            self.assertEqual(lookup.kwargs["id"], RECORD_ID)
            self.assertEqual(str(lookup.kwargs["chat_id"]), CHAT_ID)
            self.assertEqual(str(delete_filter.kwargs["chat_id"]), CHAT_ID)
            self.assertEqual(delete_filter.kwargs["create_time__gte"], record.create_time)
            query_set.return_value.filter.return_value.delete.assert_called_once()
            chat_history.assert_called_once_with(CHAT_ID)
            chat_history.return_value.clear.assert_called_once()
            chat_count.return_value.update_chat.assert_called_once()

    def test_chat_must_belong_to_current_user(self):
        """会话不属于当前应用与对话用户时拒绝，不查询也不删除记录。"""
        with patched_truncate(chat_exists=False) as (query_set, chat_history, _chat_count):
            with self.assertRaises(AppApiException):
                HistoricalConversationRecordSerializer(data=DATA).truncate(RECORD_ID)

            ownership = query_set.return_value.filter.call_args
            self.assertEqual(str(ownership.kwargs["chat_user_id"]), DATA["chat_user_id"])
            self.assertEqual(str(ownership.kwargs["application_id"]), DATA["application_id"])
            query_set.return_value.filter.return_value.delete.assert_not_called()
            chat_history.assert_not_called()

    def test_record_must_belong_to_chat(self):
        """记录不存在或不属于该会话时拒绝，不删除、不清历史缓存。"""
        with patched_truncate() as (query_set, chat_history, chat_count):
            query_set.return_value.filter.return_value.first.return_value = None

            with self.assertRaises(AppApiException):
                HistoricalConversationRecordSerializer(data=DATA).truncate(RECORD_ID)

            query_set.return_value.filter.return_value.delete.assert_not_called()
            chat_history.assert_not_called()
            chat_count.assert_not_called()

    def test_truncate_routes(self):
        """对话端与调试端的截断路由均已注册，且不被分页路由抢先匹配。"""
        from application.views import DebugHistoricalConversation
        from chat.views.v3 import ChatRecordTruncateView

        chat_match = resolve(
            f"/chat/api/v3/application/{DATA['application_id']}/chat/{CHAT_ID}/chat_record/{RECORD_ID}/truncate"
        )
        self.assertIs(chat_match.func.view_class, ChatRecordTruncateView)
        debug_match = resolve(
            f"/admin/api/workspace/default/application/{DATA['application_id']}"
            f"/historical_conversation_record/{CHAT_ID}/{RECORD_ID}/truncate"
        )
        self.assertIs(debug_match.func.view_class, DebugHistoricalConversation.RecordTruncateView)
