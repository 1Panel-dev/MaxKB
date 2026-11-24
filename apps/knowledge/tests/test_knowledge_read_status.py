from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from knowledge.models import Knowledge, KnowledgeType


@override_settings(ROOT_URLCONF="knowledge.urls")
class KnowledgeReadStatusTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=SimpleNamespace(id=uuid4(), type="TEST"))
        permissions = self.enterContext(patch("common.auth.authentication._build"))
        permissions.return_value.hasPermission.return_value = True

    def test_sync_reads_distinguish_supported_and_unsupported_knowledge(self):
        for kind, status in ((KnowledgeType.BASE, 404), (KnowledgeType.WEB, 200)):
            knowledge = Knowledge.objects.create(name="Knowledge", type=kind)
            for suffix in ("sync_setting", "sync_log/1/10"):
                with self.subTest(kind=kind, suffix=suffix):
                    response = self.client.get(f"/workspace/default/knowledge/{knowledge.id}/{suffix}")
                    self.assertEqual(response.status_code, status)
                    self.assertEqual(response.json()["code"], status)

    def test_paragraph_reads_for_missing_knowledge_return_not_found(self):
        prefix = f"/workspace/default/knowledge/{uuid4()}"
        paragraphs = f"document/{uuid4()}/paragraph"
        paragraph_id = uuid4()
        for suffix in (
            paragraphs,
            f"{paragraphs}/1/10",
            f"{paragraphs}/{paragraph_id}",
            f"{paragraphs}/{paragraph_id}/problem",
            f"problem/{uuid4()}/paragraph",
        ):
            with self.subTest(suffix=suffix):
                response = self.client.get(f"{prefix}/{suffix}")
                self.assertEqual(response.status_code, 404)
                self.assertEqual(response.json()["code"], 404)
