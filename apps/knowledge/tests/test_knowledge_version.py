from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from common.exception.app_exception import AppApiException
from knowledge.models import Knowledge, KnowledgeFolder, KnowledgeWorkflow, KnowledgeWorkflowVersion
from knowledge.serializers.knowledge_version import KnowledgeWorkflowVersionSerializer
from knowledge.serializers.knowledge_workflow import KnowledgeWorkflowSerializer
from users.models import User


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


class KnowledgeWorkflowPublishTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        folder = KnowledgeFolder.objects.create(id="publish-test", name="Publish tests")
        cls.knowledge = Knowledge.objects.create(name="Workflow", desc="", folder=folder)
        cls.user = User.objects.create(username="workflow-publisher")
        cls.workflow = KnowledgeWorkflow.objects.create(
            knowledge=cls.knowledge,
            work_flow={"nodes": [], "edges": []},
            default_model_setting={"llm": {"model_id": "test-model"}},
        )

    def publish(self, payload=None):
        return KnowledgeWorkflowSerializer.Operate(
            data={
                "user_id": str(self.user.id),
                "workspace_id": "default",
                "knowledge_id": str(self.knowledge.id),
            }
        ).publish(payload)

    def test_publish_persists_title_and_notes_in_history(self):
        notes = "  修复知识库同步\n保留工作流配置\n"
        self.assertTrue(self.publish({"publish_name": "  版本 V1  ", "publish_desc": notes}))

        version = KnowledgeWorkflowVersion.objects.get(knowledge=self.knowledge)
        self.assertEqual(version.name, "版本 V1")
        self.assertEqual(version.publish_desc, notes)
        self.assertEqual(version.work_flow, self.workflow.work_flow)
        self.assertEqual(version.default_model_setting, self.workflow.default_model_setting)
        self.assertEqual(version.publish_user_id, self.user.id)
        self.assertEqual(version.publish_user_name, self.user.username)
        self.assertEqual(version.workspace_id, self.workflow.workspace_id)
        self.workflow.refresh_from_db()
        self.assertTrue(self.workflow.is_publish)
        self.assertIsNotNone(self.workflow.publish_time)

        history = KnowledgeWorkflowVersionSerializer.Query(data={"workspace_id": "default"}).list(
            {"knowledge_id": str(self.knowledge.id)}
        )
        self.assertEqual(history[0]["name"], "版本 V1")
        self.assertEqual(history[0]["publish_desc"], notes)

    def test_legacy_publish_defaults_to_timestamp_and_empty_notes(self):
        published_at = timezone.now()
        for payload in (None, {}, {"publish_name": None, "publish_desc": None}, {"publish_name": "  "}):
            with (
                self.subTest(payload=payload),
                patch("knowledge.serializers.knowledge_workflow.timezone.now", return_value=published_at),
            ):
                self.publish(payload)
                version = KnowledgeWorkflowVersion.objects.filter(knowledge=self.knowledge).latest("create_time")
                self.assertEqual(version.name, timezone.localtime(published_at).strftime("%Y-%m-%d %H:%M:%S"))
                self.assertEqual(version.publish_desc, "")

    def test_republishing_creates_an_independent_version(self):
        self.publish({"publish_name": "V1", "publish_desc": "First release"})
        self.publish({"publish_name": "V2", "publish_desc": ""})

        versions = KnowledgeWorkflowVersion.objects.filter(knowledge=self.knowledge).order_by("create_time")
        self.assertEqual(list(versions.values_list("name", "publish_desc")), [("V1", "First release"), ("V2", "")])

    def test_publish_accepts_field_limits(self):
        self.publish({"publish_name": "版" * 128, "publish_desc": "说" * 1024})

        version = KnowledgeWorkflowVersion.objects.get(knowledge=self.knowledge)
        self.assertEqual(version.name, "版" * 128)
        self.assertEqual(version.publish_desc, "说" * 1024)

    def test_invalid_publish_does_not_create_a_version_or_mark_workflow_published(self):
        for field, value in (
            ("publish_name", "版" * 129),
            ("publish_desc", "说" * 1025),
            ("publish_desc", "说" + " " * 1024),
        ):
            with self.subTest(field=field, length=len(value)):
                with self.assertRaises(ValidationError) as error:
                    self.publish({"publish_name": "V1", field: value})

                self.assertIn(field, error.exception.detail)
                self.assertFalse(KnowledgeWorkflowVersion.objects.filter(knowledge=self.knowledge).exists())
                self.workflow.refresh_from_db()
                self.assertFalse(self.workflow.is_publish)
                self.assertIsNone(self.workflow.publish_time)
