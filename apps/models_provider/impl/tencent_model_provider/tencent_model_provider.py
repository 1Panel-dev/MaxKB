#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
from common.utils.common import get_file_content
from models_provider.base_model_provider import (
    IModelProvider,
    ModelProvideInfo,
    ModelInfo,
    ModelTypeConst,
    ModelInfoManage,
)
from models_provider.impl.tencent_model_provider.credential.embedding import TencentEmbeddingCredential
from models_provider.impl.tencent_model_provider.credential.image import TencentVisionModelCredential
from models_provider.impl.tencent_model_provider.credential.llm import TencentLLMModelCredential
from models_provider.impl.tencent_model_provider.credential.stt import TencentSTTModelCredential
from models_provider.impl.tencent_model_provider.credential.tokenhub_stt import TencentTokenhubSTTModelCredential
from models_provider.impl.tencent_model_provider.credential.tti import TencentTTIModelCredential
from models_provider.impl.tencent_model_provider.credential.ttv import TencentTTVModelCredential
from models_provider.impl.tencent_model_provider.model.embedding import TencentEmbeddingModel
from models_provider.impl.tencent_model_provider.model.image import TencentVision
from models_provider.impl.tencent_model_provider.model.llm import TencentModel
from models_provider.impl.tencent_model_provider.model.stt import TencentSpeechToText, TencentWandSpeechToText
from models_provider.impl.tencent_model_provider.model.tti import TencentTextToImageModel
from models_provider.impl.tencent_model_provider.model.ttv import TencentVideoModel
from maxkb.conf import PROJECT_DIR
from django.utils.translation import gettext as _


def _create_model_info(model_name, description, model_type, credential_class, model_class):
    return ModelInfo(
        name=model_name,
        desc=description,
        model_type=model_type,
        model_credential=credential_class(),
        model_class=model_class,
    )


def _get_tencent_icon_path():
    return os.path.join(
        PROJECT_DIR, "apps", "models_provider", "impl", "tencent_model_provider", "icon", "tencent_icon_svg"
    )


def _initialize_model_info():
    model_info_list = [
        _create_model_info(
            "hy4-preview",
            _("The latest generation productivity model with upgraded Agent and complex task execution capabilities."),
            ModelTypeConst.LLM,
            TencentLLMModelCredential,
            TencentModel,
        ),
        _create_model_info(
            "hy3",
            _(
                "Tuned on real business scenarios, balancing effectiveness and cost-effectiveness, with reinforced Coding, long-text, reasoning and Agent capabilities."
            ),
            ModelTypeConst.LLM,
            TencentLLMModelCredential,
            TencentModel,
        ),
        _create_model_info(
            "hy3-preview",
            _(
                "Designed for Agent workloads, using a MoE architecture that supports interleaved thinking, structured output, Function Calling and Cache caching."
            ),
            ModelTypeConst.LLM,
            TencentLLMModelCredential,
            TencentModel,
        ),
        _create_model_info(
            "hy-mt2-pro",
            _("Tencent Hybrid multilingual translation model."),
            ModelTypeConst.LLM,
            TencentLLMModelCredential,
            TencentModel,
        ),
        _create_model_info(
            "hy-mt2-plus",
            _("Tencent Hybrid multilingual translation model."),
            ModelTypeConst.LLM,
            TencentLLMModelCredential,
            TencentModel,
        ),
        _create_model_info(
            "hy-mt2-lite",
            _("Tencent Hybrid multilingual translation model."),
            ModelTypeConst.LLM,
            TencentLLMModelCredential,
            TencentModel,
        ),
        _create_model_info(
            "hunyuan-role-latest",
            _("Hunyuan's latest role-playing model based on the Hunyuan model with role-playing scene fine-tuning."),
            ModelTypeConst.LLM,
            TencentLLMModelCredential,
            TencentModel,
        ),
        _create_model_info(
            "hy-role",
            _("Hunyuan's role-playing model with better basic effects in role-playing scenarios."),
            ModelTypeConst.LLM,
            TencentLLMModelCredential,
            TencentModel,
        ),
        _create_model_info(
            "asr-sentence",
            _(
                "This interface is used to recognize short audio files within 60 seconds. Supports Mandarin Chinese, English, Cantonese, Japanese, Vietnamese, Malay, Indonesian, Filipino, Thai, Portuguese, Turkish, Arabic, Hindi, French, German, and 23 Chinese dialects."
            ),
            ModelTypeConst.STT,
            TencentSTTModelCredential,
            TencentSpeechToText,
        ),
        _create_model_info(
            "wand-asr-v1", _(""), ModelTypeConst.STT, TencentTokenhubSTTModelCredential, TencentWandSpeechToText
        ),
        _create_model_info(
            "hy-asr-3.0-preview", _(""), ModelTypeConst.STT, TencentTokenhubSTTModelCredential, TencentWandSpeechToText
        ),
    ]

    model_info_embedding_list = [
        _create_model_info(
            "kinfra-text-embedding-0.6b",
            _("Tencent TokenHub text embedding model, 1024 dimensions."),
            ModelTypeConst.EMBEDDING,
            TencentEmbeddingCredential,
            TencentEmbeddingModel,
        ),
        _create_model_info(
            "kinfra-text-embedding-4b",
            _("Tencent TokenHub text embedding model, 2560 dimensions."),
            ModelTypeConst.EMBEDDING,
            TencentEmbeddingCredential,
            TencentEmbeddingModel,
        ),
        _create_model_info(
            "kinfra-vl-embedding-2b",
            _("Tencent TokenHub multimodal embedding model, 2048 dimensions."),
            ModelTypeConst.EMBEDDING,
            TencentEmbeddingCredential,
            TencentEmbeddingModel,
        ),
        _create_model_info(
            "kinfra-vl-embedding-8b",
            _("Tencent TokenHub multimodal embedding model, 4096 dimensions."),
            ModelTypeConst.EMBEDDING,
            TencentEmbeddingCredential,
            TencentEmbeddingModel,
        ),
    ]
    tencent_embedding_model_info = model_info_embedding_list[0]

    model_info_vision_list = [
        _create_model_info(
            "hunyuan-vision",
            _("Mixed element visual model"),
            ModelTypeConst.IMAGE,
            TencentVisionModelCredential,
            TencentVision,
        )
    ]

    model_info_tti_list = [
        _create_model_info(
            "hy-image-v3",
            _("Hunyuan Hy-Image 3.0 text-to-image model."),
            ModelTypeConst.TTI,
            TencentTTIModelCredential,
            TencentTextToImageModel,
        )
    ]

    model_info_ttv_list = [
        _create_model_info(
            "hy-video-1.5",
            _("Hunyuan HY-Video 1.5 text-to-video model."),
            ModelTypeConst.TTV,
            TencentTTVModelCredential,
            TencentVideoModel,
        )
    ]

    model_info_itv_list = [
        _create_model_info(
            "hy-video-1.5",
            _("Hunyuan HY-Video 1.5 image-to-video model."),
            ModelTypeConst.ITV,
            TencentTTVModelCredential,
            TencentVideoModel,
        ),
        _create_model_info(
            "yt-video-2.0",
            _("Tencent YT-Video 2.0 image-to-video model."),
            ModelTypeConst.ITV,
            TencentTTVModelCredential,
            TencentVideoModel,
        ),
    ]

    model_info_manage = (
        ModelInfoManage.builder()
        .append_model_info_list(model_info_list)
        .append_model_info_list(model_info_embedding_list)
        .append_model_info_list(model_info_vision_list)
        .append_default_model_info(model_info_vision_list[0])
        .append_model_info_list(model_info_tti_list)
        .append_default_model_info(model_info_tti_list[0])
        .append_model_info_list(model_info_ttv_list)
        .append_default_model_info(model_info_ttv_list[0])
        .append_model_info_list(model_info_itv_list)
        .append_default_model_info(model_info_itv_list[0])
        .append_default_model_info(model_info_list[0])
        .append_default_model_info(tencent_embedding_model_info)
        .build()
    )

    return model_info_manage


class TencentModelProvider(IModelProvider):
    def __init__(self):
        self._model_info_manage = _initialize_model_info()

    def get_model_info_manage(self):
        return self._model_info_manage

    def get_model(self, model_type, model_name, model_credential, **model_kwargs):
        # STT 模型：模型名不以 asr- 开头的一律走 Tencent Tokenhub WAND 识别
        if model_type == ModelTypeConst.STT.name and not model_name.startswith("asr-"):
            return TencentWandSpeechToText.new_instance(model_type, model_name, model_credential, **model_kwargs)
        return super().get_model(model_type, model_name, model_credential, **model_kwargs)

    def get_model_provide_info(self):
        icon_path = _get_tencent_icon_path()
        icon_data = get_file_content(icon_path)
        return ModelProvideInfo(provider="model_tencent_provider", name=_("Tencent Cloud"), icon=icon_data)
