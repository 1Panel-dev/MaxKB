import base64
import threading
from http import HTTPStatus
from typing import Dict
from urllib.parse import urlsplit, urlunsplit

import dashscope

from django.utils.translation import gettext as _

from common.utils.common import _remove_empty_lines
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_tts import BaseTextToSpeech


class _QwenTtsRealtimeCallback:
    def __init__(self):
        self.audio_chunks = []
        self.error = None
        self.finished = threading.Event()

    def on_open(self):
        pass

    def on_event(self, event):
        event_type = event.get("type")
        if event_type == "response.audio.delta":
            try:
                self.audio_chunks.append(base64.b64decode(event["delta"]))
            except (KeyError, ValueError) as e:
                self.error = "Failed to decode realtime TTS audio: %s" % e
                self.finished.set()
        elif event_type == "error":
            error = event.get("error") or {}
            self.error = "code: %s, message: %s" % (error.get("code"), error.get("message"))
            self.finished.set()
        elif event_type == "session.finished":
            self.finished.set()

    def on_close(self, close_status_code, close_msg):
        if close_status_code not in (None, 1000, 1001) and self.error is None:
            self.error = "WebSocket closed, status_code: %s, message: %s" % (close_status_code, close_msg)
        self.finished.set()


class AliyunBaiLianTextToSpeech(MaxKBBaseModel, BaseTextToSpeech):
    api_key: str
    base_url: str
    model: str
    params: dict

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get("api_key")
        self.base_url = kwargs.get("base_url")
        self.model = kwargs.get("model")
        self.params = kwargs.get("params")

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {"params": {}}
        for key, value in model_kwargs.items():
            if key not in ["model_id", "use_local", "streaming"]:
                optional_params["params"][key] = value

        return AliyunBaiLianTextToSpeech(
            model=model_name,
            api_key=model_credential.get("api_key"),
            base_url=model_credential.get("api_base", "https://dashscope.aliyuncs.com/api/v1"),
            **optional_params,
        )

    def check_auth(self):
        if "qwen-audio" in self.model and "tts-next" in self.model:
            self.text_to_speech("一位女性清晰地说：“你好，欢迎使用。”")
        else:
            self.text_to_speech(_("Hello"))

    def _get_qwen_realtime_url(self):
        parsed_url = urlsplit(self.base_url)
        scheme = "wss" if parsed_url.scheme == "https" else "ws"
        return urlunsplit((scheme, parsed_url.netloc, "/api-ws/v1/realtime", "", ""))

    def _text_to_speech_qwen_realtime(self, text):
        from dashscope.audio.qwen_tts_realtime import QwenTtsRealtime

        params = dict(self.params or {})
        voice = params.pop("voice", "Cherry")
        sample_rate = int(params.pop("sample_rate", 24000))
        params.pop("audio_format", None)
        params.pop("response_format", None)

        callback = _QwenTtsRealtimeCallback()
        synthesizer = QwenTtsRealtime(
            model=self.model,
            callback=callback,
            url=self._get_qwen_realtime_url(),
        )
        try:
            synthesizer.connect()
            synthesizer.update_session(
                voice=voice,
                mode="commit",
                audio_format="mp3",
                sample_rate=sample_rate,
                **params,
            )
            synthesizer.append_text(text)
            synthesizer.commit()
            synthesizer.finish()
            if not callback.finished.wait(timeout=30):
                raise TimeoutError("Qwen realtime TTS timed out after 30 seconds")
            if callback.error:
                raise Exception("Qwen realtime TTS request failed, %s" % callback.error)
            audio = b"".join(callback.audio_chunks)
            if not audio:
                raise Exception("Qwen realtime TTS returned no audio")
            return audio
        finally:
            synthesizer.close()

    def _text_to_speech_qwen_audio(self, text):
        import requests

        params = dict(self.params or {})
        if "speech_rate" in params and "rate" not in params:
            params["rate"] = params.pop("speech_rate")

        if "tts-next" in self.model:
            params.pop("voice", None)
            payload_input = {"text_prompt": text, **params}
        else:
            payload_input = {"text": text, **params}

        response = requests.post(
            f"{self.base_url.rstrip('/')}/services/audio/tts/SpeechSynthesizer",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={"model": self.model, "input": payload_input},
            timeout=300,
        )
        if response.status_code != HTTPStatus.OK:
            error = response.json()
            raise Exception(
                "Qwen Audio TTS request failed, status_code: %s, code: %s, message: %s"
                % (response.status_code, error.get("code"), error.get("message"))
            )

        audio_url = ((response.json().get("output") or {}).get("audio") or {}).get("url")
        if not audio_url:
            raise Exception("Qwen Audio TTS response does not contain an audio URL")
        audio = requests.get(audio_url, timeout=30)
        audio.raise_for_status()
        return audio.content

    def text_to_speech(self, text):
        audio = None
        dashscope.api_key = self.api_key
        dashscope.base_http_api_url = self.base_url
        text = _remove_empty_lines(text)
        if "sambert" in self.model:
            from dashscope.audio.tts import SpeechSynthesizer

            audio = SpeechSynthesizer.call(model=self.model, text=text, **self.params).get_audio_data()
        elif "qwen" in self.model and "realtime" in self.model:
            audio = self._text_to_speech_qwen_realtime(text)
        elif "qwen-audio" in self.model and "tts" in self.model:
            audio = self._text_to_speech_qwen_audio(text)
        elif "qwen" in self.model:
            import requests

            response = dashscope.MultiModalConversation.call(
                # 如需使用指令控制功能，请将model替换为qwen3-tts-instruct-flash
                model=self.model,
                api_key=self.api_key,
                text=text,
                **self.params,
            )
            if response.status_code != HTTPStatus.OK:
                raise Exception(
                    "Qwen TTS request failed, status_code: %s, code: %s, message: %s"
                    % (response.status_code, response.code, response.message)
                )
            # 这个的接口返回格式和上面两个不太一样，直接返回了一个url地址，下载后就是音频文件
            audio_url = response.output.audio.url
            res = requests.get(audio_url, timeout=30)
            res.raise_for_status()
            audio = res.content
        elif "MiniMax" in self.model:
            import requests

            api_url = f"{self.base_url}/services/aigc/multimodal-generation/generation"
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {"model": self.model, "input": {"text": text, **self.params}}
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            audio_hex = response.json().get("output", {}).get("data", {}).get("audio")
            if audio_hex:
                audio = bytes.fromhex(audio_hex)
            else:
                raise Exception("Failed to get audio data from response" + str(response.text))
        else:
            from dashscope.audio.tts_v2 import SpeechSynthesizer

            synthesizer = SpeechSynthesizer(model=self.model, **self.params)
            audio = synthesizer.call(text)
        if audio is None:
            raise Exception("Failed to generate audio")
        if isinstance(audio, str):
            raise Exception(audio)
        return audio
