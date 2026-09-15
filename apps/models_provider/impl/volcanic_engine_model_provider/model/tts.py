# coding=utf-8
"""
单向流式语音合成 HTTP 接口。

接口文档: https://docs.volcengine.com/docs/6561/2528925
"""

import base64
import codecs
import json
from typing import Dict
from uuid import uuid4

import requests
from django.utils.translation import gettext as _

from common.utils.common import _remove_empty_lines
from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_tts import BaseTextToSpeech

DEFAULT_API_URL = "https://openspeech.bytedance.com/api/v3/tts/unidirectional"
DEFAULT_VOICE_TYPE = "zh_female_cancan_mars_bigtts"
DEFAULT_FORMAT = "mp3"
DEFAULT_SAMPLE_RATE = 24000

# audio_params 中仅在用户显式设置时才透传的字段
OPTIONAL_AUDIO_PARAM_KEYS = ("bit_rate",)

# 音频发送完毕后服务端返回该结束码，属于正常结束
STREAM_END_CODE = 20000000

REQUEST_TIMEOUT = (10, 600)


class VolcanicEngineTextToSpeech(MaxKBBaseModel, BaseTextToSpeech):
    api_url: str
    api_key: str
    model_name: str
    params: dict

    def __init__(self, **kwargs):
        kwargs["api_url"] = kwargs.get("api_url") or DEFAULT_API_URL
        kwargs["params"] = kwargs.get("params") or {}
        super().__init__(**kwargs)
        self.api_url = kwargs.get("api_url")
        self.api_key = kwargs.get("api_key")
        self.model_name = kwargs.get("model_name")
        self.params = kwargs.get("params")

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {
            "params": {
                "voice_type": DEFAULT_VOICE_TYPE,
                "format": DEFAULT_FORMAT,
                "sample_rate": DEFAULT_SAMPLE_RATE,
                "speech_rate": 0,
                "loudness_rate": 0,
            }
        }
        for key, value in model_kwargs.items():
            if key not in ["model_id", "use_local", "streaming"]:
                optional_params["params"][key] = value
        return VolcanicEngineTextToSpeech(
            api_url=model_credential.get("api_url"),
            api_key=model_credential.get("api_key"),
            model_name=model_name,
            **optional_params,
        )

    def check_auth(self):
        self.text_to_speech(_("Hello"))

    def _build_audio_params(self) -> dict:
        params = self.params or {}
        audio_params = {
            "format": params.get("format") or DEFAULT_FORMAT,
            "sample_rate": int(params.get("sample_rate") or DEFAULT_SAMPLE_RATE),
            "speech_rate": int(params.get("speech_rate") or 0),
            "loudness_rate": int(params.get("loudness_rate") or 0),
        }
        for key in OPTIONAL_AUDIO_PARAM_KEYS:
            value = params.get(key)
            if value:
                audio_params[key] = int(value)
        return audio_params

    def _build_req_params(self, text: str) -> dict:
        params = self.params or {}
        req_params = {
            "text": text,
            "speaker": params.get("voice_type") or DEFAULT_VOICE_TYPE,
            "audio_params": self._build_audio_params(),
        }
        # 仅当 speaker 为复刻音色时需要指定模型版本
        if params.get("model"):
            req_params["model"] = params["model"]
        return req_params

    def text_to_speech(self, text):
        headers = {
            "X-Api-Key": self.api_key,
            # 模型ID 即接口要求的 resource id（seed-tts-2.0 / seed-icl-2.0）
            "X-Api-Resource-Id": self.model_name,
            "X-Api-Request-Id": str(uuid4()),
            "Content-Type": "application/json",
            "Connection": "keep-alive",
        }
        payload = {"req_params": self._build_req_params(_remove_empty_lines(text))}
        audio = bytearray()
        buffer = ""
        decoder = codecs.getincrementaldecoder("utf-8")()
        with requests.post(
            self.api_url, json=payload, headers=headers, stream=True, timeout=REQUEST_TIMEOUT
        ) as response:
            if response.status_code != 200:
                raise Exception(f"语音合成请求失败: HTTP {response.status_code}, {response.text[:500]}")
            for chunk in response.iter_content(chunk_size=None):
                if not chunk:
                    continue
                buffer += decoder.decode(chunk)
                buffer, finished = self._consume(buffer, audio)
                if finished:
                    break
        if buffer.strip():
            maxkb_logger.warning(f"语音合成响应存在未解析内容: {buffer[:200]}")
        if not audio:
            raise Exception("No audio data received")
        return bytes(audio)

    @staticmethod
    def _consume(content: str, audio: bytearray) -> tuple:
        """解析缓冲区中已完整的 JSON 分片，把 base64 音频累加到 audio。

        返回 (未解析完的剩余内容, 是否已收到结束标记)
        """
        decoder = json.JSONDecoder()
        index = 0
        length = len(content)
        while index < length:
            while index < length and content[index] in " \r\n\t":
                index += 1
            if index >= length:
                break
            try:
                chunk, end = decoder.raw_decode(content, index)
            except ValueError:
                # 分片不完整，等待后续内容
                break
            code = chunk.get("code", 0)
            if code == STREAM_END_CODE:
                return "", True
            if code > 0:
                raise Exception(f"Error code: {code}, message: {chunk.get('message')}")
            data = chunk.get("data")
            if data:
                audio.extend(base64.b64decode(data))
            index = end
        return content[index:], False
