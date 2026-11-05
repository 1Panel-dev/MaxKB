# coding=utf-8
import os
import unittest
from unittest import mock

from application.flow.agent_temp_dir import agent_run_temp_dir


class AgentRunTempDirTest(unittest.TestCase):
    def test_without_chat_id_uses_uuid_only(self):
        with mock.patch(
            "application.flow.agent_temp_dir.uuid.uuid7",
            return_value="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        ):
            path = agent_run_temp_dir(None)
        self.assertEqual(path, os.path.join("/tmp", "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"))

    def test_with_chat_id_still_unique_per_run(self):
        values = iter(
            [
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
            ]
        )
        with mock.patch(
            "application.flow.agent_temp_dir.uuid.uuid7",
            side_effect=lambda: next(values),
        ):
            first = agent_run_temp_dir("chat-abc")
            second = agent_run_temp_dir("chat-abc")
        self.assertEqual(
            first,
            os.path.join("/tmp", "chat-abc-11111111-1111-1111-1111-111111111111"),
        )
        self.assertEqual(
            second,
            os.path.join("/tmp", "chat-abc-22222222-2222-2222-2222-222222222222"),
        )
        self.assertNotEqual(first, second)


if __name__ == "__main__":
    unittest.main()
