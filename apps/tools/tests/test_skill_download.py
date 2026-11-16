"""Skill downloads preserve ZIP bytes and expose a browser-readable filename."""

import io
from types import SimpleNamespace
from unittest.mock import Mock, patch
from zipfile import ZIP_DEFLATED, ZipFile

from django.test import SimpleTestCase
from django.utils.http import parse_header_parameters

from common.exception.app_exception import AppApiException
from knowledge.models import File
from tools.models import Tool, ToolType
from tools.serializers.tool import ToolSerializer


class SkillDownloadTests(SimpleTestCase):
    user_id = "00000000-0000-0000-0000-000000000001"
    tool_id = "00000000-0000-0000-0000-000000000002"
    file_id = "00000000-0000-0000-0000-000000000003"

    def setUp(self):
        buffer = io.BytesIO()
        with ZipFile(buffer, "w", ZIP_DEFLATED) as archive:
            archive.writestr("SKILL.md", "# Test skill\nDownload regression fixture.")
        self.zip_bytes = buffer.getvalue()
        self.file = SimpleNamespace(file_name="公文排版技能.zip", get_bytes=Mock(return_value=self.zip_bytes))
        self.tool_query = Mock()
        self.tool_query.filter.return_value.first.return_value = SimpleNamespace(code=self.file_id)
        self.file_query = Mock()
        self.file_query.filter.return_value.first.return_value = self.file
        self.enterContext(
            patch("tools.serializers.tool.QuerySet", side_effect={Tool: self.tool_query, File: self.file_query}.get)
        )

    def download(self):
        return ToolSerializer.DownloadSkillFile(
            data={"user_id": self.user_id, "workspace_id": "test-workspace", "tool_id": self.tool_id}
        ).download()

    def test_unicode_and_ascii_filenames_keep_valid_zip_payloads(self):
        for filename in (
            "公文排版技能.zip",
            "技能 文件 (1).zip",
            "技能;测试.zip",
            "office-skill.zip",
            'skill;"draft".zip',
        ):
            with self.subTest(filename=filename):
                self.file.file_name = filename

                response = self.download()

                disposition, parameters = parse_header_parameters(response["Content-Disposition"])
                self.assertEqual(disposition, "attachment")
                self.assertEqual(parameters["filename"], filename)
                self.assertNotIn("=?utf-8?", response["Content-Disposition"].lower())
                self.assertEqual(response["Content-Type"], "application/zip")
                self.assertEqual(response.content, self.zip_bytes)
                with ZipFile(io.BytesIO(response.content)) as archive:
                    self.assertIsNone(archive.testzip())
                    self.assertEqual(archive.namelist(), ["SKILL.md"])
                    self.assertIn(b"Download regression fixture.", archive.read("SKILL.md"))

    def test_download_lookup_remains_scoped_to_workspace_and_skill_type(self):
        self.download()

        self.tool_query.filter.assert_called_once_with(
            id=self.tool_id, workspace_id="test-workspace", tool_type=ToolType.SKILL
        )
        self.file_query.filter.assert_called_once_with(id=self.file_id)

    def test_missing_or_out_of_scope_tool_cannot_download_file(self):
        self.tool_query.filter.return_value.first.return_value = None

        with self.assertRaises(AppApiException):
            self.download()

        self.file_query.filter.assert_not_called()
        self.file.get_bytes.assert_not_called()

    def test_missing_skill_file_is_reported(self):
        self.file_query.filter.return_value.first.return_value = None

        with self.assertRaises(AppApiException):
            self.download()

        self.file.get_bytes.assert_not_called()
