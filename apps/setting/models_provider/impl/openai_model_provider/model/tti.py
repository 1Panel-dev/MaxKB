from typing import Dict

import requests
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from openai import OpenAI

from common.config.tokenizer_manage_config import TokenizerManage
from common.util.common import bytes_to_uploaded_file
from dataset.serializers.file_serializers import FileSerializer
from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_tti import BaseTextToImage


def custom_get_token_ids(text: str):
    tokenizer = TokenizerManage.get_tokenizer()
    return tokenizer.encode(text)


class OpenAITextToImage(MaxKBBaseModel, BaseTextToImage):
    api_base: str
    api_key: str
    model: str
    params: dict

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.api_base = kwargs.get('api_base')
        self.model = kwargs.get('model')
        self.params = kwargs.get('params')

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {'params': {}}
        for key, value in model_kwargs.items():
            if key not in ['model_id', 'use_local', 'streaming']:
                optional_params['params'][key] = value
        return OpenAITextToImage(
            model=model_name,
            api_base=model_credential.get('api_base'),
            api_key=model_credential.get('api_key'),
            **optional_params,
        )

    def check_auth(self):
        chat = OpenAI(api_key=self.api_key, base_url=self.api_base)
        response_list = chat.models.with_raw_response.list()

        # self.generate_image('生成一个小猫图片')

    def generate_image(self, prompt: str, negative_prompt: str = None):

        chat = OpenAI(api_key=self.api_key, base_url=self.api_base)
        res = chat.images.generate(model=self.model, prompt=prompt, **self.params)

        file_urls = []
        for content in res.data:
            url = content.url
            print(url)
            file_name = 'generated_image.png'
            file = bytes_to_uploaded_file(requests.get(url).content, file_name)
            meta = {'debug': True}
            file_url = FileSerializer(data={'file': file, 'meta': meta}).upload()
            file_urls.append(file_url)

        return file_urls
