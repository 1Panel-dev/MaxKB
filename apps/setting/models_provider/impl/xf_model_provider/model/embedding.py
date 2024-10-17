# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： embedding.py
    @date：2024/10/17 15:29
    @desc:
"""

import base64
import json
from typing import Dict, Optional

import numpy as np
from langchain_community.embeddings import SparkLLMTextEmbeddings
from numpy import ndarray

from setting.models_provider.base_model_provider import MaxKBBaseModel


class XFEmbedding(MaxKBBaseModel, SparkLLMTextEmbeddings):
    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return XFEmbedding(
            spark_app_id=model_credential.get('spark_app_id'),
            spark_api_key=model_credential.get('spark_api_key'),
            spark_api_secret=model_credential.get('spark_api_secret')
        )

    @staticmethod
    def _parser_message(
            message: str,
    ) -> Optional[ndarray]:
        data = json.loads(message)
        code = data["header"]["code"]
        if code != 0:
            # 这里是讯飞的QPS限制会报错,所以不建议用讯飞的向量模型
            raise Exception(f"Request error: {code}, {data}")
        else:
            text_base = data["payload"]["feature"]["text"]
            text_data = base64.b64decode(text_base)
            dt = np.dtype(np.float32)
            dt = dt.newbyteorder("<")
            text = np.frombuffer(text_data, dtype=dt)
            if len(text) > 2560:
                array = text[:2560]
            else:
                array = text
            return array
