# coding=utf-8
"""
    @project: MaxKB
    @file: image.py
    @desc: AWS Bedrock Vision-Language Model Implementation
"""
from typing import Dict, List

from botocore.config import Config
from langchain_aws import ChatBedrock
from langchain_core.messages import BaseMessage, get_buffer_string

from common.config.tokenizer_manage_config import TokenizerManage
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.aws_bedrock_model_provider.model.llm import _update_aws_credentials


class BedrockVLModel(MaxKBBaseModel, ChatBedrock):
    """
    AWS Bedrock Vision-Language Model
    Supports Claude 3 models with vision capabilities (Haiku, Sonnet, Opus)
    """

    @staticmethod
    def is_cache_model():
        return False

    def __init__(self, model_id: str, region_name: str, credentials_profile_name: str,
                 streaming: bool = False, config: Config = None, **kwargs):
        super().__init__(
            model_id=model_id,
            region_name=region_name,
            credentials_profile_name=credentials_profile_name,
            streaming=streaming,
            config=config,
            **kwargs
        )

    @classmethod
    def new_instance(cls, model_type: str, model_name: str, model_credential: Dict[str, str],
                     **model_kwargs) -> 'BedrockVLModel':
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)

        config = {}
        # Check if proxy URL is provided
        if 'base_url' in model_credential and model_credential['base_url']:
            proxy_url = model_credential['base_url']
            config = Config(
                proxies={
                    'http': proxy_url,
                    'https': proxy_url
                },
                connect_timeout=60,
                read_timeout=60
            )
        _update_aws_credentials(
            model_credential['access_key_id'],
            model_credential['access_key_id'],
            model_credential['secret_access_key']
        )

        return cls(
            model_id=model_name,
            region_name=model_credential['region_name'],
            credentials_profile_name=model_credential['access_key_id'],
            streaming=model_kwargs.pop('streaming', True),
            model_kwargs=optional_params,
            config=config
        )

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        """
        Get the number of tokens from messages
        Falls back to local tokenizer if the model's tokenizer fails
        """
        try:
            return super().get_num_tokens_from_messages(messages)
        except Exception as e:
            tokenizer = TokenizerManage.get_tokenizer()
            return sum([len(tokenizer.encode(get_buffer_string([m]))) for m in messages])

    def get_num_tokens(self, text: str) -> int:
        """
        Get the number of tokens from text
        Falls back to local tokenizer if the model's tokenizer fails
        """
        try:
            return super().get_num_tokens(text)
        except Exception as e:
            tokenizer = TokenizerManage.get_tokenizer()
            return len(tokenizer.encode(text))
