# -*- coding:utf-8 -*-
#
#   author: iflytek
#
#  错误码链接：https://www.xfyun.cn/document/error-code （code返回错误码时必看）
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import asyncio
import base64
import hashlib
import hmac
import json
import ssl
from datetime import datetime, UTC
from typing import Dict
from urllib.parse import urlencode, urlparse

import websockets
from django.utils.translation import gettext as _

from common.utils.common import _remove_empty_lines
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_tts import BaseTextToSpeech

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


class XFSparkSuperHumanoidTextToSpeech(MaxKBBaseModel, BaseTextToSpeech):
    """讯飞超拟人语音合成 (Super Humanoid TTS)"""
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
        self.params = kwargs.get('params') or {}

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        spark_api_url = model_credential.get('spark_api_url')
        vcn = model_kwargs.get('vcn', 'x5_lingxiaoxuan_flow')

        params = {'vcn': vcn}
        for k, v in model_kwargs.items():
            if k not in ['model_id', 'use_local', 'streaming', 'vcn']:
                params[k] = v

        return XFSparkSuperHumanoidTextToSpeech(
            spark_app_id=model_credential.get('spark_app_id'),
            spark_api_key=model_credential.get('spark_api_key'),
            spark_api_secret=model_credential.get('spark_api_secret'),
            spark_api_url=spark_api_url,
            params=params
        )

    def create_url(self):
        url = self.spark_api_url
        host = urlparse(url).hostname

        gmt_format = '%a, %d %b %Y %H:%M:%S GMT'
        date = datetime.now(UTC).strftime(gmt_format)

        signature_origin = f"host: {host}\n"
        signature_origin += f"date: {date}\n"
        signature_origin += f"GET {urlparse(url).path} HTTP/1.1"

        signature_sha = hmac.new(
            self.spark_api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()

        signature_sha = base64.b64encode(signature_sha).decode('utf-8')

        authorization_origin = \
            f'api_key="{self.spark_api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')

        v = {
            "authorization": authorization,
            "date": date,
            "host": host
        }

        url = url + '?' + urlencode(v)
        return url

    def check_auth(self):
        self.text_to_speech(_('Hello'))

    def text_to_speech(self, text):
        text = _remove_empty_lines(text)

        async def handle():
            try:
                async with websockets.connect(self.create_url(), max_size=1000000000, ssl=ssl_context) as ws:
                    await self.send(ws, text)
                    return await self.handle_message(ws)
            except websockets.exceptions.InvalidStatus as e:
                if e.response.status_code == 401:
                    raise Exception(
                        _("Authentication failed (HTTP 401). Please check: "
                          "1) API URL is correct for TTS service; "
                          "2) APP ID, API Key, and API Secret are correct; "
                          "3) Your iFlytek account has TTS service enabled.")
                    )
                else:
                    raise Exception(f"WebSocket connection failed: HTTP {e.response.status_code}")
            except Exception as e:
                if "Authentication failed" in str(e):
                    raise
                raise Exception(f"iFlytek TTS service error: {str(e)}")

        return asyncio.run(handle())

    @staticmethod
    async def handle_message(ws):
        audio_bytes: bytes = b''
        while True:
            res = await ws.recv()
            message = json.loads(res)

            if "header" in message and "code" in message["header"]:
                code = message["header"]["code"]
                sid = message["header"].get("sid", "unknown")

                if code != 0:
                    errMsg = message["header"].get("message", "Unknown error")
                    raise Exception(f"sid: {sid} call error: {errMsg} code is: {code}")

                if "payload" in message and "audio" in message["payload"]:
                    audio = base64.b64decode(message["payload"]["audio"]["audio"])
                    audio_bytes += audio

                    if message["payload"]["audio"].get("status") == 2:
                        break
            else:
                raise Exception(
                    f"Unexpected response from iFlytek API. Response: {json.dumps(message, ensure_ascii=False)}"
                )

        return audio_bytes

    async def send(self, ws, text):
        vcn_value = self.params.get("vcn", "x5_lingxiaoxuan_flow")

        # 确保 vcn 值符合超拟人格式
        if not vcn_value or not (str(vcn_value).startswith('x5_') or str(vcn_value).startswith('x6_')):
            vcn_value = 'x5_lingxiaoxuan_flow'

        audio_params = {
            "encoding": self.params.get("encoding", "lame"),
            "sample_rate": self.params.get("sample_rate", 24000),
            "channels": self.params.get("channels", 1),
            "bit_depth": self.params.get("bit_depth", 16),
            "frame_size": self.params.get("frame_size", 0)
        }

        tts_params = {
            "vcn": vcn_value,
            "audio": audio_params,
            "volume": self.params.get("volume", 50),
            "speed": self.params.get("speed", 50),
            "pitch": self.params.get("pitch", 50)
        }

        encoded_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        payload_text_obj = {
            "encoding": "utf8",
            "compress": "raw",
            "format": "plain",
            "status": 2,
            "seq": 0,
            "text": encoded_text
        }

        d = {
            "header": {"app_id": self.spark_app_id, "status": 2},
            "parameter": {"tts": tts_params},
            "payload": {"text": payload_text_obj}
        }

        await ws.send(json.dumps(d))