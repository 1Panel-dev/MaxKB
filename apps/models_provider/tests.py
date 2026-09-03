from io import BytesIO
from unittest.mock import patch

from django.test import SimpleTestCase

from models_provider.impl.aimlapi_model_provider.const import ATTRIBUTION_HEADERS, get_default_headers
from models_provider.impl.aimlapi_model_provider.model.llm import AIMLAPIChatModel
from models_provider.impl.aimlapi_model_provider.model.tti import AIMLAPITextToImage
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


class AIMLAPIAttributionTest(SimpleTestCase):
    """AI/ML API 渠道归因请求头：格式错误的 partner id 不会报错，只会静默丢失归因，所以必须有测试"""

    credential = {'api_key': 'test-key', 'api_base': 'https://api.aimlapi.com/v1'}

    def test_partner_id_matches_gateway_pattern(self):
        self.assertRegex(ATTRIBUTION_HEADERS['X-AIMLAPI-Partner-ID'], r'^part_[A-Za-z0-9]{1,64}$')
        self.assertRegex(ATTRIBUTION_HEADERS['X-AIMLAPI-Source'], r'^(web|agent|mcp)/[a-z0-9-]{1,32}$')

    def test_headers_are_only_sent_to_aimlapi(self):
        headers = get_default_headers('https://api.aimlapi.com/v1')
        self.assertEqual(sorted(headers), ['HTTP-Referer', 'X-AIMLAPI-Partner-ID', 'X-AIMLAPI-Source', 'X-Title'])
        # API URL 指向其他服务商或中转代理时不带归因请求头
        for api_base in ['https://api.openai.com/v1', 'https://aimlapi.com.example.com/v1', 'http://127.0.0.1:8000/v1']:
            self.assertEqual(get_default_headers(api_base), {}, api_base)

    def test_caller_headers_win_and_constant_is_not_mutated(self):
        headers = get_default_headers('https://api.aimlapi.com/v1', {'X-Title': 'Custom', 'X-Extra': '1'})
        self.assertEqual(headers['X-Title'], 'Custom')
        self.assertEqual(headers['X-Extra'], '1')
        self.assertEqual(headers['X-AIMLAPI-Partner-ID'], ATTRIBUTION_HEADERS['X-AIMLAPI-Partner-ID'])
        self.assertEqual(ATTRIBUTION_HEADERS['X-Title'], 'MaxKB')
        self.assertNotIn('X-Extra', ATTRIBUTION_HEADERS)

    def test_chat_model_sends_attribution_headers(self):
        model = AIMLAPIChatModel.new_instance('LLM', 'openai/gpt-4o-mini', self.credential)
        self.assertEqual(model.default_headers['X-AIMLAPI-Partner-ID'],
                         ATTRIBUTION_HEADERS['X-AIMLAPI-Partner-ID'])

    def test_chat_model_omits_unset_params_instead_of_sending_null(self):
        # AI/ML API 上部分模型（openai/gpt-4o-mini、deepseek/deepseek-chat 等）
        # 在 temperature/top_p/seed/tools 为 null 时返回 400，未设置的参数必须省略
        model = AIMLAPIChatModel.new_instance(
            'LLM', 'openai/gpt-4o-mini', self.credential,
            model_id='1', streaming=True,
            temperature=None, max_tokens=None, top_p=None, seed=None, tools=None,
        )
        self.assertEqual(model.model_kwargs, {})
        params = model._default_params
        for key in ['temperature', 'max_tokens', 'max_completion_tokens', 'top_p', 'seed', 'tools']:
            self.assertNotIn(key, params)
        self.assertEqual([key for key, value in params.items() if value is None], [])

    def test_chat_model_keeps_params_that_are_set(self):
        model = AIMLAPIChatModel.new_instance(
            'LLM', 'openai/gpt-4o-mini', self.credential, model_id='1', temperature=0.7, max_tokens=8192)
        params = model._default_params
        self.assertEqual(params['temperature'], 0.7)
        # langchain-openai 会把 max_tokens 转换成 max_completion_tokens 下发
        self.assertEqual(params['max_completion_tokens'], 8192)

    def test_text_to_image_omits_auto_params(self):
        model = AIMLAPITextToImage.new_instance(
            'TTI', 'openai/gpt-image-1', self.credential, model_id='1', size='auto', quality='auto', n=1)
        self.assertEqual(model.params, {'n': 1})
        model = AIMLAPITextToImage.new_instance(
            'TTI', 'flux/schnell', self.credential, model_id='1', size='1024x1024', quality=None, n=2)
        self.assertEqual(model.params, {'size': '1024x1024', 'n': 2})
