# coding=utf-8
import uuid_utils.compat as uuid

from django.test import TestCase

from users.models.user_group import SystemUserGroup


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
