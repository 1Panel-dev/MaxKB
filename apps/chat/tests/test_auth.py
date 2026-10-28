from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.core import signing
from django.test import SimpleTestCase

from chat.views.v3.chat import BaseAuthView
from common.auth.constants.operate_constants import Operate
from common.exception.app_exception import AppApiException


class BaseAuthViewTest(SimpleTestCase):
    def setUp(self):
        self.user = SimpleNamespace(id="chat-user-id", username="chat-user")
        self.view = BaseAuthView()
        self.view.request = Mock()

    def test_access_token_login_validates_authorization_and_keeps_operate_token(self):
        access_token = "application-access-token"
        application_access_token = SimpleNamespace(
            application_id="application-id",
            application=SimpleNamespace(workspace_id="application-workspace"),
        )

        with (
            patch(
                "chat.views.v3.chat.ChatUserAccessTokenSerializer.create_token_and_cache",
            ) as validate_authorization,
            patch("chat.views.v3.chat.ApplicationAccessToken.objects.filter") as filter_access_token,
            patch("chat.views.v3.chat.cache.set") as cache_set,
            patch("chat.views.v3.chat.record_log") as record_log,
            patch("common.auth.common.get_key", return_value="test-signing-key"),
        ):
            filter_access_token.return_value.select_related.return_value.first.return_value = application_access_token
            filter_access_token.return_value.values_list.return_value.first.return_value = "application-id"

            token = self.view.create_token_and_cache(self.user, access_token, Operate.OIDC)

        validate_authorization.assert_called_once_with(access_token, self.user)
        self.assertEqual(
            signing.loads(token, key="test-signing-key"),
            {
                "id": self.user.id,
                "type": "CHAT_USER",
                "login_type": "OIDC",
                "kwargs": {"application_id": "application-id"},
            },
        )
        cache_set.assert_called_once_with(token, self.user, timeout=7200, version="CHAT_USER_TOKEN")
        record_log.assert_called_once_with(
            menu="Chat User/login",
            operate="Log in",
            request=self.view.request,
            user={"username": "chat-user"},
            status=200,
            operation_object={"name": "chat-user"},
            workspace_id="application-workspace",
        )

    def test_login_without_access_token_records_audit_log(self):
        with (
            patch("chat.views.v3.chat.record_log", create=True) as record_log,
            patch("chat.views.v3.chat.ChatUserAccessTokenSerializer.create_token_and_cache") as validate_authorization,
            patch("chat.views.v3.chat.ApplicationAccessToken.objects.filter") as filter_access_token,
            patch("chat.views.v3.chat.cache.set"),
            patch("common.auth.common.get_key", return_value="test-signing-key"),
        ):
            self.view.create_token_and_cache(self.user, None, Operate.LOCAL)

        validate_authorization.assert_not_called()
        filter_access_token.assert_not_called()
        record_log.assert_called_once_with(
            menu="Chat User/login",
            operate="Log in",
            request=self.view.request,
            user={"username": "chat-user"},
            status=200,
            operation_object={"name": "chat-user"},
            workspace_id="default",
        )

    def test_failed_authorization_records_failed_login_log(self):
        with (
            patch(
                "chat.views.v3.chat.ChatUserAccessTokenSerializer.create_token_and_cache",
                side_effect=AppApiException(1005, "access denied"),
            ),
            patch("chat.views.v3.chat.record_log") as record_log,
            patch("chat.views.v3.chat.cache.set") as cache_set,
        ):
            with self.assertRaises(AppApiException):
                self.view.create_token_and_cache(self.user, "application-access-token", Operate.OIDC)

        cache_set.assert_not_called()
        record_log.assert_called_once_with(
            menu="Chat User/login",
            operate="Log in",
            request=self.view.request,
            user={"username": "chat-user"},
            status=500,
            operation_object={"name": "chat-user"},
            workspace_id="default",
        )
