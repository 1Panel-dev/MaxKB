from types import SimpleNamespace
from unittest.mock import patch
from django.test import SimpleTestCase
from common.exception.app_exception import AppUnauthorizedFailed
from knowledge.models import FileSourceType
from oss.serializers.file import auth


class SkillFileAuthTests(SimpleTestCase):
    def test_anonymous_package_read_requires_authentication_even_with_public_files(self):
        file = SimpleNamespace(id="package", source_type=FileSourceType.TOOL, meta={})
        with patch("oss.serializers.file.Tool.objects.filter") as query:
            query.return_value.first.return_value = object()
            with self.assertRaises(AppUnauthorizedFailed):
                auth(file, None)
