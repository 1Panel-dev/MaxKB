# coding=utf-8

from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

import application.serializers.application_chat as application_chat_serializer
from application.serializers.application_chat import ApplicationChatQuerySerializers


class ChatExportToRowTests(SimpleTestCase):
    def setUp(self):
        def make_row(details):
            return {
                "chat_id": "chat-1",
                "abstract": "abstract",
                "problem_text": "",
                "details": details,
                "answer_text": "",
                "vote_status": None,
                "vote_reason": None,
                "vote_other_content": None,
                "improve_paragraph_list": [],
                "asker": {"username": "u"},
                "message_tokens": 1,
                "answer_tokens": 2,
                "ip_address": "1.1.1.1",
                "source": None,
                "run_time": 1.0,
                "create_time": None,
            }

        self.make_row = make_row
        self.question = {"type": "question-node", "answer": "optimized"}
        self.search = {
            "type": "search-knowledge-node",
            "name": "kb",
            "paragraph_list": [{"title": "t", "content": "c"}],
        }

    def test_dict_form(self):
        row = self.make_row({"q": self.question, "s": self.search})
        result = ApplicationChatQuerySerializers.to_row(row)
        self.assertEqual(result[3], "optimized")
        self.assertEqual(result[8], "kb:1")
        self.assertIn("kb:\nt:\nc", result[9])

    def test_list_form(self):
        row = self.make_row([self.question, self.search])
        result = ApplicationChatQuerySerializers.to_row(row)
        self.assertEqual(result[3], "optimized")
        self.assertEqual(result[8], "kb:1")
        self.assertIn("kb:\nt:\nc", result[9])

    def test_loop_nested_form(self):
        loop = {"type": "loop-node", "loop_node_data": [{"q": self.question, "s": self.search}]}
        row = self.make_row([loop])
        result = ApplicationChatQuerySerializers.to_row(row)
        self.assertEqual(result[3], "optimized")
        self.assertEqual(result[8], "kb:1")
        self.assertIn("kb:\nt:\nc", result[9])

    def test_v3_raw_list_form(self):
        start = {"type": "start-node", "name": "开始", "question": "你好"}
        ai = {"type": "ai-chat-node", "name": "AI 对话", "node_id": "n1", "answer": "你好！有什么我可以帮你的吗？"}
        row = self.make_row([start, ai])
        result = ApplicationChatQuerySerializers.to_row(row)
        self.assertEqual(result[2], "你好")
        self.assertEqual(result[4], "你好！有什么我可以帮你的吗？")

    def test_v3_execution_details_form(self):
        start = {"type": "start-node", "name": "开始", "question": "你好"}
        ai = {"type": "ai-chat-node", "name": "AI 对话", "node_id": "n1", "answer": "hi"}
        details = [{"execution_details": [start, ai], "paragraph_list": [], "padding_problem_text": None}]
        row = self.make_row(details)
        result = ApplicationChatQuerySerializers.to_row(row)
        self.assertEqual(result[2], "你好")
        self.assertEqual(result[4], "hi")

    def test_v3_answer_includes_reasoning(self):
        ai = {
            "type": "ai-chat-node",
            "name": "AI 对话",
            "node_id": "n1",
            "reasoning_content": "思考过程",
            "answer": "答案",
        }
        row = self.make_row([ai])
        result = ApplicationChatQuerySerializers.to_row(row)
        self.assertEqual(result[4], "思考过程\n\n答案")

    def test_v3_answer_from_node_messages(self):
        ai = {
            "type": "ai-chat-node",
            "name": "AI 对话",
            "node_id": "n1",
            "messages": [
                {"type": "REASONING", "content": "思考过程"},
                {"type": "TEXT", "content": "你好"},
            ],
        }
        row = self.make_row([ai])
        result = ApplicationChatQuerySerializers.to_row(row)
        self.assertEqual(result[4], "思考过程\n\n你好")

    def test_v3_answer_from_record_messages(self):
        details = [
            {
                "messages": [
                    {"type": "REASONING", "content": "思考过程"},
                    {"type": "TEXT", "content": "你好"},
                ],
                "execution_details": [],
            }
        ]
        result = ApplicationChatQuerySerializers.to_row(self.make_row(details))
        self.assertEqual(result[4], "思考过程\n\n你好")

    def test_empty_details(self):
        for details in ({}, None, []):
            result = ApplicationChatQuerySerializers.to_row(self.make_row(details))
            self.assertEqual((result[3], result[8], result[9]), ("", "", ""))


class ChatExportStreamingTests(SimpleTestCase):
    def test_export_streams_saved_workbook_in_bounded_chunks(self):
        workbook_size = 2 * 1024 * 1024 + 123

        class FakeWorksheet:
            def append(self, _):
                pass

        class FakeWorkbook:
            def create_sheet(self, title):
                self.title = title
                return FakeWorksheet()

            def save(self, target):
                target.write(b"x" * workbook_size)

            def close(self):
                pass

        with (
            patch.object(
                ApplicationChatQuerySerializers,
                "get_query_set",
                return_value=SimpleNamespace(),
            ),
            patch.object(
                application_chat_serializer,
                "native_stream_search",
                return_value=iter([]),
            ) as stream_search,
            patch.object(
                application_chat_serializer.openpyxl,
                "Workbook",
                return_value=FakeWorkbook(),
            ),
        ):
            response = ApplicationChatQuerySerializers(data={"select_ids": []}).export(
                {"select_ids": []},
                with_valid=False,
            )
            chunks = list(response.streaming_content)

        self.assertEqual(stream_search.call_args.kwargs["chunk_size"], 500)
        self.assertGreater(len(chunks), 1)
        self.assertLessEqual(max(map(len, chunks)), 1024 * 1024)
        self.assertEqual(b"".join(chunks), b"x" * workbook_size)
