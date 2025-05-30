from typing import Dict

from openai import OpenAI

from common.config.tokenizer_manage_config import TokenizerManage
from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_tti import BaseTextToImage


def custom_get_token_ids(text: str):
    tokenizer = TokenizerManage.get_tokenizer()
    return tokenizer.encode(text)


class RegoloTextToImage(MaxKBBaseModel, BaseTextToImage):
    api_base: str
    api_key: str
    model: str
    params: dict

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.api_base = "https://api.regolo.ai/v1"
        self.model = kwargs.get('model')
        self.params = kwargs.get('params')

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {'params': {'size': '1024x1024', 'quality': 'standard', 'n': 1}}
        for key, value in model_kwargs.items():
            if key not in ['model_id', 'use_local', 'streaming']:
                optional_params['params'][key] = value
        return RegoloTextToImage(
            model=model_name,
            api_base="https://api.regolo.ai/v1",
            api_key=model_credential.get('api_key'),
            **optional_params,
        )

    def is_cache_model(self):
        return False

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
            file_urls.append(url)

        return file_urls
