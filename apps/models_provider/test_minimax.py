# coding=utf-8
import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import httpx
from langchain_core.messages import HumanMessage


class MiniMaxProviderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from django.conf import settings

        if not settings.configured:
            settings.configure(USE_I18N=False)
        # Isolate application services; provider lookup, forms and SDK transport stay real.
        dependencies = {
            'common.utils.common': SimpleNamespace(
                encryption=Mock(), get_file_content=Mock(), _remove_empty_lines=Mock()
            ),
            'maxkb.conf': SimpleNamespace(PROJECT_DIR=str(Path(__file__).resolve().parents[2])),
        }
        services = patch.dict('sys.modules', dependencies)
        services.start()
        cls.addClassCleanup(services.stop)
        from models_provider.impl.minimax_model_provider.minimax_model_provider import MiniMaxModelProvider

        cls.provider = MiniMaxModelProvider()

    def capture(self, name, base=None, params=None, stream=False, content='Hello'):
        captured = []

        def respond(request):
            body = json.loads(request.content)
            captured.append((str(request.url), body))
            if body.get('stream'):
                chunk = {
                    'id': 'test', 'object': 'chat.completion.chunk', 'created': 0, 'model': name,
                    'choices': [{'index': 0, 'delta': {'content': 'OK'}, 'finish_reason': None}],
                }
                return httpx.Response(
                    200, headers={'content-type': 'text/event-stream'},
                    text=f'data: {json.dumps(chunk)}\n\ndata: [DONE]\n\n',
                )
            return httpx.Response(200, json={
                'id': 'test', 'object': 'chat.completion', 'created': 0, 'model': name,
                'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': 'OK'},
                             'finish_reason': 'stop'}],
                'usage': {'prompt_tokens': 1, 'completion_tokens': 1, 'total_tokens': 2},
            })

        credential = self.provider.get_model_credential('LLM', name)
        options = credential.get_model_params_setting_form(name).get_default_form_data()
        options.update(params or {})
        with httpx.Client(transport=httpx.MockTransport(respond)) as client:
            model = self.provider.get_model(
                'LLM', name, {'api_key': 'test-key', 'api_base': base},
                http_client=client, max_retries=0, **options,
            )
            messages = [HumanMessage(content=content)]
            result = ''.join(chunk.content for chunk in model.stream(messages)) if stream else model.invoke(messages).content
            self.assertEqual(result, 'OK')
        self.assertEqual(len(captured), 1)
        return captured[0]

    def test_current_catalog_and_default(self):
        self.assertEqual(
            [model['name'] for model in self.provider.get_model_list('LLM')],
            ['MiniMax-M3.1-Flash', 'MiniMax-M3'],
        )
        manager = self.provider.get_model_info_manage()
        self.assertEqual(manager.default_model_dict['LLM'].name, 'MiniMax-M3.1-Flash')

    def test_default_and_regional_requests(self):
        for name in ('MiniMax-M3.1-Flash', 'MiniMax-M3'):
            for base in (None, 'https://api.minimaxi.com/v1', 'https://api.minimax.io/v1'):
                for stream in (False, True):
                    with self.subTest(name=name, base=base, stream=stream):
                        url, body = self.capture(name, base, stream=stream)
                        self.assertEqual(url, (base or 'https://api.minimaxi.com/v1') + '/chat/completions')
                        self.assertEqual(body['model'], name)
                        self.assertEqual(body['max_completion_tokens'], 8192)
                        self.assertEqual(body['temperature'], 1.0)
                        self.assertTrue(body['reasoning_split'])
                        # Omission uses adaptive thinking and the API's default effort.
                        for key in ('thinking', 'reasoning_effort', 'service_tier'):
                            self.assertNotIn(key, body)

    def test_saved_and_custom_names_survive_default_adapter_lookup(self):
        for name in ('MiniMax-M2.7', 'MiniMax-M2.7-highspeed', 'MiniMax-M2.5',
                     'MiniMax-M2.5-highspeed', 'saved-custom-model'):
            with self.subTest(name=name):
                url, body = self.capture(name, 'https://proxy.example/v1', {'max_tokens': 321})
                self.assertEqual(url, 'https://proxy.example/v1/chat/completions')
                self.assertEqual(body['model'], name)
                self.assertEqual(body['max_completion_tokens'], 321)

    def test_flash_output_limit_is_model_specific(self):
        for name, maximum in (('MiniMax-M3.1-Flash', 524288), ('MiniMax-M3', 192000),
                              ('MiniMax-M2.7', 192000), ('saved-custom-model', 192000)):
            with self.subTest(name=name):
                form = self.provider.get_model_credential('LLM', name).get_model_params_setting_form(name)
                self.assertEqual(form.max_tokens.attrs['max'], maximum)
                self.assertEqual(form.get_default_form_data()['max_tokens'], 8192)
                self.assertEqual(next(field for field in form.to_form_list() if field['field'] == 'max_tokens')
                                 ['attrs']['max'], maximum)
        _, body = self.capture('MiniMax-M3.1-Flash', params={'max_tokens': 524288})
        self.assertEqual(body['max_completion_tokens'], 524288)

    def test_explicit_thinking_effort_and_multimodal_content(self):
        content = [
            {'type': 'text', 'text': 'Describe this image'},
            {'type': 'image_url', 'image_url': {'url': 'https://example.com/image.png'}},
        ]
        for effort in ('low', 'medium', 'high', 'xhigh', 'max'):
            with self.subTest(effort=effort):
                _, body = self.capture('MiniMax-M3.1-Flash', params={
                    'reasoning_effort': effort, 'extra_body': {'thinking': {'type': 'adaptive'}},
                }, content=content)
                self.assertEqual(body['reasoning_effort'], effort)
                self.assertEqual(body['thinking'], {'type': 'adaptive'})
                self.assertEqual(body['messages'][0]['content'], content)
                self.assertTrue(body['reasoning_split'])
                self.assertNotIn('service_tier', body)
        _, body = self.capture('MiniMax-M3', params={'extra_body': {'thinking': {'type': 'disabled'}}})
        self.assertEqual(body['thinking'], {'type': 'disabled'})

    def test_nontext_catalogs_are_preserved(self):
        expected = {
            'TTS': ['speech-2.8-hd', 'speech-2.8-turbo'],
            'TTI': ['image-01'],
            'TTV': ['MiniMax-H3', 'MiniMax-H3-Max', 'MiniMax-Hailuo-2.3'],
            'ITV': ['MiniMax-H3', 'MiniMax-H3-Max', 'MiniMax-Hailuo-2.3'],
        }
        for model_type, names in expected.items():
            with self.subTest(model_type=model_type):
                self.assertEqual([model['name'] for model in self.provider.get_model_list(model_type)], names)
                self.assertEqual(self.provider.get_model_info_manage().default_model_dict[model_type].name, names[0])


if __name__ == '__main__':
    unittest.main()
