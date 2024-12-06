from typing import Dict

from langchain_openai.chat_models import ChatOpenAI

from common.config.tokenizer_manage_config import TokenizerManage
from setting.models_provider.base_model_provider import MaxKBBaseModel


def custom_get_token_ids(text: str):
    tokenizer = TokenizerManage.get_tokenizer()
    return tokenizer.encode(text)


class ZhiPuImage(MaxKBBaseModel, ChatOpenAI):

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return ZhiPuImage(
            model_name=model_name,
            openai_api_key=model_credential.get('api_key'),
            openai_api_base='https://open.bigmodel.cn/api/paas/v4',
            # stream_options={"include_usage": True},
            streaming=True,
            **optional_params,
        )
