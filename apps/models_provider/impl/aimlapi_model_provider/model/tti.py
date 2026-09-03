# coding=utf-8
"""
    @project: MaxKB
    @Author：aimlapi.com
    @file： tti.py
    @date：2026/09/03 10:00
    @desc:
"""
from typing import Dict

from openai import NotFoundError, OpenAI

from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.aimlapi_model_provider.const import API_BASE, get_default_headers
from models_provider.impl.base_tti import BaseTextToImage

# 表单中选择“自动”表示该参数不下发，由模型自己决定
AUTO_VALUE = 'auto'
# 仅用于校验 API Key 的占位模型名，不会真正生成图片
CREDENTIAL_CHECK_MODEL = 'maxkb-credential-check'


class AIMLAPITextToImage(MaxKBBaseModel, BaseTextToImage):
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
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        # 未设置的参数一律省略，不下发 None。AI/ML API 上不同图片模型接受的取值不同，
        # 例如 openai/gpt-image-1 的 quality 只接受 low/medium/high，
        # 下发 standard 或 null 都会返回 400。
        params = {}
        for key, value in model_kwargs.items():
            if key in ['model_id', 'use_local', 'streaming']:
                continue
            if value is None or value == AUTO_VALUE or value == '':
                continue
            params[key] = value
        params.setdefault('n', 1)
        return AIMLAPITextToImage(
            model=model_name,
            api_base=model_credential.get('api_base') or API_BASE,
            api_key=model_credential.get('api_key'),
            params=params,
        )

    def get_client(self):
        return OpenAI(api_key=self.api_key, base_url=self.api_base,
                      default_headers=get_default_headers(self.api_base))

    def check_auth(self):
        # AI/ML API 的 GET /v1/models 是公开接口，任意 Key 都返回 200，因此不能用它校验 Key。
        # 这里向图片接口发送一个模型名不存在的请求：Key 无效返回 401，Key 有效返回 404，
        # 既能真正校验 Key，又不会产生任何生成费用。
        try:
            self.get_client().images.generate(model=CREDENTIAL_CHECK_MODEL, prompt='ping', n=1)
        except NotFoundError:
            return True
        return True

    def generate_image(self, prompt: str, negative_prompt: str = None):
        res = self.get_client().images.generate(model=self.model, prompt=prompt, **self.params)
        file_urls = []
        try:
            for content in res.data:
                if content.url:
                    file_urls.append(content.url)
                elif content.b64_json:
                    file_urls.append(content.b64_json)
            return file_urls
        except Exception as e:
            raise RuntimeError(f"AIMLAPITextToImage generate_image error: {e}") from e
