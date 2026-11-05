"""Shared regression cases for workspace resources that can move between folders."""

import json
from types import SimpleNamespace
from unittest.mock import patch

from common.auth.constants.permission_constants import PermissionConstants, RESOURCE_PERMISSION_MAP
from common.auth.constants.role_constants import RoleConstants
from common.exception.app_exception import AppApiException, AppUnauthorizedFailed
from django.urls import resolve
from rest_framework.exceptions import ValidationError


class ResourceMoveTests:
    workspace_id = "test-workspace"
    resource_id = "00000000-0000-0000-0000-000000000001"
    other_id = "00000000-0000-0000-0000-000000000002"

    def setUp(self):
        super().setUp()
        self.enterContext(patch("common.log.log.Log"))
        self.enterContext(patch(f"{self.view_module}.get_{self.domain}_operation_object", return_value={}))
        self.enterContext(patch(f"{self.view_module}.get_{self.domain}_operation_object_batch", return_value={}))

    def permission(self, operation):
        return getattr(PermissionConstants, f"{self.domain.upper()}_{operation}")

    def request(self, operations=(), *, roles=(), workspace_id=None, resource_id=None):
        kwargs = {
            "workspace_id": workspace_id or self.workspace_id,
            f"{self.domain}_id": resource_id or self.resource_id,
        }
        permissions = {}
        for operation in operations:
            permission = self.permission(operation)
            factory = (
                permission.get_workspace_permission()
                if operation == "BATCH_MOVE"
                else getattr(permission, f"get_workspace_{self.domain}_permission")()
            )
            resolved = factory(None, kwargs)
            key = resolved.get_resource_permission_key(resolved.resource_id)
            permissions[key] = permissions.get(key, 0) | resolved.bit()
        return SimpleNamespace(
            auth=SimpleNamespace(
                roles=[str(role.get_workspace_role()(None, kwargs)) for role in roles], permissions=permissions
            ),
            user=SimpleNamespace(id=self.resource_id, type="test"),
            META={},
            path=f"/admin/api/workspace/{self.workspace_id}/{self.domain}/{self.resource_id}/move/target",
            data={},
            query_params={},
        )

    def call_move(self, request):
        return self.view.Move().put(
            request,
            workspace_id=self.workspace_id,
            **{f"{self.domain}_id": self.resource_id, "folder_id": "target"},
        )

    def test_resource_manage_grants_move_but_view_does_not(self):
        permission = self.permission("MOVE")
        self.assertIn(permission, RESOURCE_PERMISSION_MAP[f"{self.domain.upper()}_MANAGE"])
        self.assertNotIn(permission, RESOURCE_PERMISSION_MAP[f"{self.domain.upper()}_VIEW"])

    def test_custom_workspace_manager_move_grant(self):
        request = self.request()
        permission = self.permission("MOVE").get_workspace_permission_workspace_manage_role()(
            None, {"workspace_id": self.workspace_id}
        )
        request.auth.permissions[permission.get_resource_permission_key(None)] = permission.bit()
        with patch(self.view_serializer) as serializer:
            serializer.return_value.move.return_value = True
            self.call_move(request)
            serializer.return_value.move.assert_called_once_with("target")

    def test_move_url_resolves_to_independent_view(self):
        self.assertIs(resolve(self.request().path).func.view_class, self.view.Move)

    def test_move_permission_allows_move_without_edit(self):
        with patch(self.view_serializer) as serializer:
            serializer.return_value.move.return_value = True
            response = self.call_move(self.request(["MOVE"]))
            self.assertEqual(json.loads(response.content)["data"], True)
            serializer.return_value.move.assert_called_once_with("target")
            serializer.return_value.edit.assert_not_called()

    def test_read_edit_and_batch_permissions_do_not_grant_single_move(self):
        for operations in ([], ["READ"], ["EDIT"], ["BATCH_MOVE"]):
            with self.subTest(operations=operations), patch(self.view_serializer) as serializer:
                with self.assertRaises(AppUnauthorizedFailed):
                    self.call_move(self.request(operations))
                serializer.assert_not_called()

    def test_user_with_only_read_or_edit_cannot_move(self):
        for operation in ("READ", "EDIT"):
            with self.subTest(operation=operation), patch(self.view_serializer) as serializer:
                with self.assertRaises(AppUnauthorizedFailed):
                    self.call_move(self.request([operation], roles=[RoleConstants.USER]))
                serializer.assert_not_called()

    def test_user_with_move_permission_can_move(self):
        with patch(self.view_serializer) as serializer:
            serializer.return_value.move.return_value = True
            self.call_move(self.request(["MOVE"], roles=[RoleConstants.USER]))
            serializer.return_value.move.assert_called_once_with("target")

    def test_move_permission_does_not_grant_edit(self):
        with patch(self.view_serializer) as serializer, self.assertRaises(AppUnauthorizedFailed):
            self.view.Operate().put(
                self.request(["MOVE"]), workspace_id=self.workspace_id, **{f"{self.domain}_id": self.resource_id}
            )
        serializer.assert_not_called()

    def test_move_permission_is_scoped_to_resource_and_workspace(self):
        for kwargs in ({"workspace_id": "other-workspace"}, {"resource_id": self.other_id}):
            with self.subTest(kwargs=kwargs), patch(self.view_serializer) as serializer:
                with self.assertRaises(AppUnauthorizedFailed):
                    self.call_move(self.request(["MOVE"], **kwargs))
                serializer.assert_not_called()

    def test_workspace_manager_can_still_move(self):
        with patch(self.view_serializer) as serializer:
            serializer.return_value.move.return_value = True
            self.call_move(self.request(roles=[RoleConstants.WORKSPACE_MANAGE]))
            serializer.return_value.move.assert_called_once_with("target")

    def test_batch_move_filters_by_move_instead_of_edit(self):
        for operation, expected in (("MOVE", [self.resource_id]), ("EDIT", []), ("READ", [])):
            with self.subTest(operation=operation), patch(self.batch_view_serializer) as serializer:
                serializer.return_value.batch_move.return_value = True
                request = self.request(["BATCH_MOVE", operation], roles=[RoleConstants.USER])
                request.data = {"id_list": [self.resource_id, self.other_id], "folder_id": "target"}
                self.view.BatchMove().put(request, workspace_id=self.workspace_id)
                serializer.return_value.batch_move.assert_called_once_with({"id_list": expected, "folder_id": "target"})

    def resource_serializer(self):
        return self.serializer_class(
            data={
                self.serializer_id_key: self.resource_id,
                "user_id": self.resource_id,
                "workspace_id": self.workspace_id,
            }
        )

    def test_move_updates_only_folder_in_current_workspace(self):
        with (
            patch(f"{self.serializer_module}.QuerySet") as query,
            patch.object(self.folder_model, "objects") as folders,
        ):
            self.assertTrue(self.resource_serializer().move("target"))
            folders.filter.assert_called_once_with(id="target", workspace_id=self.workspace_id)
            query.return_value.filter.assert_any_call(id=self.resource_id, workspace_id=self.workspace_id)
            query.return_value.filter.return_value.update.assert_called_once_with(folder_id="target")
            query.return_value.filter.return_value.save.assert_not_called()

    def test_move_rejects_missing_or_foreign_folder(self):
        with (
            patch(f"{self.serializer_module}.QuerySet") as query,
            patch.object(self.folder_model, "objects") as folders,
        ):
            folders.filter.return_value.exists.return_value = False
            with self.assertRaises(ValidationError):
                self.resource_serializer().move("foreign-folder")
            folders.filter.assert_called_once_with(id="foreign-folder", workspace_id=self.workspace_id)
            query.return_value.filter.return_value.update.assert_not_called()

    def test_move_rejects_missing_or_foreign_resource(self):
        with (
            patch(f"{self.serializer_module}.QuerySet") as query,
            patch.object(self.folder_model, "objects") as folders,
        ):
            query.return_value.filter.return_value.filter.return_value.exists.return_value = False
            with self.assertRaises(AppApiException):
                self.resource_serializer().move("target")
            folders.filter.assert_not_called()
            query.return_value.filter.return_value.update.assert_not_called()

    def test_edit_cannot_change_folder(self):
        with patch(f"{self.serializer_module}.QuerySet") as query:
            resource = SimpleNamespace(folder_id="original")
            query.return_value.get.return_value = resource
            query.return_value.filter.return_value.first.return_value = resource
            serializer = self.resource_serializer()
            serializer.is_valid(raise_exception=True)
            # Exercise edit validation without opening a database transaction.
            with self.assertRaises(ValidationError):
                self.serializer_class.edit.__wrapped__(serializer, {"folder_id": "target"})
            self.assertEqual(resource.folder_id, "original")
            query.return_value.filter.return_value.update.assert_not_called()
