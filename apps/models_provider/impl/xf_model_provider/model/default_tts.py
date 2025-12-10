# coding=utf-8
"""
    @project: MaxKB
    @Author：
    @file： default_tts.py
    @date：2025/12/9
    @desc: 讯飞 TTS 工厂类，根据 api_version 路由到具体实现
"""
from typing import Dict

from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_tts import BaseTextToSpeech


class XFSparkDefaultTextToSpeech(MaxKBBaseModel, BaseTextToSpeech):
    """讯飞 TTS 工厂类，根据 api_version 参数路由到具体实现"""

    def check_auth(self):
        pass

    def text_to_speech(self, text):
        pass

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        from models_provider.impl.xf_model_provider.model.tts import XFSparkTextToSpeech
        from models_provider.impl.xf_model_provider.model.super_humanoid_tts import XFSparkSuperHumanoidTextToSpeech

        api_version = model_credential.get('api_version', 'online')

        if api_version == 'super_humanoid':
            # 超拟人：从 credential 获取 vcn_super，构造统一的 credential 格式
            vcn = model_credential.get('vcn_super', 'x5_lingxiaoxuan_flow')
            unified_credential = {
                'spark_app_id': model_credential.get('spark_app_id'),
                'spark_api_key': model_credential.get('spark_api_key'),
                'spark_api_secret': model_credential.get('spark_api_secret'),
                'spark_api_url': model_credential.get('spark_api_url_super'),
            }
            return XFSparkSuperHumanoidTextToSpeech.new_instance(
                model_type, model_name, unified_credential, vcn=vcn, **model_kwargs
            )
        else:
            # 在线语音：从 credential 获取 vcn_online
            vcn = model_credential.get('vcn_online', 'xiaoyan')
            unified_credential = {
                'spark_app_id': model_credential.get('spark_app_id'),
                'spark_api_key': model_credential.get('spark_api_key'),
                'spark_api_secret': model_credential.get('spark_api_secret'),
                'spark_api_url': model_credential.get('spark_api_url'),
            }
            return XFSparkTextToSpeech.new_instance(
                model_type, model_name, unified_credential, vcn=vcn, **model_kwargs
            )
