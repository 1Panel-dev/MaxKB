from django.test import TestCase

from users.models import User
from users.models.user_group import SystemUserGroup, SystemUserGroupRelation
from users.serializers.user import UserManageSerializer


class UserManagementGroupPreservationTests(TestCase):
    def test_status_and_password_changes_preserve_user_groups(self):
        user = User.objects.create(
            username="system-user",
            nick_name="System User",
            password="encrypted-password",
            role="USER",
            source="LOCAL",
        )
        group = SystemUserGroup.objects.create(name="system-user-group", workspace_id="default")
        SystemUserGroupRelation.objects.create(user=user, group=group)
        operate = UserManageSerializer.Operate(data={"id": user.id})

        operate.edit({"is_active": False}, user.id, with_valid=True)
        operate.edit({"is_active": True}, user.id, with_valid=True)
        operate.re_password({"password": "Password1!", "re_password": "Password1!"}, with_valid=True)

        self.assertTrue(SystemUserGroupRelation.objects.filter(user=user, group=group).exists())
