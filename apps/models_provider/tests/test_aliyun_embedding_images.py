"""Qwen3 image inputs preserve document images while meeting processor dimensions."""

import base64
import os
from io import BytesIO
from unittest import skipUnless

import dashscope
from django.test import SimpleTestCase
from PIL import Image

from models_provider.impl.aliyun_bai_lian_model_provider.model.embedding import AliyunBaiLianEmbedding


def image_data_url(size, mode="RGB", color="black", image_format="PNG"):
    output = BytesIO()
    Image.new(mode, size, color).save(output, format=image_format)
    mime = "image/jpeg" if image_format == "JPEG" else "image/png"
    return f"data:{mime};base64," + base64.b64encode(output.getvalue()).decode("ascii")


def decode_image(data_url):
    return Image.open(BytesIO(base64.b64decode(data_url.split(";base64,", 1)[1])))


class AliyunImagePreparationTests(SimpleTestCase):
    def setUp(self):
        self.model = AliyunBaiLianEmbedding("test-key", "qwen3-vl-embedding", "http://127.0.0.1:0/api/v1", {})

    def test_thin_document_images_are_padded_with_original_pixels_preserved(self):
        for size in ((756, 2), (2, 197), (537, 2), (9, 192), (153, 1), (827, 2), (711, 2), (897, 4)):
            with self.subTest(size=size):
                original = image_data_url(size)
                with decode_image(self.model._prepare_image_input(original)) as result:
                    self.assertGreaterEqual(min(result.size), 32)
                    self.assertLessEqual(max(result.size) / min(result.size), 200)
                    left, top = (result.width - size[0]) // 2, (result.height - size[1]) // 2
                    self.assertEqual(result.getpixel((left, top)), (0, 0, 0))
                    self.assertEqual(result.getpixel((left + size[0] - 1, top + size[1] - 1)), (0, 0, 0))
                    self.assertEqual(result.getpixel((0, 0)), (255, 255, 255))
                with decode_image(original) as unchanged:
                    self.assertEqual(unchanged.size, size)

    def test_large_aspect_ratio_is_padded_even_when_both_sides_exceed_one_patch(self):
        with decode_image(self.model._prepare_image_input(image_data_url((8001, 32)))) as result:
            self.assertEqual(result.size, (8001, 41))
            self.assertLessEqual(result.width / result.height, 200)

    def test_valid_images_and_ratio_boundary_are_not_reencoded(self):
        for size in ((831, 82), (561, 75), (32, 32), (6400, 32)):
            original = image_data_url(size)
            self.assertEqual(self.model._prepare_image_input(original), original)

    def test_transparent_pixels_are_composited_onto_white(self):
        original = image_data_url((2, 3), "RGBA", (0, 0, 0, 0))
        with decode_image(self.model._prepare_image_input(original)) as result:
            self.assertEqual(result.mode, "RGB")
            self.assertEqual(result.getextrema(), ((255, 255), (255, 255), (255, 255)))

    def test_thin_jpeg_is_returned_as_a_valid_png_data_url(self):
        result = self.model._prepare_image_input(image_data_url((2, 197), image_format="JPEG"))
        self.assertTrue(result.startswith("data:image/png;base64,"))
        with decode_image(result) as image:
            self.assertEqual(image.format, "PNG")
            self.assertEqual(image.size, (32, 197))

    def test_remote_urls_are_not_downloaded(self):
        url = "https://example.com/image.png"
        self.assertEqual(self.model._prepare_image_input(url), url)

    def test_other_models_keep_their_existing_image_input(self):
        self.model.model_name = "tongyi-embedding-vision-plus"
        original = image_data_url((756, 2))
        self.assertEqual(self.model._prepare_image_input(original), original)


@skipUnless(os.environ.get("ALIYUN_EMBEDDING_TEST_URL"), "Start the local Aliyun Postman simulation")
class AliyunImageHTTPTests(SimpleTestCase):
    def setUp(self):
        previous_key, previous_url = dashscope.api_key, dashscope.base_http_api_url
        self.addCleanup(setattr, dashscope, "api_key", previous_key)
        self.addCleanup(setattr, dashscope, "base_http_api_url", previous_url)
        self.model = AliyunBaiLianEmbedding(
            "test-key", "qwen3-vl-embedding", os.environ["ALIYUN_EMBEDDING_TEST_URL"], {"dimension": 256}
        )

    def test_original_thin_image_reproduces_processor_rejection(self):
        with self.assertRaisesRegex(Exception, "status=400.*processor error"):
            self.model._call_multimodal([{"image": image_data_url((756, 2))}])

    def test_document_image_batch_passes_through_real_sdk_after_padding(self):
        sizes = ((756, 2), (2, 197), (537, 2), (9, 192), (831, 82), (561, 75), (153, 1), (827, 2), (711, 2), (897, 4))
        vectors = self.model.embed_images([image_data_url(size) for size in sizes])
        self.assertEqual([vector[0] for vector in vectors], list(range(len(sizes))))
        self.assertTrue(all(len(vector) == 256 for vector in vectors))

    def test_text_embeddings_keep_the_existing_request_contract(self):
        vectors = self.model.embed_documents(["first", "second"])
        self.assertEqual([vector[0] for vector in vectors], [0, 1])
