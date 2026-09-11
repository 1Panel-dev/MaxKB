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
from application.workflow.i_node import INode
from knowledge.models import File, FileSourceType
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
        chat_id = workflow_params.get("chat_id")

        self.write_context("document_list", document)
        if document is None or not isinstance(document, list):
            self.write_context("content", "")
            self.write_context("document_list", [])
            return

        # 按工作流类型确定归属资源 id(知识库/应用/工具),均取自工作流入参
        application_id = None
        tool_id = None
        knowledge_id = None
        workflow_type = self.get_workflow_type()
        if workflow_type == WorkflowType.KNOWLEDGE:
            knowledge_id = workflow_params.get("knowledge_id")
        elif workflow_type == WorkflowType.APPLICATION:
            application_id = workflow_params.get("application_id")
        elif workflow_type == WorkflowType.TOOL:
            tool_id = workflow_params.get("tool_id")

        # doc 文件中内嵌的图片另存为文件
        def save_image(image_list):
            for image in image_list:
                meta = {
                    "debug": False if (application_id or knowledge_id or tool_id) else True,
                    "chat_id": chat_id,
                    "application_id": str(application_id) if application_id else None,
                    "knowledge_id": str(knowledge_id) if knowledge_id else None,
                    "tool_id": str(tool_id) if tool_id else None,
                    "file_id": str(image.id),
                }
                file_bytes = image.meta.pop("content")
                new_file = File(
                    id=meta["file_id"],
                    file_name=image.file_name,
                    file_size=len(file_bytes),
                    source_type=FileSourceType.APPLICATION.value
                    if application_id
                    else FileSourceType.KNOWLEDGE.value
                    if knowledge_id
                    else FileSourceType.TOOL.value,
                    source_id=application_id or knowledge_id or tool_id,
                    meta=meta,
                )
                if not QuerySet(File).filter(id=new_file.id).exists():
                    new_file.save(file_bytes)

        get_buffer = FileBufferHandle().get_buffer
        content = []
        document_list = []
        for doc in document:
            file = QuerySet(File).filter(id=doc["file_id"]).first()
            buffer = io.BytesIO(file.get_bytes())
            buffer.name = doc["name"]  # this is the important line

            for split_handle in parse_table_handle_list + split_handles:
                if split_handle.support(buffer, get_buffer):
                    buffer.seek(0)
                    file_content = split_handle.get_content(buffer, save_image)
                    content.append("### " + doc["name"] + "\n" + file_content)
                    document_list.append({"id": str(file.id), "name": doc["name"], "content": file_content})
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
                "enableException": self.node.properties.get("enableException"),
            }
        )
        return details
