from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.http import QueryDict
from django.test import SimpleTestCase

from common.exception.app_exception import BadRequest400
from models_provider.views.provide import Provide


def request_with_params(**params):
    query_params = QueryDict(mutable=True)
    query_params.update(params)
    return SimpleNamespace(query_params=query_params)


class ProvideParameterValidationTests(SimpleTestCase):
    def test_model_type_list_requires_provider(self):
        with self.assertRaises(BadRequest400):
            Provide.ModelTypeList().get(request_with_params())

    def test_model_params_form_requires_all_query_parameters(self):
        request = request_with_params(provider="model_openai_provider", model_type="LLM")

        with self.assertRaises(BadRequest400):
            Provide.ModelParamsForm().get(request)

    def test_model_form_requires_all_query_parameters(self):
        request = request_with_params(provider="model_openai_provider", model_name="gpt-4o")

        with self.assertRaises(BadRequest400):
            Provide.ModelForm().get(request)

    def test_model_form_allows_empty_model_name(self):
        provider = MagicMock()
        provider.get_model_credential.return_value.to_form_list.return_value = [{"field": "api_key"}]
        request = request_with_params(
            provider="test_provider",
            model_type="LLM",
            model_name="",
        )

        with patch("models_provider.views.provide.ModelProvideConstants", {"test_provider": provider}):
            response = Provide.ModelForm().get(request)

        self.assertEqual(200, response.status_code)
        provider.get_model_credential.assert_called_once_with("LLM", "")

    def test_unknown_provider_is_bad_request(self):
        requests = (
            (Provide.ModelTypeList(), request_with_params(provider="missing")),
            (Provide.ModelList(), request_with_params(provider="missing", model_type="LLM")),
            (
                Provide.ModelParamsForm(),
                request_with_params(provider="missing", model_type="LLM", model_name="missing"),
            ),
            (
                Provide.ModelForm(),
                request_with_params(provider="missing", model_type="LLM", model_name="missing"),
            ),
        )

        for view, request in requests:
            with self.subTest(view=view.__class__.__name__), self.assertRaises(BadRequest400):
                view.get(request)

    def test_model_list_requires_provider_and_model_type(self):
        requests = (
            request_with_params(model_type="LLM"),
            request_with_params(provider="model_openai_provider"),
        )

        for request in requests:
            with self.subTest(params=request), self.assertRaises(BadRequest400):
                Provide.ModelList().get(request)

    def test_model_list_rejects_invalid_model_type(self):
        provider = MagicMock()
        provider.get_model_type_list.return_value = [{"value": "LLM"}]

        with patch("models_provider.views.provide.ModelProvideConstants", {"test_provider": provider}):
            with self.assertRaises(BadRequest400):
                Provide.ModelList().get(request_with_params(provider="test_provider", model_type="INVALID"))

    def test_model_list_returns_provider_models(self):
        provider = MagicMock()
        provider.get_model_type_list.return_value = [{"value": "LLM"}]
        provider.get_model_list.return_value = [{"name": "test-model"}]

        with patch("models_provider.views.provide.ModelProvideConstants", {"test_provider": provider}):
            response = Provide.ModelList().get(request_with_params(provider="test_provider", model_type="LLM"))

        self.assertEqual(200, response.status_code)
        provider.get_model_list.assert_called_once_with(
            "LLM",
            api_key=None,
            api_base=None,
            credential=None,
        )
