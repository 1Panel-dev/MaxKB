"""Folder tree honors permissions granted through user groups."""

from types import SimpleNamespace
from unittest.mock import patch

from application.models import ApplicationFolder
from django.test import TestCase
from knowledge.models import KnowledgeFolder
from system_manage.models import WorkspaceUserGroupResourcePermission
from tools.models import ToolFolder
from users.models import User
from users.models.user_group import SystemUserGroup, SystemUserGroupRelation

from folders.serializers.folder import FolderTreeSerializer


class FolderTreeUserGroupPermissionTests(TestCase):
    workspace_id = "00000000-0000-0000-0000-000000000010"
    user_id = "00000000-0000-0000-0000-000000000011"
    group_id = "00000000-0000-0000-0000-000000000012"
    allowed_folder_id = "00000000-0000-0000-0000-000000000013"
    other_folder_id = "00000000-0000-0000-0000-000000000014"
    folder_types = (
        ("KNOWLEDGE", KnowledgeFolder),
        ("APPLICATION", ApplicationFolder),
        ("TOOL", ToolFolder),
    )

    def setUp(self):
        self.user = User.objects.create(
            id=self.user_id,
            username="folder-tree-user",
            nick_name="folder tree user",
            password="x",
            role="USER",
        )
        group = SystemUserGroup.objects.create(id=self.group_id, name="group B", workspace_id=self.workspace_id)
        SystemUserGroupRelation.objects.create(user=self.user, group=group)

        for source, folder_model in self.folder_types:
            root = folder_model.objects.create(id=self.workspace_id, name="root", workspace_id=self.workspace_id)
            folder_model.objects.create(
                id=self.allowed_folder_id, name="111", workspace_id=self.workspace_id, parent=root
            )
            folder_model.objects.create(
                id=self.other_folder_id, name="other", workspace_id=self.workspace_id, parent=root
            )
            WorkspaceUserGroupResourcePermission.objects.create(
                workspace_id=self.workspace_id,
                user_group=group,
                auth_target_type=source,
                target=self.allowed_folder_id,
                permission_list=["VIEW"],
            )

    @patch("folders.serializers.folder.is_workspace_manage", return_value=False)
    def test_group_granted_folder_appears_in_each_resource_tree(self, _is_workspace_manage):
        for source, _folder_model in self.folder_types:
            with self.subTest(source=source):
                result = FolderTreeSerializer(
                    data={"workspace_id": self.workspace_id, "source": source}
                ).get_folder_tree(SimpleNamespace(id=self.user_id), name=None)

                root = next(node for node in result if node["id"] == self.workspace_id)
                child_ids = [child["id"] for child in root["children"]]
                self.assertIn(self.allowed_folder_id, child_ids)
                self.assertNotIn(self.other_folder_id, child_ids)
