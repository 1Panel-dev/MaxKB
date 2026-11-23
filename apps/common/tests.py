import json

from django.test import SimpleTestCase

from common.handle.impl.response.loop_to_response import LoopToResponse
from common.handle.impl.response.openai_to_response import OpenaiToResponse
from common.handle.impl.response.system_to_response import SystemToResponse
from common.utils.common import markdown_to_plain_text


class ResponseTokenUsageTestCase(SimpleTestCase):
    """Every response implementation must report the token counts the call sites pass.

    Call sites pass prompt tokens first, completion tokens second:
    workflow_manage.py (to_block_response/to_stream_chunk_response) and
    base_chat_step.py call them as (..., is_end, message_tokens, answer_tokens).
    """

    prompt_tokens = 1000
    completion_tokens = 7

    def assert_usage(self, prompt_tokens, completion_tokens, expected_prompt, expected_completion):
        self.assertEqual((prompt_tokens, completion_tokens),
                         (expected_prompt, expected_completion))

    def test_system_block_response_keeps_prompt_and_completion_tokens(self):
        body = json.loads(SystemToResponse().to_block_response(
            'chat-1', 'record-1', 'answer', True, self.prompt_tokens, self.completion_tokens, {}).content)
        data = body['data']
        self.assert_usage(data['prompt_tokens'], data['completion_tokens'],
                          self.prompt_tokens, self.completion_tokens)

    def test_system_stream_chunk_keeps_prompt_and_completion_tokens(self):
        chunk = SystemToResponse().to_stream_chunk_response(
            'chat-1', 'record-1', 'node-1', [], '', True, self.prompt_tokens, self.completion_tokens, {})
        usage = json.loads(chunk[len('data: '):].strip())['usage']
        self.assert_usage(usage['prompt_tokens'], usage['completion_tokens'],
                          self.prompt_tokens, self.completion_tokens)
        self.assertEqual(usage['total_tokens'], self.prompt_tokens + self.completion_tokens)

    def test_loop_stream_chunk_keeps_prompt_and_completion_tokens(self):
        chunk = LoopToResponse().to_stream_chunk_response(
            'chat-1', 'record-1', 'node-1', [], '', True, self.prompt_tokens, self.completion_tokens, {})
        self.assert_usage(chunk['usage']['prompt_tokens'], chunk['usage']['completion_tokens'],
                          self.prompt_tokens, self.completion_tokens)

    def test_openai_responses_keep_prompt_and_completion_tokens(self):
        body = json.loads(OpenaiToResponse().to_block_response(
            'chat-1', 'record-1', 'answer', True, self.prompt_tokens, self.completion_tokens, {}).content)
        self.assert_usage(body['usage']['prompt_tokens'], body['usage']['completion_tokens'],
                          self.prompt_tokens, self.completion_tokens)


class MarkdownToPlainTextTestCase(SimpleTestCase):
    def test_removes_embedded_markup_contents(self):
        cases = {
            'before <audio src="clip.mp3">audio fallback</audio> after': "before after",
            'before <video src="clip.mp4">video fallback</video> after': "before after",
            'before <form_rander>{"label":"private"}</form_rander> after': "before after",
        }

        for markup, expected in cases.items():
            with self.subTest(markup=markup):
                self.assertEqual(markdown_to_plain_text(markup), expected)


class SmartSplitParagraphTestCase(SimpleTestCase):
    """smart_split_paragraph must treat the full-width exclamation/question marks
    as split points just like their ASCII counterparts (the list is documented as
    中英文感叹号/问号)."""

    def test_splits_at_full_width_exclamation_and_question_marks(self):
        from common.utils.split_model import smart_split_paragraph
        for mark in ('！', '？'):
            with self.subTest(mark=mark):
                text = '内' * 60 + mark + '容' * 200
                parts = smart_split_paragraph(text, 100)
                self.assertEqual(len(parts[0]), 61)
                self.assertTrue(parts[0].endswith(mark))
                self.assertEqual(''.join(parts), text)

    def test_ascii_and_period_split_points_still_work(self):
        from common.utils.split_model import smart_split_paragraph
        for mark in ('!', '?', '.', '。'):
            with self.subTest(mark=mark):
                text = 'x' * 60 + mark + 'y' * 200
                parts = smart_split_paragraph(text, 100)
                self.assertEqual(len(parts[0]), 61)
                self.assertTrue(parts[0].endswith(mark))
                self.assertEqual(''.join(parts), text)

    def test_hard_cut_when_no_split_point_in_window(self):
        from common.utils.split_model import smart_split_paragraph
        parts = smart_split_paragraph('z' * 250, 100)
        self.assertEqual([len(part) for part in parts], [100, 100, 50])
