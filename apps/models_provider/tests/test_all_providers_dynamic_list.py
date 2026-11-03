# coding=utf-8
"""全供应商动态模型列表一致性测试。

验证约定：
- 提供了 api_key 时，动态列表来自实时查询（mock 官方接口）；
- 模型类型不是按关键词猜出来的唯一来源：凡是内置 model_info_list 里已有的模型，
  类型与实现必须沿用原有逻辑（builtin-name-first）；
- 每个供应商按其内置的模型类型集合逐一校验。
"""

import importlib
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from models_provider.constants.model_provider_constants import ModelProvideConstants

API_KEY = "test-key"


def _builtin_catalog(provider):
    """返回 {model_type: [name, ...]}，数据完全取自供应商原有内置逻辑。"""
    catalog = {}
    for info in provider.get_model_info_manage().model_list:
        catalog.setdefault(info.model_type, [])
        if info.name not in catalog[info.model_type]:
            catalog[info.model_type].append(info.name)
    return catalog


def _dynamic_names(provider, model_type, api_base=None):
    return sorted(m["name"] for m in provider.get_model_list(model_type, api_key=API_KEY, api_base=api_base))


class AllProvidersDynamicModelListTest(SimpleTestCase):
    def _load_provider(self, name):
        try:
            return ModelProvideConstants[name]
        except Exception:
            self.skipTest(f"provider {name} unavailable in this environment")

    def test_openai_compatible_providers_use_original_types(self):
        """默认 OpenAI 兼容协议的供应商：mock /models 返回内置模型名，动态列表类型须与内置一致。"""
        special = {
            "aliyun_bai_lian_model_provider",
            "model_gemini_provider",
            "model_anthropic_provider",
            "model_aws_bedrock_provider",
        }
        tested = []
        for name in ModelProvideConstants:
            if name in special:
                continue
            provider = self._load_provider(name)
            catalog = _builtin_catalog(provider)
            all_names = list(dict.fromkeys(n for names in catalog.values() for n in names))
            if not all_names:
                continue
            api_base = provider.get_dynamic_default_api_base() or "https://dynamic-test.example.com/v1"
            calls = []

            def fake_get(url, headers=None, timeout=None, **kwargs):
                calls.append(url)
                resp = Mock()
                resp.status_code = 200
                resp.json.return_value = {"object": "list", "data": [{"id": n} for n in all_names]}
                return resp

            with patch("models_provider.base_model_provider.requests.get", side_effect=fake_get):
                for model_type, names in catalog.items():
                    # 跨类型重名模型不参与断言（动态列表只归属一次）。
                    duplicated = {n for n in names if sum(n in ns for ns in catalog.values()) > 1}
                    expected = sorted(n for n in names if n not in duplicated)
                    if not expected:
                        continue
                    actual = _dynamic_names(provider, model_type, api_base)
                    # 内置模型必须出现在动态列表中（新模型可按关键词归入同类型，允许超集）。
                    self.assertTrue(
                        set(expected).issubset(actual),
                        f"{name} / {model_type}: builtin models missing from dynamic list: {expected} vs {actual}",
                    )
            self.assertTrue(calls, f"{name}: dynamic fetch never issued a request")
            tested.append(name)
        self.assertGreaterEqual(len(tested), 10)

    def test_openai_compatible_metadata_modalities_classification(self):
        """官方 /models 返回 input/output_modalities 时按元数据判型（如 DeepSeek 新返回结构）。"""
        provider = self._load_provider("model_deepseek_provider")
        items = [
            {"id": "deepseek-flash", "input_modalities": ["text", "image"], "output_modalities": ["text"]},
            {"id": "deepseek-v4-pro", "input_modalities": ["text"], "output_modalities": ["text"]},
            {"id": "deepseek-image", "input_modalities": ["text"], "output_modalities": ["image"]},
        ]

        def fake_get(url, headers=None, timeout=None, **kwargs):
            resp = Mock()
            resp.status_code = 200
            resp.json.return_value = {"object": "list", "data": items}
            return resp

        with patch("models_provider.base_model_provider.requests.get", side_effect=fake_get):
            llm = _dynamic_names(provider, "LLM")
            # 带 image 输入的多模态对话模型在本供应商无 IMAGE 实现时归入 LLM；纯绘图模型归 TTI 且不混入 LLM。
            self.assertIn("deepseek-flash", llm)
            self.assertIn("deepseek-v4-pro", llm)
            self.assertNotIn("deepseek-image", llm)

    def test_anthropic_uses_x_api_key_header(self):
        provider = self._load_provider("model_anthropic_provider")
        catalog = _builtin_catalog(provider)
        all_names = list(dict.fromkeys(n for names in catalog.values() for n in names))
        headers_seen = []

        def fake_get(url, headers=None, timeout=None, **kwargs):
            headers_seen.append(headers or {})
            resp = Mock()
            resp.status_code = 200
            resp.json.return_value = {"data": [{"id": n} for n in all_names]}
            return resp

        with patch("models_provider.base_model_provider.requests.get", side_effect=fake_get):
            for model_type, names in catalog.items():
                duplicated = {n for n in names if sum(n in ns for ns in catalog.values()) > 1}
                expected = sorted(n for n in names if n not in duplicated)
                if not expected:
                    continue
                actual = _dynamic_names(provider, model_type)
                self.assertTrue(set(expected).issubset(actual), f"anthropic / {model_type}")
        self.assertTrue(headers_seen and headers_seen[0].get("x-api-key") == API_KEY)

    def test_gemini_native_models_endpoint_keeps_builtin_types(self):
        provider = self._load_provider("model_gemini_provider")
        catalog = _builtin_catalog(provider)
        all_names = list(dict.fromkeys(n for names in catalog.values() for n in names))

        def fake_get(url, headers=None, timeout=None, **kwargs):
            resp = Mock()
            if url.endswith("/v1beta/models") and "/openai/" not in url:
                resp.status_code = 200
                resp.json.return_value = {
                    "models": [{"name": f"models/{n}"} for n in all_names],
                }
            else:
                resp.status_code = 200
                resp.json.return_value = {"data": [{"id": n} for n in all_names]}
            return resp

        with patch("models_provider.base_model_provider.requests.get", side_effect=fake_get):
            for model_type, names in catalog.items():
                duplicated = {n for n in names if sum(n in ns for ns in catalog.values()) > 1}
                expected = sorted(n for n in names if n not in duplicated)
                if not expected:
                    continue
                actual = _dynamic_names(provider, model_type)
                self.assertTrue(set(expected).issubset(actual), f"gemini / {model_type}")

    def test_aliyun_dashscope_list_keeps_builtin_types(self):
        provider = self._load_provider("aliyun_bai_lian_model_provider")
        catalog = _builtin_catalog(provider)
        all_names = list(dict.fromkeys(n for names in catalog.values() for n in names))
        dashscope = importlib.import_module("dashscope")

        response = Mock()
        response.status_code = 200
        response.output = {"models": [{"model": n} for n in all_names]}

        with patch.object(dashscope.Models, "list", return_value=response):
            for model_type, names in catalog.items():
                duplicated = {n for n in names if sum(n in ns for ns in catalog.values()) > 1}
                expected = sorted(n for n in names if n not in duplicated)
                if not expected:
                    continue
                actual = _dynamic_names(provider, model_type)
                self.assertTrue(set(expected).issubset(actual), f"aliyun / {model_type}")

    def test_bedrock_list_foundation_models_keeps_builtin_types(self):
        provider = self._load_provider("model_aws_bedrock_provider")
        catalog = _builtin_catalog(provider)
        all_names = list(dict.fromkeys(n for names in catalog.values() for n in names))
        boto3 = importlib.import_module("boto3")

        client = Mock()
        client.list_foundation_models.return_value = {"modelSummaries": [{"modelId": n} for n in all_names]}
        credential = {
            "access_key_id": "AKIA_TEST",
            "secret_access_key": "SECRET_TEST",
            "region_name": "us-east-1",
        }

        with patch.object(boto3, "client", return_value=client):
            for model_type, names in catalog.items():
                duplicated = {n for n in names if sum(n in ns for ns in catalog.values()) > 1}
                expected = sorted(n for n in names if n not in duplicated)
                if not expected:
                    continue
                models = provider.get_model_list(model_type, api_key="SECRET_TEST", credential=credential)
                actual = sorted(m["name"] for m in models)
                self.assertTrue(set(expected).issubset(actual), f"bedrock / {model_type}")
