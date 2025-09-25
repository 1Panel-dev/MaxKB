# coding=utf-8
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor

from django.db.models import QuerySet

from application.flow.i_step_node import NodeResult
from application.flow.step_node.speech_to_text_step_node.i_speech_to_text_node import ISpeechToTextNode
from common.utils.common import split_and_transcribe, any_to_mp3
from knowledge.models import File
from models_provider.tools import get_model_instance_by_model_workspace_id


class BaseSpeechToTextNode(ISpeechToTextNode):

    def save_context(self, details, workflow_manage):
        self.context['answer'] = details.get('answer')
        self.context['result'] = details.get('answer')
        if self.node_params.get('is_result', False):
            self.answer_text = details.get('answer')

    def execute(self, stt_model_id, chat_id, audio, model_params_setting=None, **kwargs) -> NodeResult:
        workspace_id = self.workflow_manage.get_body().get('workspace_id')
        stt_model = get_model_instance_by_model_workspace_id(stt_model_id, workspace_id, **model_params_setting)
        audio_list = audio
        self.context['audio_list'] = audio

        def process_audio_item(audio_item, model):
            file = QuerySet(File).filter(id=audio_item['file_id']).first()
            # 根据file_name 吧文件转成mp3格式
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

        def process_audio_items(audio_list, model):
            with ThreadPoolExecutor(max_workers=5) as executor:
                results = list(executor.map(lambda item: process_audio_item(item, model), audio_list))
            return results

        result = process_audio_items(audio_list, stt_model)
        content = []
        result_content = []
        for item in result:
            for key, value in item.items():
                content.append(f'### {key}\n{value}')
                result_content.append(value)
        return NodeResult({'answer': '\n'.join(result_content), 'result': '\n'.join(result_content),
                           'content': content}, {})

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'answer': self.context.get('answer'),
            'content': self.context.get('content'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message,
            'audio_list': self.context.get('audio_list'),
        }
