# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： reranker.py.py
    @date：2024/9/2 16:42
    @desc:
"""
from typing import Dict

from langchain_community.document_compressors import DashScopeRerank

from setting.models_provider.base_model_provider import MaxKBBaseModel


class AliyunBaiLianReranker(MaxKBBaseModel, DashScopeRerank):
    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return AliyunBaiLianReranker(model=model_name, dashscope_api_key=model_credential.get('dashscope_api_key'),
                                     top_n=model_kwargs.get('top_n', 3))
