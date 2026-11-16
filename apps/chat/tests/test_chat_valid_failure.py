# coding=utf-8
import json
from contextlib import contextmanager
from unittest.mock import patch

from django.test import SimpleTestCase

from chat.serializers.chat import ChatSerializers
from common.exception.app_exception import AppChatNumOutOfBoundsFailed, ChatException
from common.handle.impl.response.openai_to_response import OpenaiToResponse

CHAT_ID = "0b1d5a02-6f5b-4d1e-9a4e-6a3c1a1a1a1a"
DATA = {
    "chat_id": CHAT_ID,
    "chat_user_id": "user-1",
    "chat_user_type": "CHAT_USER",
    "application_id": "0b1d5a02-6f5b-4d1e-9a4e-6a3c1a1a1a1b",
    "debug": False,
    "ip_address": "127.0.0.1",
    "source": {"type": "ONLINE"},
}
LIMIT_ERROR = AppChatNumOutOfBoundsFailed(1002, "The number of visits exceeds today's visits")


@contextmanager
def patched_chat(limit_error=LIMIT_ERROR, access_error=None, save_error=None, record_error=None):
    """隔离 DB：准入/额度校验、落库、工作流全部打桩，只测 chat 的编排。"""
    with (
        patch.object(ChatSerializers, "is_valid_chat", side_effect=access_error),
        patch.object(ChatSerializers, "is_valid_chat_record", side_effect=record_error) as is_valid_chat_record,
        patch.object(ChatSerializers, "get_application", return_value=object()),
        patch.object(ChatSerializers, "valid_limit", side_effect=limit_error),
        patch.object(ChatSerializers, "save_failure_record", side_effect=save_error) as save_failure_record,
        patch.object(ChatSerializers, "chat_work_flow", return_value="ok") as workflow,
    ):
        save_failure_record.is_valid_chat_record = is_valid_chat_record
        yield save_failure_record, workflow


def read_frames(response):
    content = b"".join(
        chunk if isinstance(chunk, bytes) else chunk.encode("utf-8") for chunk in response.streaming_content
    ).decode("utf-8")
    return [frame[len("data: ") :] for frame in content.split("\n\n") if frame]


class ChatValidFailureTests(SimpleTestCase):
    def test_stream_limit_failure_is_saved_and_returned_as_failure_frame(self):
        """流式：额度校验失败时落库，并以 FAILURE 帧 + [DONE] 返回，不进入工作流。"""
        with patched_chat() as (save_failure_record, workflow):
            response = ChatSerializers(data=DATA).chat({"message": {"content": "hi"}, "stream": True})
            frames = read_frames(response)

        workflow.assert_not_called()
        save_failure_record.assert_called_once()
        _instance, chat_record_id, block = save_failure_record.call_args.args
        self.assertEqual(block["type"], "FAILURE")
        self.assertEqual(block["content"], LIMIT_ERROR.message)
        # 校验失败的错误码随块落库，并放在 extra 里下发
        self.assertEqual(block["extra"], {"code": LIMIT_ERROR.code})

        self.assertEqual(frames[-1], "[DONE]")
        payload = json.loads(frames[0])
        self.assertEqual(payload["chat_id"], CHAT_ID)
        # 返回的记录 id 与落库的记录 id 一致，前端可据此定位这条失败记录
        self.assertEqual(payload["chat_record_id"], chat_record_id)
        self.assertEqual(payload["content"][0]["type"], "FAILURE")
        self.assertEqual(payload["content"][0]["content"], LIMIT_ERROR.message)
        self.assertEqual(payload["content"][0]["extra"], {"code": LIMIT_ERROR.code})

    def test_block_limit_failure_is_saved_and_raised(self):
        """非流式：额度校验失败时落库，并抛出原异常（保留原状态码）。"""
        with patched_chat() as (save_failure_record, workflow):
            with self.assertRaises(AppChatNumOutOfBoundsFailed):
                ChatSerializers(data=DATA).chat({"message": {"content": "hi"}, "stream": False})

        workflow.assert_not_called()
        save_failure_record.assert_called_once()

    def test_existing_record_is_not_overwritten(self):
        """带 chat_record_id（重答/表单续跑）时不落库，避免覆盖已有记录，但仍返回失败。"""
        record_id = "0b1d5a02-6f5b-4d1e-9a4e-6a3c1a1a1a1c"
        with patched_chat() as (save_failure_record, _workflow):
            response = ChatSerializers(data=DATA).chat(
                {"message": {"content": "hi"}, "stream": True, "chat_record_id": record_id}
            )
            frames = read_frames(response)

        save_failure_record.assert_not_called()
        self.assertEqual(json.loads(frames[0])["chat_record_id"], record_id)

    def test_access_failure_is_raised_without_saving(self):
        """准入校验（会话归属/应用）失败时直接抛出，不落库。"""
        error = ChatException(500, "Conversation does not exist")
        with patched_chat(limit_error=None, access_error=error) as (save_failure_record, workflow):
            with self.assertRaises(ChatException):
                ChatSerializers(data=DATA).chat({"message": {"content": "hi"}, "stream": True})

        save_failure_record.assert_not_called()
        workflow.assert_not_called()

    def test_record_not_in_chat_is_raised_before_limit_check_and_workflow(self):
        """chat_record_id 不属于当前会话（或不存在）时直接抛出：不落库、不进工作流。"""
        record_id = "0b1d5a02-6f5b-4d1e-9a4e-6a3c1a1a1a1c"
        error = ChatException(500, "Conversation record does not exist")
        with patched_chat(limit_error=None, record_error=error) as (save_failure_record, workflow):
            with self.assertRaises(ChatException):
                ChatSerializers(data=DATA).chat(
                    {"message": {"content": "hi"}, "stream": True, "chat_record_id": record_id, "position": {"id": "n"}}
                )

        save_failure_record.is_valid_chat_record.assert_called_once_with(record_id)
        save_failure_record.assert_not_called()
        workflow.assert_not_called()

    def test_chat_record_must_belong_to_current_chat(self):
        """记录归属校验按 (id, chat_id) 查询：查不到即拒绝；未带 chat_record_id 时不查库。"""
        serializer = ChatSerializers(data=DATA)
        serializer.is_valid(raise_exception=True)
        record_id = "0b1d5a02-6f5b-4d1e-9a4e-6a3c1a1a1a1c"

        with patch("chat.serializers.chat.QuerySet") as query_set:
            serializer.is_valid_chat_record(None)
            query_set.assert_not_called()

            query_set.return_value.filter.return_value.exists.return_value = False
            with self.assertRaises(ChatException):
                serializer.is_valid_chat_record(record_id)
            self.assertEqual(query_set.return_value.filter.call_args.kwargs["id"], record_id)
            self.assertEqual(str(query_set.return_value.filter.call_args.kwargs["chat_id"]), CHAT_ID)

            query_set.return_value.filter.return_value.exists.return_value = True
            serializer.is_valid_chat_record(record_id)

    def test_save_error_does_not_mask_validation_failure(self):
        """落库出错时仍按校验失败返回，不把落库异常抛给调用方。"""
        with patched_chat(save_error=RuntimeError("db down")):
            response = ChatSerializers(data=DATA).chat({"message": {"content": "hi"}, "stream": True})
            frames = read_frames(response)

        self.assertEqual(json.loads(frames[0])["content"][0]["content"], LIMIT_ERROR.message)

    def test_openai_stream_skips_failure_frame(self):
        """OpenAI 流式格式不表达 FAILURE 块，只以 [DONE] 收尾（与工作流运行出错的行为一致）。"""
        with patched_chat():
            response = ChatSerializers(data=DATA).chat(
                {"message": {"content": "hi"}, "stream": True}, base_to_response=OpenaiToResponse()
            )
            frames = read_frames(response)

        self.assertEqual(frames, ["[DONE]"])

    def test_passing_validation_runs_workflow(self):
        """校验全部通过时正常进入工作流，不落失败记录。"""
        with patched_chat(limit_error=None) as (save_failure_record, workflow):
            result = ChatSerializers(data=DATA).chat({"message": {"content": "hi"}, "stream": True})

        self.assertEqual(result, "ok")
        workflow.assert_called_once()
        save_failure_record.assert_not_called()
