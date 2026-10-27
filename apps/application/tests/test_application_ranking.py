# coding=utf-8
"""应用概览用户排行（分页 / 汇总 / 导出）测试。"""

import io

from django.test import TestCase
from django.utils import timezone
from openpyxl import load_workbook

from application.models import Application, ApplicationFolder, Chat, ChatRecord
from application.serializers.application_stats import ApplicationStatisticsSerializer
from users.models import User


def make_user(username):
    return User.objects.create(
        username=username,
        nick_name=username,
        password="x",
        role="USER",
        source="LOCAL",
    )


class ApplicationRankingSerializerTests(TestCase):
    def setUp(self):
        today = timezone.localdate()
        self.today_str = today.strftime("%Y-%m-%d")
        self.user = make_user("owner")
        folder = ApplicationFolder.objects.create(
            id="default",
            name="默认分组",
            workspace_id="default",
            user=self.user,
        )
        self.application = Application.objects.create(
            name="测试应用",
            workspace_id="default",
            folder=folder,
            user=self.user,
            model_setting={"prompt": "hello"},
            model_params_setting={},
            knowledge_setting={},
            icon="./favicon.ico",
            work_flow={},
        )
        self.serializer_data = {
            "application_id": str(self.application.id),
            "workspace_id": "default",
            "start_time": self.today_str,
            "end_time": self.today_str,
        }

    @staticmethod
    def make_chat(application, chat_user_id, username, create_time=None):
        chat = Chat.objects.create(
            application=application,
            abstract="",
            chat_user_id=chat_user_id,
            chat_user_type="ANONYMOUS_USER",
            asker={"username": username},
        )
        if create_time is not None:
            Chat.objects.filter(id=chat.id).update(create_time=create_time)
        return chat

    @staticmethod
    def make_record(chat, message_tokens, answer_tokens, create_time=None):
        record = ChatRecord.objects.create(
            chat=chat,
            problem_text="问题",
            answer_text="答案",
            message_tokens=message_tokens,
            answer_tokens=answer_tokens,
            index=1,
        )
        if create_time is not None:
            ChatRecord.objects.filter(id=record.id).update(create_time=create_time)
        return record

    def test_user_tokens_ranking_order_and_pagination(self):
        # u1: 30 tokens, u2: 50 tokens, u3: 40 tokens
        c1 = self.make_chat(self.application, "u1", "alice")
        self.make_record(c1, 10, 20)
        c2 = self.make_chat(self.application, "u2", "bob")
        self.make_record(c2, 30, 20)
        c3 = self.make_chat(self.application, "u3", "carol")
        self.make_record(c3, 20, 20)

        page = ApplicationStatisticsSerializer(data=self.serializer_data).get_ranking_statistics("userTokens", 1, 2)
        self.assertEqual(page.total, 3)
        self.assertEqual(page.size, 2)
        self.assertEqual(page.current, 1)
        self.assertEqual(len(page.records), 2)
        # 按 total_tokens 降序
        self.assertEqual(page.records[0]["chat_user_id"], "u2")
        self.assertEqual(page.records[1]["chat_user_id"], "u3")
        self.assertEqual(page.records[0]["asker"]["username"], "bob")
        self.assertEqual(page.records[0]["total_tokens"], 50)
        self.assertEqual(page.records[0]["chat_record_count"], 1)

        page2 = ApplicationStatisticsSerializer(data=self.serializer_data).get_ranking_statistics("userTokens", 2, 2)
        self.assertEqual(len(page2.records), 1)
        self.assertEqual(page2.records[0]["chat_user_id"], "u1")

    def test_questions_ranking_order(self):
        c1 = self.make_chat(self.application, "u1", "alice")
        self.make_record(c1, 1, 1)
        self.make_record(c1, 1, 1)
        c2 = self.make_chat(self.application, "u2", "bob")
        self.make_record(c2, 1, 1)

        page = ApplicationStatisticsSerializer(data=self.serializer_data).get_ranking_statistics("questions", 1, 10)
        self.assertEqual(page.total, 2)
        # 按对话次数降序
        self.assertEqual(page.records[0]["chat_user_id"], "u1")
        self.assertEqual(page.records[0]["chat_record_count"], 2)

    def test_ranking_name_search(self):
        c1 = self.make_chat(self.application, "u1", "alice")
        self.make_record(c1, 10, 0)
        c2 = self.make_chat(self.application, "u2", "bob")
        self.make_record(c2, 5, 0)

        data = {**self.serializer_data, "name": "ali"}
        page = ApplicationStatisticsSerializer(data=data).get_ranking_statistics("userTokens", 1, 10)
        self.assertEqual(page.total, 1)
        self.assertEqual(page.records[0]["chat_user_id"], "u1")

    def test_aggregations(self):
        c1 = self.make_chat(self.application, "u1", "alice")
        self.make_record(c1, 10, 20)
        self.make_record(c1, 5, 5)
        serializer = ApplicationStatisticsSerializer(data=self.serializer_data)
        self.assertEqual(serializer.get_tokens_aggregation(), 40)
        self.assertEqual(serializer.get_chat_record_aggregation(), 2)

    def test_export(self):
        c1 = self.make_chat(self.application, "u1", "alice")
        self.make_record(c1, 10, 20)
        c2 = self.make_chat(self.application, "u2", "bob")
        self.make_record(c2, 5, 5)
        response = ApplicationStatisticsSerializer(data=self.serializer_data).export_ranking_statistics("userTokens")
        self.assertEqual(response.status_code, 200)
        self.assertIn("spreadsheet", response["Content-Type"])
        # 导出内容为 xlsx（zip 魔数）
        raw = b"".join(response.streaming_content) if response.streaming else response.content
        self.assertEqual(raw[:2], b"PK")

    def _workbook_rows(self, kind):
        serializer = ApplicationStatisticsSerializer(data=self.serializer_data)
        response = serializer.export_ranking_statistics(kind)
        raw = b"".join(response.streaming_content) if response.streaming else response.content
        workbook = load_workbook(io.BytesIO(raw))
        return workbook.active

    def test_export_user_tokens_cells(self):
        c1 = self.make_chat(self.application, "u1", "alice")
        self.make_record(c1, 30, 0)  # 30 tokens
        c2 = self.make_chat(self.application, "u2", "bob")
        self.make_record(c2, 5, 5)  # 10 tokens
        ws = self._workbook_rows("userTokens")
        # 表头 + 2 行
        self.assertEqual(ws.max_row, 3)
        self.assertEqual(ws.cell(2, 2).value, "bob")  # 40 tokens -> 第一
        self.assertEqual(ws.cell(2, 3).value, 40)
        self.assertEqual(ws.cell(3, 2).value, "alice")
        self.assertEqual(ws.cell(3, 3).value, 30)
        # 占比 = 该用户 tokens / 总 tokens
        self.assertAlmostEqual(ws.cell(2, 4).value, 40 / 70)
        self.assertAlmostEqual(ws.cell(3, 4).value, 30 / 70)

    def test_export_questions_cells(self):
        c1 = self.make_chat(self.application, "u1", "alice")
        self.make_record(c1, 10, 0)
        self.make_record(c1, 10, 0)  # 2 次对话
        c2 = self.make_chat(self.application, "u2", "bob")
        self.make_record(c2, 5, 0)  # 1 次对话
        ws = self._workbook_rows("questions")
        self.assertEqual(ws.max_row, 3)
        # 按对话次数降序：alice(2) 在前
        self.assertEqual(ws.cell(2, 2).value, "alice")
        self.assertEqual(ws.cell(2, 5).value, 2)
        # 占比 = 对话次数 / 总对话次数
        self.assertAlmostEqual(ws.cell(2, 4).value, 2 / 3)
        self.assertAlmostEqual(ws.cell(3, 4).value, 1 / 3)
