# coding=utf-8
"""
@project: MaxKB
@file： text_to_speech_node.py
@desc:
"""

import io
import mimetypes

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.translation import gettext_lazy as _
from pydub import AudioSegment
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode
from application.workflow.message.struct.content import NodeInfo, Position
from application.workflow.message.struct.text_content import TextContent
from application.workflow.status import Status
from common.utils.common import _remove_empty_lines
from knowledge.models import FileSourceType
from models_provider.tools import get_model_instance_by_model_workspace_id
from oss.serializers.file import FileSerializer


class TextToSpeechNodeSerializer(serializers.Serializer):
    tts_model_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Model id"))
    tts_model_id_type = serializers.CharField(required=False, default="custom", label=_("Model id type"))
    tts_model_id_reference = serializers.ListField(
        required=False, child=serializers.CharField(), allow_empty=True, label=_("Reference Field")
    )
    is_result = serializers.BooleanField(required=False, label=_("Whether to return content"))
    content_list = serializers.ListField(required=True, label=_("Text content"))
    model_params_setting = serializers.DictField(required=False, label=_("Model parameter settings"))


def _bytes_to_uploaded_file(file_bytes, file_name="generated_audio.mp3"):
    content_type, _ = mimetypes.guess_type(file_name)
    if content_type is None:
        content_type = "application/octet-stream"
    file_stream = io.BytesIO(file_bytes)
    file_size = len(file_bytes)
    uploaded_file = InMemoryUploadedFile(
        file=file_stream,
        field_name=None,
        name=file_name,
        content_type=content_type,
        size=file_size,
        charset=None,
    )
    return uploaded_file


class TextToSpeechNode(INode):
    serializer_class = TextToSpeechNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = "text-to-speech-node"

    def execute(self):
        node_params = self.get_parameters()
        workflow_params = self.get_workflow_parameters()
        workflow_type = self.get_workflow_type()

        tts_model_id = node_params.get("tts_model_id")
        tts_model_id_type = node_params.get("tts_model_id_type", "custom")
        tts_model_id_reference = node_params.get("tts_model_id_reference")
        model_params_setting = node_params.get("model_params_setting")
        content_list_ref = node_params.get("content_list")
        is_result = node_params.get("is_result", False)

        content = (
            self.workflow_manage.get_reference_field(content_list_ref[0], content_list_ref[1:])
            if content_list_ref
            else ""
        )

        if tts_model_id_type == "reference" and tts_model_id_reference:
            reference_data = self.workflow_manage.get_reference_field(
                tts_model_id_reference[0],
                tts_model_id_reference[1:],
            )
            if reference_data and isinstance(reference_data, dict):
                tts_model_id = reference_data.get("tts_model_id", reference_data.get("model_id", tts_model_id))
                model_params_setting = reference_data.get("model_params_setting")

        if not tts_model_id:
            raise Exception(_("Model is not allowed to be empty"))

        content = _remove_empty_lines(str(content))
        max_length = 1024
        content_chunks = [content[i : i + max_length] for i in range(0, len(content), max_length)]

        audio_segments = []
        temp_files = []

        for chunk in content_chunks:
            self._check_cancelled()
            self.write_context("content", chunk)
            workspace_id = workflow_params.get("workspace_id")
            model = get_model_instance_by_model_workspace_id(tts_model_id, workspace_id, **(model_params_setting or {}))
            audio_byte = model.text_to_speech(chunk)
            temp_file = io.BytesIO(audio_byte)
            audio_segment = AudioSegment.from_file(temp_file)
            audio_segments.append(audio_segment)
            temp_files.append(temp_file)

        combined_audio = AudioSegment.empty()
        for segment in audio_segments:
            combined_audio += segment

        output_buffer = io.BytesIO()
        combined_audio.export(output_buffer, format="mp3")
        combined_bytes = output_buffer.getvalue()
        file_name = "combined_audio.mp3"
        file = _bytes_to_uploaded_file(combined_bytes, file_name)
        file_url = self._upload_file(file, workflow_params, workflow_type)

        file_id = file_url.split("/")[-1]
        audio_list = [{"file_id": file_id, "file_name": file_name, "url": file_url}]

        for temp_file in temp_files:
            temp_file.close()
        output_buffer.close()

        audio_label = f'<audio src="{file_url}" controls style="width: 300px; height: 43px"></audio>'
        self.write_context("answer", audio_label)
        self.write_context("result", audio_list)

        if is_result:
            node_info = NodeInfo(self.get_node_id(), self.get_node_name(), Status.SUCCESS)
            self.write(
                TextContent(self.get_node_id(), audio_label, Status.SUCCESS, node_info, Position(self.get_node_id()))
            )

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
                "content": self.get_context("content"),
                "answer": self.get_context("answer"),
                "result": self.get_context("result"),
            }
        )
        return details
