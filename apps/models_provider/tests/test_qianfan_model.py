# coding=utf-8
from unittest.mock import MagicMock

from django.test import SimpleTestCase
from langchain_core.messages import HumanMessage

from common.exception.app_exception import AppApiException
from models_provider.impl.qianfan_model_provider.credential.llm import QianfanLLMModelCredential
from models_provider.impl.qianfan_model_provider.model.image import QianfanVisionModel
from models_provider.impl.qianfan_model_provider.model.llm import QianfanChatModel

CRED = {"api_base": "https://qianfan.baidubce.com/v2", "api_key": "sk-test"}


class QianfanModelConstructionTests(SimpleTestCase):
    def test_client_params_are_not_sent_in_request_body(self):
        for model_class in (QianfanChatModel, QianfanVisionModel):
            with self.subTest(model=model_class.__name__):
                model = model_class.new_instance(
                    "LLM",
                    "ernie-5.1",
                    CRED,
                    temperature=0.95,
                    max_tokens=1,
                    request_timeout=5.0,
                    max_retries=0,
                )

                # 客户端配置项应真正作用于 OpenAI 客户端
                self.assertEqual(5.0, model.request_timeout)
                self.assertEqual(0, model.max_retries)

                # 且不应混入接口请求体
                self.assertNotIn("request_timeout", model.extra_body)
                self.assertNotIn("max_retries", model.extra_body)

                payload = model._get_request_payload([HumanMessage(content="1")])
                self.assertNotIn("request_timeout", payload)
                self.assertNotIn("max_retries", payload)


class QianfanLLMCredentialTests(SimpleTestCase):
    def _mock_provider(self, model):
        provider = MagicMock()
        provider.get_model.return_value = model
        return provider

    def test_validation_propagates_provider_error_message(self):
        model = MagicMock()
        model.invoke.side_effect = RuntimeError("Error code: 500 - {'error': {'code': 'internal_error'}}")

        credential = QianfanLLMModelCredential()
        with self.assertRaises(AppApiException) as raised:
            credential.is_valid(
                "LLM",
                "ernie-5.1",
                CRED,
                {"temperature": 0.95},
                self._mock_provider(model),
                raise_exception=True,
            )

        self.assertIn("Error code: 500 - {'error': {'code': 'internal_error'}}", raised.exception.message)

    def test_validation_returns_false_when_not_raising(self):
        model = MagicMock()
        model.invoke.side_effect = RuntimeError("boom")

        credential = QianfanLLMModelCredential()
        result = credential.is_valid(
            "LLM",
            "ernie-5.1",
            CRED,
            {"temperature": 0.95},
            self._mock_provider(model),
            raise_exception=False,
        )

        self.assertFalse(result)
