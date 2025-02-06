#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import (
    IModelProvider, ModelProvideInfo, ModelInfo, ModelTypeConst, ModelInfoManage
)
from setting.models_provider.impl.aws_bedrock_model_provider.credential.embedding import BedrockEmbeddingCredential
from setting.models_provider.impl.aws_bedrock_model_provider.credential.llm import BedrockLLMModelCredential
from setting.models_provider.impl.aws_bedrock_model_provider.model.embedding import BedrockEmbeddingModel
from setting.models_provider.impl.aws_bedrock_model_provider.model.llm import BedrockModel
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


def _get_aws_bedrock_icon_path():
    return os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'aws_bedrock_model_provider',
                        'icon', 'bedrock_icon_svg')


def _initialize_model_info():
    model_info_list = [
        _create_model_info(
            'anthropic.claude-v2:1',
            _('An update to Claude 2 that doubles the context window and improves reliability, hallucination rates, and evidence-based accuracy in long documents and RAG contexts.'),
            ModelTypeConst.LLM,
            BedrockLLMModelCredential,
            BedrockModel
        ),
        _create_model_info(
            'anthropic.claude-v2',
            _('Anthropic is a powerful model that can handle a variety of tasks, from complex dialogue and creative content generation to detailed command obedience.'),
            ModelTypeConst.LLM,
            BedrockLLMModelCredential,
            BedrockModel
        ),
        _create_model_info(
            'anthropic.claude-3-haiku-20240307-v1:0',
            _("The Claude 3 Haiku is Anthropic's fastest and most compact model, with near-instant responsiveness. The model can answer simple queries and requests quickly. Customers will be able to build seamless AI experiences that mimic human interactions. Claude 3 Haiku can process images and return text output, and provides 200K context windows."),
            ModelTypeConst.LLM,
            BedrockLLMModelCredential,
            BedrockModel
        ),
        _create_model_info(
            'anthropic.claude-3-sonnet-20240229-v1:0',
            _("The Claude 3 Sonnet model from Anthropic strikes the ideal balance between intelligence and speed, especially when it comes to handling enterprise workloads. This model offers maximum utility while being priced lower than competing products, and it's been engineered to be a solid choice for deploying AI at scale."),
            ModelTypeConst.LLM,
            BedrockLLMModelCredential,
            BedrockModel
        ),
        _create_model_info(
            'anthropic.claude-3-5-sonnet-20240620-v1:0',
            _('The Claude 3.5 Sonnet raises the industry standard for intelligence, outperforming competing models and the Claude 3 Opus in extensive evaluations, with the speed and cost-effectiveness of our mid-range models.'),
            ModelTypeConst.LLM,
            BedrockLLMModelCredential,
            BedrockModel
        ),
        _create_model_info(
            'anthropic.claude-instant-v1',
            _('A faster, more affordable but still very powerful model that can handle a range of tasks including casual conversation, text analysis, summarization and document question answering.'),
            ModelTypeConst.LLM,
            BedrockLLMModelCredential,
            BedrockModel
        ),
        _create_model_info(
            'amazon.titan-text-premier-v1:0',
            _("Titan Text Premier is the most powerful and advanced model in the Titan Text series, designed to deliver exceptional performance for a variety of enterprise applications. With its cutting-edge features, it delivers greater accuracy and outstanding results, making it an excellent choice for organizations looking for a top-notch text processing solution."),
            ModelTypeConst.LLM,
            BedrockLLMModelCredential,
            BedrockModel
        ),
        _create_model_info(
            'amazon.titan-text-lite-v1',
            _('Amazon Titan Text Lite is a lightweight, efficient model ideal for fine-tuning English-language tasks, including summarization and copywriting, where customers require smaller, more cost-effective, and highly customizable models.'),
            ModelTypeConst.LLM,
            BedrockLLMModelCredential,
            BedrockModel),
        _create_model_info(
            'amazon.titan-text-express-v1',
            _('Amazon Titan Text Express has context lengths of up to 8,000 tokens, making it ideal for a variety of high-level general language tasks, such as open-ended text generation and conversational chat, as well as support in retrieval-augmented generation (RAG). At launch, the model is optimized for English, but other languages are supported.'),
            ModelTypeConst.LLM,
            BedrockLLMModelCredential,
            BedrockModel),
        _create_model_info(
            'mistral.mistral-7b-instruct-v0:2',
            _('7B dense converter for rapid deployment and easy customization. Small in size yet powerful in a variety of use cases. Supports English and code, as well as 32k context windows.'),
            ModelTypeConst.LLM,
            BedrockLLMModelCredential,
            BedrockModel),
        _create_model_info(
            'mistral.mistral-large-2402-v1:0',
            _('Advanced Mistral AI large-scale language model capable of handling any language task, including complex multilingual reasoning, text understanding, transformation, and code generation.'),
            ModelTypeConst.LLM,
            BedrockLLMModelCredential,
            BedrockModel),
        _create_model_info(
            'meta.llama3-70b-instruct-v1:0',
            _('Ideal for content creation, conversational AI, language understanding, R&D, and enterprise applications'),
            ModelTypeConst.LLM,
            BedrockLLMModelCredential,
            BedrockModel),
        _create_model_info(
            'meta.llama3-8b-instruct-v1:0',
            _('Ideal for limited computing power and resources, edge devices, and faster training times.'),
            ModelTypeConst.LLM,
            BedrockLLMModelCredential,
            BedrockModel),
    ]
    embedded_model_info_list = [
        _create_model_info(
            'amazon.titan-embed-text-v1',
            _('Titan Embed Text is the largest embedding model in the Amazon Titan Embed series and can handle various text embedding tasks, such as text classification, text similarity calculation, etc.'),
            ModelTypeConst.EMBEDDING,
            BedrockEmbeddingCredential,
            BedrockEmbeddingModel
        ),
    ]

    model_info_manage = ModelInfoManage.builder() \
        .append_model_info_list(model_info_list) \
        .append_default_model_info(model_info_list[0]) \
        .append_model_info_list(embedded_model_info_list) \
        .append_default_model_info(embedded_model_info_list[0]) \
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
