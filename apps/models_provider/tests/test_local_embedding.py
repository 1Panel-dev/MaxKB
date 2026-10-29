import tempfile
from unittest.mock import patch

from django.test import SimpleTestCase

from models_provider.impl.local_model_provider.model.embedding import model
from models_provider.tests.local_model_helpers import build_local_sentence_transformer


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


class LocalEmbeddingInferenceTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.directory = tempfile.TemporaryDirectory(prefix="maxkb-embedding-")
        cls.addClassCleanup(cls.directory.cleanup)
        cls.offline = patch.dict("os.environ", {"HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"})
        cls.offline.start()
        cls.addClassCleanup(cls.offline.stop)
        cls.model_path = build_local_sentence_transformer(cls.directory.name)
        cls.embedding = model.LocalEmbedding.new_instance("EMBEDDING", cls.model_path, {"device": "cpu"})

    def test_batches_queries_and_normalization_preserve_order(self):
        import numpy as np

        texts = ["hello world", "文档查询", "test", "hello world"]
        batch = np.asarray(self.embedding.embed_documents(texts))
        singles = np.asarray([self.embedding.embed_query(text) for text in texts])
        self.assertEqual(batch.shape, (4, 12))
        self.assertTrue(np.isfinite(batch).all())
        np.testing.assert_allclose(np.linalg.norm(batch, axis=1), 1, atol=1e-6)
        np.testing.assert_allclose(batch, singles, atol=1e-6)
        np.testing.assert_allclose(batch[0], batch[3], atol=1e-6)
        self.assertGreater(np.linalg.norm(batch[0] - batch[1]), 0.01)

    def test_empty_inputs_and_long_text_are_supported(self):
        import numpy as np

        self.assertEqual(self.embedding.embed_documents([]), [])
        for text in ("", "文档 " * 500):
            vector = np.asarray(self.embedding.embed_query(text))
            self.assertEqual(vector.shape, (12,))
            self.assertTrue(np.isfinite(vector).all())
            self.assertAlmostEqual(float(np.linalg.norm(vector)), 1, places=5)

    def test_loading_the_saved_model_again_preserves_vectors(self):
        import numpy as np

        reloaded = model.LocalEmbedding.new_instance("EMBEDDING", self.model_path, {"device": "cpu"})
        np.testing.assert_allclose(
            self.embedding.embed_documents(["hello", "文档"]),
            reloaded.embed_documents(["hello", "文档"]),
            atol=1e-6,
        )
