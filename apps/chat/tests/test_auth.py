from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.core import signing
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from chat.views.v3.chat import BaseAuthView, FILE_AUTH_COOKIE, Logout
from common.auth.constants.operate_constants import Operate
from common.exception.app_exception import AppApiException


class BaseAuthViewTest(SimpleTestCase):
    def setUp(self):
        self.user = SimpleNamespace(id="chat-user-id", username="chat-user")
        self.view = BaseAuthView()
        self.view.request = Mock()

    def test_file_auth_cookie_supports_cross_site_https_login(self):
        request = RequestFactory().post("/chat/api/v3/auth/login", HTTP_X_FORWARDED_PROTO="https")

        response = self.view.generate(request, "chat-token", HttpResponse(), path="/chat/portal")
        cookie = response.cookies[FILE_AUTH_COOKIE]

        self.assertTrue(cookie["secure"])
        self.assertEqual(cookie["samesite"], "None")

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


class ChatLogoutTest(SimpleTestCase):
    def test_https_logout_clears_cross_site_file_auth_cookie(self):
        request = APIRequestFactory().post(
            "/chat/api/v3/auth/logout?accessToken=access-token",
            HTTP_AUTHORIZATION="Bearer chat-token",
            HTTP_X_FORWARDED_PROTO="https",
        )
        force_authenticate(
            request,
            user=SimpleNamespace(
                id="chat-user-id",
                type="CHAT_USER",
                username="chat-user",
                email="chat-user@example.com",
                phone="",
                nick_name="Chat User",
            ),
        )

        with patch("chat.views.v3.chat.cache.delete"), patch("common.log.log.Log.save"):
            response = Logout.as_view()(request)

        cookie = response.cookies[FILE_AUTH_COOKIE]
        self.assertEqual(cookie["max-age"], 0)
        self.assertTrue(cookie["secure"])
        self.assertEqual(cookie["samesite"], "None")
