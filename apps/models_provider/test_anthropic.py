# coding=utf-8
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch


class AnthropicProviderModelsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from django.conf import settings

        if not settings.configured:
            settings.configure(USE_I18N=False)
        # Isolate application services; provider lookup and model lists stay real.
        dependencies = {
            'common.utils.common': SimpleNamespace(
                encryption=Mock(), get_file_content=Mock(), _remove_empty_lines=Mock()
            ),
            'common.config.tokenizer_manage_config': SimpleNamespace(TokenizerManage=Mock()),
            'maxkb.conf': SimpleNamespace(PROJECT_DIR=str(Path(__file__).resolve().parents[2])),
        }
        services = patch.dict('sys.modules', dependencies)
        services.start()
        cls.addClassCleanup(services.stop)
        from models_provider.impl.anthropic_model_provider.anthropic_model_provider import AnthropicModelProvider

        cls.manage = AnthropicModelProvider().get_model_info_manage()

    def names(self, model_type):
        return [m['name'] for m in self.manage.get_model_list_by_model_type(model_type)]

    def test_llm_models_are_current_claude_models(self):
        self.assertEqual(self.names('LLM'), ['claude-opus-4-6', 'claude-sonnet-4-6', 'claude-haiku-4-5-20251001'])

    def test_vision_model_is_a_current_claude_model(self):
        self.assertEqual(self.names('IMAGE'), ['claude-sonnet-4-6'])

    def test_default_models_are_current(self):
        self.assertEqual(self.manage.default_model_dict['LLM'].name, 'claude-opus-4-6')
        self.assertEqual(self.manage.default_model_dict['IMAGE'].name, 'claude-sonnet-4-6')
