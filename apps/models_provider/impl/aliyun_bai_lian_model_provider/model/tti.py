# coding=utf-8
from http import HTTPStatus
from typing import Dict

from dashscope import ImageSynthesis, MultiModalConversation
from dashscope.aigc.image_generation import ImageGeneration

from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_tti import BaseTextToImage


class QwenTextToImageModel(MaxKBBaseModel, BaseTextToImage):
    api_key: str
    model_name: str
    params: dict
    api_base: str

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
        api_base = model_credential.get('api_base')
        if api_base is None:
            api_base = 'https://dashscope.aliyuncs.com/api/v1'

        chat_tong_yi = QwenTextToImageModel(
            model_name=model_name,
            api_key=model_credential.get('api_key'),
            api_base=api_base,
            **optional_params,
        )
        return chat_tong_yi

    def check_auth(self):
        # from openai import OpenAI
        #
        # client = OpenAI(
        #     # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
        #     api_key=self.api_key,
        #     base_url=self.api_base,
        # )
        # client.chat.completions.create(
        #     # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        #     model="qwen-max",
        #     messages=[
        #         {"role": "system", "content": "You are a helpful assistant."},
        #         {"role": "user", "content": gettext('Hello')},
        #     ]
        #
        # )
        return True

    def generate_image(self, prompt: str, negative_prompt: str = None):
        import dashscope
        dashscope.base_http_api_url = self.api_base
        if self.model_name.startswith("wan2.6") or self.model_name.startswith("z"):
            from dashscope.api_entities.dashscope_response import Message
            # 以下为北京地域url，各地域的base_url不同
            message = Message(
                role="user",
                content=[
                    {
                        'text': prompt
                    }
                ]
            )
            rsp = ImageGeneration.call(
                model=self.model_name,
                api_key=self.api_key,
                messages=[message],
                negative_prompt=negative_prompt,
                **self.params
            )
            file_urls = []
            if rsp.status_code == HTTPStatus.OK:
                for result in rsp.output.choices:
                    if isinstance(result.message.content, list):
                        for item in result.message.content:
                            if isinstance(item, dict) and item.get('image'):
                                file_urls.append(item.get('image'))
                    elif isinstance(result.message.content, dict):
                        if result.message.content.get('image'):
                            file_urls.append(result.message.content.get('image'))
            else:
                maxkb_logger.error('sync_call Failed, status_code: %s, code: %s, message: %s' %
                                   (rsp.status_code, rsp.code, rsp.message))
                raise Exception('sync_call Failed, status_code: %s, code: %s, message: %s' %
                                (rsp.status_code, rsp.code, rsp.message))
            return file_urls
        elif self.model_name.startswith("wan") or self.model_name.startswith("qwen-image-plus"):
            rsp = ImageSynthesis.call(api_key=self.api_key,
                                      model=self.model_name,
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
                raise Exception('sync_call Failed, status_code: %s, code: %s, message: %s' %
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
            rsp = MultiModalConversation.call(
                api_key=self.api_key,
                model=self.model_name,
                messages=messages,
                result_format='message',
                stream=False,
                negative_prompt=negative_prompt,
                **self.params
            )
            file_urls = []
            if rsp.status_code == HTTPStatus.OK:
                for result in rsp.output.choices:
                    if isinstance(result.message.content, list):
                        for item in result.message.content:
                            if isinstance(item, dict) and item.get('image'):
                                file_urls.append(item.get('image'))
                    elif isinstance(result.message.content, dict):
                        if result.message.content.get('image'):
                            file_urls.append(result.message.content.get('image'))
            else:
                maxkb_logger.error('sync_call Failed, status_code: %s, code: %s, message: %s' %
                                   (rsp.status_code, rsp.code, rsp.message))
                raise Exception('sync_call Failed, status_code: %s, code: %s, message: %s' %
                                (rsp.status_code, rsp.code, rsp.message))
            return file_urls
