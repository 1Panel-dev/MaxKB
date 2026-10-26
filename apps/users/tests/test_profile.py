from unittest.mock import patch

import uuid_utils.compat as uuid
from django.core.cache import cache
from django.test import SimpleTestCase, override_settings

from common.auth.struct.auth import Auth
from users.models import User
from users.serializers.user import UserProfileSerializer


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "user-profile-tests",
        }
    }
)
class UserProfilePasswordCacheTests(SimpleTestCase):
    def setUp(self):
        cache.clear()
        self.user = User(
            id=uuid.uuid4(),
            username="profile-user",
            nick_name="Profile User",
            email="profile@example.com",
            password="hash-v1",
            role="USER",
            source="LOCAL",
            language="en-US",
        )
        self.auth = Auth(roles=set(), permissions={})

    def _profile(self):
        with (
            patch("users.serializers.user.DatabaseModelManage.get_model", return_value=None),
            patch("users.serializers.user.get_workspace_list_by_user", return_value=[]),
        ):
            return UserProfileSerializer().profile(self.user, self.auth)

    def test_profile_caches_default_password_check_for_same_hash(self):
        with patch("users.serializers.user.password_verify", return_value=True) as verify_password:
            first = self._profile()
            second = self._profile()

        self.assertTrue(first["is_edit_password"])
        self.assertTrue(second["is_edit_password"])
        verify_password.assert_called_once()

    def test_profile_rechecks_when_password_hash_changes(self):
        with patch("users.serializers.user.password_verify", side_effect=[True, False]) as verify_password:
            first = self._profile()
            self.user.password = "hash-v2"
            second = self._profile()

        self.assertTrue(first["is_edit_password"])
        self.assertFalse(second["is_edit_password"])
        self.assertEqual(verify_password.call_count, 2)
