from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from application.models import Application, ApplicationAccessToken, ApplicationFolder, Chat
from chat.serializers.portal import PortalConversationQuerySerializer, PortalHistoricalConversationSerializer
from common.database_model_manage.database_model_manage import DatabaseModelManage
from xpack.models.application_setting import ApplicationSetting


class PortalHistoryVisibilityTests(TestCase):
    user_id = "01a1f6cf-9369-77d2-abf6-70f9db09c494"

    def setUp(self):
        DatabaseModelManage.init()
        folder, _ = ApplicationFolder.objects.get_or_create(id="default", defaults={"name": "默认分组"})
        self.application = Application.objects.create(
            name="测试应用",
            folder=folder,
            is_publish=True,
            is_portal=True,
        )
        ApplicationAccessToken.objects.create(
            application=self.application,
            access_token="portal-history-test-token",
            authentication=False,
        )
        ApplicationSetting.objects.create(application=self.application, show_history=False)
        now = timezone.now()
        for index in range(6):
            chat = Chat.objects.create(
                application=self.application,
                abstract=f"chat-{index}",
                chat_user_id=self.user_id,
            )
            Chat.objects.filter(id=chat.id).update(update_time=now + timedelta(minutes=index))

    def test_grouped_history_returns_latest_five_when_history_setting_is_disabled(self):
        with patch("django.core.cache.cache.get", return_value=True):
            result = PortalHistoricalConversationSerializer.Query(data={}).page(1, 20, self.user_id)

        application = result["records"][0]
        self.assertFalse(application["show_history"])
        self.assertEqual(application["count"], 6)
        self.assertEqual(
            [conversation["abstract"] for conversation in application["conversations"]],
            ["chat-5", "chat-4", "chat-3", "chat-2", "chat-1"],
        )

    def test_application_history_remains_queryable_when_history_setting_is_disabled(self):
        with patch("django.core.cache.cache.get", return_value=True):
            result = PortalConversationQuerySerializer(data={"application_id": self.application.id}).page(
                1, 5, self.user_id
            )

        self.assertEqual(
            [conversation["abstract"] for conversation in result["records"]],
            ["chat-5", "chat-4", "chat-3", "chat-2", "chat-1"],
        )
