import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


class DummyMaxKBBaseModel:
    def __init__(self, **kwargs):
        pass


class DummyBaseTextToSpeech:
    pass


class FakeWebSocket:
    def __init__(self, messages):
        self.messages = iter(messages)
        self.sent = []

    async def recv(self):
        return next(self.messages)

    async def send(self, message):
        self.sent.append(message)


class FakeWebSocketConnection:
    def __init__(self, websocket):
        self.websocket = websocket

    async def __aenter__(self):
        return self.websocket

    async def __aexit__(self, exc_type, exc_value, traceback):
        return False


def remove_empty_lines(text):
    return "\n".join(line for line in text.splitlines() if line.strip())


def load_tts_module():
    requests_module = types.ModuleType("requests")
    requests_module.post = Mock()
    websockets_module = types.ModuleType("websockets")
    websockets_module.connect = Mock()

    django_module = types.ModuleType("django")
    django_utils_module = types.ModuleType("django.utils")
    translation_module = types.ModuleType("django.utils.translation")
    translation_module.gettext = lambda value: value

    common_module = types.ModuleType("common")
    common_utils_module = types.ModuleType("common.utils")
    common_utils_common_module = types.ModuleType("common.utils.common")
    common_utils_common_module._remove_empty_lines = remove_empty_lines

    models_provider_module = types.ModuleType("models_provider")
    base_model_provider_module = types.ModuleType("models_provider.base_model_provider")
    base_model_provider_module.MaxKBBaseModel = DummyMaxKBBaseModel
    impl_module = types.ModuleType("models_provider.impl")
    base_tts_module = types.ModuleType("models_provider.impl.base_tts")
    base_tts_module.BaseTextToSpeech = DummyBaseTextToSpeech

    modules = {
        "requests": requests_module,
        "websockets": websockets_module,
        "django": django_module,
        "django.utils": django_utils_module,
        "django.utils.translation": translation_module,
        "common": common_module,
        "common.utils": common_utils_module,
        "common.utils.common": common_utils_common_module,
        "models_provider": models_provider_module,
        "models_provider.base_model_provider": base_model_provider_module,
        "models_provider.impl": impl_module,
        "models_provider.impl.base_tts": base_tts_module,
    }

    module_path = Path(__file__).resolve().parents[2] / "apps/models_provider/impl/minimax_model_provider/model/tts.py"
    spec = importlib.util.spec_from_file_location("minimax_tts_under_test", module_path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    return module, requests_module, websockets_module


class MiniMaxTextToSpeechTest(unittest.TestCase):
    def setUp(self):
        self.module, self.requests, self.websockets = load_tts_module()
        self.response = Mock()
        self.response.json.return_value = {"base_resp": {"status_code": 0}}
        self.requests.post.return_value = self.response
        self.model = self.module.MiniMaxTextToSpeech(
            api_key="key",
            api_base="https://api.minimax.io/v1",
            model="speech-test",
            params={
                "voice_setting": {"voice_id": "test-voice"},
                "audio_setting": {"format": "mp3"},
                "language_boost": "English",
                "pronunciation_dict": {"tone": ["test/t e s t"]},
                "voice_modify": {"pitch": 0},
                "output_format": "hex",
                "stream": True,
            },
        )

    def test_new_instance_uses_voice_setting_payload(self):
        model = self.module.MiniMaxTextToSpeech.new_instance(
            "TTS",
            "speech-test",
            {"api_base": "https://api.minimax.io/v1", "api_key": "key"},
        )

        self.assertEqual(model.params["voice_setting"], {"voice_id": "English_Graceful_Lady"})
        self.assertNotIn("voice_id", model.params)

    def test_async_create_posts_supported_fields_and_returns_task_id(self):
        self.response.json.return_value = {
            "task_id": "task-123",
            "base_resp": {"status_code": 0},
        }

        task_id = self.model.text_to_speech_async_create("Hello\n\nworld")

        self.assertEqual(task_id, "task-123")
        request = self.requests.post.call_args
        self.assertEqual(request.args[0], "https://api.minimax.io/v1/t2a_async_v2")
        self.assertEqual(
            request.kwargs["json"],
            {
                "model": "speech-test",
                "text": "Hello\nworld",
                "voice_setting": {"voice_id": "test-voice"},
                "audio_setting": {"format": "mp3"},
                "language_boost": "English",
                "pronunciation_dict": {"tone": ["test/t e s t"]},
                "voice_modify": {"pitch": 0},
            },
        )

    def test_async_query_posts_task_id(self):
        expected = {
            "data": {"status": 2, "audio": "0001"},
            "base_resp": {"status_code": 0},
        }
        self.response.json.return_value = expected

        result = self.model.text_to_speech_async_query("task-123")

        self.assertEqual(result, expected)
        request = self.requests.post.call_args
        self.assertEqual(
            request.args[0],
            "https://api.minimax.io/v1/query/t2a_async_query_v2",
        )
        self.assertEqual(request.kwargs["json"], {"task_id": "task-123"})

    def test_websocket_url_supports_both_regional_api_bases(self):
        endpoints = {
            "https://api.minimax.io/v1": "wss://api.minimax.io/ws/v1/t2a_v2",
            "https://api.minimaxi.com/v1": "wss://api.minimaxi.com/ws/v1/t2a_v2",
        }

        for api_base, expected in endpoints.items():
            with self.subTest(api_base=api_base):
                self.model.api_base = api_base
                self.assertEqual(self.model._websocket_url(), expected)

    def test_websocket_synthesis_combines_audio_frames(self):
        websocket = FakeWebSocket(
            [
                json.dumps({"event": "connected_success", "base_resp": {"status_code": 0}}),
                json.dumps({"event": "task_started", "base_resp": {"status_code": 0}}),
                json.dumps({"event": "task_continued", "data": {"audio": "0001"}, "is_final": False}),
                json.dumps({"event": "task_continued", "data": None, "is_final": False}),
                json.dumps({"event": "task_continued", "data": {"audio": "ff"}, "is_final": True}),
                json.dumps({"event": "task_finished", "base_resp": {"status_code": 0}}),
            ]
        )
        self.websockets.connect.return_value = FakeWebSocketConnection(websocket)

        audio = self.model.text_to_speech_websocket("Hello\n\nworld")

        self.assertEqual(audio, b"\x00\x01\xff")
        self.websockets.connect.assert_called_once_with(
            "wss://api.minimax.io/ws/v1/t2a_v2",
            additional_headers={"Authorization": "Bearer key"},
            ping_interval=None,
            open_timeout=60,
            max_size=None,
        )
        sent_messages = [json.loads(message) for message in websocket.sent]
        self.assertEqual(sent_messages[0]["event"], "task_start")
        self.assertEqual(sent_messages[0]["model"], "speech-test")
        self.assertNotIn("output_format", sent_messages[0])
        self.assertNotIn("stream", sent_messages[0])
        self.assertEqual(
            sent_messages[1],
            {"event": "task_continue", "text": "Hello\nworld"},
        )
        self.assertEqual(sent_messages[2], {"event": "task_finish"})


if __name__ == "__main__":
    unittest.main()
