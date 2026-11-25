# coding=utf-8
"""
@project: MaxKB
@Author:  虎虎虎
@file:    document_extract_node.py
@date:    2026/9/11
@desc:    文档内容提取节点：把引用到的文件解析为文本内容,并保存文档内嵌图片
"""

import io

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.file_access import generated_file_target, get_authorized_file
from application.workflow.i_node import INode
from common.handle.impl.text.zip_split_handle import ZipSplitHandle
from knowledge.models import File
from knowledge.serializers.document import FileBufferHandle, parse_table_handle_list, split_handles

splitter = "\n`-----------------------------------`\n"


class DocumentExtractNodeSerializer(serializers.Serializer):
    document_list = serializers.ListField(required=False, label=_("document"))


class DocumentExtractNode(INode):
    serializer_class = DocumentExtractNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = "document-extract-node"

    def execute(self):
        node_params = self.get_parameters()
        workflow_params = self.get_workflow_parameters()
        document_reference = node_params.get("document_list") or []
        document = (
            self.workflow_manage.get_reference_field(document_reference[0], document_reference[1:])
            if document_reference
            else None
        )
        self.write_context("document_list", document)
        if document is None or not isinstance(document, list):
            self.write_context("content", "")
            self.write_context("document_list", [])
            return

        # doc 文件中内嵌的图片另存为文件,按根资源存储(见 generated_file_target)
        def save_image(image_list):
            source_type, source_id, target_meta = generated_file_target(workflow_params)
            for image in image_list:
                meta = {**target_meta, "file_id": str(image.id)}
                file_bytes = image.meta.pop("content")
                new_file = File(
                    id=meta["file_id"],
                    file_name=image.file_name,
                    file_size=len(file_bytes),
                    source_type=source_type,
                    source_id=source_id,
                    meta=meta,
                )
                if not QuerySet(File).filter(id=new_file.id).exists():
                    new_file.save(file_bytes)

        get_buffer = FileBufferHandle().get_buffer
        content = []
        document_list = []
        for doc in document:
            file = get_authorized_file(doc["file_id"], workflow_params)
            buffer = io.BytesIO(file.get_bytes())
            buffer.name = doc["name"]  # this is the important line

            for split_handle in parse_table_handle_list + split_handles:
                if split_handle.support(buffer, get_buffer):
                    buffer.seek(0)
                    if isinstance(split_handle, ZipSplitHandle):
                        extracted_documents = split_handle.get_documents(
                            buffer, save_image, parse_table_handle_list + split_handles
                        )
                    else:
                        extracted_documents = [
                            {"name": doc["name"], "content": split_handle.get_content(buffer, save_image)}
                        ]
                    file_content = "\n\n".join(item["content"] for item in extracted_documents)
                    content.append("### " + doc["name"] + "\n" + file_content)
                    document_list.extend(
                        {
                            "id": str(file.id),
                            "name": item["name"],
                            "content": item["content"],
                            "meta": {**(doc.get("meta") or {}), "source_file_id": str(file.id)},
                        }
                        for item in extracted_documents
                    )
                    break

        self.write_context("content", splitter.join(content))
        self.write_context("document_list", document_list)

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        content = (self.get_context("content") or "").split(splitter)
        details.update(
            {
                # 不保存 content 全部内容,因为 content 可能非常大
                "content": [file_content[:500] for file_content in content],
                "document_list": self.get_context("document_list"),
            }
        )
        return details
