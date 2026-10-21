"""Workflow Web sources persist images before splitting and bind them on write."""

import os
from unittest import skipUnless
from unittest.mock import MagicMock, patch
from uuid import uuid4

import boto3
from botocore.config import Config
from django.test import SimpleTestCase, TestCase

from application.workflow.common import WorkflowType
from application.workflow.nodes.data_source_web_node.data_source_web_node import DataSourceWebNode
from application.workflow.nodes.document_split_node.document_split_node import DocumentSplitNode
from application.workflow.nodes.knowledge_write_node.knowledge_write_node import KnowledgeWriteNode
from common.utils.fork import ChildLink, Fork
from knowledge.models import File, FileSourceType, Knowledge, KnowledgeType, Paragraph, ParagraphAsset


NODE_MODULE = "application.workflow.nodes.data_source_web_node.data_source_web_node"


def source_node(parameters):
    node = DataSourceWebNode.__new__(DataSourceWebNode)
    node.get_workflow_parameters = MagicMock(return_value=parameters)
    node._check_cancelled = MagicMock()
    node.get_node_id = MagicMock(return_value="web")
    node.write_context = MagicMock()
    return node


class WorkflowWebImageSourceTests(SimpleTestCase):
    def test_full_import_and_single_document_sync_localize_images_before_output(self):
        for single in (False, True):
            with self.subTest(single=single):
                parameters = {
                    "knowledge_id": "knowledge-id",
                    "data_source": {"source_url": "https://example.com/page.html"},
                    "workflow_source": {"source_scope": "web-scope"},
                }
                if single:
                    parameters["workflow_sync_document"] = {"name": "existing title"}
                node = source_node(parameters)
                remote = "![chart](https://example.com/chart.png)"
                local = "![chart](./oss/file/00000000-0000-0000-0000-000000000001)"
                response = Fork.Response.success(remote, [])

                def crawl(_depth, _visited, handler):
                    handler(ChildLink(parameters["data_source"]["source_url"], None), response)

                with (
                    patch(f"{NODE_MODULE}.Fork") as fetch,
                    patch(f"{NODE_MODULE}.ForkManage") as crawler,
                    patch(f"{NODE_MODULE}.internalize_web_images", return_value=local) as internalize,
                ):
                    fetch.return_value.fork.return_value = response
                    crawler.return_value.fork.side_effect = crawl
                    node.execute()

                internalize.assert_called_once_with(remote, "knowledge-id")
                document = node.write_context.call_args_list[0].args[1][0]
                self.assertEqual(document["content"], local)
                self.assertEqual(document["meta"]["source_type"], "web")
                self.assertEqual(document["meta"]["source_scope"], "web-scope")
                self.assertEqual(document["meta"]["source_url"], parameters["data_source"]["source_url"])
                if single:
                    self.assertEqual(document["name"], "existing title")

    def test_failed_page_does_not_download_images_or_publish_a_document(self):
        documents = []
        handler = source_node({})._get_collect_handler(documents, knowledge_id="knowledge-id")
        with patch(f"{NODE_MODULE}.internalize_web_images") as internalize:
            with self.assertRaisesRegex(ValueError, "unavailable"):
                handler(ChildLink("https://example.com/page.html", None), Fork.Response.error("unavailable"))
        internalize.assert_not_called()
        self.assertEqual(documents, [])


@skipUnless(os.environ.get("WORKFLOW_WEB_IMAGE_TEST_URL"), "Start the local workflow Web Postman simulation")
class WorkflowWebImageHTTPTests(TestCase):
    def setUp(self):
        self.base_url = os.environ["WORKFLOW_WEB_IMAGE_TEST_URL"].rstrip("/")
        self.knowledge = Knowledge.objects.create(name="Workflow Web images", desc="", type=KnowledgeType.WORKFLOW)
        self.parameters = {
            "knowledge_id": str(self.knowledge.id),
            "knowledge_action_id": str(uuid4()),
            "workflow_source": {"source_scope": "web-scope", "source_type": "web"},
            "data_source": {"source_url": f"{self.base_url}/site/page.html"},
        }
        client = boto3.client(
            "s3",
            endpoint_url=f"{self.base_url}/storage",
            aws_access_key_id="test-key",
            aws_secret_access_key="test-secret",
            region_name="us-east-1",
            config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
        )
        self.enterContext(patch("knowledge.models.knowledge.get_s3_client", return_value=client))
        self.enterContext(patch("knowledge.models.knowledge.get_bucket", return_value="bucket"))
        self.enterContext(patch("knowledge.models.knowledge.is_seaweedfs_enabled", return_value=True))

    def import_page(self):
        web = source_node(self.parameters)
        web.execute()
        downloaded = web.write_context.call_args_list[0].args[1]
        splitter = DocumentSplitNode.__new__(DocumentSplitNode)
        splitter.get_parameters = MagicMock(return_value={"document_list": ["web", "document_list"]})
        splitter.get_workflow_parameters = MagicMock(return_value=self.parameters)
        splitter.get_workflow_type = MagicMock(return_value=WorkflowType.KNOWLEDGE)
        splitter.get_reference_content = MagicMock(return_value=downloaded)
        splitter.write_context = MagicMock()
        splitter.execute()
        documents = next(
            call.args[1] for call in splitter.write_context.call_args_list if call.args[0] == "paragraph_list"
        )
        writer = KnowledgeWriteNode.__new__(KnowledgeWriteNode)
        writer.get_workflow_parameters = MagicMock(return_value=self.parameters)
        return writer.save(documents, None)[0][0]

    def test_crawl_download_split_and_write_share_one_local_image(self):
        document = self.import_page()
        file = File.objects.get()
        self.assertEqual(file.source_type, FileSourceType.PARAGRAPH)
        self.assertTrue(Paragraph.objects.filter(id=file.source_id, document=document).exists())
        assets = list(ParagraphAsset.objects.filter(document=document))
        self.assertEqual(len(assets), 2)
        self.assertEqual({asset.file_id for asset in assets}, {file.id})
        self.assertTrue(file.get_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
        paragraphs = list(Paragraph.objects.filter(document=document))
        self.assertFalse(any(f"{self.base_url}/site/chart.png" in p.content for p in paragraphs))
        self.assertTrue(any(f"/oss/file/{file.id}" in p.content for p in paragraphs))
        self.assertEqual(document.meta["source_url"], self.parameters["data_source"]["source_url"])
        second = self.import_page()
        self.assertEqual(File.objects.count(), 1)
        self.assertEqual(
            set(ParagraphAsset.objects.filter(document=second).values_list("file_id", flat=True)), {file.id}
        )

    def test_missing_image_preserves_remote_reference_and_imports_text(self):
        self.parameters["data_source"]["source_url"] = f"{self.base_url}/site/missing.html"
        self.parameters["workflow_sync_document"] = {"name": "retained title"}
        document = self.import_page()
        self.assertEqual(document.name, "retained title")
        self.assertFalse(File.objects.exists())
        self.assertFalse(ParagraphAsset.objects.exists())
        self.assertTrue(Paragraph.objects.filter(document=document, content__contains="/site/missing.png").exists())
