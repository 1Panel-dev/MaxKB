import datetime
import json
import unittest
from unittest import mock

from common.handle.impl.response.openai_to_response import OpenaiToResponse


class OpenaiToResponseCreatedTestCase(unittest.TestCase):
    """`created` must be a Unix timestamp, as in the OpenAI API, not the seconds field of the clock."""

    NOW = datetime.datetime(2026, 11, 3, 2, 35, 7, tzinfo=datetime.timezone.utc)

    def test_block_response_created_is_unix_timestamp(self):
        with mock.patch('common.handle.impl.response.openai_to_response.timezone.now', return_value=self.NOW):
            response = OpenaiToResponse().to_block_response('chat', 'record', 'hi', True, 1, 2)
        self.assertEqual(json.loads(response.content)['created'], int(self.NOW.timestamp()))

    def test_stream_chunk_created_is_unix_timestamp(self):
        with mock.patch('common.handle.impl.response.openai_to_response.timezone.now', return_value=self.NOW):
            chunk = OpenaiToResponse().to_stream_chunk_response('chat', 'record', 'node', [], 'hi', False, 1, 2)
        payload = json.loads(chunk[len('data: '):])
        self.assertEqual(payload['created'], int(self.NOW.timestamp()))
