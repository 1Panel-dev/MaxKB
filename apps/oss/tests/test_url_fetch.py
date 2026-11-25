from unittest.mock import patch

from django.test import SimpleTestCase

from oss.url_fetch import FETCH_URL_CODE, fetch_public_url


class PublicDownloadTests(SimpleTestCase):
    def test_fetch_runs_in_tool_executor_with_byte_limit(self):
        with patch("common.utils.tool_code.ToolExecutor.exec_code", return_value={"content": "ok"}) as run:
            self.assertEqual(fetch_public_url("https://example.com", 32), {"content": "ok"})
        run.assert_called_once_with(
            FETCH_URL_CODE, {"url": "https://example.com", "file_limit": 32}, function_name="fetch_url"
        )

    def test_nonpublic_destination_is_rejected_before_connect(self):
        import socket

        namespace = {}
        exec(FETCH_URL_CODE, namespace)
        addresses = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443))]
        with (
            patch.object(socket, "getaddrinfo", return_value=addresses),
            patch.object(socket.socket, "connect") as connect,
        ):
            with self.assertRaisesRegex(ValueError, "disallowed IP"):
                namespace["fetch_url"]("https://example.com", 32)
        connect.assert_not_called()

    def test_media_redirect_revalidates_the_next_location(self):
        from application.workflow.media_download import download_http_bytes

        with patch(
            "common.utils.tool_code.ToolExecutor.exec_code",
            side_effect=[
                {"status_code": 302, "location": "/media"},
                {"status_code": 200, "content": "YWJj"},
            ],
        ) as run:
            self.assertEqual(download_http_bytes("https://example.com/start", 32), b"abc")
        self.assertEqual(run.call_args.args[1], {"url": "https://example.com/media", "file_limit": 32, "binary": True})
