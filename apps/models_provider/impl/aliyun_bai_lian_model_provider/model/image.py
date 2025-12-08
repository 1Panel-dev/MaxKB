# coding=utf-8
import datetime
import time
from typing import Dict, Optional, Any, Iterator

import requests
from langchain_community.chat_models import ChatTongyi
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import HumanMessage, BaseMessageChunk, AIMessage
from django.utils.translation import gettext
from langchain_core.runnables import RunnableConfig

from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_chat_open_ai import BaseChatOpenAI
import json


class QwenVLChatModel(MaxKBBaseModel, BaseChatOpenAI):

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        chat_tong_yi = QwenVLChatModel(
            model_name=model_name,
            openai_api_key=model_credential.get('api_key'),
            openai_api_base='https://dashscope.aliyuncs.com/compatible-mode/v1',
            # stream_options={"include_usage": True},
            streaming=True,
            stream_usage=True,
            extra_body=optional_params
        )
        return chat_tong_yi

    def check_auth(self, api_key):
        chat = ChatTongyi(api_key=api_key, model_name='qwen-max')
        chat.invoke([HumanMessage([{"type": "text", "text": gettext('Hello')}])])

    def get_upload_policy(self, api_key, model_name):
        """获取文件上传凭证"""
        url = "https://dashscope.aliyuncs.com/api/v1/uploads"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        params = {
            "action": "getPolicy",
            "model": model_name
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"Failed to get upload policy: {response.text}")

        return response.json()['data']

    def upload_file_to_oss(self, policy_data, file_stream, file_name):
        """将文件流上传到临时存储OSS"""
        # 构建OSS上传的目标路径
        key = f"{policy_data['upload_dir']}/{file_name}"

        # 构建上传数据
        files = {
            'OSSAccessKeyId': (None, policy_data['oss_access_key_id']),
            'Signature': (None, policy_data['signature']),
            'policy': (None, policy_data['policy']),
            'x-oss-object-acl': (None, policy_data['x_oss_object_acl']),
            'x-oss-forbid-overwrite': (None, policy_data['x_oss_forbid_overwrite']),
            'key': (None, key),
            'success_action_status': (None, '200'),
            'file': (file_name, file_stream)
        }

        # 执行上传请求
        response = requests.post(policy_data['upload_host'], files=files)
        if response.status_code != 200:
            raise Exception(f"Failed to upload file: {response.text}")

        return f"oss://{key}"

    def upload_file_and_get_url(self, file_stream, file_name):
        max_retries = 3

        retry_delay = 1  # 初始重试延迟（秒）

        for attempt in range(max_retries):
            try:
                # 1. 获取上传凭证，上传凭证接口有限流，超出限流将导致请求失败
                policy_data = self.get_upload_policy(self.openai_api_key.get_secret_value(), self.model_name)
                # 2. 上传文件到OSS
                oss_url = self.upload_file_to_oss(policy_data, file_stream, file_name)
                return oss_url
            except Exception as e:
                if attempt < max_retries - 1:
                    # 指数退避策略
                    time.sleep(retry_delay * (2 ** attempt))
                    continue
                else:
                    raise Exception(f"文件上传失败，已重试{max_retries}次: {str(e)}")

    def stream(
            self,
            input: LanguageModelInput,
            config: Optional[RunnableConfig] = None,
            *,
            stop: Optional[list[str]] = None,
            **kwargs: Any,
    ) -> Iterator[BaseMessageChunk]:
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.openai_api_key.get_secret_value()}",
            "Content-Type": "application/json",
            "X-DashScope-OssResourceResolve": "enable"
        }
        # 遍历input 获取所有的content 构造新的消息体
        messages = []
        for message in input:
            if message.type == "human":
                messages.append({
                    "role": "user",
                    "content": message.content
                })
            elif message.type == "ai":
                messages.append({
                    "role": "assistant",
                    "content": message.content
                })
            elif message.type == "system":
                messages.append({
                    "role": "system",
                    "content": message.content
                })

        data = {
            "model": self.model_name,
            "messages": messages,
            **self.extra_body,
            "stream": True,
        }

        # 增加重试机制
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, json=data, stream=True, timeout=30)
                if response.status_code != 200:
                    raise Exception(f"Failed to get response: {response.text}")

                for line in response.iter_lines():
                    if line:
                        try:
                            decoded_line = line.decode('utf-8')
                            # 检查是否是有效的SSE数据行
                            if decoded_line.startswith('data: '):
                                # 提取JSON部分
                                json_str = decoded_line[6:]  # 移除 'data: ' 前缀
                                # 检查是否是结束标记
                                if json_str.strip() == '[DONE]':
                                    continue

                                # 尝试解析JSON
                                chunk_data = json.loads(json_str)

                                if 'choices' in chunk_data and chunk_data['choices']:
                                    delta = chunk_data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        yield AIMessage(content=content)
                        except json.JSONDecodeError:
                            # 忽略无法解析的行
                            continue
                        except Exception as e:
                            # 处理其他可能的异常
                            continue
                break  # 成功执行则退出重试循环

            except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError) as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))  # 指数退避
                    continue
                else:
                    raise Exception(f"网络连接失败，已重试{max_retries}次: {str(e)}")
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))
                    continue
                else:
                    raise Exception(f"请求失败，已重试{max_retries}次: {str(e)}")
