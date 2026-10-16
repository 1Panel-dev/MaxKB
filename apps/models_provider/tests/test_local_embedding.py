from unittest.mock import patch

from django.test import SimpleTestCase

from models_provider.impl.local_model_provider.model.embedding import model


class LocalEmbeddingDeviceTests(SimpleTestCase):
    def test_default_device(self):
        for platform, expected_device in [("darwin", "cpu"), ("linux", None), ("win32", None)]:
            for credential in [{}, {"device": None}]:
                with self.subTest(platform=platform, credential=credential):
                    with (
                        patch.object(model.sys, "platform", platform),
                        patch.object(model, "LocalEmbedding") as factory,
                    ):
                        # Run the real factory method while mocking model loading and inference.
                        embedding = self.new_instance("EMBEDDING", "test-model", credential)

                        self.assertEqual(factory.call_args.kwargs["model_kwargs"], {"device": expected_device})
                        factory.return_value.embed_query.assert_called_once_with("test")
                        self.assertIs(embedding, factory.return_value)

    def test_explicit_device_is_preserved(self):
        for device in ["cpu", "mps", "cuda:0"]:
            with self.subTest(device=device):
                with patch.object(model.sys, "platform", "darwin"), patch.object(model, "LocalEmbedding") as factory:
                    self.new_instance("EMBEDDING", "test-model", {"device": device})

                    self.assertEqual(factory.call_args.kwargs["model_kwargs"], {"device": device})

    new_instance = staticmethod(model.LocalEmbedding.new_instance)
