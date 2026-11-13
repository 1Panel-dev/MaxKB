# coding=utf-8
from django.test import SimpleTestCase

from common.exception.app_exception import AppApiException
from models_provider.impl.xf_model_provider.credential.embedding import XunFeiOpenAIEmbeddingCredential
from models_provider.impl.xf_model_provider.model.embedding import XunFeiOpenAIEmbeddingModel


class _FakeProvider:
    def get_model_type_list(self):
        return [{"key": "Embedding Model", "value": "EMBEDDING"}]


class XunfeiOpenAIEmbeddingTests(SimpleTestCase):
    def _credential(self):
        return {
            "api_base": "https://maas-api.cn-huabei-1.xf-yun.com/v2",
            "api_key": "ak-4ca28ba5xxxxxxxxxxxxxxxx",
            "model_id": "sde0a5839",
        }

    def test_new_instance_uses_model_id_as_model_name(self):
        model = XunFeiOpenAIEmbeddingModel.new_instance("EMBEDDING", "embedding", self._credential())
        self.assertEqual(model.model_name, "sde0a5839")
        self.assertIsNotNone(model.client)

    def test_new_instance_falls_back_to_model_name_without_model_id(self):
        credential = {k: v for k, v in self._credential().items() if k != "model_id"}
        model = XunFeiOpenAIEmbeddingModel.new_instance("EMBEDDING", "embedding", credential)
        self.assertEqual(model.model_name, "embedding")

    def test_credential_default_api_base(self):
        credential = XunFeiOpenAIEmbeddingCredential()
        data = credential.get_default_form_data()
        self.assertEqual(data["api_base"], "https://maas-api.cn-huabei-1.xf-yun.com/v2")

    def test_credential_requires_model_id(self):
        credential = XunFeiOpenAIEmbeddingCredential()
        with self.assertRaises(AppApiException):
            credential.is_valid(
                "EMBEDDING",
                "embedding",
                {"api_base": "https://maas-api.cn-huabei-1.xf-yun.com/v2", "api_key": "ak-xxx"},
                {},
                _FakeProvider(),
                raise_exception=True,
            )
