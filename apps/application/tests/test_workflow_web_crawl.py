"""A missing child page must not discard the rest of a Web workflow import."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from application.workflow.common import CancelledException
from application.workflow.nodes.data_source_web_node.data_source_web_node import DataSourceWebNode
from common.utils.fork import Fork
from common.exception.app_exception import AppApiException
from knowledge.serializers.common import MetaSerializer


ROOT_URL = "https://example.com"


class WorkflowWebCrawlTests(SimpleTestCase):
    def test_knowledge_source_validation_still_rejects_all_http_failures(self):
        for status in (404, 403, 429, 500, 503):
            with (
                self.subTest(status=status),
                patch(
                    "knowledge.serializers.common.Fork.fork", return_value=Fork.Response.error("unavailable", status)
                ),
            ):
                with self.assertRaises(AppApiException):
                    MetaSerializer.WebMeta(data={"source_url": ROOT_URL}).is_valid(raise_exception=True)

    def node(self, *, single=False):
        node = DataSourceWebNode.__new__(DataSourceWebNode)
        parameters = {"data_source": {"source_url": ROOT_URL}}
        if single:
            parameters["workflow_sync_document"] = {"name": "Existing page"}
        node.get_workflow_parameters = MagicMock(return_value=parameters)
        node.get_node_id = MagicMock(return_value="web")
        node._check_cancelled = MagicMock()
        node.write_context = MagicMock()
        return node

    def fetch(self, statuses):
        def get(url, _headers):
            html = (
                '<body>Index<a href="/missing">Missing</a><a href="/working">Working</a></body>'
                if url == ROOT_URL
                else "<body>Valid child content</body>"
            )
            return SimpleNamespace(
                status_code=statuses.get(url, 200),
                content=html.encode(),
                content_type="text/html",
                encoding="utf-8",
                apparent_encoding="utf-8",
            )

        return get

    def test_missing_child_is_skipped_and_later_pages_are_imported(self):
        node = self.node()
        with patch.object(Fork, "requests_get", side_effect=self.fetch({ROOT_URL + "/missing": 404})) as fetch:
            node.execute()

        documents = node.write_context.call_args_list[0].args[1]
        self.assertEqual([doc["meta"]["source_url"] for doc in documents], [ROOT_URL, ROOT_URL + "/working"])
        self.assertEqual(documents[1]["content"], "Valid child content")
        self.assertEqual(fetch.call_count, 3)

    def test_missing_root_or_single_document_still_fails_without_publishing(self):
        for single in (False, True):
            with self.subTest(single=single):
                node = self.node(single=single)
                with patch.object(Fork, "requests_get", side_effect=self.fetch({ROOT_URL: 404})):
                    with self.assertRaisesRegex(ValueError, "404"):
                        node.execute()
                node.write_context.assert_not_called()

    def test_auth_and_server_failures_do_not_publish_incomplete_snapshots(self):
        for status in (401, 403, 429, 500, 503):
            with self.subTest(status=status):
                node = self.node()
                with patch.object(Fork, "requests_get", side_effect=self.fetch({ROOT_URL + "/missing": status})):
                    with self.assertRaises(ValueError):
                        node.execute()
                node.write_context.assert_not_called()

    def test_cancellation_is_not_swallowed_when_skipping_a_missing_child(self):
        node = self.node()
        node._check_cancelled.side_effect = [None, CancelledException()]
        with patch.object(Fork, "requests_get", side_effect=self.fetch({ROOT_URL + "/missing": 404})):
            with self.assertRaises(CancelledException):
                node.execute()
        node.write_context.assert_not_called()
