import base64
import mimetypes
from typing import Dict

from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_chat_open_ai import BaseChatOpenAI


class VolcanicEngineImage(MaxKBBaseModel, BaseChatOpenAI):

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return VolcanicEngineImage(
            model_name=model_name,
            openai_api_key=model_credential.get('api_key'),
            openai_api_base=model_credential.get('api_base'),
            # stream_options={"include_usage": True},
            streaming=True,
            stream_usage=True,
            extra_body=optional_params
        )

    @staticmethod
    def is_cache_model():
        return False

    def upload_file_and_get_url(self, file_stream, file_name):
        """上传文件并获取文件URL"""
        base64_video = base64.b64encode(file_stream).decode("utf-8")
        video_format = get_video_format(file_name)
        return f'data:{video_format};base64,{base64_video}'



def get_video_format(file_name):
    extension = file_name.split('.')[-1].lower()
    format_map = {
        'mp4': 'video/mp4',
        'avi': 'video/avi',
        'mov': 'video/mov',
        'wmv': 'video/x-ms-wmv'
    }
    return format_map.get(extension, 'video/mp4')
