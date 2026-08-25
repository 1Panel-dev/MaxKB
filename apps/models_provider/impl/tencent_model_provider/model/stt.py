import base64
import json
import os
import traceback

import requests
from typing import Dict, Optional

from tencentcloud.asr.v20190614 import asr_client, models
from tencentcloud.common import credential
from tencentcloud.common.exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile

from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_stt import BaseSpeechToText


class TencentSpeechToText(MaxKBBaseModel, BaseSpeechToText):
    hunyuan_secret_id: str
    hunyuan_secret_key: str
    model: str
    params: dict

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hunyuan_secret_id = kwargs.get('hunyuan_secret_id')
        self.hunyuan_secret_key = kwargs.get('hunyuan_secret_key')
        self.model = kwargs.get('model')
        self.params = kwargs.get('params')

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return TencentSpeechToText(
            hunyuan_secret_id=model_credential.get('SecretId'),
            hunyuan_secret_key=model_credential.get('SecretKey'),
            model=model_name,
            params=model_kwargs,
            **model_kwargs
        )

    def check_auth(self):
        cwd = os.path.dirname(os.path.abspath(__file__))
        with open(f'{cwd}/iat_mp3_16k.mp3', 'rb') as f:
            self.speech_to_text(f)

    def speech_to_text(self, audio_file):
        try:
            cred = credential.Credential(self.hunyuan_secret_id, self.hunyuan_secret_key)
            # 实例化一个http选项，可选的，没有特殊需求可以跳过
            httpProfile = HttpProfile()
            httpProfile.endpoint = "asr.tencentcloudapi.com"

            # 实例化一个client选项，可选的，没有特殊需求可以跳过
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            # 实例化要请求产品的client对象,clientProfile是可选的
            client = asr_client.AsrClient(cred, "", clientProfile)
            buf = audio_file.read()
            _v = base64.b64encode(buf)

            # 实例化一个请求对象,每个接口都会对应一个request对象
            req = models.SentenceRecognitionRequest()
            params = {
                "EngSerViceType": self.params.get('EngSerViceType'),
                "SourceType": 1,
                "VoiceFormat": "mp3",
                "Data": _v.decode(),
                **self.params
            }
            req.from_json_string(json.dumps(params))

            # 返回的resp是一个SentenceRecognitionResponse的实例，与请求对象对应
            resp = client.SentenceRecognition(req)
            # 输出json格式的字符串回包
            return resp.Result


        except TencentCloudSDKException as err:
            maxkb_logger.error(f":Error: {str(err)}: {traceback.format_exc()}")
            raise err


DEFAULT_WAND_BASE_URL = 'https://tokenhub.tencentmaas.com/v1/wand/asrproxy/sync_transcribe'


class TencentWandSpeechToText(MaxKBBaseModel, BaseSpeechToText):
    api_key: str
    model: str
    params: dict
    base_url: Optional[str] = DEFAULT_WAND_BASE_URL

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.model = kwargs.get('model')
        self.params = kwargs.get('params') or {}
        self.base_url = kwargs.get('base_url') or DEFAULT_WAND_BASE_URL

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        instance_kwargs = {
            "api_key": model_credential.get('api_key'),
            "model": model_name,
            "params": model_kwargs,
            **model_kwargs,
        }
        base_url = model_credential.get('base_url')
        if base_url:
            instance_kwargs["base_url"] = base_url
        return TencentWandSpeechToText(**instance_kwargs)

    def check_auth(self):
        cwd = os.path.dirname(os.path.abspath(__file__))
        with open(f'{cwd}/iat_mp3_16k.mp3', 'rb') as f:
            self.speech_to_text(f)

    def speech_to_text(self, audio_file):
        try:
            payload = {"model": self.model}
            # 仅使用上传音频文件的 base64 data，不提供 input_url 兜底
            audio_data = audio_file.read()
            payload["data"] = base64.b64encode(audio_data).decode('utf-8')
            for key in ("source", "voice_encode_format"):
                if self.params.get(key):
                    payload[key] = self.params[key]

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=300)
            response.raise_for_status()
            result = response.json()
            if result.get("status") != "completed":
                maxkb_logger.error(f"WAND ASR task not completed: {result}")
                raise Exception(f"WAND ASR task not completed: {result}")
            output = result.get("output") or {}
            text = output.get("text")
            if not text:
                sentences = output.get("sentences") or []
                text = " ".join([s.get('text', '') for s in sentences if s.get('text')])
            return text
        except Exception as e:
            maxkb_logger.error(f"WAND ASR Error: {str(e)}: {traceback.format_exc()}")
            raise e
