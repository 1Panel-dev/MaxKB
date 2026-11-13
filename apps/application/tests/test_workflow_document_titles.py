"""Workflow splitting preserves display titles independently of uploaded-file names."""

from unittest.mock import MagicMock

from django.test import SimpleTestCase

from application.workflow.common import WorkflowType
from application.workflow.nodes.document_split_node.document_split_node import DocumentSplitNode


class WorkflowDocumentTitleTests(SimpleTestCase):
    def test_smart_and_custom_split_preserve_web_titles_and_source_metadata(self):
        for strategy in ("auto", "custom"):
            for title in (
                "01 纯文本基线（图片/URL 恒定）",
                "02 内容变更用例（段落增 / 改 / 删）",
                "04 图片变量控制（复用 / 失效 / 不可下载）",
                "https://example.test/docs/page.html",
                "普通网页标题",
            ):
                with self.subTest(strategy=strategy, title=title):
                    source_meta = {
                        "source_type": "web",
                        "source_url": "https://example.test/docs/page.html",
                        "source_scope": "web-source",
                    }
                    source = {
                        "id": "source-id",
                        "name": title,
                        "content": "## 第一章\n正文一\n\n## 第二章\n正文二",
                        "meta": source_meta,
                    }
                    node = DocumentSplitNode.__new__(DocumentSplitNode)
                    node.get_parameters = MagicMock(
                        return_value={
                            "document_list": ["web", "document_list"],
                            "split_strategy": strategy,
                            "document_name_relate_problem": True,
                        }
                    )
                    node.get_workflow_parameters = MagicMock(return_value={"knowledge_id": "knowledge-id"})
                    node.get_workflow_type = MagicMock(return_value=WorkflowType.KNOWLEDGE)
                    node.get_reference_content = MagicMock(return_value=[source])
                    context = {}
                    node.write_context = context.__setitem__

                    node.execute()

                    self.assertEqual(len(context["paragraph_list"]), 1)
                    document = context["paragraph_list"][0]
                    self.assertEqual(document["name"], title)
                    self.assertEqual(document["source_file_id"], "source-id")
                    self.assertEqual(
                        document["meta"],
                        {**source_meta, "knowledge_id": "knowledge-id", "source_file_id": "source-id"},
                    )
                    self.assertEqual(len(document["paragraphs"]), 2)
                    for paragraph in document["paragraphs"]:
                        self.assertIn(title, paragraph["problem_list"])
                        self.assertTrue(paragraph["chunks"])
