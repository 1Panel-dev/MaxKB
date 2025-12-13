import os
import re
from typing import Dict, List, Sequence, Optional, Any

from botocore.config import Config
from langchain_aws import BedrockRerank
from langchain_core.callbacks import Callbacks
from langchain_core.documents import BaseDocumentCompressor, Document
from pydantic import ConfigDict

from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.aws_bedrock_model_provider.model.llm import _update_aws_credentials


class BedrockRerankerModel(MaxKBBaseModel, BaseDocumentCompressor):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    model_id: Optional[str] = None
    model_arn: Optional[str] = None
    region_name: Optional[str] = None
    credentials_profile_name: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    config: Optional[Any] = None
    top_n: Optional[int] = 3

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type: str, model_name: str, model_credential: Dict[str, str],
                     **model_kwargs) -> 'BedrockRerankerModel':
        top_n = model_kwargs.get('top_n', 3)
        region_name = model_credential['region_name']
        model_arn = f"arn:aws:bedrock:{region_name}::foundation-model/{model_name}"

        config = None
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

        _update_aws_credentials(model_credential['access_key_id'], model_credential['access_key_id'],
                                model_credential['secret_access_key'])

        return BedrockRerankerModel(
            model_id=model_name,
            model_arn=model_arn,
            region_name=region_name,
            credentials_profile_name=model_credential['access_key_id'],
            aws_access_key_id=model_credential['access_key_id'],
            aws_secret_access_key=model_credential['secret_access_key'],
            config=config,
            top_n=top_n
        )

    def compress_documents(self, documents: Sequence[Document], query: str,
                          callbacks: Optional[Callbacks] = None) -> Sequence[Document]:
        """Compress documents using Bedrock reranking."""
        if not documents:
            return []

        reranker = BedrockRerank(
            model_arn=self.model_arn,
            region_name=self.region_name,
            credentials_profile_name=self.credentials_profile_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            config=self.config,
            top_n=self.top_n
        )
        return reranker.compress_documents(documents, query, callbacks)

