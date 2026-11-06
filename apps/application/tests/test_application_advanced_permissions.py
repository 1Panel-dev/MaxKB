from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase

from application.views.application import ApplicationAPI
from application.views.application_api_key import ApplicationApiKeyEnable
from common.auth.constants.group_constants import Group
from common.auth.constants.operate_constants import Operate
from common.auth.constants.permission_constants import PermissionConstants
from common.auth.struct.permission import Permission, Role
from common.exception.app_exception import AppUnauthorizedFailed


class ApplicationAdvancedPermissionTests(TestCase):
    workspace_id = "workspace-a"
    application_id = "00000000-0000-0000-0000-000000000001"

    def kwargs(self):
        return {"workspace_id": self.workspace_id, "application_id": self.application_id}

    def request_with_permission(self, permission_constant):
        permission = permission_constant.get_workspace_application_permission()(None, self.kwargs())
        return self.request_with_permissions(permission)

    def request_with_permissions(self, *permission_values, roles=None):
        permissions = {}
        for permission in permission_values:
            permissions[permission.get_resource_permission_key(permission.resource_id)] = permission.bit()
        resolved_roles = [Role("USER", self.workspace_id)] if roles is None else roles
        return SimpleNamespace(
            auth=SimpleNamespace(roles=resolved_roles, permissions=permissions),
            user=SimpleNamespace(id=self.application_id, type="test"),
            META={"REMOTE_ADDR": "127.0.0.1"},
            path="/test",
            data={
                "enable_api_key": True,
                "id_list": [self.application_id],
                "clean_time": 30,
                "file_clean_time": 7,
            },
            query_params={},
            build_absolute_uri=lambda _: "http://localhost/",
        )

    def test_backend_api_access_uses_dedicated_permission(self):
        request = self.request_with_permission(PermissionConstants.APPLICATION_OVERVIEW_BACKEND_API_ACCESS)
        with (
            patch("application.views.application_api_key.ApiKeyEnableSerializer") as serializer,
            patch("application.views.application_api_key.get_application_operation_object", return_value={}),
        ):
            serializer.return_value.edit.return_value = {}
            ApplicationApiKeyEnable.put(ApplicationApiKeyEnable(), request, **self.kwargs())
            serializer.assert_called_once()

    def test_backend_api_access_rejects_legacy_api_key_permission(self):
        request = self.request_with_permission(PermissionConstants.APPLICATION_OVERVIEW_API_KEY)
        with self.assertRaises(AppUnauthorizedFailed):
            ApplicationApiKeyEnable.put(ApplicationApiKeyEnable(), request, **self.kwargs())

    def test_export_skills_uses_dedicated_permission(self):
        request = self.request_with_permission(PermissionConstants.APPLICATION_EXPORT_SKILLS)
        with (
            patch("application.views.application.ApplicationOperateSerializer") as serializer,
            patch("application.views.application.get_application_operation_object", return_value={}),
        ):
            serializer.return_value.export_skills.return_value = {}
            ApplicationAPI.ExportSkills.get(ApplicationAPI.ExportSkills(), request, **self.kwargs())
            serializer.assert_called_once()

    def test_export_skills_rejects_application_export_permission(self):
        request = self.request_with_permission(PermissionConstants.APPLICATION_EXPORT)
        with self.assertRaises(AppUnauthorizedFailed):
            ApplicationAPI.ExportSkills.get(ApplicationAPI.ExportSkills(), request, **self.kwargs())

    def test_mcp_permission_bits_exist_for_role_tree(self):
        self.assertEqual(PermissionConstants.APPLICATION_MCP_CONFIG.value.operate, Operate.MCP_CONFIG)
        self.assertEqual(PermissionConstants.RESOURCE_APPLICATION_MCP_CONFIG.value.operate, Operate.MCP_CONFIG)
        self.assertEqual(
            PermissionConstants.APPLICATION_OVERVIEW_BACKEND_API_ACCESS.value.operate,
            Operate.BACKEND_API_ACCESS,
        )

    def test_batch_clean_time_rejects_application_read_permission(self):
        request = self.request_with_permissions(
            PermissionConstants.APPLICATION_READ.get_workspace_permission()(None, self.kwargs()),
            PermissionConstants.APPLICATION_CHAT_LOG_CLEAR_POLICY.get_workspace_application_permission()(
                None, self.kwargs()
            ),
            roles=[],
        )
        with (
            patch("application.views.application.ApplicationBatchOperateSerializer"),
            patch("application.views.application.result.success"),
            self.assertRaises(AppUnauthorizedFailed),
        ):
            ApplicationAPI.BatchCleanTime.put(ApplicationAPI.BatchCleanTime(), request, workspace_id=self.workspace_id)

    def test_batch_clean_time_accepts_dedicated_workspace_permission(self):
        request = self.request_with_permissions(
            Permission(
                group=Group.APPLICATION,
                sub_group=Group.APPLICATION,
                operate=Operate.CLEAR_POLICY,
                bit_index=42,
                workspace_id=self.workspace_id,
            ),
            PermissionConstants.APPLICATION_CHAT_LOG_CLEAR_POLICY.get_workspace_application_permission()(
                None, self.kwargs()
            ),
            roles=[],
        )
        with (
            patch("application.views.application.ApplicationBatchOperateSerializer") as serializer,
            patch("application.views.application.get_application_operation_object_batch", return_value=[]),
            patch("application.views.application.result.success"),
        ):
            serializer.return_value.batch_clean_time.return_value = True
            ApplicationAPI.BatchCleanTime.put(ApplicationAPI.BatchCleanTime(), request, workspace_id=self.workspace_id)
            serializer.return_value.batch_clean_time.assert_called_once()
