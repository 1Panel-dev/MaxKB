import base64
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.conf import settings


class AliyunBaiLianTtsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not settings.configured:
            settings.configure(USE_I18N=False)

    def test_qwen_tts_reports_dashscope_error_instead_of_missing_output(self):
        from models_provider.impl.aliyun_bai_lian_model_provider.model.tts import AliyunBaiLianTextToSpeech

        model = AliyunBaiLianTextToSpeech(
            api_key="invalid-key",
            base_url="https://dashscope.aliyuncs.com/api/v1",
            model="qwen3-tts-flash",
            params={},
        )
        response = SimpleNamespace(
            status_code=401,
            code="InvalidApiKey",
            message="Invalid API-key provided.",
            output=None,
        )

        with patch("dashscope.MultiModalConversation.call", return_value=response):
            with self.assertRaisesRegex(
                Exception,
                r"status_code: 401, code: InvalidApiKey, message: Invalid API-key provided\.",
            ):
                model.text_to_speech("Hello")

    def test_qwen_realtime_tts_returns_collected_audio(self):
        from models_provider.impl.aliyun_bai_lian_model_provider.model.tts import AliyunBaiLianTextToSpeech

        model = AliyunBaiLianTextToSpeech(
            api_key="test-key",
            base_url="https://dashscope-intl.aliyuncs.com/api/v1",
            model="qwen3-tts-flash-realtime",
            params={"voice": "Cherry", "speech_rate": 1},
        )
        state = {}

        class FakeQwenTtsRealtime:
            def __init__(self, model, callback, url):
                state.update(model=model, callback=callback, url=url)

            def connect(self):
                state["connected"] = True

            def update_session(self, **kwargs):
                state["session"] = kwargs

            def append_text(self, text):
                state["text"] = text

            def commit(self):
                state["committed"] = True

            def finish(self):
                state["finished"] = True
                callback = state["callback"]
                callback.on_event(
                    {
                        "type": "response.audio.delta",
                        "delta": base64.b64encode(b"ID3-test-audio").decode(),
                    }
                )
                callback.on_event({"type": "response.done"})
                callback.on_event({"type": "session.finished"})

            def close(self):
                state["closed"] = True

        with (
            patch("dashscope.audio.qwen_tts_realtime.QwenTtsRealtime", FakeQwenTtsRealtime),
            patch("dashscope.MultiModalConversation.call", side_effect=AssertionError("HTTP TTS should not be used")),
        ):
            audio = model.text_to_speech("Hello")

        self.assertEqual(audio, b"ID3-test-audio")
        self.assertEqual(state["url"], "wss://dashscope-intl.aliyuncs.com/api-ws/v1/realtime")
        self.assertEqual(state["session"]["mode"], "commit")
        self.assertEqual(state["session"]["voice"], "Cherry")
        self.assertEqual(state["session"]["audio_format"], "mp3")
        self.assertEqual(state["text"], "Hello")
        self.assertTrue(state["committed"])
        self.assertTrue(state["finished"])
        self.assertTrue(state["closed"])

    def test_qwen_audio_tts_uses_audio_generation_endpoint(self):
        from models_provider.impl.aliyun_bai_lian_model_provider.model.tts import AliyunBaiLianTextToSpeech

        model = AliyunBaiLianTextToSpeech(
            api_key="test-key",
            base_url="https://workspace.cn-beijing.maas.aliyuncs.com/api/v1",
            model="qwen-audio-3.1-tts-next",
            params={"voice": "Cherry", "speech_rate": 0.8, "format": "mp3"},
        )
        response = Mock(status_code=200)
        response.json.return_value = {"output": {"audio": {"url": "https://example.com/audio.mp3"}}}
        download = Mock(content=b"ID3-qwen-audio")

        with (
            patch("requests.post", return_value=response) as post,
            patch("requests.get", return_value=download) as get,
            patch("dashscope.MultiModalConversation.call", side_effect=AssertionError("wrong endpoint")),
        ):
            audio = model.text_to_speech("Hello")

        self.assertEqual(audio, b"ID3-qwen-audio")
        post.assert_called_once_with(
            "https://workspace.cn-beijing.maas.aliyuncs.com/api/v1/services/audio/tts/SpeechSynthesizer",
            headers={"Authorization": "Bearer test-key", "Content-Type": "application/json"},
            json={
                "model": "qwen-audio-3.1-tts-next",
                "input": {"text_prompt": "Hello", "rate": 0.8, "format": "mp3"},
            },
            timeout=300,
        )
        get.assert_called_once_with("https://example.com/audio.mp3", timeout=30)

    def test_qwen_audio_tts_plus_uses_text_and_voice(self):
        from models_provider.impl.aliyun_bai_lian_model_provider.model.tts import AliyunBaiLianTextToSpeech

        model = AliyunBaiLianTextToSpeech(
            api_key="test-key",
            base_url="https://workspace.cn-beijing.maas.aliyuncs.com/api/v1",
            model="qwen-audio-3.1-tts-plus",
            params={"voice": "longanhuan_v3.1", "format": "wav", "sample_rate": 24000},
        )
        response = Mock(status_code=200)
        response.json.return_value = {"output": {"audio": {"url": "https://example.com/audio.wav"}}}
        download = Mock(content=b"RIFF-qwen-audio")

        with (
            patch("requests.post", return_value=response) as post,
            patch("requests.get", return_value=download),
            patch("dashscope.MultiModalConversation.call", side_effect=AssertionError("wrong endpoint")),
        ):
            audio = model.text_to_speech("Hello")

        self.assertEqual(audio, b"RIFF-qwen-audio")
        post.assert_called_once_with(
            "https://workspace.cn-beijing.maas.aliyuncs.com/api/v1/services/audio/tts/SpeechSynthesizer",
            headers={"Authorization": "Bearer test-key", "Content-Type": "application/json"},
            json={
                "model": "qwen-audio-3.1-tts-plus",
                "input": {
                    "text": "Hello",
                    "voice": "longanhuan_v3.1",
                    "format": "wav",
                    "sample_rate": 24000,
                },
            },
            timeout=300,
        )

    def test_qwen_audio_tts_next_check_auth_uses_audio_generation_prompt(self):
        from models_provider.impl.aliyun_bai_lian_model_provider.model.tts import AliyunBaiLianTextToSpeech

        model = AliyunBaiLianTextToSpeech(
            api_key="test-key",
            base_url="https://workspace.cn-beijing.maas.aliyuncs.com/api/v1",
            model="qwen-audio-3.1-tts-next",
            params={},
        )

        with patch.object(AliyunBaiLianTextToSpeech, "text_to_speech") as text_to_speech:
            model.check_auth()

        text_to_speech.assert_called_once_with("一位女性清晰地说：“你好，欢迎使用。”")

    def test_qwen_audio_tts_next_params_omit_unused_voice(self):
        from models_provider.impl.aliyun_bai_lian_model_provider.credential.tts import AliyunBaiLianTTSModelCredential

        form = AliyunBaiLianTTSModelCredential().get_model_params_setting_form("qwen-audio-3.1-tts-next")

        self.assertEqual(form.get_default_form_data(), {"speech_rate": 1})

    def test_qwen_audio_tts_plus_uses_matching_default_voice(self):
        from models_provider.impl.aliyun_bai_lian_model_provider.credential.tts import AliyunBaiLianTTSModelCredential

        form = AliyunBaiLianTTSModelCredential().get_model_params_setting_form("qwen-audio-3.1-tts-plus")

        self.assertEqual(form.get_default_form_data(), {"voice": "longanhuan_v3.1", "speech_rate": 1})

    def test_qwen_realtime_tts_reports_server_error_event(self):
        from models_provider.impl.aliyun_bai_lian_model_provider.model.tts import AliyunBaiLianTextToSpeech

        model = AliyunBaiLianTextToSpeech(
            api_key="invalid-key",
            base_url="https://dashscope.aliyuncs.com/api/v1",
            model="qwen3-tts-flash-realtime",
            params={},
        )

        class FakeQwenTtsRealtime:
            def __init__(self, model, callback, url):
                self.callback = callback

            def connect(self):
                pass

            def update_session(self, **kwargs):
                pass

            def append_text(self, text):
                pass

            def commit(self):
                pass

            def finish(self):
                self.callback.on_event(
                    {
                        "type": "error",
                        "error": {"code": "InvalidApiKey", "message": "Invalid API-key provided."},
                    }
                )

            def close(self):
                pass

        with (
            patch("dashscope.audio.qwen_tts_realtime.QwenTtsRealtime", FakeQwenTtsRealtime),
            patch("dashscope.MultiModalConversation.call", side_effect=AssertionError("HTTP TTS should not be used")),
        ):
            with self.assertRaisesRegex(
                Exception,
                r"code: InvalidApiKey, message: Invalid API-key provided\.",
            ):
                model.text_to_speech("Hello")


if __name__ == "__main__":
    unittest.main()
