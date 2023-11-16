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
from setting.models_provider.impl.wenxin_model_provider.wenxin_model_provider import WenxinModelProvider


class ModelProvideConstants(Enum):
    model_azure_provider = AzureModelProvider()
    model_wenxin_provider = WenxinModelProvider()
