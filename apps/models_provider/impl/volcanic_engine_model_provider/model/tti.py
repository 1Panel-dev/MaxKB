# coding=utf-8

'''
requires Python 3.6 or later

pip install asyncio
pip install websockets

'''
from typing import Dict
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_tti import BaseTextToImage

from volcenginesdkarkruntime import Ark


class VolcanicEngineTextToImage(MaxKBBaseModel, BaseTextToImage):
    api_key: str
    model_version: str
    params: dict

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.model_version = kwargs.get('model_version')
        self.params = kwargs.get('params')

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {'params': {}}
        for key, value in model_kwargs.items():
            if key not in ['model_id', 'use_local', 'streaming']:
                optional_params['params'][key] = value
        return VolcanicEngineTextToImage(
            model_version=model_name,
            api_key=model_credential.get('api_key'),
            **optional_params
        )

    def check_auth(self):
        return True

    def generate_image(self, prompt: str, negative_prompt: str = None):
        client = Ark(
            # 此为默认路径，您可根据业务所在地域进行配置
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
            api_key=self.api_key,
        )
        file_urls = []
        imagesResponse = client.images.generate(
            model=self.model_version,
            prompt=prompt,
            **self.params
        )
        file_urls.append(imagesResponse.data[0].url)
        return file_urls
