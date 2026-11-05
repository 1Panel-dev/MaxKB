import json
from types import SimpleNamespace
from unittest.mock import Mock, patch

from common.auth.constants.permission_constants import PermissionConstants
from common.auth.constants.role_constants import RoleConstants
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.exception.app_exception import AppUnauthorizedFailed
from django.test import SimpleTestCase
from tools.models import Tool, ToolScope
from tools.views.tool import ToolView


class ToolDetailPermissionTests(SimpleTestCase):
    workspace_id = "test-workspace"
    tool_id = "00000000-0000-0000-0000-000000000001"

    def setUp(self):
        self.get_authorized_tool = Mock()
        self.get_authorized_tool.return_value.exists.return_value = True
        self.enterContext(patch.dict(DatabaseModelManage.model_dict, {"get_authorized_tool": self.get_authorized_tool}))
        self.tools = self.enterContext(patch.object(Tool, "objects"))
        self.serializer = self.enterContext(patch("tools.views.tool.ToolSerializer.Operate"))
        self.serializer.return_value.one.return_value = {"id": self.tool_id, "is_active": True}
        self.enterContext(patch("common.log.log.Log"))

    def request(self, *, roles=(), permissions=(), workspace_id=None):
        kwargs = {"workspace_id": workspace_id or self.workspace_id, "tool_id": self.tool_id}
        resolved_permissions = [permission(None, kwargs) for permission in permissions]
        return SimpleNamespace(
            auth=SimpleNamespace(
                roles=[str(role.get_workspace_role()(None, kwargs)) for role in roles],
                permissions={p.get_resource_permission_key(p.resource_id): p.bit() for p in resolved_permissions},
            ),
            user=SimpleNamespace(id=self.tool_id, type="test"),
            META={},
            path=f"/admin/api/workspace/{self.workspace_id}/tool/{self.tool_id}",
            data={},
            query_params={},
        )

    def get_detail(self, request):
        return ToolView.Operate().get(request, workspace_id=self.workspace_id, tool_id=self.tool_id)

    def assert_denied(self, request):
        with self.assertRaises(AppUnauthorizedFailed) as error:
            self.get_detail(request)
        self.assertEqual(error.exception.code, 403)
        self.serializer.assert_not_called()

    def test_user_can_read_workspace_authorized_shared_tool(self):
        response = self.get_detail(self.request(roles=[RoleConstants.USER]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["data"], {"id": self.tool_id, "is_active": True})
        self.tools.filter.assert_called_once_with(id=self.tool_id, scope=ToolScope.SHARED)
        self.get_authorized_tool.assert_called_once_with(self.tools.filter.return_value, self.workspace_id)
        self.serializer.assert_called_once_with(data={"id": self.tool_id, "workspace_id": self.workspace_id})

    def test_custom_role_with_tool_list_permission_can_read_authorized_shared_tool(self):
        self.get_detail(self.request(permissions=[PermissionConstants.TOOL_READ.get_workspace_permission()]))
        self.serializer.return_value.one.assert_called_once()

    def test_existing_resource_permission_can_read_authorized_shared_tool(self):
        self.get_detail(self.request(permissions=[PermissionConstants.TOOL_READ.get_workspace_tool_permission()]))
        self.serializer.return_value.one.assert_called_once()

    def test_shared_authorization_does_not_grant_access_to_non_members(self):
        self.assert_denied(self.request())

    def test_role_in_another_workspace_does_not_grant_access(self):
        self.assert_denied(self.request(roles=[RoleConstants.USER], workspace_id="other-workspace"))

    def test_permission_in_another_workspace_does_not_grant_access(self):
        self.assert_denied(
            self.request(
                permissions=[PermissionConstants.TOOL_READ.get_workspace_permission()], workspace_id="other-workspace"
            )
        )

    def test_unshared_or_unauthorized_tool_requires_personal_permission(self):
        self.get_authorized_tool.return_value.exists.return_value = False
        self.assert_denied(self.request(roles=[RoleConstants.USER]))

    def test_tool_list_permission_does_not_grant_access_to_unshared_or_unauthorized_tool(self):
        self.get_authorized_tool.return_value.exists.return_value = False
        self.assert_denied(self.request(permissions=[PermissionConstants.TOOL_READ.get_workspace_permission()]))

    def test_missing_shared_authorization_handler_does_not_grant_access(self):
        with patch.dict(DatabaseModelManage.model_dict, {"get_authorized_tool": None}):
            self.assert_denied(self.request(roles=[RoleConstants.USER]))
        self.tools.filter.assert_not_called()

    def test_personal_permission_works_without_shared_authorization_handler(self):
        with patch.dict(DatabaseModelManage.model_dict, {"get_authorized_tool": None}):
            self.get_detail(self.request(permissions=[PermissionConstants.TOOL_READ.get_workspace_tool_permission()]))
        self.serializer.return_value.one.assert_called_once()
        self.tools.filter.assert_not_called()

    def test_existing_personal_tool_read_permission_still_works(self):
        self.get_authorized_tool.return_value.exists.return_value = False
        self.get_detail(self.request(permissions=[PermissionConstants.TOOL_READ.get_workspace_tool_permission()]))
        self.serializer.return_value.one.assert_called_once()

    def test_existing_user_resource_permission_still_works(self):
        self.get_authorized_tool.return_value.exists.return_value = False
        self.get_detail(
            self.request(
                roles=[RoleConstants.USER], permissions=[PermissionConstants.TOOL.get_workspace_tool_permission()]
            )
        )
        self.serializer.return_value.one.assert_called_once()

    def test_existing_workspace_manager_access_still_works(self):
        self.get_authorized_tool.return_value.exists.return_value = False
        self.get_detail(self.request(roles=[RoleConstants.WORKSPACE_MANAGE]))
        self.serializer.return_value.one.assert_called_once()

    def test_shared_read_access_does_not_allow_edit_or_delete(self):
        for method in ("put", "delete"):
            with self.subTest(method=method), self.assertRaises(AppUnauthorizedFailed):
                getattr(ToolView.Operate(), method)(
                    self.request(roles=[RoleConstants.USER]), workspace_id=self.workspace_id, tool_id=self.tool_id
                )
        self.serializer.assert_not_called()

    def test_workspace_tool_edit_permission_does_not_grant_shared_read_access(self):
        self.assert_denied(self.request(permissions=[PermissionConstants.TOOL_EDIT.get_workspace_permission()]))
