from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase


class AliyunBaiLianSttTests(SimpleTestCase):
    def test_qwen_file_recognition_preserves_model_params(self):
        from models_provider.impl.aliyun_bai_lian_model_provider.model.stt import AliyunBaiLianAsrSpeechToText

        model = AliyunBaiLianAsrSpeechToText(
            api_key="test-key",
            api_url="https://dashscope.aliyuncs.com/api/v1",
            model="qwen-audio-asr",
            params={"language": "zh"},
        )

        class Response(dict):
            status_code = 200

        message = SimpleNamespace(content=[{"text": "你好"}])
        response = Response(output={"choices": [{"message": message}]})

        with patch("dashscope.MultiModalConversation.call", return_value=response) as call:
            text = model.speech_to_text(BytesIO(b"audio"))

        self.assertEqual(text, "你好")
        self.assertNotIn("format", call.call_args.kwargs)
        self.assertNotIn("sample_rate", call.call_args.kwargs)
        self.assertEqual(call.call_args.kwargs["language"], "zh")

    def test_qwen_audio_31_asr_uses_non_realtime_http_api(self):
        from models_provider.impl.aliyun_bai_lian_model_provider.model.stt import AliyunBaiLianAsrSpeechToText

        model = AliyunBaiLianAsrSpeechToText(
            api_key="test-key",
            api_url="https://dashscope.aliyuncs.com/api/v1",
            model="qwen-audio-3.1-asr-flash",
            params={"language_hints": ["zh"]},
        )
        response = Mock(status_code=200)
        response.json.return_value = {"output": {"text": "你好"}}

        with (
            patch(
                "dashscope.MultiModalConversation.call",
                side_effect=AssertionError("non-realtime ASR must not use MultiModalConversation"),
            ),
            patch("requests.post", return_value=response) as post,
        ):
            text = model.speech_to_text(BytesIO(b"audio"))

        self.assertEqual(text, "你好")
        post.assert_called_once()
        self.assertEqual(
            post.call_args.args[0],
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
        )
        self.assertEqual(
            post.call_args.kwargs["headers"],
            {
                "Authorization": "Bearer test-key",
                "Content-Type": "application/json",
                "X-DashScope-SSE": "disable",
            },
        )
        payload = post.call_args.kwargs["json"]
        self.assertEqual(payload["model"], "qwen-audio-3.1-asr-flash")
        self.assertEqual(payload["parameters"], {"format": "mp3", "sample_rate": "16000", "language_hints": ["zh"]})
        self.assertEqual(
            payload["input"]["messages"],
            [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_audio",
                            "input_audio": {"data": "data:audio/mp3;base64,YXVkaW8="},
                        }
                    ],
                }
            ],
        )
