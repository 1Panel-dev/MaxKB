#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import (
    IModelProvider, ModelProvideInfo, ModelInfo, ModelTypeConst, ModelInfoManage
)
from setting.models_provider.impl.tencent_model_provider.credential.embedding import TencentEmbeddingCredential
from setting.models_provider.impl.tencent_model_provider.credential.image import TencentVisionModelCredential
from setting.models_provider.impl.tencent_model_provider.credential.llm import TencentLLMModelCredential
from setting.models_provider.impl.tencent_model_provider.credential.tti import TencentTTIModelCredential
from setting.models_provider.impl.tencent_model_provider.model.embedding import TencentEmbeddingModel
from setting.models_provider.impl.tencent_model_provider.model.image import TencentVision
from setting.models_provider.impl.tencent_model_provider.model.llm import TencentModel
from setting.models_provider.impl.tencent_model_provider.model.tti import TencentTextToImageModel
from smartdoc.conf import PROJECT_DIR
from django.utils.translation import gettext as _

def _create_model_info(model_name, description, model_type, credential_class, model_class):
    return ModelInfo(
        name=model_name,
        desc=description,
        model_type=model_type,
        model_credential=credential_class(),
        model_class=model_class
    )


def _get_tencent_icon_path():
    return os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'tencent_model_provider',
                        'icon', 'tencent_icon_svg')


def _initialize_model_info():
    model_info_list = [_create_model_info(
        'hunyuan-pro',
        _('The most effective version of the current hybrid model, the trillion-level parameter scale MOE-32K long article model. Reaching the absolute leading level on various benchmarks, with complex instructions and reasoning, complex mathematical capabilities, support for function call, and application focus optimization in fields such as multi-language translation, finance, law, and medical care'),
        ModelTypeConst.LLM,
        TencentLLMModelCredential,
        TencentModel
    ),
        _create_model_info(
            'hunyuan-standard',
            _('A better routing strategy is adopted to simultaneously alleviate the problems of load balancing and expert convergence. For long articles, the needle-in-a-haystack index reaches 99.9%'),
            ModelTypeConst.LLM,
            TencentLLMModelCredential,
            TencentModel),
        _create_model_info(
            'hunyuan-lite',
            _('Upgraded to MOE structure, the context window is 256k, leading many open source models in multiple evaluation sets such as NLP, code, mathematics, industry, etc.'),
            ModelTypeConst.LLM,
            TencentLLMModelCredential,
            TencentModel),
        _create_model_info(
            'hunyuan-role',
            _("Hunyuan's latest version of the role-playing model, a role-playing model launched by Hunyuan's official fine-tuning training, is based on the Hunyuan model combined with the role-playing scene data set for additional training, and has better basic effects in role-playing scenes."),
            ModelTypeConst.LLM,
            TencentLLMModelCredential,
            TencentModel),
        _create_model_info(
            'hunyuan-functioncall',
            _("Hunyuan's latest MOE architecture FunctionCall model has been trained with high-quality FunctionCall data and has a context window of 32K, leading in multiple dimensions of evaluation indicators."),
            ModelTypeConst.LLM,
            TencentLLMModelCredential,
            TencentModel),
        _create_model_info(
            'hunyuan-code',
            _("Hunyuan's latest code generation model, after training the base model with 200B high-quality code data, and iterating on high-quality SFT data for half a year, the context long window length has been increased to 8K, and it ranks among the top in the automatic evaluation indicators of code generation in the five major languages; the five major languages In the manual high-quality evaluation of 10 comprehensive code tasks that consider all aspects, the performance is in the first echelon."),
            ModelTypeConst.LLM,
            TencentLLMModelCredential,
            TencentModel),
    ]

    tencent_embedding_model_info = _create_model_info(
        'hunyuan-embedding',
        _("Tencent's Hunyuan Embedding interface can convert text into high-quality vector data. The vector dimension is 1024 dimensions."),
        ModelTypeConst.EMBEDDING,
        TencentEmbeddingCredential,
        TencentEmbeddingModel
    )

    model_info_embedding_list = [tencent_embedding_model_info]

    model_info_vision_list = [_create_model_info(
        'hunyuan-vision',
        _('Mixed element visual model'),
        ModelTypeConst.IMAGE,
        TencentVisionModelCredential,
        TencentVision)]

    model_info_tti_list = [_create_model_info(
        'hunyuan-dit',
        _('Hunyuan graph model'),
        ModelTypeConst.TTI,
        TencentTTIModelCredential,
        TencentTextToImageModel)]

    model_info_manage = ModelInfoManage.builder() \
        .append_model_info_list(model_info_list) \
        .append_model_info_list(model_info_embedding_list) \
        .append_model_info_list(model_info_vision_list) \
        .append_default_model_info(model_info_vision_list[0]) \
        .append_model_info_list(model_info_tti_list) \
        .append_default_model_info(model_info_tti_list[0]) \
        .append_default_model_info(model_info_list[0]) \
        .append_default_model_info(tencent_embedding_model_info) \
        .build()

    return model_info_manage


class TencentModelProvider(IModelProvider):
    def __init__(self):
        self._model_info_manage = _initialize_model_info()

    def get_model_info_manage(self):
        return self._model_info_manage

    def get_model_provide_info(self):
        icon_path = _get_tencent_icon_path()
        icon_data = get_file_content(icon_path)
        return ModelProvideInfo(
            provider='model_tencent_provider',
            name=_('Tencent Hunyuan'),
            icon=icon_data
        )
