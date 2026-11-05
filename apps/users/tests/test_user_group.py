# coding=utf-8
import uuid_utils.compat as uuid

from django.test import TestCase

from common.auth.constants.role_constants import RoleConstants
from common.database_model_manage.database_model_manage import DatabaseModelManage
from users.models import User
from users.models.user_group import SystemUserGroup
from users.models.user_group import SystemUserGroupRelation
from users.serializers.user_group import UserGroupListPageSerializer


class SystemUserGroupWorkspaceIsolationTests(TestCase):
    def test_same_group_name_allowed_in_different_workspaces(self):
        SystemUserGroup.objects.create(id=uuid.uuid7(), name="test", workspace_id="default")
        group = SystemUserGroup.objects.create(id=uuid.uuid7(), name="test", workspace_id="jin-feixue")
        self.assertEqual(SystemUserGroup.objects.filter(name="test").count(), 2)
        self.assertEqual(group.workspace_id, "jin-feixue")

    def test_same_group_name_rejected_in_same_workspace(self):
        SystemUserGroup.objects.create(id=uuid.uuid7(), name="test", workspace_id="default")
        with self.assertRaises(Exception):
            SystemUserGroup.objects.create(id=uuid.uuid7(), name="test", workspace_id="default")


class SystemUserGroupMemberRoleFilterTests(TestCase):
    def test_filter_members_by_role(self):
        DatabaseModelManage.init()
        role_model = DatabaseModelManage.get_model("role_model")
        user_role_relation_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
        if role_model is None or user_role_relation_model is None:
            self.skipTest("Role search requires the enterprise role model")

        group = SystemUserGroup.objects.create(name="test-group", workspace_id="workspace-1")
        target_user = User.objects.create(
            username="target-user",
            nick_name="Target User",
            password="encrypted-password",
            role=RoleConstants.USER.name,
        )
        other_user = User.objects.create(
            username="other-user",
            nick_name="Other User",
            password="encrypted-password",
            role=RoleConstants.USER.name,
        )
        SystemUserGroupRelation.objects.create(user=target_user, group=group)
        SystemUserGroupRelation.objects.create(user=other_user, group=group)

        target_role = role_model.objects.create(role_name="知识库管理员", type=RoleConstants.USER.name)
        other_role = role_model.objects.create(role_name="应用管理员", type=RoleConstants.USER.name)
        user_role_relation_model.objects.create(
            user=target_user,
            role=target_role,
            workspace_id=group.workspace_id,
        )
        user_role_relation_model.objects.create(
            user=other_user,
            role=other_role,
            workspace_id=group.workspace_id,
        )

        result = UserGroupListPageSerializer.Query(
            data={
                "workspace_id": group.workspace_id,
                "group_id": group.id,
                "role": "知识库管理员",
            }
        ).page(1, 20)

        self.assertEqual(["target-user"], [member["username"] for member in result["records"]])
