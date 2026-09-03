# coding=utf-8
"""
    @project: MaxKB
    @Author：aimlapi.com
    @file： const.py
    @date：2026/09/03 10:00
    @desc: AI/ML API 供应商的公共常量与请求参数处理
"""
from typing import Dict, Optional
from urllib.parse import urlparse

from models_provider.base_model_provider import MaxKBBaseModel

# AI/ML API 的默认接口地址，兼容 OpenAI 协议
API_BASE = 'https://api.aimlapi.com/v1'

# 渠道归因请求头：HTTP-Referer / X-Title 标识调用方（即 MaxKB 本身），
# X-AIMLAPI-* 是 AI/ML API 用于渠道统计的请求头。
# 该常量是共享的，任何时候都不要就地修改，请使用 get_default_headers 生成新字典。
ATTRIBUTION_HEADERS = {
    'HTTP-Referer': 'https://github.com/1Panel-dev/MaxKB',
    'X-Title': 'MaxKB',
    'X-AIMLAPI-Partner-ID': 'part_BOQuEVgOgdpgCUqh5u0YkgzL',
    'X-AIMLAPI-Source': 'agent/maxkb',
}

# 只有请求发往 AI/ML API 自己的域名时才携带归因请求头。
# 用户可以把 API URL 改成其他服务商或中转代理，此时不应把这些请求头带过去。
ATTRIBUTION_HOSTS = {'api.aimlapi.com'}


def is_aimlapi_endpoint(api_base: Optional[str]) -> bool:
    """
    判断接口地址是否指向 AI/ML API
    @param api_base: 用户填写的 API URL，为空时使用默认地址
    """
    if not api_base:
        return True
    hostname = urlparse(api_base if '//' in api_base else f'//{api_base}').hostname
    return (hostname or '').lower() in ATTRIBUTION_HOSTS


def get_default_headers(api_base: Optional[str], default_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    生成请求头，调用方自定义的请求头优先级更高（合并而不是覆盖）
    @param api_base:        API URL
    @param default_headers: 调用方自定义的请求头
    @return: 新的请求头字典
    """
    if not is_aimlapi_endpoint(api_base):
        return {**(default_headers or {})}
    return {**ATTRIBUTION_HEADERS, **(default_headers or {})}


def filter_optional_params(model_kwargs: Dict[str, object]) -> Dict[str, object]:
    """
    在 MaxKB 默认过滤逻辑之上再丢弃取值为 None 的参数。
    AI/ML API 上不同模型对 null 的容忍度不一样：google/gemini-2.5-flash 可以接受，
    而 openai/gpt-4o-mini、deepseek/deepseek-chat 等模型在 temperature、top_p、seed、
    tools 为 null 时直接返回 400。因此未设置的参数必须省略，而不是以 None 发送。
    """
    optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
    return {key: value for key, value in optional_params.items() if value is not None}
