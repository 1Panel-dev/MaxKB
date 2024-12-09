# coding=utf-8
from http import HTTPStatus
from pathlib import PurePosixPath
from typing import Dict
from urllib.parse import unquote, urlparse

import requests
from dashscope import ImageSynthesis
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import HumanMessage

from common.util.common import bytes_to_uploaded_file
from dataset.serializers.file_serializers import FileSerializer
from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_tti import BaseTextToImage


class QwenTextToImageModel(MaxKBBaseModel, BaseTextToImage):
    api_key: str
    model_name: str
    params: dict

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.model_name = kwargs.get('model_name')
        self.params = kwargs.get('params')

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {'params': {}}
        for key, value in model_kwargs.items():
            if key not in ['model_id', 'use_local', 'streaming']:
                optional_params['params'][key] = value
        chat_tong_yi = QwenTextToImageModel(
            model_name=model_name,
            api_key=model_credential.get('api_key'),
            **optional_params,
        )
        return chat_tong_yi

    def check_auth(self):
        chat = ChatTongyi(api_key=self.api_key, model_name='qwen-max')
        chat.invoke([HumanMessage([{"type": "text", "text": "你好"}])])

    def generate_image(self, prompt: str, negative_prompt: str = None):
        # api_base='https://dashscope.aliyuncs.com/compatible-mode/v1',
        rsp = ImageSynthesis.call(api_key=self.api_key,
                                  model=self.model_name,
                                  prompt=prompt,
                                  negative_prompt=negative_prompt,
                                  **self.params)
        file_urls = []
        if rsp.status_code == HTTPStatus.OK:
            for result in rsp.output.results:
                file_name = PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]
                file = bytes_to_uploaded_file(requests.get(result.url).content, file_name)
                meta = {'debug': True}
                file_url = FileSerializer(data={'file': file, 'meta': meta}).upload()
                file_urls.append(file_url)
        else:
            print('sync_call Failed, status_code: %s, code: %s, message: %s' %
                  (rsp.status_code, rsp.code, rsp.message))
        return file_urls
