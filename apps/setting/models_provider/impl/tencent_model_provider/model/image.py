from typing import Dict

from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_chat_open_ai import BaseChatOpenAI


class TencentVision(MaxKBBaseModel, BaseChatOpenAI):

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return TencentVision(
            model_name=model_name,
            openai_api_base='https://api.hunyuan.cloud.tencent.com/v1',
            openai_api_key=model_credential.get('api_key'),
            # stream_options={"include_usage": True},
            streaming=True,
            stream_usage=True,
            extra_body=optional_params
        )
