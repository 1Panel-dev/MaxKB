# coding=utf-8
import asyncio
import json
from typing import Dict
from urllib.parse import urlsplit, urlunsplit

import requests
import websockets

from django.utils.translation import gettext as _

from common.utils.common import _remove_empty_lines
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_tts import BaseTextToSpeech


class MiniMaxTextToSpeech(MaxKBBaseModel, BaseTextToSpeech):
    ASYNC_REQUEST_FIELDS = {
        "voice_setting",
        "audio_setting",
        "language_boost",
        "pronunciation_dict",
        "voice_modify",
    }
    WEBSOCKET_REQUEST_FIELDS = {
        "voice_setting",
        "audio_setting",
        "language_boost",
        "pronunciation_dict",
    }

    api_base: str
    api_key: str
    model: str
    params: dict

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get("api_key")
        self.api_base = kwargs.get("api_base")
        self.model = kwargs.get("model")
        self.params = kwargs.get("params") or {}

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {"params": {"voice_setting": {"voice_id": "English_Graceful_Lady"}}}
        for key, value in model_kwargs.items():
            if key not in ["model_id", "use_local", "streaming"]:
                optional_params["params"][key] = value
        return MiniMaxTextToSpeech(
            model=model_name,
            api_base=model_credential.get("api_base") or "https://api.minimaxi.com/v1",
            api_key=model_credential.get("api_key"),
            **optional_params,
        )

    def check_auth(self):
        self.text_to_speech(_("Hello"))

    @staticmethod
    def _raise_api_error(result):
        base_response = result.get("base_resp", {})
        if base_response.get("status_code", 0) != 0:
            error_message = base_response.get("status_msg", "Unknown error")
            raise Exception(f"MiniMax TTS API error: {error_message}")

    def _post_tts_operation(self, path, payload):
        response = requests.post(
            f"{self.api_base.rstrip('/')}/{path.lstrip('/')}",
            json=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=60,
        )
        response.raise_for_status()

        result = response.json()
        self._raise_api_error(result)
        return result

    def _synthesis_params(self, overrides=None):
        params = {**self.params, **(overrides or {})}
        params.setdefault("audio_setting", {"format": "mp3"})
        return params

    def _filtered_synthesis_params(self, allowed_fields, overrides=None):
        return {key: value for key, value in self._synthesis_params(overrides).items() if key in allowed_fields}

    @staticmethod
    def _decode_audio(result):
        audio_hex = result.get("data", {}).get("audio", "")
        if not audio_hex:
            raise Exception("MiniMax TTS API returned empty audio data")
        try:
            return bytes.fromhex(audio_hex)
        except ValueError as error:
            raise Exception("MiniMax TTS API returned invalid audio data") from error

    def text_to_speech_async_create(self, text, **params):
        result = self._post_tts_operation(
            "t2a_async_v2",
            {
                "model": self.model,
                "text": _remove_empty_lines(text),
                **self._filtered_synthesis_params(self.ASYNC_REQUEST_FIELDS, params),
            },
        )
        task_id = result.get("task_id") or result.get("data", {}).get("task_id")
        if not task_id:
            raise Exception("MiniMax TTS async create returned no task ID")
        return task_id

    def text_to_speech_async_query(self, task_id):
        return self._post_tts_operation(
            "query/t2a_async_query_v2",
            {"task_id": task_id},
        )

    def _websocket_url(self):
        parsed_url = urlsplit(self.api_base.rstrip("/"))
        if parsed_url.scheme in {"https", "wss"}:
            websocket_scheme = "wss"
        elif parsed_url.scheme in {"http", "ws"}:
            websocket_scheme = "ws"
        else:
            raise ValueError("MiniMax TTS API URL must use HTTP or HTTPS")

        path_prefix = parsed_url.path.rstrip("/")
        if path_prefix.endswith("/v1"):
            path_prefix = path_prefix[:-3]
        websocket_path = f"{path_prefix}/ws/v1/t2a_v2"
        return urlunsplit((websocket_scheme, parsed_url.netloc, websocket_path, "", ""))

    @classmethod
    def _load_websocket_message(cls, message):
        result = json.loads(message)
        if not isinstance(result, dict):
            raise Exception("MiniMax TTS WebSocket returned an invalid message")
        cls._raise_api_error(result)
        return result

    def text_to_speech_websocket(self, text, **params):
        text = _remove_empty_lines(text)

        async def handle():
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with websockets.connect(
                self._websocket_url(),
                additional_headers=headers,
                ping_interval=None,
                open_timeout=60,
                max_size=None,
            ) as websocket:
                connected = self._load_websocket_message(await websocket.recv())
                if connected.get("event") != "connected_success":
                    raise Exception("MiniMax TTS WebSocket connection was not acknowledged")

                await websocket.send(
                    json.dumps(
                        {
                            "event": "task_start",
                            "model": self.model,
                            **self._filtered_synthesis_params(self.WEBSOCKET_REQUEST_FIELDS, params),
                        }
                    )
                )
                started = self._load_websocket_message(await websocket.recv())
                if started.get("event") != "task_started":
                    raise Exception("MiniMax TTS WebSocket task was not started")

                await websocket.send(
                    json.dumps(
                        {
                            "event": "task_continue",
                            "text": text,
                        }
                    )
                )

                audio = bytearray()
                while True:
                    result = self._load_websocket_message(await websocket.recv())
                    event = result.get("event")
                    if event == "task_result":
                        audio_hex = result.get("data", {}).get("audio", "")
                        if audio_hex:
                            try:
                                audio.extend(bytes.fromhex(audio_hex))
                            except ValueError as error:
                                raise Exception("MiniMax TTS WebSocket returned invalid audio data") from error
                    elif event == "task_finished":
                        break
                    else:
                        raise Exception(f"MiniMax TTS WebSocket returned unexpected event: {event}")

                if not audio:
                    raise Exception("MiniMax TTS WebSocket returned empty audio data")
                return bytes(audio)

        return asyncio.run(handle())

    def text_to_speech(self, text):
        result = self._post_tts_operation(
            "t2a_v2",
            {
                "model": self.model,
                "text": _remove_empty_lines(text),
                **self._synthesis_params(),
                "stream": False,
            },
        )
        return self._decode_audio(result)
