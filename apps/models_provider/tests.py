from io import BytesIO
from unittest.mock import patch

from django.test import SimpleTestCase
from langchain_core.documents import Document

from models_provider.impl.vllm_model_provider.model.whisper_sst import VllmWhisperSpeechToText
from models_provider.impl.xinference_model_provider.model.reranker import XInferenceReranker


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


class XInferenceRerankerTest(SimpleTestCase):
    @patch('xinference_client.RESTfulClient')
    def test_compress_documents_accepts_string_documents(self, client_mock):
        client_mock.return_value.get_model.return_value.rerank.return_value = {
            'results': [{'document': 'current result', 'relevance_score': 0.9}]
        }
        model = XInferenceReranker(server_url='http://localhost', model_uid='reranker', api_key=None)

        result = model.compress_documents([Document(page_content='query text')], 'query')

        self.assertEqual(result[0].page_content, 'current result')
        self.assertEqual(result[0].metadata['relevance_score'], 0.9)

    def test_extracts_text_from_legacy_document_object(self):
        result = {'document': {'text': 'legacy result'}}

        self.assertEqual(XInferenceReranker._get_document_text(result), 'legacy result')

    def test_extracts_text_from_current_document_string(self):
        result = {'document': 'current result'}

        self.assertEqual(XInferenceReranker._get_document_text(result), 'current result')
