# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： model_provider_constants.py
    @date：2023/11/2 14:55
    @desc:
"""
from enum import Enum

from setting.models_provider.impl.azure_model_provider.azure_model_provider import AzureModelProvider
from setting.models_provider.impl.deepseek_model_provider.deepseek_model_provider import DeepSeekModelProvider
from setting.models_provider.impl.gemini_model_provider.gemini_model_provider import GeminiModelProvider
from setting.models_provider.impl.kimi_model_provider.kimi_model_provider import KimiModelProvider
from setting.models_provider.impl.ollama_model_provider.ollama_model_provider import OllamaModelProvider
from setting.models_provider.impl.openai_model_provider.openai_model_provider import OpenAIModelProvider
from setting.models_provider.impl.qwen_model_provider.qwen_model_provider import QwenModelProvider
from setting.models_provider.impl.wenxin_model_provider.wenxin_model_provider import WenxinModelProvider
from setting.models_provider.impl.xf_model_provider.xf_model_provider import XunFeiModelProvider
from setting.models_provider.impl.zhipu_model_provider.zhipu_model_provider import ZhiPuModelProvider
from setting.models_provider.impl.local_model_provider.local_model_provider import LocalModelProvider


class ModelProvideConstants(Enum):
    model_azure_provider = AzureModelProvider()
    model_wenxin_provider = WenxinModelProvider()
    model_ollama_provider = OllamaModelProvider()
    model_openai_provider = OpenAIModelProvider()
    model_kimi_provider = KimiModelProvider()
    model_qwen_provider = QwenModelProvider()
    model_zhipu_provider = ZhiPuModelProvider()
    model_xf_provider = XunFeiModelProvider()
    model_deepseek_provider = DeepSeekModelProvider()
    model_gemini_provider = GeminiModelProvider()
    model_local_provider = LocalModelProvider()
