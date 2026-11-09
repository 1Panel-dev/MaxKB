from types import SimpleNamespace
from unittest.mock import patch

from django.core.cache import cache
from django.http import QueryDict
from django.test import SimpleTestCase, TestCase

from common.auth.constants.permission_constants import PermissionConstants
from common.auth.constants.role_constants import RoleConstants
from common.auth.handle.impl.user_token import get_auth
from common.auth.struct.aggregate_permission import AggregatePermission
from common.auth.struct.auth import Principal
from common.auth.struct.permission import Permission
from common.constants.authentication_type import UserType
from common.constants.cache_version import Cache_Version
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.exception.app_exception import AppUnauthorizedFailed
from role_setting.models import RolePermission, RoleSetting, UserRoleRelation
from system_manage.models import ChatUser, UserGroup, UserGroupRelation
from system_manage.models.log_management import Log
from system_manage.serializers.chat_user import ChatUserSerializer
from system_manage.views import (
    resource_chat_user_group,
    user_group_resource_permission,
    user_resource_permission,
)
from system_manage.views.resource_chat_user import ResourceChatUser, get_chat_user_permission_constant
from users.models import User


class ChatUserPermissionTests(SimpleTestCase):
    workspace_id = "workspace-1"
    resource_id = "resource-1"

    @staticmethod
    def build_permissions(items, request, kwargs, compare):
        for item in items:
            if callable(item) and not isinstance(item, AggregatePermission):
                item(request, kwargs)
        return SimpleNamespace(hasPermission=lambda *args, **kwargs: True)

    @classmethod
    def build_extended_user_request(cls, permission_constant):
        source = permission_constant.value
        permission = Permission(
            group=source.group,
            sub_group=source.sub_group,
            operate=source.operate,
            bit_index=source.bit_index,
            workspace_id=cls.workspace_id,
            resource_id=cls.resource_id,
        )
        return SimpleNamespace(
            query_params={},
            data=[],
            auth=SimpleNamespace(
                roles={f"EXTENDS_USER:w:{cls.workspace_id}"},
                permissions={permission.get_resource_permission_key(cls.resource_id): permission.bit()},
            ),
        )

    @classmethod
    def endpoint_kwargs(cls):
        return {
            "workspace_id": cls.workspace_id,
            "resource_type": "APPLICATION",
            "resource_id": cls.resource_id,
            "user_group_id": "group-1",
        }

    def test_supported_resources_keep_existing_permissions(self):
        self.assertEqual(
            PermissionConstants.APPLICATION_CHAT_USER_READ,
            get_chat_user_permission_constant("APPLICATION", "READ"),
        )
        self.assertEqual(
            PermissionConstants.KNOWLEDGE_CHAT_USER_EDIT,
            get_chat_user_permission_constant("KNOWLEDGE", "EDIT"),
        )

    def test_tool_resource_returns_forbidden_without_i18n_key(self):
        with self.assertRaises(AppUnauthorizedFailed) as context:
            get_chat_user_permission_constant("TOOL", "READ")

        self.assertEqual(403, context.exception.status_code)
        self.assertNotIn("CHAT_USER", str(context.exception.message))

    def test_list_page_and_group_endpoints_reject_tool_permission(self):
        kwargs = {
            "workspace_id": "workspace-1",
            "resource_type": "TOOL",
            "resource_id": "resource-1",
            "user_group_id": "group-1",
        }

        with patch("common.auth.authentication._build", side_effect=self.build_permissions):
            with self.assertRaises(AppUnauthorizedFailed):
                ResourceChatUser.get(ResourceChatUser(), SimpleNamespace(), **kwargs)
            with self.assertRaises(AppUnauthorizedFailed):
                ResourceChatUser.Page.get(
                    ResourceChatUser.Page(),
                    SimpleNamespace(),
                    **kwargs,
                    current_page=1,
                    page_size=20,
                )
            with self.assertRaises(AppUnauthorizedFailed):
                resource_chat_user_group.ResourceChatUserGroup.get(
                    resource_chat_user_group.ResourceChatUserGroup(), SimpleNamespace(), **kwargs
                )

    def test_extended_user_can_read_chat_users_and_groups(self):
        request = self.build_extended_user_request(PermissionConstants.APPLICATION_CHAT_USER_READ)
        kwargs = self.endpoint_kwargs()
        group_kwargs = {key: value for key, value in kwargs.items() if key != "user_group_id"}

        with (
            patch("system_manage.views.resource_chat_user.ResourceChatUserQuerySerializer") as user_query,
            patch("system_manage.views.resource_chat_user_group.ResourceChatUserGroupQuerySerializer") as group_query,
        ):
            user_query.return_value.list.return_value = []
            user_query.return_value.page.return_value = []
            group_query.return_value.list.return_value = []
            group_query.return_value.page.return_value = []

            ResourceChatUser.get(ResourceChatUser(), request, **kwargs)
            ResourceChatUser.Page.get(ResourceChatUser.Page(), request, **kwargs, current_page=1, page_size=20)
            resource_chat_user_group.ResourceChatUserGroup.get(
                resource_chat_user_group.ResourceChatUserGroup(), request, **group_kwargs
            )
            resource_chat_user_group.ResourceChatUserGroup.Page.get(
                resource_chat_user_group.ResourceChatUserGroup.Page(),
                request,
                **group_kwargs,
                current_page=1,
                page_size=20,
            )

    def test_extended_user_can_edit_chat_users_and_groups(self):
        request = self.build_extended_user_request(PermissionConstants.APPLICATION_CHAT_USER_EDIT)
        kwargs = self.endpoint_kwargs()
        group_kwargs = {key: value for key, value in kwargs.items() if key != "user_group_id"}

        with (
            patch("system_manage.views.resource_chat_user.ResourceChatUserSerializer") as user_edit,
            patch("system_manage.views.resource_chat_user_group.ResourceChatUserGroupSerializer") as group_edit,
        ):
            user_edit.return_value.edit.return_value = []
            group_edit.return_value.edit.return_value = []
            ResourceChatUser.put(ResourceChatUser(), request, **kwargs)
            resource_chat_user_group.ResourceChatUserGroup.put(
                resource_chat_user_group.ResourceChatUserGroup(), request, **group_kwargs
            )

        user_edit.return_value.edit.assert_called_once_with([])
        group_edit.return_value.edit.assert_called_once_with([])


class ResourcePermissionViewTests(SimpleTestCase):
    workspace_id = "workspace-1"
    other_workspace_id = "workspace-2"
    resources = ("APPLICATION", "KNOWLEDGE", "TOOL", "MODEL")
    resource_permission_bits = {
        "APPLICATION": (1 << 0, 1 << 1),
        "KNOWLEDGE": (1 << 2, 1 << 3),
        "TOOL": (1 << 4, 1 << 5),
        "MODEL": (1 << 6, 1 << 7),
    }

    @staticmethod
    def build_request(roles, permissions=None):
        return SimpleNamespace(
            query_params=QueryDict(),
            data={},
            user=None,
            META={},
            path="/",
            auth=SimpleNamespace(roles=set(roles), permissions=permissions or {}),
        )

    def detailed_permissions(self, resource, operations):
        read_bit, edit_bit = self.resource_permission_bits[resource]
        bits = 0
        if "READ" in operations:
            bits |= read_bit
        if "EDIT" in operations:
            bits |= edit_bit
        return {"RESOURCE_PERMISSION": bits}

    def endpoint_calls(self, request, workspace_id, resource):
        user_view = user_resource_permission.WorkSpaceUserResourcePermissionView()
        user_group_view = user_group_resource_permission.WorkSpaceUserGroupResourcePermissionView()
        user_kwargs = {
            "workspace_id": workspace_id,
            "user_id": "user-1",
            "resource": resource,
        }
        user_group_kwargs = {
            "workspace_id": workspace_id,
            "user_group_id": "group-1",
            "resource": resource,
        }
        return {
            ("READ", "user list"): lambda: user_view.get(request, **user_kwargs),
            ("READ", "user page"): lambda: user_view.Page.get(
                user_view.Page(), request, **user_kwargs, current_page=1, page_size=20
            ),
            ("EDIT", "user edit"): lambda: user_view.put(request, **user_kwargs),
            ("READ", "user group list"): lambda: user_group_view.get(request, **user_group_kwargs),
            ("READ", "user group page"): lambda: user_group_view.Page.get(
                user_group_view.Page(), request, **user_group_kwargs, current_page=1, page_size=20
            ),
            ("EDIT", "user group edit"): lambda: user_group_view.put(request, **user_group_kwargs),
        }

    def assert_endpoint_operations(self, request, workspace_id, resource, allowed_operations):
        with (
            patch.object(Log, "save"),
            patch("system_manage.views.user_resource_permission.result.success", return_value=True),
            patch("system_manage.views.user_resource_permission.UserResourcePermissionSerializer") as user_serializer,
            patch(
                "system_manage.views.user_group_resource_permission.UserGroupResourcePermissionSerializer"
            ) as user_group_serializer,
        ):
            user_serializer.return_value.list.return_value = None
            user_serializer.return_value.page.return_value = None
            user_serializer.return_value.edit.return_value = None
            user_group_serializer.return_value.list.return_value = None
            user_group_serializer.return_value.page.return_value = None
            user_group_serializer.return_value.edit.return_value = None

            for (operation, endpoint), call in self.endpoint_calls(request, workspace_id, resource).items():
                with self.subTest(resource=resource, endpoint=endpoint):
                    if operation in allowed_operations:
                        self.assertIs(True, call())
                    else:
                        with self.assertRaises(AppUnauthorizedFailed):
                            call()

    def test_builtin_admin_can_access_all_resource_authorization_endpoints(self):
        request = self.build_request({"ADMIN"})

        for resource in self.resources:
            with self.subTest(resource=resource):
                self.assert_endpoint_operations(
                    request,
                    self.workspace_id,
                    resource,
                    {"READ", "EDIT"},
                )

    def test_builtin_workspace_manager_can_access_own_workspace(self):
        request = self.build_request(
            {
                "WORKSPACE_MANAGE",
                f"WORKSPACE_MANAGE:w:{self.workspace_id}",
            }
        )

        for resource in self.resources:
            with self.subTest(resource=resource):
                self.assert_endpoint_operations(
                    request,
                    self.workspace_id,
                    resource,
                    {"READ", "EDIT"},
                )

    def test_builtin_workspace_manager_cannot_access_other_workspace(self):
        request = self.build_request(
            {
                "WORKSPACE_MANAGE",
                f"WORKSPACE_MANAGE:w:{self.workspace_id}",
            }
        )

        for resource in self.resources:
            with self.subTest(resource=resource):
                self.assert_endpoint_operations(request, self.other_workspace_id, resource, set())

    def test_inherited_roles_need_matching_read_and_edit_permissions(self):
        roles_list = (
            {"EXTENDS_ADMIN"},
            {f"EXTENDS_WORKSPACE_MANAGE:w:{self.workspace_id}"},
        )

        for roles in roles_list:
            for resource in self.resources:
                with self.subTest(roles=roles, resource=resource, permissions="none"):
                    self.assert_endpoint_operations(
                        self.build_request(roles),
                        self.workspace_id,
                        resource,
                        set(),
                    )
                with self.subTest(roles=roles, resource=resource, permissions="READ"):
                    self.assert_endpoint_operations(
                        self.build_request(roles, self.detailed_permissions(resource, {"READ"})),
                        self.workspace_id,
                        resource,
                        {"READ"},
                    )
                with self.subTest(roles=roles, resource=resource, permissions="EDIT"):
                    self.assert_endpoint_operations(
                        self.build_request(roles, self.detailed_permissions(resource, {"EDIT"})),
                        self.workspace_id,
                        resource,
                        {"EDIT"},
                    )


class ResourceTargetPermissionViewTests(SimpleTestCase):
    workspace_id = "workspace-1"
    other_workspace_id = "workspace-2"
    target = "target-1"
    resources = ("APPLICATION", "KNOWLEDGE", "TOOL", "MODEL")
    resource_authorization_bits = {
        "APPLICATION": 1 << 10,
        "KNOWLEDGE": 1 << 10,
        "TOOL": 1 << 9,
        "MODEL": 1 << 5,
    }
    system_authorization_permissions = {
        "APPLICATION": ("SYSTEM_RESOURCE_APPLICATION", 1 << 5),
        "KNOWLEDGE": ("SYSTEM_RESOURCE_KNOWLEDGE", 1 << 8),
        "TOOL": ("SYSTEM_RESOURCE_TOOL", 1 << 5),
        "MODEL": ("SYSTEM_RESOURCE_MODEL", 1 << 3),
    }

    @staticmethod
    def build_request(roles, permissions=None):
        return SimpleNamespace(
            query_params=QueryDict(),
            data={},
            user=SimpleNamespace(
                id="user-1",
                type="SYSTEM_USER",
                email="user@example.com",
                phone="",
                nick_name="User",
                username="user-1",
            ),
            META={},
            path="/",
            auth=SimpleNamespace(roles=set(roles), permissions=permissions or {}),
        )

    def detailed_permissions(self, resource, workspace_id, workspace_manage=False):
        permission = {f"{resource}:w:{workspace_id}:r:{self.target}": self.resource_authorization_bits[resource]}
        if workspace_manage:
            permission[f"{resource}_WORKSPACE_MANAGE:w:{workspace_id}"] = self.resource_authorization_bits[resource]
        return permission

    def system_authorization(self, resource):
        key, bit = self.system_authorization_permissions[resource]
        return {key: bit}

    def endpoint_calls(self, request, workspace_id, resource):
        user_view = user_resource_permission.WorkspaceResourceUserPermissionView()
        user_group_view = user_group_resource_permission.WorkspaceResourceUserGroupPermissionView()
        kwargs = {
            "workspace_id": workspace_id,
            "target": self.target,
            "resource": resource,
        }
        return {
            "user list": lambda: user_view.get(request, **kwargs),
            "user page": lambda: user_view.Page.get(user_view.Page(), request, **kwargs, current_page=1, page_size=20),
            "user edit": lambda: user_view.put(request, **kwargs),
            "user group list": lambda: user_group_view.get(request, **kwargs),
            "user group page": lambda: user_group_view.Page.get(
                user_group_view.Page(), request, **kwargs, current_page=1, page_size=20
            ),
            "user group edit": lambda: user_group_view.put(request, **kwargs),
        }

    def assert_endpoint_access(self, request, workspace_id, resource, allowed):
        with (
            patch.object(Log, "save"),
            patch("system_manage.views.user_resource_permission.result.success", return_value=True),
            patch("system_manage.views.user_resource_permission.ResourceUserPermissionSerializer") as user_serializer,
            patch(
                "system_manage.views.user_group_resource_permission.ResourceUserGroupPermissionSerializer"
            ) as user_group_serializer,
        ):
            user_serializer.return_value.list.return_value = None
            user_serializer.return_value.page.return_value = None
            user_serializer.return_value.edit.return_value = None
            user_group_serializer.return_value.list.return_value = None
            user_group_serializer.return_value.page.return_value = None
            user_group_serializer.return_value.edit.return_value = None

            for endpoint, call in self.endpoint_calls(request, workspace_id, resource).items():
                with self.subTest(resource=resource, endpoint=endpoint):
                    if allowed:
                        self.assertIs(True, call())
                    else:
                        with self.assertRaises(AppUnauthorizedFailed):
                            call()

    def test_builtin_admin_can_access_target_authorization_endpoints(self):
        request = self.build_request({"ADMIN"})

        for resource in self.resources:
            with self.subTest(resource=resource):
                self.assert_endpoint_access(request, self.workspace_id, resource, True)

    def test_workspace_manager_is_limited_to_own_workspace(self):
        request = self.build_request(
            {
                "WORKSPACE_MANAGE",
                f"WORKSPACE_MANAGE:w:{self.workspace_id}",
            }
        )

        for resource in self.resources:
            with self.subTest(resource=resource, workspace="own"):
                self.assert_endpoint_access(request, self.workspace_id, resource, True)
            with self.subTest(resource=resource, workspace="other"):
                self.assert_endpoint_access(request, self.other_workspace_id, resource, False)

    def test_inherited_admin_requires_system_resource_authorization_permission(self):
        for resource in self.resources:
            roles = {"EXTENDS_ADMIN"}
            with self.subTest(resource=resource, permissions="none"):
                self.assert_endpoint_access(self.build_request(roles), self.workspace_id, resource, False)
            with self.subTest(resource=resource, permissions="system authorization"):
                self.assert_endpoint_access(
                    self.build_request(roles, self.system_authorization(resource)),
                    self.workspace_id,
                    resource,
                    True,
                )
                self.assert_endpoint_access(
                    self.build_request(roles, self.system_authorization(resource)),
                    self.other_workspace_id,
                    resource,
                    True,
                )

    def test_inherited_workspace_manager_is_limited_to_workspace(self):
        roles = {f"EXTENDS_WORKSPACE_MANAGE:w:{self.workspace_id}"}

        for resource in self.resources:
            with self.subTest(resource=resource, permissions="none"):
                self.assert_endpoint_access(self.build_request(roles), self.workspace_id, resource, False)
            with self.subTest(resource=resource, permissions="resource authorization"):
                permissions = self.detailed_permissions(resource, self.workspace_id)
                self.assert_endpoint_access(
                    self.build_request(roles, permissions),
                    self.workspace_id,
                    resource,
                    True,
                )
                self.assert_endpoint_access(
                    self.build_request(roles, permissions),
                    self.other_workspace_id,
                    resource,
                    False,
                )


class ResourcePermissionRealAuthTests(TestCase):
    workspace_id = "workspace-1"
    other_workspace_id = "workspace-2"
    target = "target-1"
    resources = ("APPLICATION", "KNOWLEDGE", "TOOL", "MODEL")
    system_auth_permissions = {
        "APPLICATION": "RESOURCE_APPLICATION_AUTH",
        "KNOWLEDGE": "RESOURCE_KNOWLEDGE_AUTH",
        "TOOL": "RESOURCE_TOOL_AUTH",
        "MODEL": "RESOURCE_MODEL_AUTH",
    }

    def setUp(self):
        DatabaseModelManage.init()
        self.user = User.objects.create(
            username="resource-permission-user",
            nick_name="Resource Permission User",
            password="encrypted-password",
            role=RoleConstants.USER.name,
        )

    def tearDown(self):
        self.clear_auth_cache()
        super().tearDown()

    def clear_auth_cache(self):
        for cache_version in (Cache_Version.PERMISSION_LIST, Cache_Version.ROLE_LIST):
            cache.delete(
                cache_version.get_key(user_id=self.user.id),
                version=cache_version.get_version(),
            )

    def assign_role(self, role_type, workspace_id, permission_names):
        role = RoleSetting.objects.create(
            role_name=f"custom-{role_type}-{workspace_id}",
            internal=False,
            type=role_type,
        )
        UserRoleRelation.objects.create(user=self.user, role=role, workspace_id=workspace_id)
        RolePermission.objects.bulk_create(
            [
                RolePermission(
                    role=role,
                    permission_id=str(PermissionConstants[permission_name].value),
                )
                for permission_name in permission_names
            ]
        )
        self.clear_auth_cache()
        return role

    def assign_builtin_role(self, role_id, workspace_id):
        UserRoleRelation.objects.create(
            user=self.user,
            role=RoleSetting.objects.get(id=role_id),
            workspace_id=workspace_id,
        )
        self.clear_auth_cache()

    def build_request(self):
        return SimpleNamespace(
            query_params=QueryDict(),
            data={},
            user=Principal(self.user.id, UserType.SYSTEM_USER, self.user),
            META={},
            path="/",
            auth=get_auth(self.user),
        )

    def assert_list_permissions(self, request, workspace_id, resource, allowed_operations):
        user_view = user_resource_permission.WorkSpaceUserResourcePermissionView()
        user_group_view = user_group_resource_permission.WorkSpaceUserGroupResourcePermissionView()
        user_kwargs = {
            "workspace_id": workspace_id,
            "user_id": str(self.user.id),
            "resource": resource,
        }
        user_group_kwargs = {
            "workspace_id": workspace_id,
            "user_group_id": "group-1",
            "resource": resource,
        }
        calls = {
            ("READ", "user list"): lambda: user_view.get(request, **user_kwargs),
            ("READ", "user page"): lambda: user_view.Page.get(
                user_view.Page(), request, **user_kwargs, current_page=1, page_size=20
            ),
            ("EDIT", "user edit"): lambda: user_view.put(request, **user_kwargs),
            ("READ", "user group list"): lambda: user_group_view.get(request, **user_group_kwargs),
            ("READ", "user group page"): lambda: user_group_view.Page.get(
                user_group_view.Page(), request, **user_group_kwargs, current_page=1, page_size=20
            ),
            ("EDIT", "user group edit"): lambda: user_group_view.put(request, **user_group_kwargs),
        }
        with (
            patch.object(Log, "save"),
            patch("system_manage.views.user_resource_permission.result.success", return_value=True),
            patch("system_manage.views.user_resource_permission.UserResourcePermissionSerializer") as user_serializer,
            patch(
                "system_manage.views.user_group_resource_permission.UserGroupResourcePermissionSerializer"
            ) as user_group_serializer,
        ):
            user_serializer.return_value.list.return_value = None
            user_serializer.return_value.page.return_value = None
            user_serializer.return_value.edit.return_value = None
            user_group_serializer.return_value.list.return_value = None
            user_group_serializer.return_value.page.return_value = None
            user_group_serializer.return_value.edit.return_value = None

            for (operation, endpoint), call in calls.items():
                with self.subTest(resource=resource, endpoint=endpoint, workspace_id=workspace_id):
                    if operation in allowed_operations:
                        self.assertIs(True, call())
                    else:
                        with self.assertRaises(AppUnauthorizedFailed):
                            call()

    def assert_target_permissions(self, request, workspace_id, resource, allowed):
        user_view = user_resource_permission.WorkspaceResourceUserPermissionView()
        user_group_view = user_group_resource_permission.WorkspaceResourceUserGroupPermissionView()
        kwargs = {
            "workspace_id": workspace_id,
            "target": self.target,
            "resource": resource,
        }
        calls = {
            "user list": lambda: user_view.get(request, **kwargs),
            "user page": lambda: user_view.Page.get(user_view.Page(), request, **kwargs, current_page=1, page_size=20),
            "user edit": lambda: user_view.put(request, **kwargs),
            "user group list": lambda: user_group_view.get(request, **kwargs),
            "user group page": lambda: user_group_view.Page.get(
                user_group_view.Page(), request, **kwargs, current_page=1, page_size=20
            ),
            "user group edit": lambda: user_group_view.put(request, **kwargs),
        }
        with (
            patch.object(Log, "save"),
            patch("system_manage.views.user_resource_permission.result.success", return_value=True),
            patch("system_manage.views.user_resource_permission.ResourceUserPermissionSerializer") as user_serializer,
            patch(
                "system_manage.views.user_group_resource_permission.ResourceUserGroupPermissionSerializer"
            ) as user_group_serializer,
        ):
            user_serializer.return_value.list.return_value = None
            user_serializer.return_value.page.return_value = None
            user_serializer.return_value.edit.return_value = None
            user_group_serializer.return_value.list.return_value = None
            user_group_serializer.return_value.page.return_value = None
            user_group_serializer.return_value.edit.return_value = None

            for endpoint, call in calls.items():
                with self.subTest(resource=resource, endpoint=endpoint, workspace_id=workspace_id):
                    if allowed:
                        self.assertIs(True, call())
                    else:
                        with self.assertRaises(AppUnauthorizedFailed):
                            call()

    def test_builtin_admin_uses_role(self):
        self.assign_builtin_role(RoleConstants.ADMIN.name, "None")
        request = self.build_request()
        for resource in self.resources:
            with self.subTest(role="ADMIN", resource=resource):
                self.assert_list_permissions(request, self.workspace_id, resource, {"READ", "EDIT"})
                self.assert_target_permissions(request, self.workspace_id, resource, True)

    def test_builtin_workspace_manage_is_limited_to_workspace(self):
        self.assign_builtin_role(RoleConstants.WORKSPACE_MANAGE.name, self.workspace_id)
        request = self.build_request()
        for resource in self.resources:
            with self.subTest(role="WORKSPACE_MANAGE", resource=resource, workspace="own"):
                self.assert_list_permissions(request, self.workspace_id, resource, {"READ", "EDIT"})
                self.assert_target_permissions(request, self.workspace_id, resource, True)
            with self.subTest(role="WORKSPACE_MANAGE", resource=resource, workspace="other"):
                self.assert_list_permissions(request, self.other_workspace_id, resource, set())
                self.assert_target_permissions(request, self.other_workspace_id, resource, False)

    def test_inherited_admin_requires_system_resource_permissions(self):
        self.assign_role(RoleConstants.ADMIN.name, "None", [])
        request = self.build_request()
        for resource in self.resources:
            with self.subTest(resource=resource, permissions="none"):
                self.assert_list_permissions(request, self.workspace_id, resource, set())
                self.assert_target_permissions(request, self.workspace_id, resource, False)

        RolePermission.objects.all().delete()
        permissions = (
            [f"{resource}_RESOURCE_PERMISSION_READ" for resource in self.resources]
            + [f"{resource}_RESOURCE_PERMISSION_EDIT" for resource in self.resources]
            + list(self.system_auth_permissions.values())
        )
        role = RoleSetting.objects.get(role_name=f"custom-{RoleConstants.ADMIN.name}-None")
        RolePermission.objects.bulk_create(
            [
                RolePermission(
                    role=role,
                    permission_id=str(PermissionConstants[permission_name].value),
                )
                for permission_name in permissions
            ]
        )
        self.clear_auth_cache()
        request = self.build_request()
        for resource in self.resources:
            with self.subTest(resource=resource, permissions="detailed"):
                self.assert_list_permissions(request, self.workspace_id, resource, {"READ", "EDIT"})
                self.assert_target_permissions(request, self.workspace_id, resource, True)
                self.assert_target_permissions(request, self.other_workspace_id, resource, True)

    def test_inherited_workspace_manage_requires_permissions_within_workspace(self):
        resources = self.resources
        self.assign_role(
            RoleConstants.WORKSPACE_MANAGE.name,
            self.workspace_id,
            [f"{resource}_RESOURCE_PERMISSION_READ" for resource in resources]
            + [f"{resource}_RESOURCE_PERMISSION_EDIT" for resource in resources]
            + [f"{resource}_RESOURCE_AUTHORIZATION" for resource in resources],
        )
        request = self.build_request()
        for resource in resources:
            with self.subTest(resource=resource, workspace="own"):
                self.assert_list_permissions(request, self.workspace_id, resource, {"READ", "EDIT"})
                self.assert_target_permissions(request, self.workspace_id, resource, True)
            with self.subTest(resource=resource, workspace="other"):
                self.assert_list_permissions(request, self.other_workspace_id, resource, set())
                self.assert_target_permissions(request, self.other_workspace_id, resource, False)


class ChatUserEditTests(TestCase):
    def test_status_and_password_changes_preserve_user_groups(self):
        user = ChatUser.objects.create(
            username="chat-user",
            nick_name="Chat User",
            password="encrypted-password",
        )
        group = UserGroup.objects.create(name="chat-user-group")
        UserGroupRelation.objects.create(user=user, group=group)
        operate = ChatUserSerializer.Operate(data={"id": user.id})

        operate.edit({"is_active": False}, with_valid=True)
        operate.edit({"is_active": True}, with_valid=True)
        operate.re_password({"password": "Password1!", "re_password": "Password1!"}, with_valid=True)

        self.assertTrue(UserGroupRelation.objects.filter(user=user, group=group).exists())
