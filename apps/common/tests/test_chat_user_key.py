from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from common.auth.handle.impl import chat_user_key
from common.auth.handle.impl.chat_user_key import ChatUserKey
from common.exception.app_exception import AppAuthenticationFailed
from portal.models import get_portal_setting

USER_ID = "40000000-0000-0000-0000-000000000001"


class ChatUserKeyPortalSwitchTest(SimpleTestCase):
    def setUp(self):
        api_key = SimpleNamespace(is_active=True, user_id=USER_ID)
        chat_user = SimpleNamespace(id=USER_ID, is_active=True, source="LOCAL")
        query_set = patch.object(chat_user_key, "QuerySet").start()
        query_set.side_effect = lambda model: SimpleNamespace(
            filter=lambda **kwargs: SimpleNamespace(
                first=lambda: api_key if model is chat_user_key.ChatUserApiKey else chat_user
            )
        )
        self.get_auth = patch.object(chat_user_key, "get_auth", return_value="auth").start()
        self.portal = patch.object(chat_user_key, "get_portal_setting", return_value=True).start()
        self.addCleanup(patch.stopall)

    def test_api_enabled_authenticates(self):
        principal, auth = ChatUserKey().handle(None, "chat-key", None)
        self.portal.assert_called_once_with("enable_api")
        self.assertEqual((principal.profile.id, auth), (USER_ID, "auth"))

    def test_api_disabled_rejects_key(self):
        self.portal.return_value = False
        with self.assertRaises(AppAuthenticationFailed):
            ChatUserKey().handle(None, "chat-key", None)
        self.get_auth.assert_not_called()


class PortalSettingTest(SimpleTestCase):
    @patch("portal.models.portal.Portal.objects")
    def test_uses_field_default_without_portal(self, objects):
        objects.values_list.return_value.first.return_value = None
        self.assertTrue(get_portal_setting("enable_api"))
        objects.values_list.return_value.first.return_value = False
        self.assertFalse(get_portal_setting("enable_knowledge_base_api"))
        objects.values_list.assert_called_with("enable_knowledge_base_api", flat=True)
