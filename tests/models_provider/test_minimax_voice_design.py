import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


class DummyMaxKBBaseModel:
    def __init__(self, **kwargs):
        pass


class DummyBaseTextToSpeech:
    pass


def load_tts_module():
    requests_module = types.ModuleType("requests")
    requests_module.post = Mock()

    django_module = types.ModuleType("django")
    django_utils_module = types.ModuleType("django.utils")
    translation_module = types.ModuleType("django.utils.translation")
    translation_module.gettext = lambda value: value

    common_module = types.ModuleType("common")
    common_utils_module = types.ModuleType("common.utils")
    common_utils_common_module = types.ModuleType("common.utils.common")
    common_utils_common_module._remove_empty_lines = lambda value: value

    models_provider_module = types.ModuleType("models_provider")
    base_model_provider_module = types.ModuleType("models_provider.base_model_provider")
    base_model_provider_module.MaxKBBaseModel = DummyMaxKBBaseModel
    impl_module = types.ModuleType("models_provider.impl")
    base_tts_module = types.ModuleType("models_provider.impl.base_tts")
    base_tts_module.BaseTextToSpeech = DummyBaseTextToSpeech

    modules = {
        "requests": requests_module,
        "django": django_module,
        "django.utils": django_utils_module,
        "django.utils.translation": translation_module,
        "common": common_module,
        "common.utils": common_utils_module,
        "common.utils.common": common_utils_common_module,
        "models_provider": models_provider_module,
        "models_provider.base_model_provider": base_model_provider_module,
        "models_provider.impl": impl_module,
        "models_provider.impl.base_tts": base_tts_module,
    }

    module_path = Path(__file__).resolve().parents[2] / "apps/models_provider/impl/minimax_model_provider/model/tts.py"
    spec = importlib.util.spec_from_file_location("minimax_tts_under_test", module_path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    return module, requests_module


class MiniMaxVoiceDesignTest(unittest.TestCase):
    def setUp(self):
        self.module, self.requests = load_tts_module()
        self.response = Mock()
        self.requests.post.return_value = self.response
        self.model = self.module.MiniMaxTextToSpeech(
            api_key="key",
            api_base="https://api.minimax.io/v1",
            model="speech-test",
            params={},
        )

    def test_voice_design_posts_required_fields_for_regional_api_bases(self):
        endpoints = {
            "https://api.minimax.io/v1/": "https://api.minimax.io/v1/voice_design",
            "https://api.minimaxi.com/v1": "https://api.minimaxi.com/v1/voice_design",
        }

        for api_base, expected_url in endpoints.items():
            with self.subTest(api_base=api_base):
                self.requests.post.reset_mock()
                self.response.reset_mock()
                self.response.json.return_value = {
                    "voice_id": "designed-voice",
                    "base_resp": {"status_code": 0},
                }
                self.model.api_base = api_base

                result = self.model.voice_design("A warm, clear narrator", "custom-voice")

                self.assertEqual(result, "designed-voice")
                self.requests.post.assert_called_once_with(
                    expected_url,
                    json={
                        "prompt": "A warm, clear narrator",
                        "voice_id": "custom-voice",
                    },
                    headers={
                        "Authorization": "Bearer key",
                        "Content-Type": "application/json",
                    },
                    timeout=60,
                )
                self.response.raise_for_status.assert_called_once_with()

    def test_voice_design_raises_api_error(self):
        self.response.json.return_value = {
            "base_resp": {
                "status_code": 1001,
                "status_msg": "Invalid prompt",
            }
        }

        with self.assertRaisesRegex(Exception, "MiniMax voice design API error: Invalid prompt"):
            self.model.voice_design("prompt", "custom-voice")

    def test_voice_design_requires_voice_id_response(self):
        self.response.json.return_value = {"base_resp": {"status_code": 0}}

        with self.assertRaisesRegex(Exception, "MiniMax voice design returned no voice ID"):
            self.model.voice_design("prompt", "custom-voice")


if __name__ == "__main__":
    unittest.main()
