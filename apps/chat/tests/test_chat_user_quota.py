# coding=utf-8
import concurrent.futures
import threading
from types import SimpleNamespace
from unittest.mock import patch

from django.db import connection
from django.test import TestCase, TransactionTestCase

from chat.serializers.chat import ChatSerializers
from common.exception.app_exception import AppApiException
from system_manage.models.chat_user_token_quota import ChatUserTokenQuota, QuotaType


class ChatUserQuotaAvailabilityTests(TestCase):
    @staticmethod
    def locked_quota_query(quota):
        return SimpleNamespace(filter=lambda **kwargs: SimpleNamespace(first=lambda: quota))

    def test_exhausted_periodic_quota_is_rejected_before_workflow_runs(self):
        """配额已用尽时，对话在开始前就被拒绝，不会触发工作流生成内容。"""
        exhausted = SimpleNamespace(
            quota_type=QuotaType.PERIODIC,
            token_limit=10,
            used_tokens=10,
            period_end=None,
            check_and_reset=lambda: None,
        )

        data = {
            "chat_id": "0b1d5a02-6f5b-4d1e-9a4e-6a3c1a1a1a1a",
            "chat_user_id": "user-1",
            "chat_user_type": "CHAT_USER",
            "application_id": "0b1d5a02-6f5b-4d1e-9a4e-6a3c1a1a1a1b",
            "debug": False,
            "ip_address": "127.0.0.1",
            "source": {"type": "ONLINE"},
        }
        instance = {"message": {"content": "hi"}, "stream": False}

        with (
            patch.object(
                ChatUserTokenQuota.objects,
                "select_for_update",
                return_value=self.locked_quota_query(exhausted),
            ),
            patch.object(ChatSerializers, "get_application", return_value=object()),
            patch.object(ChatSerializers, "is_valid_chat"),
            patch.object(ChatSerializers, "is_valid_intraday_access_num"),
            patch.object(ChatSerializers, "save_failure_record") as save_failure_record,
            patch.object(ChatSerializers, "chat_work_flow") as workflow,
        ):
            serializer = ChatSerializers(data=data)
            with self.assertRaises(AppApiException):
                serializer.chat(instance)
            workflow.assert_not_called()
            save_failure_record.assert_called_once()

    def test_available_quota_lets_workflow_run(self):
        """配额未用尽时，前置校验不拦截，正常进入工作流。"""
        available = SimpleNamespace(
            quota_type=QuotaType.PERIODIC,
            token_limit=10,
            used_tokens=1,
            period_end=None,
            check_and_reset=lambda: None,
        )

        data = {
            "chat_id": "0b1d5a02-6f5b-4d1e-9a4e-6a3c1a1a1a1a",
            "chat_user_id": "user-1",
            "chat_user_type": "CHAT_USER",
            "application_id": "0b1d5a02-6f5b-4d1e-9a4e-6a3c1a1a1a1b",
            "debug": False,
            "ip_address": "127.0.0.1",
            "source": {"type": "ONLINE"},
        }
        instance = {"message": {"content": "hi"}, "stream": False}

        with (
            patch.object(
                ChatUserTokenQuota.objects,
                "select_for_update",
                return_value=self.locked_quota_query(available),
            ),
            patch.object(ChatSerializers, "get_application", return_value=object()),
            patch.object(ChatSerializers, "is_valid_chat"),
            patch.object(ChatSerializers, "is_valid_intraday_access_num"),
            patch.object(ChatSerializers, "chat_work_flow", return_value="ok") as workflow,
        ):
            serializer = ChatSerializers(data=data)
            self.assertEqual(serializer.chat(instance), "ok")
            workflow.assert_called_once()

    def test_check_available_over_limit_raises(self):
        """预校验：当前周期已用满则抛异常。"""
        quota = SimpleNamespace(
            quota_type=QuotaType.PERIODIC,
            token_limit=10,
            used_tokens=10,
            period_end=None,
            check_and_reset=lambda: None,
        )

        with patch.object(
            ChatUserTokenQuota.objects,
            "select_for_update",
            return_value=self.locked_quota_query(quota),
        ):
            with self.assertRaises(AppApiException):
                ChatUserTokenQuota.check_available("user-1")

    def test_check_available_within_limit_passes(self):
        """预校验：未用满时不拦截。"""
        quota = SimpleNamespace(
            quota_type=QuotaType.PERIODIC,
            token_limit=10,
            used_tokens=1,
            period_end=None,
            check_and_reset=lambda: None,
        )

        with patch.object(
            ChatUserTokenQuota.objects,
            "select_for_update",
            return_value=self.locked_quota_query(quota),
        ):
            ChatUserTokenQuota.check_available("user-1")


class ChatUserQuotaConsumeTests(TransactionTestCase):
    def test_recording_over_limit_does_not_raise(self):
        """记录实际用量时即使超出上限也不抛异常，并如实累计，保证对话记录能落库。"""
        ChatUserTokenQuota.objects.create(
            user_id="user-1",
            quota_type=QuotaType.PERIODIC,
            token_limit=10,
            used_tokens=9,
        )

        ChatUserTokenQuota.consume("user-1", 5)

        quota = ChatUserTokenQuota.objects.get(user_id="user-1")
        self.assertEqual(quota.used_tokens, 14)
        self.assertEqual(quota.total_tokens, 5)

    def test_concurrent_consumption_preserves_every_increment(self):
        ChatUserTokenQuota.objects.create(user_id="concurrent-user")
        barrier = threading.Barrier(2)

        def synchronize_reset(_quota):
            try:
                barrier.wait(timeout=2)
            except threading.BrokenBarrierError:
                pass

        def consume():
            try:
                ChatUserTokenQuota.consume("concurrent-user", 10)
            finally:
                connection.close()

        with (
            patch.object(ChatUserTokenQuota, "check_and_reset", new=synchronize_reset),
            concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor,
        ):
            futures = [executor.submit(consume) for _ in range(2)]
            for future in futures:
                future.result()

        quota = ChatUserTokenQuota.objects.get(user_id="concurrent-user")
        self.assertEqual(quota.used_tokens, 20)
        self.assertEqual(quota.total_tokens, 20)
