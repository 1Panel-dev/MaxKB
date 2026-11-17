# coding=utf-8
from unittest.mock import patch

from django.test import SimpleTestCase
from django.utils.translation import gettext_lazy as _

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
        }

    def test_new_instance_uses_model_name_directly(self):
        model = XunFeiOpenAIEmbeddingModel.new_instance("EMBEDDING", "xop3qwen8bembedding", self._credential())
        self.assertEqual(model.model_name, "xop3qwen8bembedding")
        self.assertIsNotNone(model.client)

    def test_new_instance_ignores_legacy_model_id(self):
        credential = {**self._credential(), "model_id": "sde0a5839"}
        model = XunFeiOpenAIEmbeddingModel.new_instance("EMBEDDING", "xop3qwen8bembedding", credential)
        self.assertEqual(model.model_name, "xop3qwen8bembedding")

    def test_credential_default_api_base(self):
        credential = XunFeiOpenAIEmbeddingCredential()
        data = credential.get_default_form_data()
        self.assertEqual(data["api_base"], "https://maas-api.cn-huabei-1.xf-yun.com/v2")

    def test_credential_requires_api_key(self):
        credential = XunFeiOpenAIEmbeddingCredential()
        with self.assertRaises(AppApiException):
            credential.is_valid(
                "EMBEDDING",
                "xop3qwen8bembedding",
                {"api_base": "https://maas-api.cn-huabei-1.xf-yun.com/v2"},
                {},
                _FakeProvider(),
                raise_exception=True,
            )

    def test_embed_query_coerces_lazy_text_to_plain_string(self):
        # gettext_lazy 代理若原样传给 OpenAI 客户端会被序列化成字符数组，
        # 讯飞 MaaS 会因此返回 500，这里断言发送的是普通字符串列表。
        model = XunFeiOpenAIEmbeddingModel.new_instance("EMBEDDING", "xop3qwen8bembedding", self._credential())
        captured = {}

        def fake_create(**kwargs):
            captured.update(kwargs)
            return type("_Resp", (), {"data": [type("_Item", (), {"embedding": [0.1, 0.2]})()]})()

        with patch.object(model.client, "create", side_effect=fake_create):
            model.embed_query(_("Hello"))

        self.assertEqual(len(captured["input"]), 1)
        self.assertIsInstance(captured["input"][0], str)
