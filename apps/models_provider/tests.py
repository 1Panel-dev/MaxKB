from io import BytesIO
from unittest.mock import patch

from django.test import SimpleTestCase

from models_provider.impl.vllm_model_provider.model.whisper_sst import VllmWhisperSpeechToText


class VllmWhisperSpeechToTextTest(SimpleTestCase):
    @patch('models_provider.impl.vllm_model_provider.model.whisper_sst.OpenAI')
    def test_normalizes_trailing_slash_in_v1_base_url(self, openai_mock):
        openai_mock.return_value.audio.transcriptions.create.return_value.text = 'transcript'
        model = VllmWhisperSpeechToText(
            api_key='test-key',
            api_url='https://vllm.example/v1/',
            model='whisper',
            params={},
        )

        result = model.speech_to_text(BytesIO(b'audio'))

        openai_mock.assert_called_once_with(
            api_key='test-key',
            base_url='https://vllm.example/v1',
        )
        self.assertEqual(result, 'transcript')
