"""Exercise the real folder models and MPTT writes in the Django test database."""

from unittest.mock import patch
from uuid import UUID

from django.test import TestCase

from application.models import ApplicationFolder
from folders.serializers.folder import FolderSerializer, FolderTreeSerializer
from knowledge.models import KnowledgeFolder
from tools.models import ToolFolder


class FolderTreeCompatibilityTests(TestCase):
    folder_types = (
        ("APPLICATION", ApplicationFolder),
        ("KNOWLEDGE", KnowledgeFolder),
        ("TOOL", ToolFolder),
    )

    def make_tree(self, model, workspace="compat-workspace"):
        root = model.objects.create(id=workspace, name=workspace, workspace_id=workspace)
        left = model.objects.create(id=f"{workspace}-left", name="A", workspace_id=workspace, parent=root)
        right = model.objects.create(id=f"{workspace}-right", name="B", workspace_id=workspace, parent=root)
        leaf = model.objects.create(id=f"{workspace}-leaf", name="leaf", workspace_id=workspace, parent=left)
        for node in (root, left, right, leaf):
            node.refresh_from_db()
        return root, left, right, leaf

    def assert_valid_tree(self, model, workspace):
        nodes = list(model.objects.filter(workspace_id=workspace))
        by_id = {node.id: node for node in nodes}
        bounds = []
        for node in nodes:
            bounds.extend([node.lft, node.rght])
            self.assertLess(node.lft, node.rght)
            if node.parent_id:
                parent = by_id[node.parent_id]
                self.assertEqual(node.tree_id, parent.tree_id)
                self.assertEqual(node.level, parent.level + 1)
                self.assertLess(parent.lft, node.lft)
                self.assertLess(node.rght, parent.rght)
        self.assertEqual(sorted(bounds), list(range(1, 2 * len(nodes) + 1)))
        self.assertEqual(len({node.tree_id for node in nodes}), 1)

    def operation(self, source, node):
        return FolderSerializer.Operate(
            data={
                "id": node.id,
                "workspace_id": node.workspace_id,
                "source": source,
                "user_id": UUID(int=1),
            }
        )

    def test_creation_and_rename_preserve_sorted_children_and_ancestry(self):
        for source, model in self.folder_types:
            with self.subTest(source=source):
                root, left, right, leaf = self.make_tree(model)
                self.assertEqual(list(root.get_children().values_list("id", flat=True)), [left.id, right.id])
                self.assertEqual(list(leaf.get_ancestors().values_list("id", flat=True)), [root.id, left.id])
                left.name = "Z"
                left.save()
                root.refresh_from_db()
                self.assertEqual(list(root.get_children().values_list("id", flat=True)), [right.id, left.id])
                self.assert_valid_tree(model, root.workspace_id)

    @patch("folders.serializers.folder.has_target_permission", return_value=True)
    def test_serializer_moves_a_subtree_without_losing_descendants(self, _permission):
        for source, model in self.folder_types:
            with self.subTest(source=source):
                root, left, right, leaf = self.make_tree(model)
                result = self.operation(source, left).edit({"parent_id": right.id})
                self.assertEqual(result["parent_id"], right.id)
                leaf.refresh_from_db()
                self.assertEqual(list(leaf.get_ancestors().values_list("id", flat=True)), [root.id, right.id, left.id])
                self.assert_valid_tree(model, root.workspace_id)

    def test_move_to_refreshes_instances_loaded_before_another_move(self):
        for source, model in self.folder_types:
            with self.subTest(source=source):
                root, left, right, leaf = self.make_tree(model)
                stale_target = model.objects.get(pk=right.pk)
                extra = model.objects.create(id="compat-extra", name="0", workspace_id=root.workspace_id, parent=root)
                extra.move_to(right, "last-child")
                leaf.move_to(stale_target, "last-child")
                leaf.refresh_from_db()
                self.assertEqual(leaf.parent_id, right.id)
                self.assert_valid_tree(model, root.workspace_id)

    def test_workspace_rebuild_preserves_other_workspaces(self):
        for source, model in self.folder_types:
            with self.subTest(source=source):
                root, _, _, _ = self.make_tree(model)
                other, _, _, _ = self.make_tree(model, "compat-other")
                columns = ("id", "parent_id", "tree_id", "lft", "rght", "level")
                before = list(model.objects.filter(workspace_id=other.workspace_id).values_list(*columns))
                model.objects.filter(workspace_id=root.workspace_id).update(lft=0, rght=0)
                FolderTreeSerializer._rebuild_workspace_tree(model, root.workspace_id)
                self.assert_valid_tree(model, root.workspace_id)
                self.assertEqual(
                    list(model.objects.filter(workspace_id=other.workspace_id).values_list(*columns)), before
                )

    @patch("folders.serializers.folder.is_workspace_manage", return_value=True)
    def test_serializer_deletes_subtree_and_closes_gaps(self, _permission):
        for source, model in self.folder_types:
            with self.subTest(source=source):
                root, left, right, leaf = self.make_tree(model)
                self.operation(source, left).delete()
                self.assertFalse(model.objects.filter(pk__in=[left.pk, leaf.pk]).exists())
                self.assertTrue(model.objects.filter(pk=right.pk).exists())
                self.assert_valid_tree(model, root.workspace_id)
