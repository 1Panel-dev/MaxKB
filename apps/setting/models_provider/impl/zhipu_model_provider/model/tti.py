from typing import Dict

import requests
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.messages import HumanMessage
from zhipuai import ZhipuAI

from common.config.tokenizer_manage_config import TokenizerManage
from common.util.common import bytes_to_uploaded_file
from dataset.serializers.file_serializers import FileSerializer
from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_tti import BaseTextToImage


def custom_get_token_ids(text: str):
    tokenizer = TokenizerManage.get_tokenizer()
    return tokenizer.encode(text)


class ZhiPuTextToImage(MaxKBBaseModel, BaseTextToImage):
    api_key: str
    model: str
    params: dict

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.model = kwargs.get('model')
        self.params = kwargs.get('params')

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {'params': {}}
        for key, value in model_kwargs.items():
            if key not in ['model_id', 'use_local', 'streaming']:
                optional_params['params'][key] = value
        return ZhiPuTextToImage(
            model=model_name,
            api_key=model_credential.get('api_key'),
            **optional_params,
        )

    def check_auth(self):
        chat = ChatZhipuAI(
            zhipuai_api_key=self.api_key,
            model_name=self.model,
        )
        chat.invoke([HumanMessage([{"type": "text", "text": "你好"}])])

        # self.generate_image('生成一个小猫图片')

    def generate_image(self, prompt: str, negative_prompt: str = None):
        # chat = ChatZhipuAI(
        #     zhipuai_api_key=self.api_key,
        #     model_name=self.model,
        # )
        chat = ZhipuAI(api_key=self.api_key)
        response = chat.images.generations(
            model=self.model,  # 填写需要调用的模型编码
            prompt=prompt,  # 填写需要生成图片的文本
            **self.params # 填写额外参数
        )
        file_urls = []
        for content in response.data:
            url = content['url']
            print(url)
            file_name = url.split('/')[-1]
            file = bytes_to_uploaded_file(requests.get(url).content, file_name)
            meta = {'debug': True}
            file_url = FileSerializer(data={'file': file, 'meta': meta}).upload()
            file_urls.append(file_url)

        return file_urls
