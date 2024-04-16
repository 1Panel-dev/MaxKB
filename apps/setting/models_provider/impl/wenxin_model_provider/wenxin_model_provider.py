# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： wenxin_model_provider.py
    @date：2023/10/31 16:19
    @desc:
"""
import os
from typing import Dict

from langchain.schema import HumanMessage
from langchain_community.chat_models import QianfanChatEndpoint
from qianfan import ChatCompletion

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import ModelProvideInfo, ModelTypeConst, BaseModelCredential, \
    ModelInfo, IModelProvider, ValidCode
from setting.models_provider.impl.wenxin_model_provider.model.qian_fan_chat_model import QianfanChatModel
from smartdoc.conf import PROJECT_DIR


class WenxinLLMModelCredential(BaseForm, BaseModelCredential):
    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], raise_exception=False):
        model_type_list = WenxinModelProvider().get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')
        model_info = [model.lower() for model in ChatCompletion.models()]
        if not model_info.__contains__(model_name.lower()):
            raise AppApiException(ValidCode.valid_error.value, f'{model_name} 模型不支持')
        for key in ['api_key', 'secret_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, f'{key} 字段为必填字段')
                else:
                    return False
        try:
            WenxinModelProvider().get_model(model_type, model_name, model_credential).invoke(
                [HumanMessage(content='你好')])
        except Exception as e:
            raise e
        return True

    def encryption_dict(self, model_info: Dict[str, object]):
        return {**model_info, 'secret_key': super().encryption(model_info.get('secret_key', ''))}

    def build_model(self, model_info: Dict[str, object]):
        for key in ['api_key', 'secret_key', 'model']:
            if key not in model_info:
                raise AppApiException(500, f'{key} 字段为必填字段')
        self.api_key = model_info.get('api_key')
        self.secret_key = model_info.get('secret_key')
        return self

    api_key = forms.PasswordInputField('API Key', required=True)

    secret_key = forms.PasswordInputField("Secret Key", required=True)


win_xin_llm_model_credential = WenxinLLMModelCredential()
model_dict = {
    'ERNIE-Bot-4': ModelInfo('ERNIE-Bot-4',
                             'ERNIE-Bot-4是百度自行研发的大语言模型，覆盖海量中文数据，具有更强的对话问答、内容创作生成等能力。',
                             ModelTypeConst.LLM, win_xin_llm_model_credential),

    'ERNIE-Bot': ModelInfo('ERNIE-Bot',
                           'ERNIE-Bot是百度自行研发的大语言模型，覆盖海量中文数据，具有更强的对话问答、内容创作生成等能力。',
                           ModelTypeConst.LLM, win_xin_llm_model_credential),

    'ERNIE-Bot-turbo': ModelInfo('ERNIE-Bot-turbo',
                                 'ERNIE-Bot-turbo是百度自行研发的大语言模型，覆盖海量中文数据，具有更强的对话问答、内容创作生成等能力，响应速度更快。',
                                 ModelTypeConst.LLM, win_xin_llm_model_credential),

    'BLOOMZ-7B': ModelInfo('BLOOMZ-7B',
                           'BLOOMZ-7B是业内知名的大语言模型，由BigScience研发并开源，能够以46种语言和13种编程语言输出文本。',
                           ModelTypeConst.LLM, win_xin_llm_model_credential),

    'Llama-2-7b-chat': ModelInfo('Llama-2-7b-chat',
                                 'Llama-2-7b-chat由Meta AI研发并开源，在编码、推理及知识应用等场景表现优秀，Llama-2-7b-chat是高性能原生开源版本，适用于对话场景。',
                                 ModelTypeConst.LLM, win_xin_llm_model_credential),

    'Llama-2-13b-chat': ModelInfo('Llama-2-13b-chat',
                                  'Llama-2-13b-chat由Meta AI研发并开源，在编码、推理及知识应用等场景表现优秀，Llama-2-13b-chat是性能与效果均衡的原生开源版本，适用于对话场景。',
                                  ModelTypeConst.LLM, win_xin_llm_model_credential),

    'Llama-2-70b-chat': ModelInfo('Llama-2-70b-chat',
                                  'Llama-2-70b-chat由Meta AI研发并开源，在编码、推理及知识应用等场景表现优秀，Llama-2-70b-chat是高精度效果的原生开源版本。',
                                  ModelTypeConst.LLM, win_xin_llm_model_credential),

    'Qianfan-Chinese-Llama-2-7B': ModelInfo('Qianfan-Chinese-Llama-2-7B',
                                            '千帆团队在Llama-2-7b基础上的中文增强版本，在CMMLU、C-EVAL等中文知识库上表现优异。',
                                            ModelTypeConst.LLM, win_xin_llm_model_credential)
}


class WenxinModelProvider(IModelProvider):

    def get_dialogue_number(self):
        return 2

    def get_model(self, model_type, model_name, model_credential: Dict[str, object],
                  **model_kwargs) -> QianfanChatEndpoint:
        return QianfanChatModel(model=model_name,
                                qianfan_ak=model_credential.get('api_key'),
                                qianfan_sk=model_credential.get('secret_key'),
                                streaming=model_kwargs.get('streaming', False))

    def get_model_type_list(self):
        return [{'key': "大语言模型", 'value': "LLM"}]

    def get_model_list(self, model_type):
        if model_type is None:
            raise AppApiException(500, '模型类型不能为空')
        return [model_dict.get(key).to_dict() for key in
                list(filter(lambda key: model_dict.get(key).model_type == model_type, model_dict.keys()))]

    def get_model_credential(self, model_type, model_name):
        if model_name in model_dict:
            return model_dict.get(model_name).model_credential
        return win_xin_llm_model_credential

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_wenxin_provider', name='千帆大模型', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'wenxin_model_provider', 'icon',
                         'azure_icon_svg')))
