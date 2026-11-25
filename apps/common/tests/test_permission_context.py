from types import SimpleNamespace

from django.test import SimpleTestCase

from common.auth.authentication import check_permissions, has_permissions
from common.auth.constants.chat_permission_constants import ChatPermissionConstants
from common.auth.struct.auth import Auth
from common.exception.app_exception import AppUnauthorizedFailed


class PermissionContextTests(SimpleTestCase):
    application_id = "00000000-0000-0000-0000-000000000002"

    def test_check_permissions_accepts_auth_without_http_request(self):
        auth = Auth(set(), {f"CHAT_USER:r:{self.application_id}": 1 << 1})

        self.assertTrue(
            check_permissions(
                ChatPermissionConstants.get_aggregate_permissions(),
                auth=auth,
                application_id=self.application_id,
            )
        )

    def test_has_permissions_keeps_request_based_allowed_behavior(self):
        auth = Auth(set(), {f"CHAT_USER:r:{self.application_id}": 1 << 1})
        request = SimpleNamespace(auth=auth)

        @has_permissions(ChatPermissionConstants.get_aggregate_permissions())
        def view(_, request, **kwargs):
            return "allowed"

        self.assertEqual(view(None, request, application_id=self.application_id), "allowed")

    def test_has_permissions_keeps_request_based_rejected_behavior(self):
        request = SimpleNamespace(auth=Auth(set(), {}))

        @has_permissions(ChatPermissionConstants.get_aggregate_permissions())
        def view(_, request, **kwargs):
            return "allowed"

        with self.assertRaises(AppUnauthorizedFailed):
            view(None, request, application_id=self.application_id)
