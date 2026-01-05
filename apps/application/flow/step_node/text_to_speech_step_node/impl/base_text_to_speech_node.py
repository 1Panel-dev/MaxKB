# coding=utf-8
import io
import mimetypes

from django.core.files.uploadedfile import InMemoryUploadedFile

from application.flow.common import WorkflowMode
from application.flow.i_step_node import NodeResult
from application.flow.step_node.text_to_speech_step_node.i_text_to_speech_node import ITextToSpeechNode
from common.utils.common import _remove_empty_lines
from knowledge.models import FileSourceType
from models_provider.tools import get_model_instance_by_model_workspace_id
from oss.serializers.file import FileSerializer
from pydub import AudioSegment


def bytes_to_uploaded_file(file_bytes, file_name="generated_audio.mp3"):
    content_type, _ = mimetypes.guess_type(file_name)
    if content_type is None:
        # 如果未能识别，设置为默认的二进制文件类型
        content_type = "application/octet-stream"
    # 创建一个内存中的字节流对象
    file_stream = io.BytesIO(file_bytes)

    # 获取文件大小
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


class BaseTextToSpeechNode(ITextToSpeechNode):
    def save_context(self, details, workflow_manage):
        self.context['answer'] = details.get('answer')
        self.context['result'] = details.get('result')
        self.context['exception_message'] = details.get('err_message')
        if self.node_params.get('is_result', False):
            self.answer_text = details.get('answer')

    def execute(self, tts_model_id,
                content, model_params_setting=None,
                max_length=1024, **kwargs) -> NodeResult:
        # 分割文本为合理片段
        content = _remove_empty_lines(content)
        content_chunks = [content[i:i + max_length]
                          for i in range(0, len(content), max_length)]

        # 生成并收集所有音频片段
        audio_segments = []
        temp_files = []

        for i, chunk in enumerate(content_chunks):
            self.context['content'] = chunk
            workspace_id = self.workflow_manage.get_body().get('workspace_id')
            model = get_model_instance_by_model_workspace_id(
                tts_model_id, workspace_id, **model_params_setting)

            audio_byte = model.text_to_speech(chunk)

            # 保存为临时音频文件用于合并
            temp_file = io.BytesIO(audio_byte)
            audio_segment = AudioSegment.from_file(temp_file)
            audio_segments.append(audio_segment)
            temp_files.append(temp_file)

        # 合并所有音频片段
        combined_audio = AudioSegment.empty()
        for segment in audio_segments:
            combined_audio += segment

        # 将合并后的音频转为字节流
        output_buffer = io.BytesIO()
        combined_audio.export(output_buffer, format="mp3")
        combined_bytes = output_buffer.getvalue()
        file_name = 'combined_audio.mp3'
        file = bytes_to_uploaded_file(combined_bytes, file_name)
        # 存储合并后的音频文件
        file_url = self.upload_file(file)
        # 生成音频标签
        audio_label = f'<audio src="{file_url}" controls style="width: 300px; height: 43px"></audio>'
        file_id = file_url.split('/')[-1]
        audio_list = [{'file_id': file_id, 'file_name': file_name, 'url': file_url}]

        # 关闭所有临时文件
        for temp_file in temp_files:
            temp_file.close()
        output_buffer.close()

        return NodeResult({
            'answer': audio_label,
            'result': audio_list
        }, {})

    def upload_file(self, file):
        if [WorkflowMode.KNOWLEDGE, WorkflowMode.KNOWLEDGE_LOOP].__contains__(
                self.workflow_manage.flow.workflow_mode):
            return self.upload_knowledge_file(file)
        return self.upload_application_file(file)

    def upload_knowledge_file(self, file):
        knowledge_id = self.workflow_params.get('knowledge_id')
        meta = {
            'debug': False,
            'knowledge_id': knowledge_id,
        }
        file_url = FileSerializer(data={
            'file': file,
            'meta': meta,
            'source_id': knowledge_id,
            'source_type': FileSourceType.KNOWLEDGE.value
        }).upload()
        return file_url

    def upload_application_file(self, file):
        application = self.workflow_manage.work_flow_post_handler.chat_info.application
        chat_id = self.workflow_params.get('chat_id')
        meta = {
            'debug': False if application.id else True,
            'chat_id': chat_id,
            'application_id': str(application.id) if application.id else None,
        }
        file_url = FileSerializer(data={
            'file': file,
            'meta': meta,
            'source_id': meta['application_id'],
            'source_type': FileSourceType.APPLICATION.value
        }).upload()
        return file_url

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'status': self.status,
            'content': self.context.get('content'),
            'err_message': self.err_message,
            'answer': self.context.get('answer'),
            'enableException': self.node.properties.get('enableException'),
        }
