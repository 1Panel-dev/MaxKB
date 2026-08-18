# coding=utf-8
"""
@project: MaxKB
@Author：虎虎虎
@file： image_generate_node.py
@date：2026/7/6 16:00
@desc:
"""

import base64
from functools import reduce

import requests
import uuid_utils.compat as uuid
from django.utils.translation import gettext_lazy as _
from langchain_core.messages import HumanMessage, AIMessage
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode
from application.workflow.message.struct.content import NodeInfo, Position
from application.workflow.message.struct.text_content import TextContent
from application.workflow.status import Status
from common.utils.common import bytes_to_uploaded_file
from knowledge.models import FileSourceType
from models_provider.tools import get_model_instance_by_model_workspace_id
from oss.serializers.file import FileSerializer


class ImageGenerateNodeSerializer(serializers.Serializer):
    model_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Model id"))
    model_id_type = serializers.CharField(required=False, default="custom", label=_("Model id type"))
    model_id_reference = serializers.ListField(
        required=False, child=serializers.CharField(), allow_empty=True, label=_("Reference Field")
    )
    prompt = serializers.CharField(required=True, label=_("Prompt word (positive)"))
    negative_prompt = serializers.CharField(
        required=False, label=_("Prompt word (negative)"), allow_null=True, allow_blank=True
    )
    dialogue_number = serializers.IntegerField(
        required=False, default=0, label=_("Number of multi-round conversations")
    )
    dialogue_type = serializers.CharField(required=False, default="NODE", label=_("Conversation storage type"))
    is_result = serializers.BooleanField(required=False, label=_("Whether to return content"))
    model_params_setting = serializers.JSONField(required=False, default=dict, label=_("Model parameter settings"))


class ImageGenerateNode(INode):
    serializer_class = ImageGenerateNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = "image-generate-node"

    def execute(self):
        node_params = self.get_parameters()
        workflow_params = self.get_workflow_parameters()

        model_id = node_params.get("model_id")
        model_id_type = node_params.get("model_id_type", "custom")
        model_id_reference = node_params.get("model_id_reference")
        prompt = node_params.get("prompt", "")
        negative_prompt = node_params.get("negative_prompt", "")
        dialogue_number = node_params.get("dialogue_number", 0)
        dialogue_type = node_params.get("dialogue_type", "NODE")
        is_result = node_params.get("is_result", False)
        model_params_setting = node_params.get("model_params_setting")

        workflow_type = self.get_workflow_type()
        if workflow_type in (WorkflowType.KNOWLEDGE, WorkflowType.TOOL):
            history_chat_record = []
        else:
            history_chat_record = workflow_params.get("history_chat_record", [])

        if model_id_type == "reference" and model_id_reference:
            reference_data = self.workflow_manage.get_reference_field(
                model_id_reference[0],
                model_id_reference[1:],
            )
            if reference_data and isinstance(reference_data, dict):
                model_id = reference_data.get("model_id", model_id)
                model_params_setting = reference_data.get("model_params_setting")

        if not model_id:
            raise Exception(_("Model is not allowed to be empty"))

        workspace_id = workflow_params.get("workspace_id")
        tti_model = get_model_instance_by_model_workspace_id(model_id, workspace_id, **(model_params_setting or {}))

        history_message = self._get_history_message(history_chat_record, dialogue_number)
        self.write_context("history_message", [{"content": m.content, "role": m.type} for m in (history_message or [])])

        question = self.workflow_manage.generate_prompt(prompt)
        self.write_context("question", question)
        self.write_context("negative_prompt", self.workflow_manage.generate_prompt(negative_prompt or ""))
        self.write_context("dialogue_type", dialogue_type)

        self._check_cancelled()
        image_urls = tti_model.generate_image(question, negative_prompt)

        file_urls = []
        for image_url in image_urls:
            file_name = "generated_image.png"
            if isinstance(image_url, str):
                if image_url.startswith("http"):
                    image_url = requests.get(image_url).content
                elif image_url.startswith("data:image"):
                    header, encoded = image_url.split(",", 1)
                    image_url = base64.b64decode(encoded)
                else:
                    image_url = base64.b64decode(image_url)
            file = bytes_to_uploaded_file(image_url, file_name)
            file_url = self._upload_file(file, workflow_params, workflow_type)
            file_urls.append(file_url)

        image_list = [{"file_id": path.split("/")[-1], "url": path} for path in file_urls]
        self.write_context("image_list", image_list)

        answer = " ".join([f"![Image]({path})" for path in file_urls])
        self.write_context("answer", answer)

        if is_result:
            node_info = NodeInfo(self.get_node_id(), self.get_node_name(), Status.SUCCESS)
            self.write(
                TextContent(str(uuid.uuid7()), answer, Status.SUCCESS, node_info, position=Position(self.get_node_id()))
            )

    def _get_history_message(self, history_chat_record, dialogue_number):
        start_index = len(history_chat_record) - dialogue_number
        return reduce(
            lambda x, y: [*x, *y],
            [
                [
                    self._generate_history_human_message(history_chat_record[index]),
                    self._generate_history_ai_message(history_chat_record[index]),
                ]
                for index in range(max(start_index, 0), len(history_chat_record))
            ],
            [],
        )

    def _generate_history_human_message(self, chat_record):
        for data in chat_record.details.values():
            if self.node.id == data.get("node_id") and "image_list" in data:
                image_list = data["image_list"]
                if len(image_list) == 0 or data.get("dialogue_type") == "WORKFLOW":
                    return HumanMessage(content=chat_record.problem_text)
                return HumanMessage(content=data.get("question", chat_record.problem_text))
        return HumanMessage(content=chat_record.problem_text)

    def _generate_history_ai_message(self, chat_record):
        for val in chat_record.details.values():
            if self.node.id == val.get("node_id") and "image_list" in val:
                if val.get("dialogue_type") == "WORKFLOW":
                    return chat_record.get_ai_message()
                image_list = val["image_list"]
                return AIMessage(
                    content=[{"type": "image_url", "image_url": {"url": f"{file_url}"}} for file_url in image_list]
                )
        return chat_record.get_ai_message()

    def _upload_file(self, file, workflow_params, workflow_type):
        if workflow_type == WorkflowType.KNOWLEDGE:
            return self._upload_knowledge_file(file, workflow_params)
        if workflow_type == WorkflowType.TOOL:
            return self._upload_tool_file(file, workflow_params)
        return self._upload_application_file(file, workflow_params)

    def _upload_knowledge_file(self, file, workflow_params):
        knowledge_id = workflow_params.get("knowledge_id")
        return FileSerializer(
            data={
                "file": file,
                "meta": {"debug": False, "knowledge_id": knowledge_id},
                "source_id": knowledge_id,
                "source_type": FileSourceType.KNOWLEDGE.value,
            }
        ).upload()

    def _upload_tool_file(self, file, workflow_params):
        tool_id = workflow_params.get("tool_id")
        return FileSerializer(
            data={
                "file": file,
                "meta": {"debug": False, "tool_id": tool_id},
                "source_id": tool_id,
                "source_type": FileSourceType.TOOL.value,
            }
        ).upload()

    def _upload_application_file(self, file, workflow_params):
        application_id = workflow_params.get("application_id")
        chat_id = workflow_params.get("chat_id")
        return FileSerializer(
            data={
                "file": file,
                "meta": {"debug": False, "chat_id": chat_id, "application_id": application_id},
                "source_id": application_id,
                "source_type": FileSourceType.APPLICATION.value,
            }
        ).upload()

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        details.update(
            {
                "question": self.get_context("question"),
                "answer": self.get_context("answer"),
                "image_list": self.get_context("image_list"),
                "negative_prompt": self.get_context("negative_prompt"),
            }
        )
        return details
