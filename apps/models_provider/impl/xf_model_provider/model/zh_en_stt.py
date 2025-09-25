import asyncio
import json
import base64
import hmac
import hashlib
import ssl
import traceback
from typing import Dict
from urllib.parse import urlencode
from datetime import datetime, timezone, UTC
import websockets
import os

from future.backports.urllib.parse import urlparse

from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_stt import BaseSpeechToText

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


def deep_merge_dict(target_dict, source_dict):

    if not isinstance(source_dict, dict):
        return source_dict
    result = target_dict.copy() if isinstance(target_dict, dict) else {}
    for key, value in source_dict.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dict(result[key], value)
        else:
            result[key] = value
    return result


class XFZhEnSparkSpeechToText(MaxKBBaseModel, BaseSpeechToText):
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

        return XFZhEnSparkSpeechToText(
            spark_app_id=model_credential.get('spark_app_id'),
            spark_api_key=model_credential.get('spark_api_key'),
            spark_api_secret=model_credential.get('spark_api_secret'),
            spark_api_url=model_credential.get('spark_api_url'),
            params=model_kwargs,
            **model_kwargs
        )

    # 生成url
    def create_url(self):
        url = self.spark_api_url
        host = urlparse(url).hostname

        gmt_format = '%a, %d %b %Y %H:%M:%S GMT'
        date = datetime.now(UTC).strftime(gmt_format)
        # 拼接字符串
        signature_origin = "host: " + host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v1 HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(
            self.spark_api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            hashlib.sha256
        ).digest()
        signature = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = (
            f'api_key="{self.spark_api_key}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{signature}"'
        )
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        params = {
            'authorization': authorization,
            'date': date,
            'host': host
        }
        auth_url = url + '?' + urlencode(params)
        return auth_url

    def check_auth(self):
        cwd = os.path.dirname(os.path.abspath(__file__))
        with open(f'{cwd}/iat_mp3_16k.mp3', 'rb') as f:
            self.speech_to_text(f)

    def speech_to_text(self, audio_file_path):
        async def handle():
            async with websockets.connect(self.create_url(), max_size=1000000000, ssl=ssl_context) as ws:
                # print("连接成功")
                # 发送音频数据
                await self.send_audio(ws, audio_file_path)
                # 接收识别结果
                return await self.handle_message(ws)
        try:
            return asyncio.run(handle())
        except Exception as err:
            maxkb_logger.error(f"语音识别错误: {str(err)}: {traceback.format_exc()}")
            return ""

    def merge_params_to_frame(self, frame,params):

        return deep_merge_dict(frame, params)

    async def send_audio(self, ws, audio_file):
        """发送音频数据"""
        chunk_size = 4000
        seq = 1
        max_chunks = 10000
        while True:
            chunk = audio_file.read(chunk_size)
            if not chunk or seq > max_chunks:
                break

            chunk_base64 = base64.b64encode(chunk).decode('utf-8')
            # 第一帧
            if seq == 1:
                frame = {
                    "header": {"app_id": self.spark_app_id, "status": 0},
                    "parameter": {
                        "iat": {
                            "domain": "slm",
                            "language": "zh_cn",
                            "accent": "mandarin",
                            "eos": 10000,
                            "vinfo": 1,
                            "result": {"encoding": "utf8", "compress": "raw", "format": "json"}
                        }
                    },
                    "payload": {
                        "audio": {
                            "encoding": "lame", "sample_rate": 16000, "channels": 1,
                            "bit_depth": 16, "seq": seq, "status": 0, "audio": chunk_base64
                        }
                    }
                }
                frame = self.merge_params_to_frame(frame,{key: value for key, value in self.params.items() if
                                            not ['model_id', 'use_local', 'streaming'].__contains__(key)})

            # 中间帧
            else:
                frame = {
                    "header": {"app_id": self.spark_app_id, "status": 1},
                    "payload": {
                        "audio": {
                            "encoding": "lame", "sample_rate": 16000, "channels": 1,
                            "bit_depth": 16, "seq": seq, "status": 1, "audio": chunk_base64
                        }
                    }
                }

                frame = self.merge_params_to_frame(frame,{key: value for key, value in self.params.items() if
                                            not ['model_id', 'use_local', 'streaming','parameter'].__contains__(key)})

            await ws.send(json.dumps(frame))
            seq += 1

        # 发送结束帧
        end_frame = {
            "header": {"app_id": self.spark_app_id, "status": 2},
            "payload": {
                "audio": {
                    "encoding": "lame", "sample_rate": 16000, "channels": 1,
                    "bit_depth": 16, "seq": seq, "status": 2, "audio": ""
                }
            }
        }

        end_frame = self.merge_params_to_frame(end_frame,{key: value for key, value in self.params.items() if
                                            not ['model_id', 'use_local', 'streaming','parameter'].__contains__(key)})

        await ws.send(json.dumps(end_frame))

    # 接受信息处理器
    async def handle_message(self, ws):
        result_text = ""
        while True:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=30.0)
                data = json.loads(message)
                if data['header']['code'] != 0:
                    raise Exception("")

                if 'payload' in data and 'result' in data['payload']:
                    result = data['payload']['result']
                    text = result.get('text', '')
                    if text:
                        text_data = json.loads(base64.b64decode(text).decode('utf-8'))
                        for ws_item in text_data.get('ws', []):
                            for cw in ws_item.get('cw', []):
                                for sw in cw.get('sw', []):
                                    result_text += sw['w']

                if data['header'].get('status') == 2:
                    break
            except asyncio.TimeoutError:
                break

        return result_text
