# coding=utf-8

import asyncio
import base64
import datetime
import hashlib
import hmac
import json
import os
import ssl
from datetime import datetime, UTC
from typing import Dict
from urllib.parse import urlencode
from urllib.parse import urlparse

import websockets

from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_image import BaseImage

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


class XFSparkImage(MaxKBBaseModel, BaseImage):
    spark_app_id: str
    spark_api_key: str
    spark_api_secret: str
    spark_api_url: str
    params: dict

    # 初始化
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spark_api_url = kwargs.get('spark_api_url')
        self.spark_app_id = kwargs.get('spark_app_id')
        self.spark_api_key = kwargs.get('spark_api_key')
        self.spark_api_secret = kwargs.get('spark_api_secret')
        self.params = kwargs.get('params')

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {'params': {}}
        for key, value in model_kwargs.items():
            if key not in ['model_id', 'use_local', 'streaming']:
                optional_params['params'][key] = value
        return XFSparkImage(
            spark_app_id=model_credential.get('spark_app_id'),
            spark_api_key=model_credential.get('spark_api_key'),
            spark_api_secret=model_credential.get('spark_api_secret'),
            spark_api_url=model_credential.get('spark_api_url'),
            **optional_params
        )

    def create_url(self):
        url = self.spark_api_url
        host = urlparse(url).hostname
        # 生成RFC1123格式的时间戳
        gmt_format = '%a, %d %b %Y %H:%M:%S GMT'
        date = datetime.now(UTC).strftime(gmt_format)

        # 拼接字符串
        signature_origin = "host: " + host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2.1/image " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.spark_api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.spark_api_key, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": host
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print('websocket url :', url)
        return url

    def check_auth(self):
        cwd = os.path.dirname(os.path.abspath(__file__))
        with open(f'{cwd}/img_1.png', 'rb') as f:
            self.image_understand(f,"一句话概述这个图片")

    def image_understand(self, image_file, question):
        async def handle():
            async with websockets.connect(self.create_url(), max_size=1000000000, ssl=ssl_context) as ws:
                # 发送 full client request
                await self.send(ws, image_file, question)
                return await self.handle_message(ws)

        return asyncio.run(handle())

    # 收到websocket消息的处理
    @staticmethod
    async def handle_message(ws):
        # print(message)
        answer = ''
        while True:
            res = await ws.recv()
            data = json.loads(res)
            code = data['header']['code']
            if code != 0:
                return f'请求错误: {code}, {data}'
            else:
                choices = data["payload"]["choices"]
                status = choices["status"]
                content = choices["text"][0]["content"]
                # print(content, end="")
                answer += content
                # print(1)
                if status == 2:
                    break
        return answer

    async def send(self, ws, image_file, question):
        text = [
            {"role": "user", "content": str(base64.b64encode(image_file.read()), 'utf-8'), "content_type": "image"},
            {"role": "user", "content": question}
        ]

        data = {
            "header": {
                "app_id": self.spark_app_id
            },
            "parameter": {
                "chat": {
                    "domain": "image",
                    "temperature": 0.5,
                    "top_k": 4,
                    "max_tokens": 2028,
                    "auditing": "default"
                }
            },
            "payload": {
                "message": {
                    "text": text
                }
            }
        }

        d = json.dumps(data)
        await ws.send(d)

    def is_cache_model(self):
        return False

    @staticmethod
    def get_len(text):
        length = 0
        for content in text:
            temp = content["content"]
            leng = len(temp)
            length += leng
        return length

    def check_len(self, text):
        print("text-content-tokens:", self.get_len(text[1:]))
        while (self.get_len(text[1:]) > 8000):
            del text[1]
        return text
