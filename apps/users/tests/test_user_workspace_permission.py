from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from common.auth.struct.auth import Auth
from common.exception.app_exception import AppUnauthorizedFailed
from users.views.user import WorkspaceUserListView


class WorkspaceUserListPermissionTests(SimpleTestCase):
    def _request(self, roles):
        return SimpleNamespace(
            auth=Auth(roles=set(roles), permissions={}),
            user=SimpleNamespace(id="user-1"),
            query_params=SimpleNamespace(get=lambda *args, **kwargs: None),
        )

    def test_workspace_scoped_manage_role_can_access_user_list(self):
        request = self._request(["WORKSPACE_MANAGE:w:workspace-1"])
        with patch("users.views.user.UserManageSerializer.get_user_list", return_value=[]):
            try:
                result = WorkspaceUserListView().get(request, workspace_id="workspace-1")
            except AppUnauthorizedFailed as exc:
                self.fail(f"workspace user denied despite matching workspace role: {exc}")
        self.assertEqual(result.status_code, 200)

    def test_global_workspace_role_alone_cannot_access_workspace_user_list(self):
        request = self._request(["WORKSPACE_MANAGE"])
        with patch("users.views.user.UserManageSerializer.get_user_list", return_value=[]):
            with self.assertRaises(AppUnauthorizedFailed):
                WorkspaceUserListView().get(request, workspace_id="workspace-1")
