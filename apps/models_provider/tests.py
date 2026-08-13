import inspect

from django.test import SimpleTestCase

from common.exception.app_exception import AppApiException
from models_provider.base_model_provider import MaxKBBaseEmbeddingModel, ModelTypeConst
from models_provider.constants.model_provider_constants import ModelProvideConstants


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
            for model_info in provider.value.get_model_info_manage().model_list
            if model_info.model_type == ModelTypeConst.EMBEDDING.name
        }

        self.assertTrue(embedding_classes)
        for embedding_class in embedding_classes:
            with self.subTest(embedding_class=embedding_class.__name__):
                self.assertTrue(issubclass(embedding_class, MaxKBBaseEmbeddingModel))
                self.assertIn("supports_image_embedding", embedding_class.__dict__)
                self.assertFalse(inspect.isabstract(embedding_class))


# Create your tests here.
