# coding=utf-8
"""
@project: MaxKB
@file： tti.py
@desc: 千帆文生图通用模型。api_base 即完整请求地址，直接使用。
"""

from typing import Dict

import requests

from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_tti import BaseTextToImage


class QianfanTextToImage(MaxKBBaseModel, BaseTextToImage):
    api_key: str
    api_base: str
    model_name: str
    params: dict = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get("api_key")
        self.api_base = kwargs.get("api_base")
        self.model_name = kwargs.get("model_name")
        self.params = kwargs.get("params", {}) or {}
        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {"params": {}}
        for key, value in model_kwargs.items():
            if key not in ["model_id", "use_local", "streaming"]:
                optional_params["params"][key] = value
        return QianfanTextToImage(
            model_name=model_name,
            api_key=model_credential.get("api_key"),
            api_base=model_credential.get("api_base"),
            **optional_params,
        )

    def check_auth(self):
        self.generate_image("a green grass field with a blue sky")

    def generate_image(self, prompt: str, negative_prompt: str = None):
        payload = {"model": self.model_name, "prompt": prompt}
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        payload.update(self.params)

        try:
            response = self._session.post(self.api_base, json=payload)
            response.raise_for_status()
            file_urls = []
            for item in response.json().get("data", []):
                if not isinstance(item, dict):
                    continue
                url = item.get("url") or item.get("b64_json")
                if not url:
                    continue
                if "://" not in url:
                    url = f"data:image/png;base64,{url}"
                file_urls.append(url)
            return file_urls
        except Exception as e:
            maxkb_logger.error(f"Exception: {e}", exc_info=True)
            raise e
