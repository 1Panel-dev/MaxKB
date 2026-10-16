import inspect
import os
from unittest import skipUnless

from django.test import SimpleTestCase

from common.exception.app_exception import AppApiException
from models_provider.base_model_provider import MaxKBBaseEmbeddingModel, ModelTypeConst
from models_provider.constants.model_provider_constants import ModelProvideConstants
from models_provider.impl.aliyun_bai_lian_model_provider.model.embedding import AliyunBaiLianEmbedding
from models_provider.impl.siliconCloud_model_provider.model.embedding import SiliconCloudEmbeddingModel


class MissingImageCapabilityEmbedding(MaxKBBaseEmbeddingModel):
    @staticmethod
    def new_instance(model_type, model_name, model_credential, **model_kwargs):
        return MissingImageCapabilityEmbedding()


class TextOnlyEmbedding(MaxKBBaseEmbeddingModel):
    @staticmethod
    def new_instance(model_type, model_name, model_credential, **model_kwargs):
        return TextOnlyEmbedding()

    def supports_image_embedding(self) -> bool:
        return False


class EmbeddingCapabilityContractTests(SimpleTestCase):
    def test_text_only_siliconflow_model_rejects_image_embedding(self):
        model = SiliconCloudEmbeddingModel("test-key", "BAAI/bge-m3", "http://127.0.0.1:0/v1", {})

        with self.assertRaises(AppApiException):
            model.embed_images(["https://example.com/chart.png"])

    def test_empty_siliconflow_image_input_returns_no_embeddings(self):
        model = SiliconCloudEmbeddingModel("test-key", "Qwen/Qwen3-VL-Embedding-8B", "http://127.0.0.1:0/v1", {})

        self.assertEqual(model.embed_images([]), [])

    def test_multimodal_model_detection_is_case_insensitive(self):
        for embedding_class in (AliyunBaiLianEmbedding, SiliconCloudEmbeddingModel):
            for model_name, expected in (
                ("qwen3-vl-embedding", True),
                ("Qwen/Qwen3-VL-Embedding-8B", True),
                ("EMBEDDING-VISION", True),
                ("MultiModal-Embedding", True),
                ("TEXT-EMBEDDING-V4", False),
                ("", False),
            ):
                with self.subTest(provider=embedding_class.__name__, model_name=model_name):
                    self.assertEqual(embedding_class._is_multimodal(model_name), expected)

    def test_capability_declaration_is_abstract(self):
        self.assertTrue(inspect.isabstract(MissingImageCapabilityEmbedding))

    def test_unsupported_provider_uses_consistent_image_embedding_error(self):
        model = TextOnlyEmbedding()

        self.assertFalse(model.supports_image_embedding())
        with self.assertRaises(AppApiException):
            model.embed_images(["data:image/png;base64,AA=="])

    def test_every_registered_embedding_provider_declares_image_capability(self):
        embedding_classes = {
            model_info.model_class
            for provider in ModelProvideConstants
            for model_info in ModelProvideConstants[provider].get_model_info_manage().model_list
            if model_info.model_type == ModelTypeConst.EMBEDDING.name
        }

        self.assertTrue(embedding_classes)
        for embedding_class in embedding_classes:
            with self.subTest(embedding_class=embedding_class.__name__):
                self.assertTrue(issubclass(embedding_class, MaxKBBaseEmbeddingModel))
                self.assertIn("supports_image_embedding", embedding_class.__dict__)
                self.assertFalse(inspect.isabstract(embedding_class))


@skipUnless(os.environ.get("SILICONFLOW_EMBEDDING_TEST_URL"), "Start the local SiliconFlow Postman simulation")
class SiliconCloudEmbeddingHTTPTests(SimpleTestCase):
    """Exercise the real HTTP client against fixtures/siliconflow.sim.yaml, with a dummy API key."""

    def setUp(self):
        self.model = SiliconCloudEmbeddingModel(
            "test-key", "Qwen/Qwen3-VL-Embedding-8B", os.environ["SILICONFLOW_EMBEDDING_TEST_URL"], {"dimensions": 2}
        )

    def test_embeds_each_image_independently_in_input_order(self):
        images = ["https://example.com/chart.png", "data:image/png;base64,aW1hZ2U="]

        self.assertEqual(self.model.embed_images(images), [[1.0, 0.0], [0.0, 1.0]])

    def test_preserves_text_query_and_document_embedding(self):
        self.assertEqual(self.model.embed_query("first text"), [0.25, 0.75])
        self.assertEqual(self.model.embed_documents(["first text", "second text"]), [[0.25, 0.75], [0.75, 0.25]])

    def test_handles_a_base_url_with_a_trailing_slash(self):
        self.model.base_url += "/"

        self.assertEqual(self.model.embed_images(["https://example.com/chart.png"]), [[1.0, 0.0]])
