# coding=utf-8
"""
@project: MaxKB
@file： speech_to_text_node.py
@desc:
"""

import asyncio
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.workflow.common import AsyncRunner, WorkflowType
from application.workflow.content_type import ContentType
from application.workflow.file_access import get_authorized_file
from application.workflow.i_node import INode
from application.workflow.message.struct.content import Content, NodeInfo, Position
from application.workflow.message.struct.text_content import TextContent
from application.workflow.status import Status
from common.utils.common import split_and_transcribe, any_to_mp3
from common.exception.app_exception import AppApiException
from models_provider.models import Model
from models_provider.tools import get_model_instance_by_model_workspace_id


class SpeechToTextNodeSerializer(serializers.Serializer):
    stt_model_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Model id"))
    stt_model_id_type = serializers.CharField(required=False, default="custom", label=_("Model id type"))
    stt_model_id_reference = serializers.ListField(
        required=False, child=serializers.CharField(), allow_empty=True, label=_("Reference Field")
    )
    is_result = serializers.BooleanField(required=False, label=_("Whether to return content"))
    audio_list = serializers.ListField(required=True, label=_("The audio file cannot be empty"))
    model_params_setting = serializers.DictField(required=False, label=_("Model parameter settings"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        # reference / default 在运行时才解析,此处只校验自定义模型
        if (self.data.get("stt_model_id_type") or "custom") in ("reference", "default"):
            return
        model_id = self.data.get("stt_model_id")
        if not model_id or not QuerySet(Model).filter(id=model_id).exists():
            raise AppApiException(500, _("The model of the node does not exist"))


def _process_audio_item(file, model):
    file_format = file.file_name.split(".")[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_format}") as temp_file:
        temp_file.write(file.get_bytes())
        temp_file_path = temp_file.name
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_amr_file:
        temp_mp3_path = temp_amr_file.name
    any_to_mp3(temp_file_path, temp_mp3_path)
    try:
        transcription = split_and_transcribe(temp_mp3_path, model)
        return {file.file_name: transcription}
    finally:
        os.remove(temp_file_path)
        os.remove(temp_mp3_path)


def _process_audio_items(file_list, model):
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(lambda file: _process_audio_item(file, model), file_list))
    return results


class SpeechToTextNode(INode):
    serializer_class = SpeechToTextNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = "speech-to-text-node"

    def __init__(self, node, workflow_manage, get_node_parameters):
        super().__init__(node, workflow_manage, get_node_parameters)
        self.async_runner = AsyncRunner()

    def cancel(self):
        self.async_runner.cancel()
        super().cancel()

    def write(self, message: Content):
        """is_result 关闭时不向用户输出正文"""
        if message.type in (ContentType.TEXT, ContentType.HTML) and not self.get_parameters().get("is_result", False):
            return
        super().write(message)

    def execute(self):
        node_params = self.get_parameters()
        workflow_params = self.get_workflow_parameters()

        stt_model_id = node_params.get("stt_model_id")
        stt_model_id_type = node_params.get("stt_model_id_type", "custom")
        stt_model_id_reference = node_params.get("stt_model_id_reference")
        model_params_setting = node_params.get("model_params_setting")
        audio_list_ref = node_params.get("audio_list")

        audio_list = self.workflow_manage.get_reference_field(audio_list_ref[0], audio_list_ref[1:])
        for audio in audio_list:
            if "file_id" not in audio:
                raise ValueError(
                    _("Parameter value error: The uploaded audio lacks file_id, and the audio upload fails")
                )

        if stt_model_id_type == "reference" and stt_model_id_reference:
            reference_data = self.workflow_manage.get_reference_field(
                stt_model_id_reference[0],
                stt_model_id_reference[1:],
            )
            if reference_data and isinstance(reference_data, dict):
                stt_model_id = reference_data.get("stt_model_id", reference_data.get("model_id", stt_model_id))
                model_params_setting = reference_data.get("model_params_setting")

        if stt_model_id_type == "default":
            default_model_setting = workflow_params.get("default_model_setting").get("STT") or {}
            if default_model_setting and isinstance(default_model_setting, dict):
                stt_model_id = default_model_setting.get("model_id", stt_model_id)
                model_params_setting = default_model_setting.get("model_params_setting")

        if not stt_model_id:
            raise Exception(_("Model is not allowed to be empty"))

        workspace_id = workflow_params.get("workspace_id")
        stt_model = get_model_instance_by_model_workspace_id(stt_model_id, workspace_id, **(model_params_setting or {}))

        self.data["audio_list"] = audio_list
        file_list = [get_authorized_file(audio["file_id"], workflow_params) for audio in audio_list]

        self._check_cancelled()
        result = self.async_runner.run_async(lambda: self._await_process(file_list, stt_model))
        content = []
        result_content = []
        for item in result:
            for key, value in item.items():
                content.append(f"### {key}\n{value}")
                result_content.append(value)

        answer = "\n".join(result_content)
        self.data["answer"] = answer
        self.write_context("result", answer)
        self.data["content"] = content

        node_info = NodeInfo(self.get_node_id(), self.get_node_name(), Status.SUCCESS)
        self.write(TextContent(self.get_node_id(), answer, Status.SUCCESS, node_info, Position(self.get_node_id())))

    async def _await_process(self, file_list, stt_model):
        return await asyncio.to_thread(_process_audio_items, file_list, stt_model)

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        details.update(
            {
                "answer": self.data.get("answer"),
                "result": self.get_context("result"),
                "content": self.data.get("content"),
                "audio_list": self.data.get("audio_list"),
            }
        )
        return details
