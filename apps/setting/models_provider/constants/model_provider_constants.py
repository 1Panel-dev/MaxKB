# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： model_provider_constants.py
    @date：2023/11/2 14:55
    @desc:
"""
from enum import Enum

from setting.models_provider.impl.aliyun_bai_lian_model_provider.aliyun_bai_lian_model_provider import \
    AliyunBaiLianModelProvider
from setting.models_provider.impl.anthropic_model_provider.anthropic_model_provider import AnthropicModelProvider
from setting.models_provider.impl.aws_bedrock_model_provider.aws_bedrock_model_provider import BedrockModelProvider
from setting.models_provider.impl.azure_model_provider.azure_model_provider import AzureModelProvider
from setting.models_provider.impl.deepseek_model_provider.deepseek_model_provider import DeepSeekModelProvider
from setting.models_provider.impl.gemini_model_provider.gemini_model_provider import GeminiModelProvider
from setting.models_provider.impl.kimi_model_provider.kimi_model_provider import KimiModelProvider
from setting.models_provider.impl.ollama_model_provider.ollama_model_provider import OllamaModelProvider
from setting.models_provider.impl.openai_model_provider.openai_model_provider import OpenAIModelProvider
from setting.models_provider.impl.qwen_model_provider.qwen_model_provider import QwenModelProvider
from setting.models_provider.impl.regolo_model_provider.regolo_model_provider import \
    RegoloModelProvider
from setting.models_provider.impl.siliconCloud_model_provider.siliconCloud_model_provider import \
    SiliconCloudModelProvider
from setting.models_provider.impl.tencent_cloud_model_provider.tencent_cloud_model_provider import \
    TencentCloudModelProvider
from setting.models_provider.impl.tencent_model_provider.tencent_model_provider import TencentModelProvider
from setting.models_provider.impl.vllm_model_provider.vllm_model_provider import VllmModelProvider
from setting.models_provider.impl.volcanic_engine_model_provider.volcanic_engine_model_provider import \
    VolcanicEngineModelProvider
from setting.models_provider.impl.wenxin_model_provider.wenxin_model_provider import WenxinModelProvider
from setting.models_provider.impl.xf_model_provider.xf_model_provider import XunFeiModelProvider
from setting.models_provider.impl.xinference_model_provider.xinference_model_provider import XinferenceModelProvider
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
    model_volcanic_engine_provider = VolcanicEngineModelProvider()
    model_tencent_provider = TencentModelProvider()
    model_tencent_cloud_provider = TencentCloudModelProvider()
    model_aws_bedrock_provider = BedrockModelProvider()
    model_local_provider = LocalModelProvider()
    model_xinference_provider = XinferenceModelProvider()
    model_vllm_provider = VllmModelProvider()
    aliyun_bai_lian_model_provider = AliyunBaiLianModelProvider()
    model_anthropic_provider = AnthropicModelProvider()
    model_siliconCloud_provider = SiliconCloudModelProvider()
    model_regolo_provider = RegoloModelProvider()
