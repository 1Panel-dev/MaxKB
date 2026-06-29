# coding=utf-8

"""
requires Python 3.6 or later

pip install asyncio
pip install websockets
"""

import base64
import json
import os
import time
import uuid
import requests
import uuid_utils.compat as uuid

from typing import Dict

from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_stt import BaseSpeechToText

audio_format = "mp3"  # wav 或者 mp3，根据实际音频格式设置


def determine_api_mode(url):
    """
    根据URL判断API模式
    """
    if "/recognize/flash" in url:
        return "sync"
    elif "/submit" in url:
        return "async_submit"
    elif "/query" in url:
        return "async_query"
    else:
        return "unknown"


class VolcanicASRClient:
    def __init__(self, appid, token):
        self.appid = appid
        self.token = token

    def _build_headers(self, url, task_id=None, x_tt_logid=None):
        """根据URL构建请求头"""
        mode = determine_api_mode(url)

        headers = {
            "X-Api-App-Key": self.appid,
            "X-Api-Access-Key": self.token,
        }

        if mode == "sync":
            headers.update(
                {
                    "X-Api-Resource-Id": "volc.bigasr.auc_turbo",
                    "X-Api-Request-Id": str(uuid.uuid4()),
                    "X-Api-Sequence": "-1",
                }
            )
        elif mode == "async_submit":
            headers.update(
                {
                    "X-Api-Resource-Id": "volc.bigasr.auc",
                    "X-Api-Request-Id": task_id or str(uuid.uuid4()),
                    "X-Api-Sequence": "-1",
                }
            )
        elif mode == "async_query":
            headers.update(
                {
                    "X-Api-Resource-Id": "volc.bigasr.auc",
                    "X-Api-Request-Id": task_id or str(uuid.uuid4()),
                    "X-Tt-Logid": x_tt_logid or "",
                }
            )

        return headers

    def _create_request_body(self, audio_data, mode="sync"):
        """创建请求体"""
        base_request = {
            "user": {"uid": self.appid if mode == "sync" else "fake_uid"},
            "audio": audio_data,
        }

        if mode == "sync":
            base_request["request"] = {
                "model_name": "bigmodel",
                "enable_itn": True,
                "enable_punc": True,
                "enable_ddc": True,
            }
        else:  # async
            base_request["request"] = {
                "model_name": "bigmodel",
                "enable_channel_split": True,
                "enable_ddc": True,
                "enable_speaker_info": True,
                "enable_punc": True,
                "enable_itn": True,
                "corpus": {"correct_table_name": "", "context": ""},
            }

        return base_request

    def process_audio(self, audio_file=None, submit_url=None):
        """
        根据submit_url自动选择处理模式
        """
        # 获取音频数据
        base64_audio = base64.b64encode(audio_file.read()).decode("utf-8")
        audio_data = {"data": base64_audio}

        # 根据URL判断API模式
        mode = determine_api_mode(submit_url)

        if mode == "sync":
            return self._sync_recognize(audio_data, submit_url)
        elif mode == "async_submit":
            return self._async_process(audio_data, submit_url)
        else:
            raise ValueError(f"Unsupported URL pattern: {submit_url}")

    def _get_audio_data(self, audio_file):
        """构建音频数据对象"""
        base64_audio = base64.b64encode(audio_file.read()).decode("utf-8")
        return {"data": base64_audio}

    def _sync_recognize(self, audio_data, submit_url):
        """同步识别模式"""
        headers = self._build_headers(submit_url)
        request_body = self._create_request_body(audio_data, mode="sync")

        response = requests.post(submit_url, json=request_body, headers=headers)
        return self._handle_response(response, "sync_recognize")

    def _async_process(self, audio_data, submit_url):
        """异步处理模式"""
        # 提交任务
        task_id = str(uuid.uuid4())
        headers = self._build_headers(submit_url, task_id=task_id)
        request_body = self._create_request_body(audio_data, mode="async")

        submit_response = requests.post(submit_url, data=json.dumps(request_body), headers=headers)

        if submit_response.headers.get("X-Api-Status-Code") == "20000000":
            x_tt_logid = submit_response.headers.get("X-Tt-Logid", "")
            # 查询结果
            return self._poll_for_result(task_id, x_tt_logid)
        else:
            print(f"Submit task failed: {submit_response.headers}")
            return None

    def _poll_for_result(self, task_id, x_tt_logid):
        """轮询查询异步任务结果"""
        query_url = "https://openspeech-direct.zijieapi.com/api/v3/auc/bigmodel/query"

        while True:
            query_response = self._query_task(task_id, x_tt_logid, query_url)
            code = query_response.headers.get("X-Api-Status-Code", "")

            if code == "20000000":  # 任务完成
                return query_response
            elif code != "20000001" and code != "20000002":  # 任务失败
                print(f"Async task failed with code: {code}")
                return None
            time.sleep(1)

    def _query_task(self, task_id, x_tt_logid, query_url):
        """执行单次查询请求"""
        headers = self._build_headers(query_url, task_id=task_id, x_tt_logid=x_tt_logid)
        response = requests.post(query_url, json.dumps({}), headers=headers)
        return self._handle_response(response, "async_query", silent=True)

    def _handle_response(self, response, operation, silent=False):
        """处理响应"""
        if "X-Api-Status-Code" in response.headers:
            if not silent:
                print(f"{operation} response header X-Api-Status-Code: {response.headers['X-Api-Status-Code']}")
                print(f"{operation} response header X-Api-Message: {response.headers['X-Api-Message']}")
                print(f"{operation} response header X-Tt-Logid: {response.headers['X-Tt-Logid']}")

                if operation == "sync_recognize":
                    print(f"sync response content: {response.json()}\n")

            return response
        else:
            print(f"{operation} failed: {response.headers}\n")
            return None


class VolcanicEngineBigModelSpeechToText(MaxKBBaseModel, BaseSpeechToText):
    volcanic_app_id: str
    volcanic_api_url: str
    volcanic_token: str
    params: dict

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.volcanic_api_url = kwargs.get("volcanic_api_url")
        self.volcanic_token = kwargs.get("volcanic_token")
        self.volcanic_app_id = kwargs.get("volcanic_app_id")
        self.params = kwargs.get("params")

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {}
        if "max_tokens" in model_kwargs and model_kwargs["max_tokens"] is not None:
            optional_params["max_tokens"] = model_kwargs["max_tokens"]
        if "temperature" in model_kwargs and model_kwargs["temperature"] is not None:
            optional_params["temperature"] = model_kwargs["temperature"]
        return VolcanicEngineBigModelSpeechToText(
            volcanic_api_url=model_credential.get("volcanic_api_url"),
            volcanic_token=model_credential.get("volcanic_token"),
            volcanic_app_id=model_credential.get("volcanic_app_id"),
            params=model_kwargs,
        )

    def check_auth(self):
        cwd = os.path.dirname(os.path.abspath(__file__))
        with open(f"{cwd}/iat_mp3_16k.mp3", "rb") as audio_file:
            self.speech_to_text(audio_file)

    def speech_to_text(self, audio_file):
        try:
            client = VolcanicASRClient(self.volcanic_app_id, self.volcanic_token)
            result = client.process_audio(audio_file, self.volcanic_api_url)
            if result.status_code == 200:
                return result.json().get("result").get("text")
        except Exception as e:
            maxkb_logger.error(f"Error getting speech to text: {e}")
