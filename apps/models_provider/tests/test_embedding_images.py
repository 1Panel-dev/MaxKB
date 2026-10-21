"""Shared SVG preparation and real provider clients against local HTTP fixtures."""

import base64
import os
from io import BytesIO
from unittest import skipUnless
from urllib.parse import quote

import dashscope
from django.test import SimpleTestCase
from PIL import Image

from models_provider.embedding_image import prepare_embedding_image
from models_provider.impl.aliyun_bai_lian_model_provider.model.embedding import AliyunBaiLianEmbedding
from models_provider.impl.siliconCloud_model_provider.model.embedding import SiliconCloudEmbeddingModel
from models_provider.impl.tencent_model_provider.model.embedding import TencentEmbeddingModel
from models_provider.impl.volcanic_engine_model_provider.model.embedding import VolcanicEngineEmbeddingModel
from models_provider.tests.image_helpers import decode_image, image_data_url, svg_data_url


class EmbeddingImagePreparationTests(SimpleTestCase):
    def test_svg_without_model_limits_keeps_its_intrinsic_size(self):
        for size in ((88, 20), (2, 3), (756, 2), (1024, 768)):
            with self.subTest(size=size), decode_image(prepare_embedding_image(svg_data_url(size=size))) as result:
                self.assertEqual(result.size, size)
                self.assertEqual(result.convert("RGB").getpixel((0, 0)), (255, 0, 0))

    def test_percent_encoded_svg_is_also_rendered(self):
        svg = base64.b64decode(svg_data_url().split(",", 1)[1])
        with decode_image(prepare_embedding_image("data:image/svg+xml," + quote(svg))) as result:
            self.assertEqual(result.size, (88, 20))

    def test_model_minimum_side_pads_without_scaling_pixels(self):
        for minimum in (28, 32, 64):
            with self.subTest(minimum=minimum):
                with decode_image(prepare_embedding_image(svg_data_url(), min_side=minimum)) as result:
                    self.assertEqual(result.size, (88, minimum))
                    pixels = result.convert("RGB")
                    top = (minimum - 20) // 2
                    self.assertEqual(pixels.getpixel((0, top - 1)), (255, 255, 255))
                    self.assertEqual(pixels.getpixel((87, top + 19)), (255, 0, 0))

    def test_minimum_pixel_area_only_adds_the_required_canvas(self):
        for size, expected in (((88, 20), (88, 47)), ((20, 88), (47, 88)), ((2, 3), (64, 64))):
            with self.subTest(size=size):
                with decode_image(prepare_embedding_image(svg_data_url(size=size), min_pixels=4096)) as result:
                    self.assertEqual(result.size, expected)
                    self.assertGreaterEqual(result.width * result.height, 4096)
                    left, top = (result.width - size[0]) // 2, (result.height - size[1]) // 2
                    self.assertEqual(result.getpixel((left, top)), (255, 0, 0))
                    self.assertEqual(result.getpixel((left + size[0] - 1, top + size[1] - 1)), (255, 0, 0))

    def test_svg_rendering_honors_both_maximum_side_and_pixel_area(self):
        for size in ((100000, 50000), (50000, 100000), (4096, 4096), (2048, 2048)):
            with self.subTest(size=size):
                with decode_image(prepare_embedding_image(svg_data_url(size=size), max_svg_pixels=1843200)) as result:
                    self.assertLessEqual(max(result.size), 2048)
                    self.assertLessEqual(result.width * result.height, 1843200)
        with decode_image(prepare_embedding_image(svg_data_url(size=(4096, 2048)), max_svg_side=1024)) as result:
            self.assertEqual(result.size, (1024, 512))

    def test_valid_raster_inputs_keep_their_original_encoding(self):
        for options, size in (({}, (2, 3)), ({"min_pixels": 4096}, (256, 16)), ({"min_side": 32}, (64, 64))):
            with self.subTest(options=options):
                original = image_data_url(size, image_format="JPEG")
                self.assertEqual(prepare_embedding_image(original, **options), original)

    def test_padding_preserves_exif_orientation(self):
        image = Image.new("RGB", (88, 20), "red")
        exif = Image.Exif()
        exif[274] = 6
        output = BytesIO()
        image.save(output, format="JPEG", exif=exif)
        original = "data:image/jpeg;base64," + base64.b64encode(output.getvalue()).decode("ascii")
        with decode_image(prepare_embedding_image(original, min_pixels=4096)) as result:
            self.assertEqual(result.size, (47, 88))
            self.assertEqual(result.getpixel((0, 0)), (255, 255, 255))
            self.assertGreater(result.getpixel((23, 44))[0], 250)

    def test_remote_urls_and_opaque_inputs_are_unchanged(self):
        for original in ("https://example.com/image.svg", "https://example.com/image.png", "cHJvdmlkZXItaW5wdXQ="):
            self.assertEqual(prepare_embedding_image(original, min_side=32), original)


@skipUnless(os.environ.get("MULTIMODAL_EMBEDDING_TEST_URL"), "Start the local multimodal Postman simulation")
class SharedEmbeddingImageHTTPTests(SimpleTestCase):
    def setUp(self):
        previous_key, previous_url = dashscope.api_key, dashscope.base_http_api_url
        self.addCleanup(setattr, dashscope, "api_key", previous_key)
        self.addCleanup(setattr, dashscope, "base_http_api_url", previous_url)
        base = os.environ["MULTIMODAL_EMBEDDING_TEST_URL"].rstrip("/")
        self.models = (
            (
                "aliyun-qwen3",
                AliyunBaiLianEmbedding("test-key", "qwen3-vl-embedding", base + "/aliyun/api/v1", {"dimension": 256}),
                1,
                (88, 32),
                (2048, 1024),
            ),
            (
                "aliyun-tongyi",
                AliyunBaiLianEmbedding("test-key", "tongyi-embedding-vision-plus", base + "/aliyun/api/v1", {}),
                1,
                (88, 20),
                (2048, 1024),
            ),
            (
                "siliconflow",
                SiliconCloudEmbeddingModel(
                    "test-key", "Qwen/Qwen3-VL-Embedding-8B", base + "/siliconflow/v1", {"dimensions": 2}
                ),
                0,
                (88, 32),
                (2048, 1024),
            ),
            (
                "tencent",
                TencentEmbeddingModel("test-key", "kinfra-vl-embedding-2b", base + "/multimodal/v1"),
                0,
                (88, 47),
                (1920, 960),
            ),
            (
                "volcengine",
                VolcanicEngineEmbeddingModel("test-key", "doubao-embedding-vision-251215", base + "/multimodal/api/v3"),
                0,
                (88, 20),
                (2048, 1024),
            ),
        )

    def test_all_providers_send_prepared_pngs_in_their_own_request_format(self):
        inputs = [svg_data_url(), svg_data_url(size=(4096, 2048)), image_data_url((96, 64))]
        for provider, model, offset, small_size, large_size in self.models:
            with self.subTest(provider=provider):
                vectors = model.embed_images(inputs)
                self.assertEqual(
                    [tuple(vector[offset : offset + 2]) for vector in vectors], [small_size, large_size, (96, 64)]
                )

    def test_new_provider_fixtures_preserve_text_requests(self):
        for provider, model, _, _, _ in self.models[-2:]:
            with self.subTest(provider=provider):
                self.assertEqual(model.embed_documents(["first", "second"]), [[0.25, 0.75], [0.75, 0.25]])

    def test_new_provider_fixtures_receive_remote_urls_without_downloading(self):
        for provider, model, _, _, _ in self.models[-2:]:
            with self.subTest(provider=provider):
                self.assertEqual(model.embed_images(["https://example.com/image.svg"]), [[1.0, 0.0]])

    def test_invalid_svg_is_rejected_by_each_provider_before_http(self):
        invalid = svg_data_url('<image href="file:///private/image.png"/>')
        for provider, model, _, _, _ in self.models:
            with self.subTest(provider=provider), self.assertRaisesRegex(ValueError, "external resources"):
                model.embed_images([invalid])
