from unittest.mock import patch
from uuid import UUID

import requests
from django.test import SimpleTestCase

from common.exception.app_exception import AppApiException
from knowledge.models import FileSourceType
from tools.serializers.tool import ToolSerializer
from tools.serializers.tool_icon import delete_tool_icon, download_tool_icon


class ToolIconTests(SimpleTestCase):
    def test_download_saves_bytes_and_returns_local_url(self):
        with (
            patch("tools.serializers.tool_icon.requests.get") as get,
            patch("tools.serializers.tool_icon.File") as file,
        ):
            response = get.return_value.__enter__.return_value
            response.status_code = 200
            response.headers = {"Content-Type": "image/png"}
            response.iter_content.return_value = [b"image", b" data"]
            icon = download_tool_icon("https://apps-assets.fit2cloud.com/tool/icon.png?v=1", "tool-id")
            self.assertEqual(icon, f"./oss/file/{file.call_args.kwargs['id']}")
            self.assertEqual(file.call_args.kwargs["source_id"], "tool-id")
            self.assertEqual(file.call_args.kwargs["file_name"], "icon.png")
            file.return_value.save.assert_called_once_with(b"image data")
            self.assertFalse(get.call_args.kwargs["allow_redirects"])

    def test_empty_icon_does_not_download(self):
        with patch("tools.serializers.tool_icon.requests.get") as get:
            self.assertEqual(download_tool_icon(None, "tool-id"), "")
            self.assertEqual(download_tool_icon("", "tool-id"), "")
            get.assert_not_called()

    def test_untrusted_url_does_not_download(self):
        with patch("tools.serializers.tool_icon.requests.get") as get:
            with self.assertRaises(AppApiException):
                download_tool_icon("http://127.0.0.1/icon.png", "tool-id")
            get.assert_not_called()

    def test_bad_responses_do_not_save_files(self):
        for status, content_type, chunks in [
            (302, "image/png", [b"image"]),
            (200, "text/html", [b"html"]),
            (200, "image/png", []),
            (200, "image/png", [b"12345"]),
        ]:
            with self.subTest(status=status, content_type=content_type, chunks=chunks):
                with (
                    patch("tools.serializers.tool_icon.requests.get") as get,
                    patch("tools.serializers.tool_icon.File") as file,
                    patch("tools.serializers.tool_icon.MAX_ICON_BYTES", 4),
                ):
                    response = get.return_value.__enter__.return_value
                    response.status_code = status
                    response.headers = {"Content-Type": content_type}
                    response.iter_content.return_value = chunks
                    with self.assertRaises(AppApiException):
                        download_tool_icon("https://apps-assets.fit2cloud.com/icon.png", "tool-id")
                    file.assert_not_called()

    def test_timeout_is_reported(self):
        with patch("tools.serializers.tool_icon.requests.get", side_effect=requests.Timeout):
            with self.assertRaises(AppApiException):
                download_tool_icon("https://apps-assets.fit2cloud.com/icon.png", "tool-id")

    def test_remote_and_static_icons_are_not_deleted(self):
        with patch("tools.serializers.tool_icon.QuerySet") as query:
            for icon in ["", None, "https://example.com/icon.png", "./tool/icon.png", "./oss/file/invalid"]:
                delete_tool_icon(icon, "tool-id")
            query.assert_not_called()

    def test_local_icon_deletion_is_scoped_to_owner(self):
        file_id = UUID("00000000-0000-0000-0000-000000000001")
        with patch("tools.serializers.tool_icon.QuerySet") as query:
            delete_tool_icon(f"./oss/file/{file_id}", "tool-id")
            self.assertEqual(query.return_value.filter.call_args.kwargs["id"], file_id)
            self.assertEqual(query.return_value.filter.call_args.kwargs["source_id"], "tool-id")
            query.return_value.filter.return_value.delete.assert_called_once()


class ToolCreateIconTests(SimpleTestCase):
    def test_create_persists_uploaded_icon_and_assigns_its_file_to_tool(self):
        icon_file_id = UUID("00000000-0000-0000-0000-000000000001")
        icon = f"./oss/file/{icon_file_id}"
        with (
            patch("tools.serializers.tool.Tool") as tool,
            patch("tools.serializers.tool.QuerySet") as query,
            patch("tools.serializers.tool.UserResourcePermissionSerializer"),
            patch.object(ToolSerializer.Operate, "one"),
            patch("django.db.transaction.Atomic.__enter__"),
            patch("django.db.transaction.Atomic.__exit__", return_value=False),
        ):
            serializer = ToolSerializer.Create(data={"user_id": str(icon_file_id), "workspace_id": "workspace"})
            serializer.is_valid(raise_exception=True)
            serializer.insert({"name": "tool", "code": "pass", "icon": icon}, with_valid=False)

            tool.return_value.save.assert_called_once()
            self.assertEqual(tool.call_args.kwargs["icon"], icon)
            query.assert_called_once()
            self.assertEqual(
                query.return_value.filter.call_args.kwargs,
                {
                    "id": icon_file_id,
                    "source_type": FileSourceType.TOOL,
                    "source_id": FileSourceType.TEMPORARY_120_MINUTE,
                },
            )
            query.return_value.filter.return_value.update.assert_called_once_with(source_id=tool.call_args.kwargs["id"])


class ToolEditIconTests(SimpleTestCase):
    def test_replacing_or_resetting_icon_deletes_previous_owned_file(self):
        tool_id = UUID("00000000-0000-0000-0000-000000000001")
        old_icon = "./oss/file/00000000-0000-0000-0000-000000000002"
        new_icon = "./oss/file/00000000-0000-0000-0000-000000000003"
        with (
            patch("tools.serializers.tool.QuerySet") as query,
            patch("tools.serializers.tool.delete_tool_icon") as delete_icon,
            patch.object(ToolSerializer.Operate, "one"),
            patch("django.db.transaction.Atomic.__enter__"),
            patch("django.db.transaction.Atomic.__exit__", return_value=False),
        ):
            stored_tool = query.return_value.filter.return_value.first.return_value
            stored_tool.id = tool_id
            stored_tool.icon = old_icon
            serializer = ToolSerializer.Operate(data={"id": str(tool_id), "workspace_id": "workspace"})
            serializer.is_valid(raise_exception=True)

            for icon in (new_icon, ""):
                with self.subTest(icon=icon):
                    serializer.edit({"icon": icon}, with_valid=False)
                    delete_icon.assert_called_with(old_icon, tool_id)
                    delete_icon.reset_mock()

            serializer.edit({"icon": old_icon}, with_valid=False)
            serializer.edit({"name": "renamed"}, with_valid=False)
            delete_icon.assert_not_called()
