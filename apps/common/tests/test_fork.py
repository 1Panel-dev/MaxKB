from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from common.utils.fork import Fork


class ForkContentTypeTests(SimpleTestCase):
    def response(self, content, content_type, encoding="utf-8"):
        return SimpleNamespace(
            status_code=200,
            content=content.encode(encoding),
            content_type=content_type,
            encoding=encoding,
            apparent_encoding=encoding,
        )

    def test_markdown_response_preserves_text_without_html_selection_or_conversion(self):
        content = "# 示例\n\n```html\n<body>keep <value> unchanged</body>\n```\n\n**正文**"
        for content_type in ("text/markdown; charset=utf-8", "TEXT/X-MARKDOWN"):
            with (
                self.subTest(content_type=content_type),
                patch.object(Fork, "requests_get", return_value=self.response(content, content_type)),
            ):
                response = Fork("https://example.com/page.md", ["body"]).fork()
                self.assertEqual(response.status, 200)
                self.assertEqual(response.content, content)
                self.assertEqual(response.child_link_list, [])

    def test_plain_text_markdown_url_with_query_is_read_as_markdown(self):
        content = "# 标题\n\n正文"
        with patch.object(Fork, "requests_get", return_value=self.response(content, "text/plain")):
            self.assertEqual(Fork("https://example.com/PAGE.MD?download=1", ["body"]).fork().content, content)

    def test_html_response_keeps_selectors_even_for_markdown_url(self):
        content = '<html><body><div id="article"><h1>Selected</h1><p>body</p></div><p>Excluded</p></body></html>'
        for url in ("https://example.com/page", "https://example.com/page.md"):
            with (
                self.subTest(url=url),
                patch.object(Fork, "requests_get", return_value=self.response(content, "text/html")),
            ):
                result = Fork(url, ["#article"]).fork()
                self.assertIn("# Selected", result.content)
                self.assertNotIn("Excluded", result.content)

    def test_markdown_encoding_and_empty_responses_are_preserved(self):
        for content in ("# 中文\n\n正文", ""):
            with (
                self.subTest(content=content),
                patch.object(Fork, "requests_get", return_value=self.response(content, "text/markdown", "gb18030")),
            ):
                self.assertEqual(Fork("https://example.com/page", ["body"]).fork().content, content)

    def test_sandbox_fetch_carries_content_type_from_http_response(self):
        body = self.response("# Markdown", "text/markdown; charset=utf-8")
        with patch("common.utils.tool_code.ToolExecutor") as executor:

            def execute(code, _parameters, *, function_name):
                namespace = {}
                with patch(
                    "requests.get",
                    return_value=SimpleNamespace(**vars(body), headers={"Content-Type": body.content_type}),
                ):
                    exec(code, namespace)
                    return namespace[function_name]("https://example.com/page.md", {})

            executor.return_value.exec_code.side_effect = execute
            response = Fork.requests_get("https://example.com/page.md", {})
        self.assertEqual(response.content, body.content)
        self.assertEqual(response.content_type, body.content_type)
