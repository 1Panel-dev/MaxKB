from types import SimpleNamespace
from django.test import SimpleTestCase
from common.exception.app_exception import AppUnauthorizedFailed
from common.utils.file_reference import validate_knowledge_source_file
from knowledge.models import FileSourceType


class FileOwnershipTests(SimpleTestCase):
    def test_temporary_file_requires_its_uploader(self):
        file = SimpleNamespace(source_type=FileSourceType.TEMPORARY_120_MINUTE, meta={"user_id": "owner"})
        self.assertIs(validate_knowledge_source_file(file, "knowledge", "owner"), file)
        with self.assertRaises(AppUnauthorizedFailed):
            validate_knowledge_source_file(file, "knowledge", "other")
