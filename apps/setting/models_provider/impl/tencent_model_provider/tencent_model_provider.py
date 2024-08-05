#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import (
    IModelProvider, ModelProvideInfo, ModelInfo, ModelTypeConst, ModelInfoManage
)
from setting.models_provider.impl.tencent_model_provider.credential.embedding import TencentEmbeddingCredential
from setting.models_provider.impl.tencent_model_provider.credential.llm import TencentLLMModelCredential
from setting.models_provider.impl.tencent_model_provider.model.embedding import TencentEmbeddingModel
from setting.models_provider.impl.tencent_model_provider.model.llm import TencentModel
from smartdoc.conf import PROJECT_DIR


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
        '当前混元模型中效果最优版本，万亿级参数规模 MOE-32K 长文模型。在各种 benchmark 上达到绝对领先的水平，复杂指令和推理，具备复杂数学能力，支持 functioncall，在多语言翻译、金融法律医疗等领域应用重点优化',
        ModelTypeConst.LLM,
        TencentLLMModelCredential,
        TencentModel
    ),
        _create_model_info(
            'hunyuan-standard',
            '采用更优的路由策略，同时缓解了负载均衡和专家趋同的问题。长文方面，大海捞针指标达到99.9%',
            ModelTypeConst.LLM,
            TencentLLMModelCredential,
            TencentModel),
        _create_model_info(
            'hunyuan-lite',
            '升级为 MOE 结构，上下文窗口为 256k ，在 NLP，代码，数学，行业等多项评测集上领先众多开源模型',
            ModelTypeConst.LLM,
            TencentLLMModelCredential,
            TencentModel),
        _create_model_info(
            'hunyuan-role',
            '混元最新版角色扮演模型，混元官方精调训练推出的角色扮演模型，基于混元模型结合角色扮演场景数据集进行增训，在角色扮演场景具有更好的基础效果',
            ModelTypeConst.LLM,
            TencentLLMModelCredential,
            TencentModel),
        _create_model_info(
            'hunyuan-functioncall ',
            '混元最新 MOE 架构 FunctionCall 模型，经过高质量的 FunctionCall 数据训练，上下文窗口达 32K，在多个维度的评测指标上处于领先。',
            ModelTypeConst.LLM,
            TencentLLMModelCredential,
            TencentModel),
        _create_model_info(
            'hunyuan-code',
            '混元最新代码生成模型，经过 200B 高质量代码数据增训基座模型，迭代半年高质量 SFT 数据训练，上下文长窗口长度增大到 8K，五大语言代码生成自动评测指标上位居前列；五大语言10项考量各方面综合代码任务人工高质量评测上，性能处于第一梯队',
            ModelTypeConst.LLM,
            TencentLLMModelCredential,
            TencentModel),
    ]

    tencent_embedding_model_info = _create_model_info(
        'hunyuan-embedding',
        '',
        ModelTypeConst.EMBEDDING,
        TencentEmbeddingCredential,
        TencentEmbeddingModel
    )

    model_info_embedding_list = [tencent_embedding_model_info]

    model_info_manage = ModelInfoManage.builder() \
        .append_model_info_list(model_info_list) \
        .append_default_model_info(model_info_list[0]) \
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
            name='腾讯混元',
            icon=icon_data
        )
