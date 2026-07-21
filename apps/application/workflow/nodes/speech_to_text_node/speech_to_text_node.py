# coding=utf-8
"""
    @project: MaxKB
    @file： speech_to_text_node.py
    @desc:
"""
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode
from application.workflow.message.struct.content import NodeInfo, Position
from application.workflow.message.struct.text_content import TextContent
from application.workflow.status import Status
from common.utils.common import split_and_transcribe, any_to_mp3
from knowledge.models import File
from models_provider.tools import get_model_instance_by_model_workspace_id


class SpeechToTextNodeSerializer(serializers.Serializer):
    stt_model_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Model id"))
    stt_model_id_type = serializers.CharField(required=False, default='custom', label=_("Model id type"))
    stt_model_id_reference = serializers.ListField(required=False, child=serializers.CharField(), allow_empty=True,
                                                   label=_("Reference Field"))
    is_result = serializers.BooleanField(required=False, label=_('Whether to return content'))
    audio_list = serializers.ListField(required=True, label=_("The audio file cannot be empty"))
    model_params_setting = serializers.DictField(required=False, label=_("Model parameter settings"))


def _process_audio_item(audio_item, model):
    file = QuerySet(File).filter(id=audio_item['file_id']).first()
    file_format = file.file_name.split('.')[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_format}') as temp_file:
        temp_file.write(file.get_bytes())
        temp_file_path = temp_file.name
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_amr_file:
        temp_mp3_path = temp_amr_file.name
    any_to_mp3(temp_file_path, temp_mp3_path)
    try:
        transcription = split_and_transcribe(temp_mp3_path, model)
        return {file.file_name: transcription}
    finally:
        os.remove(temp_file_path)
        os.remove(temp_mp3_path)


def _process_audio_items(audio_list, model):
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(lambda item: _process_audio_item(item, model), audio_list))
    return results


class SpeechToTextNode(INode):
    serializer_class = SpeechToTextNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = 'speech-to-text-node'

    def execute(self):
        node_params = self.get_parameters()
        workflow_params = self.get_workflow_parameters()

        stt_model_id = node_params.get('stt_model_id')
        stt_model_id_type = node_params.get('stt_model_id_type', 'custom')
        stt_model_id_reference = node_params.get('stt_model_id_reference')
        model_params_setting = node_params.get('model_params_setting')
        audio_list_ref = node_params.get('audio_list')
        is_result = node_params.get('is_result', False)

        audio_list = self.workflow_manage.get_reference_field(audio_list_ref[0], audio_list_ref[1:])
        for audio in audio_list:
            if 'file_id' not in audio:
                raise ValueError(
                    _("Parameter value error: The uploaded audio lacks file_id, and the audio upload fails"))

        if stt_model_id_type == 'reference' and stt_model_id_reference:
            reference_data = self.workflow_manage.get_reference_field(
                stt_model_id_reference[0], stt_model_id_reference[1:],
            )
            if reference_data and isinstance(reference_data, dict):
                stt_model_id = reference_data.get('stt_model_id', reference_data.get('model_id', stt_model_id))
                model_params_setting = reference_data.get('model_params_setting')

        if not stt_model_id:
            raise Exception(_('Model is not allowed to be empty'))

        workspace_id = workflow_params.get('workspace_id')
        stt_model = get_model_instance_by_model_workspace_id(stt_model_id, workspace_id,
                                                             **(model_params_setting or {}))

        self.write_context('audio_list', audio_list)

        result = _process_audio_items(audio_list, stt_model)
        content = []
        result_content = []
        for item in result:
            for key, value in item.items():
                content.append(f'### {key}\n{value}')
                result_content.append(value)

        answer = '\n'.join(result_content)
        self.write_context('answer', answer)
        self.write_context('result', answer)
        self.write_context('content', content)

        if is_result:
            node_info = NodeInfo(self.get_node_id(), self.get_node_name(), Status.SUCCESS)
            self.write(TextContent(self.get_node_id(), answer, Status.SUCCESS, node_info,
                                   Position(self.get_node_id())))
