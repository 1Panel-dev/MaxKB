import json
from types import SimpleNamespace
from unittest.mock import patch
from uuid import UUID

from Crypto.PublicKey import RSA
from django.test import SimpleTestCase

from common.utils.rsa_util import rsa_long_encrypt
from knowledge.services.paragraph_assets import resolve_visual_processor


class VisualToolProcessorTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        key = RSA.generate(2048)
        cls.key_pair = {"key": key.publickey().export_key(), "value": key.export_key()}

    def setUp(self):
        self.asset = SimpleNamespace(file_id=UUID("10000000-0000-0000-0000-000000000001"))
        self.data_url = "data:image/png;base64,aW1hZ2U="
        self.tool = SimpleNamespace(
            code="def enhance_image(image_base64, **kwargs): return {}",
            input_field_list=[{"name": "image_base64"}],
            init_field_list=[
                {"field": "model", "default_value": "default-vision-model"},
                {"field": "api_base", "default_value": "https://example.com/v1"},
            ],
            init_params=None,
        )
        self.enterContext(patch("common.utils.rsa_util.get_key_pair", return_value=self.key_pair))
        self.enterContext(patch("knowledge.services.paragraph_assets.filter_authorized_ids", return_value=["tool-id"]))
        tools = self.enterContext(patch("knowledge.services.paragraph_assets.Tool.objects.filter"))
        tools.return_value.first.return_value = self.tool
        self.enterContext(patch("knowledge.services.paragraph_assets._image_data_url", return_value=self.data_url))
        executor = self.enterContext(patch("knowledge.services.paragraph_assets.ToolExecutor"))
        self.execute = executor.return_value.exec_code
        self.execute.return_value = {"description": "recognized image"}

    def process(self):
        processor = resolve_visual_processor({"strategy": "tool", "tool_id": "tool-id"}, "workspace-1")
        return processor(self.asset, {})

    def test_saved_parameters_are_decrypted_and_override_defaults(self):
        saved = {"api_key": "test-api-key", "model": "saved-vision-model", "image_base64": "stale-image"}
        self.tool.init_params = rsa_long_encrypt(json.dumps(saved))

        self.assertEqual(self.process(), {"description": "recognized image"})

        self.execute.assert_called_once_with(
            self.tool.code,
            {
                "api_base": "https://example.com/v1",
                "api_key": "test-api-key",
                "model": "saved-vision-model",
                "image_base64": "aW1hZ2U=",
            },
        )

    def test_unconfigured_tool_uses_startup_defaults(self):
        self.process()

        self.execute.assert_called_once_with(
            self.tool.code,
            {
                "model": "default-vision-model",
                "api_base": "https://example.com/v1",
                "image_base64": "aW1hZ2U=",
            },
        )

    def test_empty_saved_parameters_use_defaults(self):
        for stored in ("", " \n "):
            with self.subTest(stored=stored):
                self.tool.init_params = stored
                self.process()
                self.assertEqual(self.execute.call_args.args[1]["model"], "default-vision-model")

    def test_decoded_parameters_remain_supported(self):
        self.tool.init_params = {"model": "decoded-model"}

        self.process()

        self.assertEqual(self.execute.call_args.args[1]["model"], "decoded-model")
        self.assertEqual(self.execute.call_args.args[1]["api_base"], "https://example.com/v1")

    def test_declared_image_parameters_receive_the_expected_formats(self):
        self.tool.init_field_list = []
        self.tool.input_field_list = [
            {"name": name} for name in ("file_id", "image", "image_url", "image_base64", "unknown")
        ]

        self.process()

        self.execute.assert_called_once_with(
            self.tool.code,
            {
                "file_id": str(self.asset.file_id),
                "image": self.data_url,
                "image_url": self.data_url,
                "image_base64": "aW1hZ2U=",
            },
        )

    def test_text_result_is_normalized_as_description(self):
        self.execute.return_value = "image description"

        self.assertEqual(self.process(), {"description": "image description"})
