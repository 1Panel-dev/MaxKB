# coding=utf-8
import io
import mimetypes

from django.core.files.uploadedfile import InMemoryUploadedFile

from application.flow.i_step_node import NodeResult, INode
from application.flow.step_node.image_understand_step_node.i_image_understand_node import IImageUnderstandNode
from application.flow.step_node.text_to_speech_step_node.i_text_to_speech_node import ITextToSpeechNode
from dataset.models import File
from dataset.serializers.file_serializers import FileSerializer
from setting.models_provider.tools import get_model_instance_by_model_user_id


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
        self.answer_text = details.get('answer')

    def execute(self, tts_model_id, chat_id,
                content, model_params_setting=None,
                **kwargs) -> NodeResult:
        self.context['content'] = content
        model = get_model_instance_by_model_user_id(tts_model_id, self.flow_params_serializer.data.get('user_id'),
                                                    **model_params_setting)
        audio_byte = model.text_to_speech(content)
        # 需要把这个音频文件存储到数据库中
        file_name = 'generated_audio.mp3'
        file = bytes_to_uploaded_file(audio_byte, file_name)
        application = self.workflow_manage.work_flow_post_handler.chat_info.application
        meta = {
            'debug': False if application.id else True,
            'chat_id': chat_id,
            'application_id': str(application.id) if application.id else None,
        }
        file_url = FileSerializer(data={'file': file, 'meta': meta}).upload()
        # 拼接一个audio标签的src属性
        audio_label = f'<audio src="{file_url}" controls style = "width: 300px; height: 43px"></audio>'
        file_id = file_url.split('/')[-1]
        audio_list = [{'file_id': file_id, 'file_name': file_name, 'url': file_url}]
        return NodeResult({'answer': audio_label, 'result': audio_list}, {})

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
        }
