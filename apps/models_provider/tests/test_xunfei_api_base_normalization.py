# coding=utf-8
from django.test import SimpleTestCase

from models_provider.impl.xf_model_provider.model.embedding import XunFeiOpenAIEmbeddingModel
from models_provider.impl.xf_model_provider.utils import DEFAULT_XUNFEI_API_BASE, normalize_xunfei_api_base


class XunfeiApiBaseNormalizationTests(SimpleTestCase):
    """讯飞 MaaS OpenAI 兼容接口必须带版本前缀，裸主机地址保存会 404。

    保存时应自动为裸主机地址补上官方默认的 /v2，从而修复「官方接口地址 + Model ID 保存报 404」。
    """

    def test_bare_host_gets_default_version(self):
        self.assertEqual(
            "https://maas-api.cn-huabei-1.xf-yun.com/v2",
            normalize_xunfei_api_base("https://maas-api.cn-huabei-1.xf-yun.com"),
        )

    def test_bare_host_with_trailing_slash_gets_default_version(self):
        self.assertEqual(
            "https://maas-api.cn-huabei-1.xf-yun.com/v2",
            normalize_xunfei_api_base("https://maas-api.cn-huabei-1.xf-yun.com/"),
        )

    def test_aliased_versioned_base_is_kept(self):
        base = "https://maas-api.cn-huabei-1.xf-yun.com/v2"
        self.assertEqual(base, normalize_xunfei_api_base(base))

    def test_v1_base_is_kept(self):
        base = "https://maas-api.cn-huabei-1.xf-yun.com/v1"
        self.assertEqual(base, normalize_xunfei_api_base(base))

    def test_custom_path_is_kept(self):
        base = "https://gateway.example.com/xunfei"
        self.assertEqual(base, normalize_xunfei_api_base(base))

    def test_full_endpoint_suffix_stripped_and_bad_version_fixed(self):
        # 用户从官方控制台复制了完整接口地址（版本段 /v2.1 并不存在）
        self.assertEqual(
            "https://maas-api.cn-huabei-1.xf-yun.com/v2",
            normalize_xunfei_api_base("https://maas-api.cn-huabei-1.xf-yun.com/v2.1/embeddings"),
        )

    def test_correct_versioned_endpoint_suffix_stripped(self):
        self.assertEqual(
            "https://maas-api.cn-huabei-1.xf-yun.com/v2",
            normalize_xunfei_api_base("https://maas-api.cn-huabei-1.xf-yun.com/v2/embeddings"),
        )

    def test_endpoint_suffix_on_bare_host_gets_default_version(self):
        self.assertEqual(
            "https://maas-api.cn-huabei-1.xf-yun.com/v2",
            normalize_xunfei_api_base("https://maas-api.cn-huabei-1.xf-yun.com/embeddings"),
        )

    def test_bad_version_without_endpoint_suffix_fixed(self):
        self.assertEqual(
            "https://maas-api.cn-huabei-1.xf-yun.com/v2",
            normalize_xunfei_api_base("https://maas-api.cn-huabei-1.xf-yun.com/v2.1"),
        )

    def test_chat_endpoint_suffix_stripped_and_version_fixed(self):
        self.assertEqual(
            "https://maas-api.cn-huabei-1.xf-yun.com/v2",
            normalize_xunfei_api_base("https://maas-api.cn-huabei-1.xf-yun.com/v2.1/chat/completions"),
        )

    def test_empty_falls_back_to_default(self):
        self.assertEqual(DEFAULT_XUNFEI_API_BASE, normalize_xunfei_api_base(""))
        self.assertEqual(DEFAULT_XUNFEI_API_BASE, normalize_xunfei_api_base(None))

    def test_new_instance_normalizes_bare_host(self):
        # 凭证不再单独提供 model_id，模型名（model_name）即 MaaS 的模型 id。
        credential = {
            "api_base": "https://maas-api.cn-huabei-1.xf-yun.com",
            "api_key": "ak-xxx",
        }
        model = XunFeiOpenAIEmbeddingModel.new_instance("EMBEDDING", "xop3qwen8bembedding", credential)
        base_url = str(model.client._client.base_url).rstrip("/")
        self.assertEqual("https://maas-api.cn-huabei-1.xf-yun.com/v2", base_url)
        self.assertEqual("xop3qwen8bembedding", model.model_name)

    def test_embedding_credential_has_no_model_id_field(self):
        from models_provider.impl.xf_model_provider.credential.embedding import XunFeiOpenAIEmbeddingCredential

        fields = XunFeiOpenAIEmbeddingCredential().to_form_list()
        field_names = {item["field"] for item in fields}
        self.assertIn("api_base", field_names)
        self.assertIn("api_key", field_names)
        self.assertNotIn("model_id", field_names)
