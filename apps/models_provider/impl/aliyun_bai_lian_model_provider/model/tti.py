# coding=utf-8
from http import HTTPStatus
from typing import Dict

from dashscope import ImageSynthesis, MultiModalConversation
from django.utils.translation import gettext
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import HumanMessage
import logging

from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_tti import BaseTextToImage


class QwenTextToImageModel(MaxKBBaseModel, BaseTextToImage):
    api_key: str
    api_base: str
    model_name: str
    params: dict

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.api_base = kwargs.get('api_base')
        self.model_name = kwargs.get('model_name')
        self.params = kwargs.get('params')

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {'params': {'size': '1024*1024', 'n': 1}}
        for key, value in model_kwargs.items():
            if key not in ['model_id', 'use_local', 'streaming']:
                optional_params['params'][key] = value
        chat_tong_yi = QwenTextToImageModel(
            model_name=model_name,
            api_key=model_credential.get('api_key'),
            api_base=model_credential.get('api_base'),
            **optional_params,
        )
        return chat_tong_yi

    def check_auth(self):
        chat = ChatTongyi(api_key=self.api_key, model_name='qwen-max')
        chat.invoke([HumanMessage([{"type": "text", "text": gettext('Hello')}])])

    def generate_image(self, prompt: str, negative_prompt: str = None):
        if self.model_name.startswith("wan"):
            # 如果提供了api_base，则使用自定义base_url，否则使用默认URL
            base_url = self.api_base or 'https://dashscope.aliyuncs.com/compatible-mode/v1'
            rsp = ImageSynthesis.call(api_key=self.api_key,
                                      model=self.model_name,
                                      base_url=base_url,
                                      prompt=prompt,
                                      negative_prompt=negative_prompt,
                                      **self.params)
            file_urls = []
            if rsp.status_code == HTTPStatus.OK:
                for result in rsp.output.results:
                    file_urls.append(result.url)
            else:
                maxkb_logger.error('sync_call Failed, status_code: %s, code: %s, message: %s' %
                                   (rsp.status_code, rsp.code, rsp.message))
            return file_urls
        elif self.model_name.startswith("qwen"):
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
            # 如果提供了api_base，则使用自定义base_url，否则使用默认URL
            base_url = self.api_base or 'https://dashscope.aliyuncs.com/v1'
            rsp = MultiModalConversation.call(
                api_key=self.api_key,
                model=self.model_name,
                messages=messages,
                result_format='message',
                base_url=base_url,
                stream=False,
                negative_prompt=negative_prompt,
                **self.params
            )
            file_urls = []
            if rsp.status_code == HTTPStatus.OK:
                for result in rsp.output.choices:
                    file_urls.append(result.message.content[0].get('image'))
            else:
                maxkb_logger.error('sync_call Failed, status_code: %s, code: %s, message: %s' %
                                   (rsp.status_code, rsp.code, rsp.message))
            return file_urls
