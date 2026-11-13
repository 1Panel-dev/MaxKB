# coding=utf-8
from django.test import SimpleTestCase

from models_provider.impl.xf_model_provider.credential.llm import XunFeiOpenAILLMModelCredential
from models_provider.impl.xf_model_provider.model.llm import XunFeiOpenAIChatModel


class XunfeiOpenAILLMModelTests(SimpleTestCase):
    def _credential(self):
        return {
            "api_base": "https://maas-api.cn-huabei-1.xf-yun.com/v2",
            "api_key": "ak-4ca28ba5xxxxxxxxxxxxxxxx",
        }

    def test_new_instance_accepts_api_base_key_and_params(self):
        model = XunFeiOpenAIChatModel.new_instance(
            "LLM",
            "spark-x2.6",
            self._credential(),
            temperature=0.5,
            max_tokens=4096,
            streaming=False,
        )

        self.assertEqual(model.openai_api_base, "https://maas-api.cn-huabei-1.xf-yun.com/v2")
        self.assertEqual(model.model_name, "spark-x2.6")
        self.assertEqual(model.temperature, 0.5)
        self.assertEqual(model.max_tokens, 4096)

    def test_new_instance_does_not_duplicate_temperature(self):
        model = XunFeiOpenAIChatModel.new_instance(
            "LLM",
            "spark-x2.6",
            self._credential(),
            temperature=0.5,
            max_tokens=4096,
            streaming=False,
        )

        # 走标准 ChatOpenAI 字段，不应再出现重复的 temperature 键。
        self.assertEqual(model.temperature, 0.5)
        self.assertEqual(model.max_tokens, 4096)
        self.assertEqual(model.model_kwargs.get("temperature"), None)
        # 请求体中 temperature/max_tokens 只出现一次，不会重复注入。
        payload = model._get_request_payload(model._convert_input([{"role": "user", "content": "hi"}]))
        self.assertEqual(payload["temperature"], 0.5)
        self.assertEqual(payload["max_tokens"], 4096)

    def test_credential_default_api_base(self):
        credential = XunFeiOpenAILLMModelCredential()
        data = credential.get_default_form_data()
        self.assertEqual(data["api_base"], "https://maas-api.cn-huabei-1.xf-yun.com/v2")

    def test_params_setting_form_returns_params(self):
        credential = XunFeiOpenAILLMModelCredential()
        form = credential.get_model_params_setting_form("spark-x2.6")
        self.assertEqual(form.temperature.default_value, 0.5)
        self.assertEqual(form.max_tokens.default_value, 4096)
