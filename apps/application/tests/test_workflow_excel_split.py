"""Excel sheet boundaries survive extraction and workflow document splitting."""

import io
from base64 import b64decode
from unittest.mock import MagicMock, patch
from uuid import uuid4
from zipfile import ZIP_DEFLATED, ZipFile

import openpyxl
import xlwt
from django.test import SimpleTestCase, TestCase

from application.workflow.common import WorkflowType
from application.workflow.nodes.document_extract_node.document_extract_node import DocumentExtractNode
from application.workflow.nodes.document_split_node.document_split_node import DocumentSplitNode
from application.workflow.nodes.knowledge_write_node.knowledge_write_node import KnowledgeWriteNode
from common.handle.impl.text.zip_split_handle import ZipSplitHandle
from knowledge.models import Document, File, FileSourceType, Knowledge, Paragraph


class WorkflowExcelSplitTests(SimpleTestCase):
    file_id = "00000000-0000-0000-0000-000000000001"
    source_meta = {"source_type": "local", "source_scope": "local-source"}

    def workbook_bytes(self, suffix, sheet_names):
        workbook = xlwt.Workbook() if suffix.lower() == ".xls" else openpyxl.Workbook()
        if suffix.lower() != ".xls":
            workbook.remove(workbook.active)
        for name in sheet_names:
            rows = [
                ["分段标题", "分段内容", "问题"],
                [f"{name}标题", f"{name}回答", f"{name}问题"],
                [f"{name}标题二", f"{name}回答二", f"{name}问题二"],
            ]
            if suffix.lower() == ".xls":
                sheet = workbook.add_sheet(name)
                for row_index, row in enumerate(rows):
                    for column_index, value in enumerate(row):
                        sheet.write(row_index, column_index, value)
            else:
                sheet = workbook.create_sheet(name)
                for row in rows:
                    sheet.append(row)
        buffer = io.BytesIO()
        workbook.save(buffer)
        return buffer.getvalue()

    def extract(self, suffix, sheet_names):
        return self.extract_file(f"knowledge{suffix}", self.workbook_bytes(suffix, sheet_names))

    def archive_bytes(self, members):
        buffer = io.BytesIO()
        with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as archive:
            for name, content in members:
                archive.writestr(name, content)
        return buffer.getvalue()

    def extract_file(self, name, content):
        file = MagicMock(id=self.file_id)
        file.get_bytes.return_value = content
        node = DocumentExtractNode.__new__(DocumentExtractNode)
        node.get_parameters = MagicMock(return_value={"document_list": ["source", "file_list"]})
        node.get_workflow_parameters = MagicMock(return_value={"knowledge_id": "knowledge-id"})
        node.get_workflow_type = MagicMock(return_value=WorkflowType.KNOWLEDGE)
        node.workflow_manage = MagicMock()
        node.workflow_manage.get_reference_field.return_value = [
            {"file_id": self.file_id, "name": name, "meta": self.source_meta}
        ]
        context = {}
        node.write_context = context.__setitem__
        with (
            patch("application.workflow.nodes.document_extract_node.document_extract_node.QuerySet") as query_set,
            patch(
                "application.workflow.nodes.document_extract_node.document_extract_node.File.save", autospec=True
            ) as save_file,
            patch("common.handle.impl.table.xlsx_parse_table_handle.xlsx_embed_cells_images", return_value={}),
        ):
            query_set.return_value.filter.return_value.first.return_value = file
            query_set.return_value.filter.return_value.exists.return_value = False
            node.execute()
        self.saved_files = [call.args for call in save_file.call_args_list]
        self.extracted_content = context["content"]
        return context["document_list"]

    def split(self, documents, **parameters):
        node = DocumentSplitNode.__new__(DocumentSplitNode)
        node.get_parameters = MagicMock(return_value={"document_list": ["extract", "document_list"], **parameters})
        node.get_workflow_parameters = MagicMock(return_value={"knowledge_id": "knowledge-id"})
        node.get_workflow_type = MagicMock(return_value=WorkflowType.KNOWLEDGE)
        node.get_reference_content = MagicMock(return_value=documents)
        context = {}
        node.write_context = context.__setitem__
        node.execute()
        return context["paragraph_list"]

    def test_smart_split_keeps_each_sheet_and_its_source_file_separate(self):
        for suffix in (".xlsx", ".XLSX", ".xls"):
            with self.subTest(suffix=suffix):
                documents = self.split(self.extract(suffix, ["Sheet1", "产品说明"]))
                self.assertEqual([document["name"] for document in documents], ["Sheet1", "产品说明"])
                for document, other_name in zip(documents, ["产品说明", "Sheet1"]):
                    self.assertEqual(document["source_file_id"], self.file_id)
                    self.assertEqual(
                        document["meta"],
                        {**self.source_meta, "source_file_id": self.file_id, "knowledge_id": "knowledge-id"},
                    )
                    self.assertEqual(len(document["paragraphs"]), 1)
                    paragraph = document["paragraphs"][0]
                    self.assertEqual(paragraph["title"].strip(), document["name"])
                    self.assertIn(f"{document['name']}回答", paragraph["content"])
                    self.assertNotIn(other_name, paragraph["content"])
                    self.assertTrue(paragraph["is_active"])
                    self.assertTrue(paragraph["chunks"])

    def test_custom_patterns_cannot_combine_different_sheets(self):
        documents = self.split(
            self.extract(".xlsx", ["Sheet1", "产品说明"]),
            split_strategy="custom",
            patterns=["NEVER_MATCH_THIS_SEPARATOR"],
        )
        self.assertEqual([document["name"] for document in documents], ["Sheet1", "产品说明"])
        self.assertNotIn("产品说明", documents[0]["paragraphs"][0]["content"])
        self.assertNotIn("Sheet1", documents[1]["paragraphs"][0]["content"])

    def test_zip_excel_sheets_keep_document_boundaries_and_archive_source(self):
        for suffix in (".xlsx", ".XLSX", ".xls"):
            for strategy in ("auto", "custom", "qa"):
                with self.subTest(suffix=suffix, strategy=strategy):
                    name = f"资料/knowledge{suffix}"
                    archive = self.archive_bytes(
                        [
                            ("资料/", b""),
                            (name, self.workbook_bytes(suffix, ["Sheet1", "产品说明"])),
                            ("__MACOSX/._knowledge.xlsx", b"ignored metadata"),
                        ]
                    )
                    extracted = self.extract_file("documents.ZIP", archive)
                    self.assertEqual([document["name"] for document in extracted], [name])
                    documents = self.split(extracted, split_strategy=strategy, patterns=["NEVER_MATCH_THIS_SEPARATOR"])
                    self.assertEqual([document["name"] for document in documents], ["Sheet1", "产品说明"])
                    for document, other_name in zip(documents, ["产品说明", "Sheet1"]):
                        self.assertEqual(document["source_file_id"], self.file_id)
                        self.assertEqual(
                            document["meta"],
                            {**self.source_meta, "source_file_id": self.file_id, "knowledge_id": "knowledge-id"},
                        )
                        content = "".join(paragraph["content"] for paragraph in document["paragraphs"])
                        self.assertIn(f"{document['name']}回答", content)
                        self.assertNotIn(other_name, content)
                        if strategy == "qa":
                            self.assertEqual(document["paragraphs"][0]["problem_list"], [f"{document['name']}问题"])

    def test_zip_mixed_files_do_not_merge_workbooks_or_split_text_headings_into_documents(self):
        archive = self.archive_bytes(
            [
                ("first.xlsx", self.workbook_bytes(".xlsx", ["Sheet1", "产品说明"])),
                ("second.xls", self.workbook_bytes(".xls", ["Sheet1"])),
                ("notes.md", "## 第一章\n正文一\n\n## 第二章\n正文二".encode()),
            ]
        )
        extracted = self.extract_file("documents.zip", archive)
        self.assertEqual([document["name"] for document in extracted], ["first.xlsx", "second.xls", "notes.md"])
        documents = self.split(extracted)
        self.assertEqual([document["name"] for document in documents], ["Sheet1", "产品说明", "Sheet1", "notes.md"])
        self.assertEqual(len(documents[-1]["paragraphs"]), 2)

    def test_zip_sheet_images_are_saved_and_rewritten_before_splitting(self):
        sheet_names = ["Sheet1", "产品说明"]
        image_ids = ["00000000-0000-0000-0000-000000000002", "00000000-0000-0000-0000-000000000003"]
        image_bytes = b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aM1cAAAAASUVORK5CYII="
        )
        workbook = openpyxl.load_workbook(io.BytesIO(self.workbook_bytes(".xlsx", sheet_names)))
        for sheet, image_id in zip(workbook, image_ids):
            sheet["B2"] = f"{sheet.title}回答 ![](./oss/file/{image_id})"
        buffer = io.BytesIO()
        workbook.save(buffer)
        archive = self.archive_bytes(
            [("knowledge.xlsx", buffer.getvalue()), *[(f"oss/file/{image_id}", image_bytes) for image_id in image_ids]]
        )

        documents = self.split(self.extract_file("documents.zip", archive))

        self.assertEqual([document["name"] for document in documents], sheet_names)
        self.assertEqual(len(self.saved_files), 2)
        for document, (saved_file, saved_bytes), original_id in zip(documents, self.saved_files, image_ids):
            self.assertEqual(saved_bytes, image_bytes)
            self.assertEqual(saved_file.meta["knowledge_id"], "knowledge-id")
            self.assertFalse(saved_file.meta["debug"])
            content = "".join(paragraph["content"] for paragraph in document["paragraphs"])
            self.assertIn(f"./oss/file/{saved_file.id}", content)
            self.assertNotIn(original_id, content)

    def test_zip_plain_content_output_remains_a_combined_string(self):
        archive = self.archive_bytes([("first.txt", b"First document"), ("second.txt", b"Second document")])
        self.assertEqual(
            ZipSplitHandle().get_content(io.BytesIO(archive), MagicMock()), "First document\n\nSecond document"
        )
        self.extract_file("documents.zip", archive)
        self.assertEqual(self.extracted_content, "### documents.zip\nFirst document\n\nSecond document")

    def test_length_limit_can_create_multiple_paragraphs_within_each_sheet(self):
        documents = self.split(self.extract(".xlsx", ["Sheet1", "产品说明"]), limit=60, chunk_size=20)
        self.assertEqual([document["name"] for document in documents], ["Sheet1", "产品说明"])
        self.assertTrue(all(len(document["paragraphs"]) > 1 for document in documents))

    def test_qa_keeps_sheet_documents_and_row_questions(self):
        for suffix in (".xlsx", ".xls"):
            with self.subTest(suffix=suffix):
                documents = self.split(self.extract(suffix, ["Sheet1", "产品说明"]), split_strategy="qa")
                self.assertEqual([document["name"] for document in documents], ["Sheet1", "产品说明"])
                for document in documents:
                    self.assertEqual(len(document["paragraphs"]), 2)
                    paragraph = document["paragraphs"][0]
                    self.assertEqual(paragraph["content"], f"{document['name']}回答")
                    self.assertEqual(paragraph["problem_list"], [f"{document['name']}问题"])

    def test_single_sheet_name_matches_qa_including_filename_like_titles(self):
        for name in ("Sheet1", "http说明"):
            with self.subTest(sheet=name):
                extracted = self.extract(".xlsx", [name])
                smart = self.split(extracted)
                qa = self.split(extracted, split_strategy="qa")
                self.assertEqual([document["name"] for document in smart], [name])
                self.assertEqual([document["name"] for document in smart], [document["name"] for document in qa])

    def test_non_excel_headings_stay_in_one_document(self):
        for name in ("notes.md", "notes.txt", "notes.docx"):
            with self.subTest(name=name):
                documents = self.split([{"name": name, "content": "## 第一章\n正文一\n\n## 第二章\n正文二"}])
                self.assertEqual([document["name"] for document in documents], [name])
                self.assertEqual(len(documents[0]["paragraphs"]), 2)

    def test_excel_without_sheet_headings_preserves_original_name(self):
        documents = self.split([{"name": "empty.xlsx", "content": ""}])
        self.assertEqual([document["name"] for document in documents], ["empty.xlsx"])
        self.assertEqual(documents[0]["paragraphs"], [])


class WorkflowExcelDatabaseTests(TestCase):
    def test_zip_sheets_are_persisted_with_separate_paragraphs_and_source_owners(self):
        workbook = openpyxl.Workbook()
        workbook.active.title = "Sheet1"
        workbook.create_sheet("产品说明")
        for sheet in workbook:
            sheet.append(["分段标题", "分段内容", "问题"])
            sheet.append([f"{sheet.title}标题", f"{sheet.title}独立回答", f"{sheet.title}问题"])
        excel_buffer = io.BytesIO()
        workbook.save(excel_buffer)
        archive_buffer = io.BytesIO()
        with ZipFile(archive_buffer, "w", compression=ZIP_DEFLATED) as archive:
            archive.writestr("资料/knowledge.xlsx", excel_buffer.getvalue())
        payload = archive_buffer.getvalue()

        for strategy in ("auto", "custom", "qa"):
            with self.subTest(strategy=strategy):
                knowledge = Knowledge.objects.create(name=f"ZIP sheet regression {strategy}", desc="")
                source = File(
                    file_name="documents.zip",
                    file_size=len(payload),
                    source_type=FileSourceType.KNOWLEDGE,
                    source_id=str(knowledge.id),
                    storage_type="seaweedfs",
                    meta={"seaweedfs_key": f"test-zip/{uuid4()}"},
                )
                File.objects.bulk_create([source])
                workflow_parameters = {
                    "knowledge_id": str(knowledge.id),
                    "knowledge_action_id": str(uuid4()),
                }
                extract = DocumentExtractNode.__new__(DocumentExtractNode)
                extract.get_parameters = MagicMock(return_value={"document_list": ["source", "file_list"]})
                extract.get_workflow_parameters = MagicMock(return_value=workflow_parameters)
                extract.get_workflow_type = MagicMock(return_value=WorkflowType.KNOWLEDGE)
                extract.workflow_manage = MagicMock()
                extract.workflow_manage.get_reference_field.return_value = [
                    {"file_id": str(source.id), "name": source.file_name, "meta": {"source_type": "local"}}
                ]
                extracted_context = {}
                extract.write_context = extracted_context.__setitem__
                with (
                    patch.object(File, "get_bytes", return_value=payload),
                    patch("common.handle.impl.table.xlsx_parse_table_handle.xlsx_embed_cells_images", return_value={}),
                ):
                    extract.execute()

                split = DocumentSplitNode.__new__(DocumentSplitNode)
                split.get_parameters = MagicMock(
                    return_value={
                        "document_list": ["extract", "document_list"],
                        "split_strategy": strategy,
                        "patterns": ["NEVER_MATCH_THIS_SEPARATOR"],
                    }
                )
                split.get_workflow_parameters = MagicMock(return_value=workflow_parameters)
                split.get_workflow_type = MagicMock(return_value=WorkflowType.KNOWLEDGE)
                split.get_reference_content = MagicMock(return_value=extracted_context["document_list"])
                split_context = {}
                split.write_context = split_context.__setitem__
                split.execute()

                writer = KnowledgeWriteNode.__new__(KnowledgeWriteNode)
                writer.get_workflow_parameters = MagicMock(return_value=workflow_parameters)
                documents, _, _ = writer.save(split_context["paragraph_list"], None)

                self.assertEqual([document.name for document in documents], workbook.sheetnames)
                self.assertEqual(Document.objects.filter(knowledge=knowledge).count(), 2)
                source_ids = []
                for document, other_name in zip(documents, reversed(workbook.sheetnames)):
                    document.refresh_from_db()
                    paragraphs = list(Paragraph.objects.filter(document=document))
                    self.assertEqual(len(paragraphs), 1)
                    self.assertIn(f"{document.name}独立回答", paragraphs[0].content)
                    self.assertNotIn(other_name, paragraphs[0].content)
                    self.assertTrue(paragraphs[0].chunks)
                    self.assertEqual(document.meta["source_type"], "local")
                    linked_file = File.objects.get(id=document.meta["source_file_id"])
                    source_ids.append(linked_file.id)
                    self.assertEqual(linked_file.file_name, source.file_name)
                    self.assertEqual(linked_file.source_type, FileSourceType.DOCUMENT)
                    self.assertEqual(linked_file.source_id, str(document.id))
                    self.assertEqual(linked_file.meta["seaweedfs_key"], source.meta["seaweedfs_key"])
                self.assertEqual(len(set(source_ids)), 2)
                self.assertIn(source.id, source_ids)
