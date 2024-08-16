from typing import List, Dict
from langchain_community.chat_models import BedrockChat
from setting.models_provider.base_model_provider import MaxKBBaseModel


def get_max_tokens_keyword(model_name):
    """
    根据模型名称返回正确的 max_tokens 关键字。

    :param model_name: 模型名称字符串
    :return: 对应的 max_tokens 关键字字符串
    """
    if 'amazon' in model_name:
        return 'maxTokenCount'
    elif 'anthropic' in model_name:
        return 'max_tokens_to_sample'
    elif 'ai21' in model_name:
        return 'maxTokens'
    elif 'cohere' in model_name or 'mistral' in model_name:
        return 'max_tokens'
    elif 'meta' in model_name:
        return 'max_gen_len'
    else:
        raise ValueError("Unsupported model supplier in model_name.")


class BedrockModel(MaxKBBaseModel, BedrockChat):

    @staticmethod
    def is_cache_model():
        return False

    def __init__(self, model_id: str, region_name: str, credentials_profile_name: str,
                 streaming: bool = False, **kwargs):
        super().__init__(model_id=model_id, region_name=region_name,
                         credentials_profile_name=credentials_profile_name, streaming=streaming, **kwargs)

    @classmethod
    def new_instance(cls, model_type: str, model_name: str, model_credential: Dict[str, str],
                     **model_kwargs) -> 'BedrockModel':
        optional_params = {}
        if 'max_tokens' in model_kwargs and model_kwargs['max_tokens'] is not None:
            keyword = get_max_tokens_keyword(model_name)
            optional_params[keyword] = model_kwargs['max_tokens']
        if 'temperature' in model_kwargs and model_kwargs['temperature'] is not None:
            optional_params['temperature'] = model_kwargs['temperature']

        return cls(
            model_id=model_name,
            region_name=model_credential['region_name'],
            credentials_profile_name=model_credential['credentials_profile_name'],
            streaming=model_kwargs.pop('streaming', True),
            model_kwargs=optional_params
        )
