#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：MaxKB
@File    ：gemini_model_provider.py
@Author  ：Brian Yang
@Date    ：5/13/24 7:47 AM
"""

import os

import requests

from common.utils.common import get_file_content
from models_provider.base_model_provider import (
    _model_type_name,
    IModelProvider,
    ModelProvideInfo,
    ModelInfo,
    ModelTypeConst,
    ModelInfoManage,
)
from models_provider.impl.gemini_model_provider.credential.embedding import GeminiEmbeddingCredential
from models_provider.impl.gemini_model_provider.credential.image import GeminiImageModelCredential
from models_provider.impl.gemini_model_provider.credential.itv import ImageToVideoModelCredential
from models_provider.impl.gemini_model_provider.credential.llm import GeminiLLMModelCredential
from models_provider.impl.gemini_model_provider.credential.stt import GeminiSTTModelCredential
from models_provider.impl.gemini_model_provider.credential.tti import GeminiTextToImageModelCredential
from models_provider.impl.gemini_model_provider.credential.ttv import TextToVideoModelCredential
from models_provider.impl.gemini_model_provider.model.embedding import GeminiEmbeddingModel
from models_provider.impl.gemini_model_provider.model.image import GeminiImage
from models_provider.impl.gemini_model_provider.model.llm import GeminiChatModel
from models_provider.impl.gemini_model_provider.model.stt import GeminiSpeechToText
from maxkb.conf import PROJECT_DIR
from django.utils.translation import gettext as _

from models_provider.impl.gemini_model_provider.model.tti import GeminiTextToImage
from models_provider.impl.gemini_model_provider.model.ttv import GenerationVideoModel

gemini_llm_model_credential = GeminiLLMModelCredential()
gemini_image_model_credential = GeminiImageModelCredential()
gemini_stt_model_credential = GeminiSTTModelCredential()
gemini_embedding_model_credential = GeminiEmbeddingCredential()
gemini_tti_model_credential = GeminiTextToImageModelCredential()
gemini_itv_model_credential = ImageToVideoModelCredential()
gemini_ttv_model_credential = TextToVideoModelCredential()

model_info_list = [
    ModelInfo(
        "gemini-1.0-pro",
        _("Latest Gemini 1.0 Pro model, updated with Google update"),
        ModelTypeConst.LLM,
        gemini_llm_model_credential,
        GeminiChatModel,
    ),
    ModelInfo(
        "gemini-1.0-pro-vision",
        _("Latest Gemini 1.0 Pro Vision model, updated with Google update"),
        ModelTypeConst.LLM,
        gemini_llm_model_credential,
        GeminiChatModel,
    ),
]

model_image_info_list = [
    ModelInfo(
        "gemini-1.5-flash",
        _("Latest Gemini 1.5 Flash model, updated with Google updates"),
        ModelTypeConst.IMAGE,
        gemini_image_model_credential,
        GeminiImage,
    ),
    ModelInfo(
        "gemini-1.5-pro",
        _("Latest Gemini 1.5 Flash model, updated with Google updates"),
        ModelTypeConst.IMAGE,
        gemini_image_model_credential,
        GeminiImage,
    ),
]

model_stt_info_list = [
    ModelInfo(
        "gemini-1.5-flash",
        _("Latest Gemini 1.5 Flash model, updated with Google updates"),
        ModelTypeConst.STT,
        gemini_stt_model_credential,
        GeminiSpeechToText,
    ),
    ModelInfo(
        "gemini-1.5-pro",
        _("Latest Gemini 1.5 Flash model, updated with Google updates"),
        ModelTypeConst.STT,
        gemini_stt_model_credential,
        GeminiSpeechToText,
    ),
]

model_embedding_info_list = [
    ModelInfo(
        "models/embedding-001", "", ModelTypeConst.EMBEDDING, gemini_embedding_model_credential, GeminiEmbeddingModel
    ),
    ModelInfo(
        "models/text-embedding-004",
        "",
        ModelTypeConst.EMBEDDING,
        gemini_embedding_model_credential,
        GeminiEmbeddingModel,
    ),
]

model_tti_info_list = [
    ModelInfo("gemini-3.1-flash-image-preview", "", ModelTypeConst.TTI, gemini_tti_model_credential, GeminiTextToImage)
]

ttv_model_info_list = [
    ModelInfo("veo-3.1-generate-preview", "", ModelTypeConst.TTV, gemini_ttv_model_credential, GenerationVideoModel)
]

itv_model_info_list = [
    ModelInfo("veo-3.1-generate-preview", "", ModelTypeConst.ITV, gemini_itv_model_credential, GenerationVideoModel)
]


model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(model_info_list)
    .append_model_info_list(model_image_info_list)
    .append_model_info_list(model_stt_info_list)
    .append_model_info_list(model_embedding_info_list)
    .append_model_info_list(model_tti_info_list)
    .append_default_model_info(model_info_list[0])
    .append_default_model_info(model_image_info_list[0])
    .append_default_model_info(model_stt_info_list[0])
    .append_default_model_info(model_embedding_info_list[0])
    .append_default_model_info(model_tti_info_list[0])
    .append_model_info_list(ttv_model_info_list)
    .append_default_model_info(ttv_model_info_list[0])
    .append_model_info_list(itv_model_info_list)
    .append_default_model_info(itv_model_info_list[0])
    .build()
)


class GeminiModelProvider(IModelProvider):
    def get_dynamic_model_info_list(self, api_key, api_base, credential=None):
        """Gemini 原生 /v1beta/models 返回 supportedGenerationMethods，可精确判型；失败时回退框架默认。"""
        base = (api_base or self.get_dynamic_default_api_base() or "").strip().rstrip("/")
        if not base:
            return None
        try:
            response = requests.get(
                base + "/v1beta/models",
                headers={"x-goog-api-key": api_key},
                timeout=15,
            )
            if response.status_code != 200:
                return None
            items = response.json().get("models") or []
            if not items:
                return None
            builtin_manage = self.get_model_info_manage()
            builtin_by_name = {}
            impl_map = {}
            for info in builtin_manage.model_list:
                builtin_by_name.setdefault(info.name, info)
                impl_map.setdefault(info.model_type, (info.model_credential, info.model_class))
            info_list = []
            for item in items:
                name = str(item.get("name") or "").removeprefix("models/")
                if not name:
                    continue
                builtin = builtin_by_name.get(name)
                if builtin is not None:
                    info_list.append(
                        ModelInfo(name, builtin.desc, builtin.model_type, builtin.model_credential, builtin.model_class)
                    )
                    continue
                methods = {str(m).lower() for m in (item.get("supportedGenerationMethods") or [])}
                if not methods:
                    # 官方接口未给出可用能力时跳过，避免误判成 LLM。
                    continue
                if "embedcontent" in methods:
                    model_type = ModelTypeConst.EMBEDDING
                elif any(m in methods for m in ("generatecontent", "counttokens", "generateanswer")):
                    model_type = ModelTypeConst.LLM
                elif "generatevideos" in methods:
                    model_type = ModelTypeConst.TTV
                else:
                    model_type = self.classify_dynamic_model(name)
                impl = impl_map.get(_model_type_name(model_type))
                if impl is None:
                    continue
                info_list.append(ModelInfo(name, _(""), model_type, impl[0], impl[1]))
            return info_list or None
        except Exception:
            return None

    def fetch_dynamic_model_ids(self, api_key, api_base, credential=None):
        """Gemini OpenAI 兼容端点：GET {base}/v1beta/openai/models，Bearer 鉴权。"""
        api_base = (api_base or self.get_dynamic_default_api_base() or "").strip().rstrip("/")
        if not api_base:
            return []
        url = api_base + "/v1beta/openai/models"
        try:
            response = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=15)
            if response.status_code != 200:
                return []
            data = response.json().get("data") or []
            return [item.get("id") for item in data if item.get("id")]
        except Exception:
            return []

    def get_dynamic_default_api_base(self):
        """Gemini 凭证表单的地址字段是 base_url，默认值推断需特殊处理。"""
        cached = getattr(self, "_dynamic_default_api_base", None)
        if cached is not None:
            return cached
        default = None
        for info in self.get_model_info_manage().model_list:
            try:
                default_data = info.model_credential.get_default_form_data()
            except Exception:
                continue
            value = str(default_data.get("base_url") or default_data.get("api_base") or "").strip()
            if value:
                default = value
                break
        self._dynamic_default_api_base = default
        return default

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(
            provider="model_gemini_provider",
            name="Gemini",
            icon=get_file_content(
                os.path.join(
                    PROJECT_DIR, "apps", "models_provider", "impl", "gemini_model_provider", "icon", "gemini_icon_svg"
                )
            ),
        )
