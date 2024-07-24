#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import (
    IModelProvider, ModelProvideInfo, ModelInfo, ModelTypeConst, ModelInfoManage
)
from setting.models_provider.impl.aws_bedrock_model_provider.credential.llm import BedrockLLMModelCredential
from setting.models_provider.impl.aws_bedrock_model_provider.model.llm import BedrockModel
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


def _get_aws_bedrock_icon_path():
    return os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'aws_bedrock_model_provider',
                        'icon', 'bedrock_icon_svg')


def _initialize_model_info():
    model_info_list = [_create_model_info(
        'amazon.titan-text-premier-v1:0',
        'Titan Text Premier 是 Titan Text 系列中功能强大且先进的型号，旨在为各种企业应用程序提供卓越的性能。凭借其尖端功能，它提供了更高的准确性和出色的结果，使其成为寻求一流文本处理解决方案的组织的绝佳选择。',
        ModelTypeConst.LLM,
        BedrockLLMModelCredential,
        BedrockModel
    ),
        _create_model_info(
            'amazon.titan-text-lite-v1',
            'Amazon Titan Text Lite 是一种轻量级的高效模型，非常适合英语任务的微调，包括摘要和文案写作等，在这种场景下，客户需要更小、更经济高效且高度可定制的模型',
            ModelTypeConst.LLM,
            BedrockLLMModelCredential,
            BedrockModel),
        _create_model_info(
            'amazon.titan-text-express-v1',
            'Amazon Titan Text Express 的上下文长度长达 8000 个令牌，因而非常适合各种高级常规语言任务，例如开放式文本生成和对话式聊天，以及检索增强生成（RAG）中的支持。在发布时，该模型针对英语进行了优化，但也支持其他语言。',
            ModelTypeConst.LLM,
            BedrockLLMModelCredential,
            BedrockModel),
        _create_model_info(
            'amazon.titan-embed-text-v2:0',
            'Amazon Titan Text Embeddings V2 是一种轻量级、高效的模型，非常适合在不同维度上执行高精度检索任务。该模型支持灵活的嵌入大小（1024、512 和 256），并优先考虑在较小维度上保持准确性，从而可以在不影响准确性的情况下降低存储成本。Titan Text Embeddings V2 适用于各种任务，包括文档检索、推荐系统、搜索引擎和对话式系统。',
            ModelTypeConst.LLM,
            BedrockLLMModelCredential,
            BedrockModel),
        _create_model_info(
            'mistral.mistral-7b-instruct-v0:2',
            '7B 密集型转换器，可快速部署，易于定制。体积虽小，但功能强大，适用于各种用例。支持英语和代码，以及 32k 的上下文窗口。',
            ModelTypeConst.EMBEDDING,
            BedrockLLMModelCredential,
            BedrockModel),
        _create_model_info(
            'mistral.mistral-large-2402-v1:0',
            '先进的 Mistral AI 大型语言模型，能够处理任何语言任务，包括复杂的多语言推理、文本理解、转换和代码生成。',
            ModelTypeConst.LLM,
            BedrockLLMModelCredential,
            BedrockModel),
        _create_model_info(
            'meta.llama3-70b-instruct-v1:0',
            '非常适合内容创作、会话式人工智能、语言理解、研发和企业应用',
            ModelTypeConst.LLM,
            BedrockLLMModelCredential,
            BedrockModel),
        _create_model_info(
            'meta.llama3-8b-instruct-v1:0',
            '非常适合有限的计算能力和资源、边缘设备和更快的训练时间。',
            ModelTypeConst.LLM,
            BedrockLLMModelCredential,
            BedrockModel),
    ]

    model_info_manage = ModelInfoManage.builder() \
        .append_model_info_list(model_info_list) \
        .append_default_model_info(model_info_list[0]) \
        .build()

    return model_info_manage


class BedrockModelProvider(IModelProvider):
    def __init__(self):
        self._model_info_manage = _initialize_model_info()

    def get_model_info_manage(self):
        return self._model_info_manage

    def get_model_provide_info(self):
        icon_path = _get_aws_bedrock_icon_path()
        icon_data = get_file_content(icon_path)
        return ModelProvideInfo(
            provider='model_aws_bedrock_provider',
            name='Amazon Bedrock',
            icon=icon_data
        )
