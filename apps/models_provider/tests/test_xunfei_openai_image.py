# coding=utf-8
from django.test import SimpleTestCase

from models_provider.impl.xf_model_provider.credential.image import XunFeiImageModelCredential
from models_provider.impl.xf_model_provider.model.image import XunFeiOpenAIImage


class XunfeiOpenAIImageTests(SimpleTestCase):
    def _credential(self):
        return {
            "api_base": "https://maas-api.cn-huabei-1.xf-yun.com/v2",
            "api_key": "ak-4ca28ba5xxxxxxxxxxxxxxxx",
        }

    def test_new_instance_accepts_api_base_key(self):
        model = XunFeiOpenAIImage.new_instance(
            "IMAGE",
            "spark-x2.6",
            self._credential(),
            temperature=0.5,
            max_tokens=4096,
            streaming=True,
        )

        self.assertEqual(model.openai_api_base, "https://maas-api.cn-huabei-1.xf-yun.com/v2")
        self.assertEqual(model.model_name, "spark-x2.6")
        self.assertEqual(model.temperature, 0.5)
        self.assertEqual(model.max_tokens, 4096)

    def test_payload_uses_max_tokens(self):
        model = XunFeiOpenAIImage.new_instance(
            "IMAGE",
            "spark-x2.6",
            self._credential(),
            temperature=0.5,
            max_tokens=4096,
            streaming=True,
        )
        payload = model._get_request_payload(model._convert_input([{"role": "user", "content": "hi"}]))
        self.assertEqual(payload["max_tokens"], 4096)
        self.assertNotIn("max_completion_tokens", payload)

    def test_credential_default_api_base(self):
        credential = XunFeiImageModelCredential()
        data = credential.get_default_form_data()
        self.assertEqual(data["api_base"], "https://maas-api.cn-huabei-1.xf-yun.com/v2")

    def test_params_setting_form_returns_params(self):
        credential = XunFeiImageModelCredential()
        form = credential.get_model_params_setting_form("spark-x2.6")
        self.assertEqual(form.temperature.default_value, 0.5)
        self.assertEqual(form.max_tokens.default_value, 4096)
