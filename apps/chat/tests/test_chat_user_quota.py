# coding=utf-8
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from chat.serializers.chat import ChatSerializers
from common.exception.app_exception import AppApiException
from system_manage.models.chat_user_token_quota import ChatUserTokenQuota, QuotaType


class ChatUserQuotaAvailabilityTests(SimpleTestCase):
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
            patch.object(ChatUserTokenQuota.objects, "filter", return_value=SimpleNamespace(first=lambda: exhausted)),
            patch.object(ChatSerializers, "get_application", return_value=object()),
            patch.object(ChatSerializers, "is_valid_chat"),
            patch.object(ChatSerializers, "is_valid_intraday_access_num"),
            patch.object(ChatSerializers, "chat_work_flow") as workflow,
        ):
            serializer = ChatSerializers(data=data)
            with self.assertRaises(AppApiException):
                serializer.chat(instance)
            workflow.assert_not_called()

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
            patch.object(ChatUserTokenQuota.objects, "filter", return_value=SimpleNamespace(first=lambda: available)),
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

        with patch.object(ChatUserTokenQuota.objects, "filter", return_value=SimpleNamespace(first=lambda: quota)):
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

        with patch.object(ChatUserTokenQuota.objects, "filter", return_value=SimpleNamespace(first=lambda: quota)):
            ChatUserTokenQuota.check_available("user-1")

    def test_recording_over_limit_does_not_raise(self):
        """记录实际用量时即使超出上限也不抛异常，并如实累计，保证对话记录能落库。"""
        quota = SimpleNamespace(
            quota_type=QuotaType.PERIODIC,
            token_limit=10,
            used_tokens=9,
            total_tokens=0,
            period_end=None,
            check_and_reset=lambda: None,
            save=Mock(),
        )

        with patch.object(ChatUserTokenQuota.objects, "filter", return_value=SimpleNamespace(first=lambda: quota)):
            ChatUserTokenQuota.consume("user-1", 5)

        self.assertEqual(quota.used_tokens, 14)
        self.assertEqual(quota.total_tokens, 5)
        quota.save.assert_called_once_with(update_fields=["used_tokens", "total_tokens"])
