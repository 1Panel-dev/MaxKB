from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from common.exception.app_exception import NotFound404
from users.serializers.user_group import UserGroupListPageSerializer


class UserGroupWorkspaceValidationTests(SimpleTestCase):
    def test_missing_or_cross_workspace_group_returns_not_found(self):
        query_set = MagicMock()
        query_set.exists.return_value = False
        serializer = UserGroupListPageSerializer.Query(data={"workspace_id": "workspace-1", "group_id": "group-1"})

        with (
            patch("users.serializers.user_group.SystemUserGroup.objects.filter", return_value=query_set),
            self.assertRaises(NotFound404) as context,
        ):
            serializer.is_valid(raise_exception=True)

        self.assertEqual(404, context.exception.status_code)
        self.assertNotIn("does not exist or does not belong", str(context.exception.message))
