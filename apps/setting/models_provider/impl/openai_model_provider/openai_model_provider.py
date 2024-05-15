# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： openai_model_provider.py
    @date：2024/3/28 16:26
    @desc:
"""
import os
from typing import Dict

from langchain.schema import HumanMessage

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, BaseModelCredential, \
    ModelInfo, \
    ModelTypeConst, ValidCode
from setting.models_provider.impl.openai_model_provider.model.openai_chat_model import OpenAIChatModel
from smartdoc.conf import PROJECT_DIR


class OpenAILLMModelCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], raise_exception=False):
        model_type_list = OpenAIModelProvider().get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')

        for key in ['api_base', 'api_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, f'{key} 字段为必填字段')
                else:
                    return False
        try:
            model = OpenAIModelProvider().get_model(model_type, model_name, model_credential)
            model.invoke([HumanMessage(content='你好')])
        except Exception as e:
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, f'校验失败,请检查参数是否正确: {str(e)}')
            else:
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'api_key': super().encryption(model.get('api_key', ''))}

    api_base = forms.TextInputField('API 域名', required=True)
    api_key = forms.PasswordInputField('API Key', required=True)


openai_llm_model_credential = OpenAILLMModelCredential()

model_dict = {
    'gpt-3.5-turbo': ModelInfo('gpt-3.5-turbo', '最新的gpt-3.5-turbo，随OpenAI调整而更新', ModelTypeConst.LLM,
                               openai_llm_model_credential,
                               ),
    'gpt-4': ModelInfo('gpt-4', '最新的gpt-4，随OpenAI调整而更新', ModelTypeConst.LLM, openai_llm_model_credential,
                       ),
    'gpt-4o': ModelInfo('gpt-4o', '最新的GPT-4o，比gpt-4-turbo更便宜、更快，随OpenAI调整而更新',
                        ModelTypeConst.LLM, openai_llm_model_credential,
                        ),
    'gpt-4-turbo': ModelInfo('gpt-4-turbo', '最新的gpt-4-turbo，随OpenAI调整而更新', ModelTypeConst.LLM,
                             openai_llm_model_credential,
                             ),
    'gpt-4-turbo-preview': ModelInfo('gpt-4-turbo-preview', '最新的gpt-4-turbo-preview，随OpenAI调整而更新',
                                     ModelTypeConst.LLM, openai_llm_model_credential,
                                     ),
    'gpt-3.5-turbo-0125': ModelInfo('gpt-3.5-turbo-0125',
                                    '2024年1月25日的gpt-3.5-turbo快照，支持上下文长度16,385 tokens', ModelTypeConst.LLM,
                                    openai_llm_model_credential,
                                    ),
    'gpt-3.5-turbo-1106': ModelInfo('gpt-3.5-turbo-1106',
                                    '2023年11月6日的gpt-3.5-turbo快照，支持上下文长度16,385 tokens', ModelTypeConst.LLM,
                                    openai_llm_model_credential,
                                    ),
    'gpt-3.5-turbo-0613': ModelInfo('gpt-3.5-turbo-0613',
                                    '[Legacy] 2023年6月13日的gpt-3.5-turbo快照，将于2024年6月13日弃用',
                                    ModelTypeConst.LLM, openai_llm_model_credential,
                                    ),
    'gpt-4o-2024-05-13': ModelInfo('gpt-4o-2024-05-13',
                                   '2024年5月13日的gpt-4o快照，支持上下文长度128,000 tokens',
                                   ModelTypeConst.LLM, openai_llm_model_credential,
                                   ),
    'gpt-4-turbo-2024-04-09': ModelInfo('gpt-4-turbo-2024-04-09',
                                        '2024年4月9日的gpt-4-turbo快照，支持上下文长度128,000 tokens',
                                        ModelTypeConst.LLM, openai_llm_model_credential,
                                        ),
    'gpt-4-0125-preview': ModelInfo('gpt-4-0125-preview', '2024年1月25日的gpt-4-turbo快照，支持上下文长度128,000 tokens',
                                    ModelTypeConst.LLM, openai_llm_model_credential,
                                    ),
    'gpt-4-1106-preview': ModelInfo('gpt-4-1106-preview', '2023年11月6日的gpt-4-turbo快照，支持上下文长度128,000 tokens',
                                    ModelTypeConst.LLM, openai_llm_model_credential,
                                    ),
}


class OpenAIModelProvider(IModelProvider):

    def get_dialogue_number(self):
        return 3

    def get_model(self, model_type, model_name, model_credential: Dict[str, object], **model_kwargs) -> OpenAIChatModel:
        azure_chat_open_ai = OpenAIChatModel(
            model=model_name,
            openai_api_base=model_credential.get('api_base'),
            openai_api_key=model_credential.get('api_key')
        )
        return azure_chat_open_ai

    def get_model_credential(self, model_type, model_name):
        if model_name in model_dict:
            return model_dict.get(model_name).model_credential
        return openai_llm_model_credential

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_openai_provider', name='OpenAI', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'openai_model_provider', 'icon',
                         'openai_icon_svg')))

    def get_model_list(self, model_type: str):
        if model_type is None:
            raise AppApiException(500, '模型类型不能为空')
        return [model_dict.get(key).to_dict() for key in
                list(filter(lambda key: model_dict.get(key).model_type == model_type, model_dict.keys()))]

    def get_model_type_list(self):
        return [{'key': "大语言模型", 'value': "LLM"}]
