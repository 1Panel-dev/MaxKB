# coding=utf-8
"""
@project: MaxKB
@Author:  虎虎虎
@file:    document_split_node.py
@date:    2026/9/11
@desc:    文档分段节点：把提取出的文档内容按策略切分为段落,供知识库写入
"""

import io
import mimetypes
from typing import List

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode
from common.chunk import text_to_chunk
from knowledge.serializers.document import FileBufferHandle, default_split_handle, md_qa_split_handle


class DocumentSplitNodeSerializer(serializers.Serializer):
    document_list = serializers.ListField(required=False, label=_("document list"))
    split_strategy = serializers.ChoiceField(
        choices=["auto", "custom", "qa"], required=False, label=_("split strategy"), default="auto"
    )
    paragraph_title_relate_problem_type = serializers.ChoiceField(
        choices=["custom", "referencing"],
        required=False,
        label=_("paragraph title relate problem type"),
        default="custom",
    )
    paragraph_title_relate_problem = serializers.BooleanField(
        required=False, label=_("paragraph title relate problem"), default=False
    )
    paragraph_title_relate_problem_reference = serializers.ListField(
        required=False, label=_("paragraph title relate problem reference"), child=serializers.CharField(), default=[]
    )
    document_name_relate_problem_type = serializers.ChoiceField(
        choices=["custom", "referencing"],
        required=False,
        label=_("document name relate problem type"),
        default="custom",
    )
    document_name_relate_problem = serializers.BooleanField(
        required=False, label=_("document name relate problem"), default=False
    )
    document_name_relate_problem_reference = serializers.ListField(
        required=False, label=_("document name relate problem reference"), child=serializers.CharField(), default=[]
    )
    limit = serializers.IntegerField(required=False, label=_("limit"), default=4096)
    limit_type = serializers.ChoiceField(
        choices=["custom", "referencing"],
        required=False,
        label=_("document name relate problem type"),
        default="custom",
    )
    limit_reference = serializers.ListField(
        required=False, label=_("limit reference"), child=serializers.CharField(), default=[]
    )
    chunk_size = serializers.IntegerField(required=False, label=_("chunk size"), default=256)
    chunk_size_type = serializers.ChoiceField(
        choices=["custom", "referencing"], required=False, label=_("chunk size type"), default="custom"
    )
    chunk_size_reference = serializers.ListField(
        required=False, label=_("chunk size reference"), child=serializers.CharField(), default=[]
    )
    patterns = serializers.ListField(required=False, label=_("patterns"), child=serializers.CharField(), default=[])
    patterns_type = serializers.ChoiceField(
        choices=["custom", "referencing"], required=False, label=_("patterns type"), default="custom"
    )
    patterns_reference = serializers.ListField(
        required=False, label=_("patterns reference"), child=serializers.CharField(), default=[]
    )
    with_filter = serializers.BooleanField(required=False, label=_("with filter"), default=False)
    with_filter_type = serializers.ChoiceField(
        choices=["custom", "referencing"], required=False, label=_("with filter type"), default="custom"
    )
    with_filter_reference = serializers.ListField(
        required=False, label=_("with filter reference"), child=serializers.CharField(), default=[]
    )


def bytes_to_uploaded_file(file_bytes, file_name="file.txt"):
    if file_name.startswith("http"):
        file_name = "file.txt"
    content_type, _unused = mimetypes.guess_type(file_name)
    if content_type is None:
        # 如果未能识别，设置为默认的二进制文件类型
        content_type = "application/octet-stream"
    # 创建一个内存中的字节流对象
    file_stream = io.BytesIO(file_bytes)
    # 获取文件大小
    file_size = len(file_bytes)
    # 创建 InMemoryUploadedFile 对象
    uploaded_file = InMemoryUploadedFile(
        file=file_stream,
        field_name=None,
        name=file_name,
        content_type=content_type,
        size=file_size,
        charset=None,
    )
    return uploaded_file


class DocumentSplitNode(INode):
    serializer_class = DocumentSplitNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = "document-split-node"

    def get_reference_content(self, fields: List[str]):
        return self.workflow_manage.get_reference_field(fields[0], fields[1:]) if fields else None

    def execute(self):
        # 通过 serializer 应用默认值(新引擎不会对 node_data 自动校验/填默认)
        serializer = DocumentSplitNodeSerializer(data=self.get_parameters())
        serializer.is_valid(raise_exception=True)
        params = serializer.data

        knowledge_id = (
            self.get_workflow_parameters().get("knowledge_id")
            if self.get_workflow_type() == WorkflowType.KNOWLEDGE
            else None
        )

        document_list = params.get("document_list")
        split_strategy = params.get("split_strategy")
        paragraph_title_relate_problem_type = params.get("paragraph_title_relate_problem_type")
        paragraph_title_relate_problem = params.get("paragraph_title_relate_problem")
        paragraph_title_relate_problem_reference = params.get("paragraph_title_relate_problem_reference")
        document_name_relate_problem_type = params.get("document_name_relate_problem_type")
        document_name_relate_problem = params.get("document_name_relate_problem")
        document_name_relate_problem_reference = params.get("document_name_relate_problem_reference")
        limit = params.get("limit")
        limit_type = params.get("limit_type")
        limit_reference = params.get("limit_reference")
        chunk_size = params.get("chunk_size")
        chunk_size_type = params.get("chunk_size_type")
        chunk_size_reference = params.get("chunk_size_reference")
        patterns = params.get("patterns")
        patterns_type = params.get("patterns_type")
        patterns_reference = params.get("patterns_reference")
        with_filter = params.get("with_filter")
        with_filter_type = params.get("with_filter_type")
        with_filter_reference = params.get("with_filter_reference")

        self.write_context("knowledge_id", knowledge_id)
        file_list = self.get_reference_content(document_list)

        # 处理引用类型的参数
        if patterns_type == "referencing":
            patterns = self.get_reference_content(patterns_reference)
        if limit_type == "referencing":
            limit = self.get_reference_content(limit_reference)
        if chunk_size_type == "referencing":
            chunk_size = self.get_reference_content(chunk_size_reference)
        if with_filter_type == "referencing":
            with_filter = self.get_reference_content(with_filter_reference)

        paragraph_list = []
        for doc in file_list:
            get_buffer = FileBufferHandle().get_buffer

            file_mem = bytes_to_uploaded_file(doc["content"].encode("utf-8"), doc["name"])
            if split_strategy == "qa":
                result = md_qa_split_handle.handle(file_mem, get_buffer, self._save_image)
            else:
                result = default_split_handle.handle(
                    file_mem, patterns, with_filter, limit, get_buffer, self._save_image
                )
            # 统一处理结果为列表
            results = result if isinstance(result, list) else [result]

            for item in results:
                self._process_split_result(
                    item,
                    knowledge_id,
                    doc.get("id"),
                    doc.get("name"),
                    split_strategy,
                    paragraph_title_relate_problem_type,
                    paragraph_title_relate_problem,
                    paragraph_title_relate_problem_reference,
                    document_name_relate_problem_type,
                    document_name_relate_problem,
                    document_name_relate_problem_reference,
                    chunk_size,
                )

            paragraph_list += results

        self.write_context("paragraph_list", paragraph_list)
        self.write_context("document_list", file_list)
        self.write_context("limit", limit)
        self.write_context("chunk_size", chunk_size)
        self.write_context("with_filter", with_filter)
        self.write_context("patterns", patterns)
        self.write_context("split_strategy", split_strategy)

    def _save_image(self, image_list):
        pass

    def _process_split_result(
        self,
        item,
        knowledge_id,
        source_file_id,
        file_name,
        split_strategy,
        paragraph_title_relate_problem_type,
        paragraph_title_relate_problem,
        paragraph_title_relate_problem_reference,
        document_name_relate_problem_type,
        document_name_relate_problem,
        document_name_relate_problem_reference,
        chunk_size,
    ):
        """处理文档分割结果"""
        item["meta"] = {
            "knowledge_id": knowledge_id,
            "source_file_id": source_file_id,
            "source_url": file_name,
        }
        if item.get("name", "file.txt") == "file.txt":
            item["name"] = file_name
        item["source_file_id"] = source_file_id
        item["paragraphs"] = item.pop("content", item.get("paragraphs", []))

        for paragraph in item["paragraphs"]:
            paragraph["problem_list"] = self._generate_problem_list(
                paragraph,
                file_name,
                split_strategy,
                paragraph_title_relate_problem_type,
                paragraph_title_relate_problem,
                paragraph_title_relate_problem_reference,
                document_name_relate_problem_type,
                document_name_relate_problem,
                document_name_relate_problem_reference,
            )
            paragraph["is_active"] = True
            paragraph["chunks"] = text_to_chunk(paragraph["content"], chunk_size)

    def _generate_problem_list(
        self,
        paragraph,
        document_name,
        split_strategy,
        paragraph_title_relate_problem_type,
        paragraph_title_relate_problem,
        paragraph_title_relate_problem_reference,
        document_name_relate_problem_type,
        document_name_relate_problem,
        document_name_relate_problem_reference,
    ):
        if paragraph_title_relate_problem_type == "referencing":
            paragraph_title_relate_problem = self.get_reference_content(paragraph_title_relate_problem_reference)
        if document_name_relate_problem_type == "referencing":
            document_name_relate_problem = self.get_reference_content(document_name_relate_problem_reference)

        problem_list = [
            item
            for p in paragraph.get("problem_list", [])
            for item in p.get("content", "").split("<br>")
            if item.strip()
        ]

        if split_strategy == "auto":
            if paragraph_title_relate_problem and paragraph.get("title"):
                problem_list.append(paragraph.get("title"))
            if document_name_relate_problem and document_name:
                problem_list.append(document_name)
        elif split_strategy == "custom":
            if paragraph_title_relate_problem and paragraph.get("title"):
                problem_list.append(paragraph.get("title"))
            if document_name_relate_problem and document_name:
                problem_list.append(document_name)
        elif split_strategy == "qa":
            if document_name_relate_problem and document_name:
                problem_list.append(document_name)

        return list(set(problem_list))

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        paragraph_list = self.get_context("paragraph_list") or []
        # 每个文档保留前 5 个分段
        limited_paragraph_list = []
        for doc in paragraph_list:
            if doc.get("paragraphs"):
                doc_copy = doc.copy()
                doc_copy["paragraphs"] = doc["paragraphs"][:5]
                limited_paragraph_list.append(doc_copy)
            else:
                limited_paragraph_list.append(doc)

        details.update(
            {
                "paragraph_list": limited_paragraph_list,
                "limit": self.get_context("limit"),
                "chunk_size": self.get_context("chunk_size"),
                "with_filter": self.get_context("with_filter"),
                "patterns": self.get_context("patterns"),
                "split_strategy": self.get_context("split_strategy"),
                "enableException": self.node.properties.get("enableException"),
            }
        )
        return details
