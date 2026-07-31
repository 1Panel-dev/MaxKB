import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


class DummyMaxKBBaseModel:
    def __init__(self, **kwargs):
        pass


class DummyBaseTextToImage:
    pass


def load_tti_module():
    requests_module = types.ModuleType('requests')
    requests_module.post = Mock()

    common_module = types.ModuleType('common')
    common_utils_module = types.ModuleType('common.utils')
    logger_module = types.ModuleType('common.utils.logger')
    logger_module.maxkb_logger = Mock()

    models_provider_module = types.ModuleType('models_provider')
    base_model_provider_module = types.ModuleType('models_provider.base_model_provider')
    base_model_provider_module.MaxKBBaseModel = DummyMaxKBBaseModel
    impl_module = types.ModuleType('models_provider.impl')
    base_tti_module = types.ModuleType('models_provider.impl.base_tti')
    base_tti_module.BaseTextToImage = DummyBaseTextToImage

    modules = {
        'requests': requests_module,
        'common': common_module,
        'common.utils': common_utils_module,
        'common.utils.logger': logger_module,
        'models_provider': models_provider_module,
        'models_provider.base_model_provider': base_model_provider_module,
        'models_provider.impl': impl_module,
        'models_provider.impl.base_tti': base_tti_module,
    }

    module_path = (
        Path(__file__).resolve().parents[2]
        / 'apps/models_provider/impl/minimax_model_provider/model/tti.py'
    )
    spec = importlib.util.spec_from_file_location('minimax_tti_under_test', module_path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    return module, requests_module


class MiniMaxTextToImageModelTest(unittest.TestCase):
    def setUp(self):
        module, self.requests = load_tti_module()
        response = Mock()
        response.json.return_value = {'data': {'image_urls': ['https://example.com/generated.png']}}
        self.requests.post.return_value = response
        self.model = module.MiniMaxTextToImageModel(
            api_key='test-key',
            api_base='https://api.example.com/v1',
            model_name='image-01',
            params={'n': 1},
        )

    def test_adds_subject_reference_from_model_params(self):
        reference_url = 'https://example.com/reference.png'
        self.model.params['subject_reference'] = reference_url

        result = self.model.generate_image('Create a portrait')

        payload = self.requests.post.call_args.kwargs['json']
        self.assertEqual(result, ['https://example.com/generated.png'])
        self.assertEqual(
            payload['subject_reference'],
            [{'type': 'character', 'image_file': reference_url}],
        )
        self.assertEqual(payload['n'], 1)

    def test_keeps_text_to_image_payload_without_reference(self):
        self.model.generate_image('Create a landscape')

        payload = self.requests.post.call_args.kwargs['json']
        self.assertNotIn('subject_reference', payload)

    def test_accepts_structured_subject_reference_argument(self):
        subject_reference = [
            {'type': 'character', 'image_file': 'data:image/png;base64,AAAA'},
        ]

        self.model.generate_image('Create a portrait', subject_reference=subject_reference)

        payload = self.requests.post.call_args.kwargs['json']
        self.assertEqual(payload['subject_reference'], subject_reference)


if __name__ == '__main__':
    unittest.main()
