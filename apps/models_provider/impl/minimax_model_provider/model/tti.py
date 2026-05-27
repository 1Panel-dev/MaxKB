# coding=utf-8
from http import HTTPStatus
from typing import Dict

import requests
from dashscope import ImageSynthesis, MultiModalConversation
from dashscope.aigc.image_generation import ImageGeneration

from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_tti import BaseTextToImage


class MiniMaxTextToImageModel(MaxKBBaseModel, BaseTextToImage):
    api_key: str
    model_name: str
    params: dict
    api_base: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.api_base = kwargs.get('api_base')
        self.model_name = kwargs.get('model_name')
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
        api_base = model_credential.get('api_base', "https://api.minimaxi.com/v1")

        minimax_model = MiniMaxTextToImageModel(
            model_name=model_name,
            api_key=model_credential.get('api_key'),
            api_base=api_base,
            **optional_params,
        )
        return minimax_model

    def check_auth(self):
        return True

    def generate_image(self, prompt: str, negative_prompt: str = None):
        headers = {"Authorization": f"Bearer {self.api_key}"}

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            **self.params,
        }
        try:
            response = requests.post(f'{self.api_base}/image_generation', headers=headers, json=payload)
            response.raise_for_status()
            file_urls = []
            data = response.json().get("data", {})
            if "image_urls" in data:
                file_urls = data["image_urls"]
            elif "image_base64" in data:
                for img in data["image_base64"]:
                    file_urls.append(f"data:image/png;base64,{img}")
            return file_urls
        except Exception as e:
            maxkb_logger.error(f'Exception: {e}', exc_info=True)
            raise e
