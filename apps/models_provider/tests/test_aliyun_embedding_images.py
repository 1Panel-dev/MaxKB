"""Qwen3 image inputs preserve document images while meeting processor dimensions."""

import base64
import os
from unittest import skipUnless
from unittest.mock import patch
from urllib.parse import quote

import dashscope
import resvg_py
from django.test import SimpleTestCase
from PIL import UnidentifiedImageError

from models_provider.impl.aliyun_bai_lian_model_provider.model.embedding import AliyunBaiLianEmbedding
from models_provider.tests.image_helpers import decode_image, image_data_url, svg_data_url


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

    def test_svg_is_rendered_to_png_without_changing_the_source(self):
        original = svg_data_url()
        with self.assertRaises(UnidentifiedImageError):
            decode_image(original)

        result = self.model._prepare_image_input(original)

        self.assertTrue(result.startswith("data:image/png;base64,"))
        with decode_image(result) as rendered:
            self.assertEqual(rendered.format, "PNG")
            self.assertEqual(rendered.size, (88, 32))
            pixels = rendered.convert("RGB")
            self.assertEqual(pixels.getpixel((0, 6)), (255, 0, 0))
            self.assertEqual(pixels.getpixel((87, 25)), (255, 0, 0))
            self.assertEqual(pixels.getpixel((0, 5)), (255, 255, 255))
            self.assertEqual(pixels.getpixel((87, 26)), (255, 255, 255))
        self.assertEqual(original, svg_data_url())

    def test_svg_badge_with_embedded_svg_logo_and_links_is_rendered(self):
        logo = svg_data_url(size=(20, 20))
        for embedded in (logo, "data:image/svg+xml," + quote(base64.b64decode(logo.split(",", 1)[1]))):
            with self.subTest(embedded_encoding=embedded.split(",", 1)[0]):
                badge = svg_data_url(
                    '<a xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="https://example.com">'
                    f'<image width="20" height="20" xlink:href="{embedded}"/></a>'
                )
                with decode_image(self.model._prepare_image_input(badge)) as rendered:
                    self.assertEqual(rendered.size, (88, 32))
                    pixels = rendered.convert("RGB")
                    self.assertEqual(pixels.getpixel((19, 16)), (255, 0, 0))
                    self.assertEqual(pixels.getpixel((20, 16)), (255, 255, 255))

    def test_svg_with_embedded_raster_keeps_image_content(self):
        raster = image_data_url((20, 20), color="blue")
        original = svg_data_url(f'<image width="20" height="20" href="{raster}"/>')
        with decode_image(self.model._prepare_image_input(original)) as rendered:
            self.assertEqual(rendered.size, (88, 32))
            self.assertEqual(rendered.convert("RGB").getpixel((19, 16)), (0, 0, 255))
            self.assertEqual(rendered.convert("RGB").getpixel((20, 16)), (255, 255, 255))

    def test_svg_render_size_is_bounded_and_thin_svg_is_padded(self):
        for size, expected in (
            ((100000, 50000), (2048, 1024)),
            ((50000, 100000), (1024, 2048)),
            ((1024, 768), (1024, 768)),
            ((2048, 1024), (2048, 1024)),
            ((756, 2), (756, 32)),
            ((2, 756), (32, 756)),
            ((2, 3), (32, 32)),
        ):
            with self.subTest(size=size):
                with decode_image(self.model._prepare_image_input(svg_data_url(size=size))) as rendered:
                    self.assertEqual(rendered.size, expected)

    def test_svg_viewport_supports_viewbox_units_and_percentage_dimensions(self):
        for attributes, expected in (
            ('viewBox="0 0 88 20"', (88, 32)),
            ('viewBox="0,0,4096,2048"', (2048, 1024)),
            ('width="88px" height="20px"', (88, 32)),
            ('width="1in" height="0.5in"', (96, 48)),
            ('width="25.4mm" height="12.7mm"', (96, 48)),
            ('width="72pt" height="36pt"', (96, 48)),
            ('width="50%" height="50%" viewBox="0 0 176 40"', (88, 32)),
            ('width="200%" height="200%" viewBox="0 0 4096 2048"', (2048, 1024)),
            ('width="1e2" height="5e1"', (100, 50)),
            ("", (300, 150)),
        ):
            with self.subTest(attributes=attributes):
                with decode_image(self.model._prepare_image_input(svg_data_url(attributes=attributes))) as rendered:
                    self.assertEqual(rendered.size, expected)
                    self.assertEqual(
                        rendered.convert("RGB").getpixel((rendered.width // 2, rendered.height // 2)), (255, 0, 0)
                    )

    def test_large_svg_is_rasterized_once_at_bounded_resolution(self):
        render = resvg_py.svg_to_bytes

        def bounded_render(**kwargs):
            self.assertEqual((kwargs["width"], kwargs["height"]), (2048, 1024))
            return render(**kwargs)

        with patch.object(resvg_py, "svg_to_bytes", side_effect=bounded_render) as renderer:
            self.model._prepare_image_input(svg_data_url(size=(100000, 50000)))
        self.assertEqual(renderer.call_count, 1)

    def test_invalid_svg_dimensions_are_rejected_before_rendering(self):
        for attributes in ('width="0" height="20"', 'width="1e999" height="20"', 'viewBox="0 0 -88 20"'):
            with self.subTest(attributes=attributes):
                with self.assertRaisesRegex(ValueError, "Invalid SVG"):
                    self.model._prepare_image_input(svg_data_url(attributes=attributes))

    def test_svg_external_resources_are_rejected_including_nested_svg(self):
        for reference in ("file:///tmp/private.png", "/tmp/private.png", "https://example.com/image.png"):
            external = svg_data_url(f'<image href="{reference}" width="20" height="20"/>')
            for original in (external, svg_data_url(f'<image href="{external}" width="20" height="20"/>')):
                with self.subTest(reference=reference, nested=original != external):
                    with self.assertRaisesRegex(ValueError, "external resources"):
                        self.model._prepare_image_input(original)

    def test_svg_nesting_is_bounded(self):
        nested = svg_data_url()
        for _ in range(6):
            nested = svg_data_url(f'<image href="{nested}" width="20" height="20"/>')
        with self.assertRaisesRegex(ValueError, "nesting"):
            self.model._prepare_image_input(nested)

    def test_invalid_image_bytes_are_not_silently_dropped(self):
        invalid = "data:image/png;base64," + base64.b64encode(b"not an image").decode("ascii")
        with self.assertRaises(UnidentifiedImageError):
            self.model._prepare_image_input(invalid)

    def test_remote_urls_are_not_downloaded(self):
        url = "https://example.com/image.png"
        self.assertEqual(self.model._prepare_image_input(url), url)

    def test_other_models_keep_their_existing_image_input(self):
        self.model.model_name = "tongyi-embedding-vision-plus"
        original = image_data_url((756, 2))
        self.assertEqual(self.model._prepare_image_input(original), original)


class AliyunImageRequestTests(SimpleTestCase):
    def setUp(self):
        self.model = AliyunBaiLianEmbedding("test-key", "qwen3-vl-embedding", "http://127.0.0.1:0/api/v1", {})

    @patch.object(AliyunBaiLianEmbedding, "_call_multimodal")
    def test_images_are_requested_individually_in_order(self, call):
        for count in (0, 1, 10, 11, 15, 20, 21):
            with self.subTest(count=count):
                call.reset_mock()
                call.side_effect = lambda items: [[float(item["image"].rsplit("/", 1)[1])] for item in items]
                images = [f"https://example.com/{index}" for index in range(count)]

                vectors = self.model.embed_images(images)

                self.assertEqual(vectors, [[float(index)] for index in range(count)])
                batches = [invocation.args[0] for invocation in call.call_args_list]
                self.assertEqual([len(batch) for batch in batches], [1] * count)
                self.assertEqual([item["image"] for batch in batches for item in batch], images)

    @patch.object(AliyunBaiLianEmbedding, "_call_multimodal")
    def test_later_image_failure_propagates_without_returning_partial_vectors(self, call):
        error = RuntimeError("second image failed")
        call.side_effect = [[[0.1]], error]

        with self.assertRaises(RuntimeError) as caught:
            self.model.embed_images(["https://example.com/image.png"] * 21)

        self.assertIs(caught.exception, error)
        self.assertEqual(call.call_count, 2)

    @patch.object(AliyunBaiLianEmbedding, "_call_multimodal")
    def test_response_must_contain_exactly_one_vector(self, call):
        for vectors in ([], [[0.1], [0.2]]):
            with self.subTest(vectors=vectors):
                call.reset_mock()
                call.return_value = vectors

                with self.assertRaisesRegex(ValueError, "unexpected number of image embeddings"):
                    self.model.embed_images(["https://example.com/image.png"] * 15)

                call.assert_called_once()

    @patch.object(AliyunBaiLianEmbedding, "_call_multimodal")
    def test_other_multimodal_models_also_request_each_image_individually(self, call):
        for model_name in ("tongyi-embedding-vision-plus", "qwen2.5-vl-embedding", "multimodal-embedding-v1"):
            with self.subTest(model_name=model_name):
                self.model.model_name = model_name
                call.reset_mock()
                call.return_value = [[0.1]]

                self.assertEqual(len(self.model.embed_images(["https://example.com/image.png"] * 15)), 15)

                self.assertEqual(call.call_count, 15)
                self.assertTrue(all(len(invocation.args[0]) == 1 for invocation in call.call_args_list))

    @patch.object(AliyunBaiLianEmbedding, "_call_multimodal")
    def test_non_image_model_does_not_send_images(self, call):
        self.model.model_name = "text-embedding-v4"

        self.assertEqual(self.model.embed_images(["https://example.com/image.png"]), [])

        call.assert_not_called()


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

    def test_document_images_pass_through_real_sdk_individually_after_padding(self):
        sizes = ((756, 2), (2, 197), (537, 2), (9, 192), (831, 82), (561, 75), (153, 1), (827, 2), (711, 2), (897, 4))
        vectors = self.model.embed_images([image_data_url(size) for size in sizes])
        self.assertEqual([vector[0] for vector in vectors], [0] * len(sizes))
        self.assertEqual([vector[1:3] for vector in vectors], [[max(32, w), max(32, h)] for w, h in sizes])
        self.assertTrue(all(len(vector) == 256 for vector in vectors))

    def test_large_image_lists_preserve_count_and_order_through_real_sdk(self):
        for count in (11, 15, 20, 21):
            with self.subTest(count=count):
                sizes = [(40 + index, 32) for index in range(count)]

                vectors = self.model.embed_images([image_data_url(size) for size in sizes])

                self.assertEqual(len(vectors), count)
                self.assertEqual([vector[0] for vector in vectors], [0] * count)
                self.assertEqual([vector[1:3] for vector in vectors], [list(size) for size in sizes])
                self.assertTrue(all(len(vector) == 256 for vector in vectors))

    def test_svg_and_raster_images_pass_through_real_sdk_individually_in_order(self):
        logo = svg_data_url(size=(20, 20))
        badge = svg_data_url(f'<image href="{logo}" width="20" height="20"/>')
        vectors = self.model.embed_images([image_data_url((32, 32)), badge, image_data_url((756, 2))])
        self.assertEqual([vector[0] for vector in vectors], [0, 0, 0])
        self.assertEqual([vector[1:3] for vector in vectors], [[32, 32], [88, 32], [756, 32]])
        self.assertTrue(all(len(vector) == 256 for vector in vectors))

    def test_text_embeddings_keep_the_existing_request_contract(self):
        vectors = self.model.embed_documents(["first", "second"])
        self.assertEqual([vector[0] for vector in vectors], [0, 1])
