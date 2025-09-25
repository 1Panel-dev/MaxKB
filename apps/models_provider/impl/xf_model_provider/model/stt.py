# -*- coding:utf-8 -*-
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
import ssl
from datetime import datetime, UTC
from typing import Dict
from urllib.parse import urlencode, urlparse

import websockets

from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_stt import BaseSpeechToText

STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


class XFSparkSpeechToText(MaxKBBaseModel, BaseSpeechToText):
    spark_app_id: str
    spark_api_key: str
    spark_api_secret: str
    spark_api_url: str
    params: dict

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spark_api_url = kwargs.get('spark_api_url')
        self.spark_app_id = kwargs.get('spark_app_id')
        self.spark_api_key = kwargs.get('spark_api_key')
        self.spark_api_secret = kwargs.get('spark_api_secret')
        self.params = kwargs.get('params')

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {}
        if 'max_tokens' in model_kwargs and model_kwargs['max_tokens'] is not None:
            optional_params['max_tokens'] = model_kwargs['max_tokens']
        if 'temperature' in model_kwargs and model_kwargs['temperature'] is not None:
            optional_params['temperature'] = model_kwargs['temperature']
        return XFSparkSpeechToText(
            spark_app_id=model_credential.get('spark_app_id'),
            spark_api_key=model_credential.get('spark_api_key'),
            spark_api_secret=model_credential.get('spark_api_secret'),
            spark_api_url=model_credential.get('spark_api_url'),
            params=model_kwargs,
            **optional_params
        )

    # 生成url
    def create_url(self):
        url = self.spark_api_url
        host = urlparse(url).hostname
        # 生成RFC1123格式的时间戳
        gmt_format = '%a, %d %b %Y %H:%M:%S GMT'
        date = datetime.now(UTC).strftime(gmt_format)

        # 拼接字符串
        signature_origin = "host: " + host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/iat " + "HTTP/1.1"
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
        with open(f'{cwd}/iat_mp3_16k.mp3', 'rb') as f:
            self.speech_to_text(f)

    def speech_to_text(self, file):
        async def handle():
            async with websockets.connect(self.create_url(), max_size=1000000000, ssl=ssl_context) as ws:
                # 发送 full client request
                await self.send(ws, file)
                return await self.handle_message(ws)

        return asyncio.run(handle())

    @staticmethod
    async def handle_message(ws):
        res = await ws.recv()
        message = json.loads(res)
        code = message["code"]
        sid = message["sid"]
        if code != 0:
            errMsg = message["message"]
            raise Exception(f"sid: {sid} call error: {errMsg} code is: {code}")
        else:
            data = message["data"]["result"]["ws"]
            result = ""
            for i in data:
                for w in i["cw"]:
                    result += w["w"]
            # print("sid:%s call success!,data is:%s" % (sid, json.dumps(data, ensure_ascii=False)))
            return result

    # 收到websocket连接建立的处理
    async def send(self, ws, file):
        frameSize = 8000  # 每一帧的音频大小
        status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧

        allowed_params = {'language','domain','accent','vad_eos','dwa','pd','ptt',
                          'pcm','ltc','rlang','vinfo','nunum','speex_size','nbest','wbest'}

        business_params = {k: v for k,v in self.params.items() if k in allowed_params}

        while True:
            buf = file.read(frameSize)
            # 文件结束
            if not buf:
                status = STATUS_LAST_FRAME
            # 第一帧处理
            # 发送第一帧音频，带business 参数
            # appid 必须带上，只需第一帧发送
            if status == STATUS_FIRST_FRAME:
                d = {
                    "common": {"app_id": self.spark_app_id},
                    "business": {
                        **business_params
                    },
                    "data": {
                        "status": 0, "format": "audio/L16;rate=16000",
                        "audio": str(base64.b64encode(buf), 'utf-8'),
                        "encoding": "lame"}
                }
                print(d)
                d = json.dumps(d)
                await ws.send(d)
                status = STATUS_CONTINUE_FRAME
            # 中间帧处理
            elif status == STATUS_CONTINUE_FRAME:
                d = {"data": {"status": 1, "format": "audio/L16;rate=16000",
                              "audio": str(base64.b64encode(buf), 'utf-8'),
                              "encoding": "lame"}}
                await ws.send(json.dumps(d))
            # 最后一帧处理
            elif status == STATUS_LAST_FRAME:
                d = {"data": {"status": 2, "format": "audio/L16;rate=16000",
                              "audio": str(base64.b64encode(buf), 'utf-8'),
                              "encoding": "lame"}}
                await ws.send(json.dumps(d))
                break
