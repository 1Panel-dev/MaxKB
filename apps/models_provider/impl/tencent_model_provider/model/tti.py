# coding=utf-8

import traceback
from typing import Dict, Optional

import requests
from django.utils.translation import gettext as _

from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_tti import BaseTextToImage


DEFAULT_WAND_IMAGE_BASE_URL = "https://tokenhub.tencentmaas.com/v1/wand/hunyuan-image/v3-generation"


class TencentTextToImageModel(MaxKBBaseModel, BaseTextToImage):
    api_key: str
    model: str
    params: dict
    base_url: Optional[str] = DEFAULT_WAND_IMAGE_BASE_URL

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get("api_key")
        self.model = kwargs.get("model")
        self.params = kwargs.get("params") or {}
        self.base_url = kwargs.get("base_url") or DEFAULT_WAND_IMAGE_BASE_URL

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(
        model_type: str, model_name: str, model_credential: Dict[str, object], **model_kwargs
    ) -> "TencentTextToImageModel":
        optional_params = {"params": {"size": "1024x1024"}}
        for key, value in model_kwargs.items():
            if key not in ["model_id", "use_local", "streaming"]:
                optional_params["params"][key] = value
        instance_kwargs = {
            "api_key": model_credential.get("api_key"),
            "model": model_name,
            "params": optional_params["params"],
            **optional_params,
        }
        base_url = model_credential.get("base_url")
        if base_url:
            instance_kwargs["base_url"] = base_url
        return TencentTextToImageModel(**instance_kwargs)

    def check_auth(self):
        self.generate_image(_("Hello"), None)

    def generate_image(self, prompt: str, negative_prompt: str = None):
        try:
            payload = {"model": self.model, "prompt": prompt}
            payload.update({key: value for key, value in self.params.items() if value not in (None, "")})
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=300)
            response.raise_for_status()
            result = response.json()
            data = result.get("data") or []
            file_urls = []
            for item in data:
                url = item.get("url")
                if url:
                    file_urls.append(url)
            if not file_urls:
                maxkb_logger.error(f"Tencent Text to Image API returned no urls: {result}")
                raise RuntimeError("Tencent Text to Image API returned no image urls")
            return file_urls
        except requests.RequestException as err:
            maxkb_logger.error(f"Tencent Text to Image API call failed: {err}: {traceback.format_exc()}")
            raise RuntimeError(f"Tencent Text to Image API call failed: {err}") from err
