from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase

from common.auth.constants.permission_constants import PermissionConstants
from common.auth.struct.aggregate_permission import AggregatePermission
from common.exception.app_exception import AppUnauthorizedFailed
from system_manage.models import ChatUser, UserGroup, UserGroupRelation
from system_manage.serializers.chat_user import ChatUserSerializer
from system_manage.views import resource_chat_user_group
from system_manage.views.resource_chat_user import ResourceChatUser, get_chat_user_permission_constant


class ChatUserPermissionTests(SimpleTestCase):
    @staticmethod
    def build_permissions(items, request, kwargs, compare):
        for item in items:
            if callable(item) and not isinstance(item, AggregatePermission):
                item(request, kwargs)
        return SimpleNamespace(hasPermission=lambda *args, **kwargs: True)

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
