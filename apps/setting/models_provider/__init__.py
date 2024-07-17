# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： __init__.py.py
    @date：2023/10/31 17:16
    @desc:
"""
import json
from typing import Dict

from common.util.rsa_util import rsa_long_decrypt
from setting.models_provider.constants.model_provider_constants import ModelProvideConstants


def get_model_(provider, model_type, model_name, credential):
    """
    获取模型实例
    @param provider:   供应商
    @param model_type: 模型类型
    @param model_name: 模型名称
    @param credential: 认证信息
    @return: 模型实例
    """
    model = get_provider(provider).get_model(model_type, model_name,
                                             json.loads(
                                                 rsa_long_decrypt(credential)),
                                             streaming=True)
    return model


def get_model(model):
    """
    获取模型实例
    @param model: model 数据库Model实例对象
    @return: 模型实例
    """
    return get_model_(model.provider, model.model_type, model.model_name, model.credential)


def get_provider(provider):
    """
    获取供应商实例
    @param provider: 供应商字符串
    @return: 供应商实例
    """
    return ModelProvideConstants[provider].value


def get_model_list(provider, model_type):
    """
    获取模型列表
    @param provider:   供应商字符串
    @param model_type: 模型类型
    @return:  模型列表
    """
    return get_provider(provider).get_model_list(model_type)


def get_model_credential(provider, model_type, model_name):
    """
    获取模型认证实例
    @param provider:   供应商字符串
    @param model_type: 模型类型
    @param model_name: 模型名称
    @return:  认证实例对象
    """
    return get_provider(provider).get_model_credential(model_type, model_name)


def get_model_type_list(provider):
    """
    获取模型类型列表
    @param provider:  供应商字符串
    @return:  模型类型列表
    """
    return get_provider(provider).get_model_type_list()


def is_valid_credential(provider, model_type, model_name, model_credential: Dict[str, object], raise_exception=False):
    """
    校验模型认证参数
    @param provider:         供应商字符串
    @param model_type:       模型类型
    @param model_name:       模型名称
    @param model_credential: 模型认证数据
    @param raise_exception:  是否抛出错误
    @return: True|False
    """
    return get_provider(provider).is_valid_credential(model_type, model_name, model_credential, raise_exception)
