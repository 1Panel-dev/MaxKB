# -*- coding:utf-8 -*-
#
#   author: iflytek
#
#  错误码链接：https://www.xfyun.cn/document/error-code （code返回错误码时必看）
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import asyncio
import base64
import datetime
import hashlib
import hmac
import json
import logging
import os
from datetime import datetime
from typing import Dict
from urllib.parse import urlencode, urlparse
import ssl
import websockets

from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_tts import BaseTextToSpeech

max_kb = logging.getLogger("max_kb")

STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


class XFSparkTextToSpeech(MaxKBBaseModel, BaseTextToSpeech):
    spark_app_id: str
    spark_api_key: str
    spark_api_secret: str
    spark_api_url: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spark_api_url = kwargs.get('spark_api_url')
        self.spark_app_id = kwargs.get('spark_app_id')
        self.spark_api_key = kwargs.get('spark_api_key')
        self.spark_api_secret = kwargs.get('spark_api_secret')

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {}
        if 'max_tokens' in model_kwargs and model_kwargs['max_tokens'] is not None:
            optional_params['max_tokens'] = model_kwargs['max_tokens']
        if 'temperature' in model_kwargs and model_kwargs['temperature'] is not None:
            optional_params['temperature'] = model_kwargs['temperature']
        return XFSparkTextToSpeech(
            spark_app_id=model_credential.get('spark_app_id'),
            spark_api_key=model_credential.get('spark_api_key'),
            spark_api_secret=model_credential.get('spark_api_secret'),
            spark_api_url=model_credential.get('spark_api_url'),
            **optional_params
        )

    # 生成url
    def create_url(self):
        url = self.spark_api_url
        host = urlparse(url).hostname
        # 生成RFC1123格式的时间戳
        gmt_format = '%a, %d %b %Y %H:%M:%S GMT'
        date = datetime.utcnow().strftime(gmt_format)

        # 拼接字符串
        signature_origin = "host: " + host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
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
        self.text_to_speech("你好")

    def text_to_speech(self, text):

        # 使用小语种须使用以下方式，此处的unicode指的是 utf16小端的编码方式，即"UTF-16LE"”
        # self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-16')), "UTF8")}
        async def handle():
            async with websockets.connect(self.create_url(), max_size=1000000000, ssl=ssl_context) as ws:
                # 发送 full client request
                await self.send(ws, text)
                return await self.handle_message(ws)

        return asyncio.run(handle())

    @staticmethod
    async def handle_message(ws):
        audio_bytes: bytes = b''
        while True:
            res = await ws.recv()
            message = json.loads(res)
            # print(message)
            code = message["code"]
            sid = message["sid"]

            if code != 0:
                errMsg = message["message"]
                raise Exception(f"sid: {sid} call error: {errMsg} code is: {code}")
            else:
                audio = message["data"]["audio"]
                audio = base64.b64decode(audio)
                audio_bytes += audio
            # 退出
            if message["data"]["status"] == 2:
                break
        return audio_bytes

    async def send(self, ws, text):
        d = {
            "common": {"app_id": self.spark_app_id},
            "business": {"aue": "lame", "sfl": 1, "auf": "audio/L16;rate=16000", "vcn": "xiaoyan", "tte": "utf8"},
            "data": {"status": 2, "text": str(base64.b64encode(text.encode('utf-8')), "UTF8")},
        }
        d = json.dumps(d)
        await ws.send(d)
