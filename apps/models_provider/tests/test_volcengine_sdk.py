"""Verify the split Ark SDK through the application's real model adapters."""

import os
from unittest import skipUnless
from unittest.mock import patch

from django.test import SimpleTestCase
from volcenginesdkarkruntime import Ark
from volcenginesdkarkruntime._exceptions import ArkAPIStatusError

from models_provider.impl.volcanic_engine_model_provider.model.embedding import VolcanicEngineEmbeddingModel
from models_provider.impl.volcanic_engine_model_provider.model.tti import VolcanicEngineTextToImage
from models_provider.impl.volcanic_engine_model_provider.model.ttv import GenerationVideoModel
from models_provider.tests.image_helpers import svg_data_url


@skipUnless(os.environ.get("VOLCENGINE_SDK_TEST_URL"), "Start the local Volcengine SDK Postman simulation")
class VolcengineSdkCompatibilityTests(SimpleTestCase):
    def setUp(self):
        self.base = os.environ["VOLCENGINE_SDK_TEST_URL"].rstrip("/")

    def embedding(self, model="fixture-embedding", api_key="fixture-key"):
        result = VolcanicEngineEmbeddingModel(api_key, model, self.base + "/ark/api/v3", dimensions=2)
        result.client.max_retries = 0
        self.addCleanup(result.client.close)
        return result

    def test_text_embedding_preserves_batch_order_and_query_shape(self):
        model = self.embedding()
        self.assertEqual(model.embed_documents(["文档", "hello", "文档"]), [[2, 0], [5, 1], [2, 2]])
        self.assertEqual(model.embed_query("查询"), [2, 0])

    def test_multimodal_embeddings_reuse_the_existing_image_contract(self):
        model = VolcanicEngineEmbeddingModel(
            "test-key", "doubao-embedding-vision-251215", self.base + "/multimodal/api/v3"
        )
        self.addCleanup(model.client.close)
        self.assertEqual(model.embed_documents(["first", "second"]), [[0.25, 0.75], [0.75, 0.25]])
        self.assertEqual(model.embed_images([svg_data_url()]), [[88, 20]])

    def test_image_generation_preserves_urls_and_base64(self):
        for response_format, expected in [("url", "https://fixture.invalid/image.png"), ("b64_json", "aW1hZ2U=")]:
            with self.subTest(response_format=response_format):
                model = VolcanicEngineTextToImage.new_instance(
                    "TEXT_TO_IMAGE",
                    "fixture-image",
                    {"api_key": "fixture-key", "volcanic_api_url": self.base + "/ark/api/v3"},
                    response_format=response_format,
                    size="1024x1024",
                    watermark=False,
                )
                self.assertEqual(model.generate_image("测试图片"), [expected])

    def test_video_task_is_polled_to_completion_then_deleted(self):
        model = GenerationVideoModel.new_instance(
            "TEXT_TO_VIDEO",
            "fixture-video",
            {"api_key": "fixture-key", "base_url": self.base + "/ark/api/v3"},
            duration="5",
            seed="42",
            camerafixed=True,
        )
        with patch("models_provider.impl.volcanic_engine_model_provider.model.ttv.time.sleep") as sleep:
            result = model.generate_video("测试视频", first_frame_url="https://fixture.invalid/first.png")
        sleep.assert_called_once_with(30)
        self.assertTrue(result.startswith("https://fixture.invalid/fixture-"))
        task_id = result.rsplit("/", 1)[1].removesuffix(".mp4")
        with Ark(api_key="fixture-key", base_url=self.base + "/ark/api/v3", max_retries=0) as client:
            with self.assertRaises(ArkAPIStatusError) as raised:
                client.content_generation.tasks.get(task_id=task_id)
        self.assertEqual(raised.exception.status_code, 404)

    def test_sdk_errors_preserve_status_instead_of_returning_vectors(self):
        for status in (400, 401, 429, 500):
            with self.subTest(status=status), self.assertRaises(ArkAPIStatusError) as raised:
                self.embedding(f"fixture-error-{status}").embed_query("test")
            self.assertEqual(raised.exception.status_code, status)

    def test_invalid_key_is_rejected(self):
        with self.assertRaises(ArkAPIStatusError) as raised:
            self.embedding(api_key="invalid-fixture-key").embed_query("test")
        self.assertEqual(raised.exception.status_code, 401)
