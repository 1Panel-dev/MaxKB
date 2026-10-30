from django.test import TestCase
from rest_framework.exceptions import ValidationError

from common.exception.app_exception import AppApiException
from knowledge.models import Knowledge, KnowledgeFolder, KnowledgeWorkflowVersion
from knowledge.serializers.knowledge_version import KnowledgeWorkflowVersionSerializer


class KnowledgeWorkflowVersionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        folder = KnowledgeFolder.objects.create(id="version-test", name="Version tests")
        cls.knowledge = Knowledge.objects.create(name="Workflow", desc="", folder=folder)
        cls.version = KnowledgeWorkflowVersion.objects.create(
            knowledge=cls.knowledge,
            name="Original version",
            publish_desc="Original notes",
            work_flow={"nodes": [], "edges": []},
        )

    def operation(self, **overrides):
        return KnowledgeWorkflowVersionSerializer.Operate(
            data={
                "workspace_id": "default",
                "knowledge_id": str(self.knowledge.id),
                "knowledge_version_id": str(self.version.id),
                **overrides,
            }
        )

    def test_edit_persists_notes_and_returns_them_on_all_read_paths(self):
        notes = "  修复知识库同步\n保留已有工作流配置\n"
        result = self.operation().edit({"name": "Updated version", "publish_desc": notes})

        self.version.refresh_from_db()
        self.assertEqual(self.version.name, "Updated version")
        self.assertEqual(self.version.publish_desc, notes)
        self.assertEqual(self.version.work_flow, {"nodes": [], "edges": []})
        self.assertEqual(result["publish_desc"], notes)
        self.assertEqual(self.operation().one()["publish_desc"], notes)
        query = KnowledgeWorkflowVersionSerializer.Query(data={"workspace_id": "default"})
        filters = {"knowledge_id": str(self.knowledge.id)}
        self.assertEqual(query.list(filters)[0]["publish_desc"], notes)
        self.assertEqual(query.page(filters, 1, 10)["records"][0]["publish_desc"], notes)

    def test_empty_notes_clear_the_saved_description(self):
        result = self.operation().edit({"publish_desc": ""})

        self.version.refresh_from_db()
        self.assertEqual(self.version.publish_desc, "")
        self.assertEqual(self.version.name, "Original version")
        self.assertEqual(result["publish_desc"], "")
        self.assertEqual(self.operation().one()["publish_desc"], "")

    def test_omitted_or_null_notes_preserve_the_saved_description(self):
        for payload in ({"name": "Renamed version"}, {"name": "Renamed version", "publish_desc": None}):
            with self.subTest(payload=payload):
                result = self.operation().edit(payload)

                self.version.refresh_from_db()
                self.assertEqual(self.version.name, "Renamed version")
                self.assertEqual(self.version.publish_desc, "Original notes")
                self.assertEqual(result["publish_desc"], "Original notes")

    def test_notes_at_the_limit_are_saved(self):
        notes = "说" * 1024
        self.operation().edit({"publish_desc": notes})

        self.version.refresh_from_db()
        self.assertEqual(self.version.publish_desc, notes)

    def test_oversized_notes_reject_the_entire_update(self):
        for notes in ("说" * 1025, "说" + " " * 1024):
            with self.subTest(notes_length=len(notes)):
                with self.assertRaises(ValidationError) as error:
                    self.operation().edit({"name": "Must not be saved", "publish_desc": notes})

                self.assertIn("publish_desc", error.exception.detail)
                self.version.refresh_from_db()
                self.assertEqual(self.version.name, "Original version")
                self.assertEqual(self.version.publish_desc, "Original notes")

    def test_new_versions_without_notes_default_to_empty(self):
        version = KnowledgeWorkflowVersion.objects.create(knowledge=self.knowledge, name="New version")

        self.assertEqual(self.operation(knowledge_version_id=str(version.id)).one()["publish_desc"], "")

    def test_another_workspace_cannot_edit_notes(self):
        with self.assertRaises(AppApiException):
            self.operation(workspace_id="other-workspace").edit({"publish_desc": "Must not be saved"})

        self.version.refresh_from_db()
        self.assertEqual(self.version.publish_desc, "Original notes")
