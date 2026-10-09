import json

from django.test import SimpleTestCase

from common.handle.impl.response.loop_to_response import LoopToResponse
from common.handle.impl.response.openai_to_response import OpenaiToResponse
from common.handle.impl.response.system_to_response import SystemToResponse
from common.utils.common import markdown_to_plain_text


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


class TokenUsageResponseTestCase(SimpleTestCase):
    """Callers pass ``message_tokens`` (prompt) then ``answer_tokens`` (completion).

    See ``application/flow/workflow_manage.py`` and
    ``application/chat_pipeline/step/chat_step/impl/base_chat_step.py``, which both
    forward the aggregated counts in that order. Every ``BaseToResponse``
    implementation must therefore report them back under those same names.
    """

    prompt_tokens = 100
    completion_tokens = 25

    def _usage_of_block_response(self, response):
        payload = json.loads(response.content)
        if 'usage' in payload:
            return payload['usage']
        return payload['data']

    def _usage_of_stream_chunk(self, chunk):
        if isinstance(chunk, dict):
            return chunk['usage']
        return json.loads(chunk[len('data: '):])['usage']

    def test_system_block_response_keeps_prompt_and_completion_apart(self):
        usage = self._usage_of_block_response(SystemToResponse().to_block_response(
            'chat-id', 'record-id', 'hi', True, self.prompt_tokens, self.completion_tokens))

        self.assertEqual(usage['prompt_tokens'], self.prompt_tokens)
        self.assertEqual(usage['completion_tokens'], self.completion_tokens)

    def test_system_stream_chunk_keeps_prompt_and_completion_apart(self):
        usage = self._usage_of_stream_chunk(SystemToResponse().to_stream_chunk_response(
            'chat-id', 'record-id', 'node-id', [], 'hi', False,
            self.prompt_tokens, self.completion_tokens))

        self.assertEqual(usage['prompt_tokens'], self.prompt_tokens)
        self.assertEqual(usage['completion_tokens'], self.completion_tokens)
        self.assertEqual(usage['total_tokens'], self.prompt_tokens + self.completion_tokens)

    def test_loop_stream_chunk_keeps_prompt_and_completion_apart(self):
        usage = self._usage_of_stream_chunk(LoopToResponse().to_stream_chunk_response(
            'chat-id', 'record-id', 'node-id', [], 'hi', False,
            self.prompt_tokens, self.completion_tokens))

        self.assertEqual(usage['prompt_tokens'], self.prompt_tokens)
        self.assertEqual(usage['completion_tokens'], self.completion_tokens)
        self.assertEqual(usage['total_tokens'], self.prompt_tokens + self.completion_tokens)

    def test_openai_stream_chunk_agrees_with_the_other_implementations(self):
        usage = self._usage_of_stream_chunk(OpenaiToResponse().to_stream_chunk_response(
            'chat-id', 'record-id', 'node-id', [], 'hi', False,
            self.prompt_tokens, self.completion_tokens))

        self.assertEqual(usage['prompt_tokens'], self.prompt_tokens)
        self.assertEqual(usage['completion_tokens'], self.completion_tokens)
        self.assertEqual(usage['total_tokens'], self.prompt_tokens + self.completion_tokens)

    def test_openai_block_response_agrees_with_the_other_implementations(self):
        usage = self._usage_of_block_response(OpenaiToResponse().to_block_response(
            'chat-id', 'record-id', 'hi', True, self.prompt_tokens, self.completion_tokens))

        self.assertEqual(usage['prompt_tokens'], self.prompt_tokens)
        self.assertEqual(usage['completion_tokens'], self.completion_tokens)
        self.assertEqual(usage['total_tokens'], self.prompt_tokens + self.completion_tokens)

    def test_zero_token_counts_are_not_swapped(self):
        usage = self._usage_of_stream_chunk(SystemToResponse().to_stream_chunk_response(
            'chat-id', 'record-id', 'node-id', [], 'hi', False, 0, 0))

        self.assertEqual(usage['prompt_tokens'], 0)
        self.assertEqual(usage['completion_tokens'], 0)

    def test_asymmetric_counts_survive_a_round_trip(self):
        """Parent applications read ``usage.prompt_tokens`` back as ``message_tokens``.

        ``application_node`` and ``tool_workflow_lib_node`` both do this, so a
        swapped pair would feed the completion count back in as the prompt count.
        """
        parent_usage = {'prompt_tokens': self.prompt_tokens, 'completion_tokens': self.completion_tokens}
        message_tokens = parent_usage.get('prompt_tokens', 0)
        answer_tokens = parent_usage.get('completion_tokens', 0)

        forwarded = self._usage_of_stream_chunk(SystemToResponse().to_stream_chunk_response(
            'chat-id', 'record-id', 'node-id', [], 'hi', False, message_tokens, answer_tokens))

        self.assertEqual(forwarded['prompt_tokens'], parent_usage['prompt_tokens'])
        self.assertEqual(forwarded['completion_tokens'], parent_usage['completion_tokens'])
