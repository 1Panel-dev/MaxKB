import os
from copy import deepcopy
from unittest import skipUnless
from unittest.mock import patch
from urllib.parse import urlparse

import cohere
import httpx
from cohere.core.api_error import ApiError
from django.test import SimpleTestCase
from langchain_core.documents import Document

from models_provider.impl.vllm_model_provider.model.reranker import VllmBgeReranker


@skipUnless(os.environ.get("VLLM_RERANK_TEST_URL"), "Start the local vLLM rerank Postman simulation")
class VllmRerankerHTTPTests(SimpleTestCase):
    def setUp(self):
        self.url = os.environ["VLLM_RERANK_TEST_URL"].rstrip("/")
        self.assertIn(urlparse(self.url).hostname, ("127.0.0.1", "localhost"))
        self.http = httpx.Client(trust_env=False, timeout=5)
        self.addCleanup(self.http.close)
        self.configure()
        real_client = cohere.Client

        def client(*args, **kwargs):
            return real_client(*args, **kwargs, httpx_client=self.http, timeout=5, max_retries=0)

        # Only configure the real SDK transport; exercise the actual adapter and response parsing.
        with patch("models_provider.impl.vllm_model_provider.model.reranker.cohere.Client", side_effect=client):
            self.model = VllmBgeReranker.new_instance(
                "RERANKER", "fixture-reranker", {"api_key": "test-key", "api_url": self.url + "/v1"}, top_n=2
            )
        self.documents = [
            Document(page_content=text, metadata={"id": index, "source": "fixture"})
            for index, text in enumerate(["北京是首都", "上海是城市", "首都在北京"])
        ]

    def configure(self, **options):
        self.http.post(self.url + "/_test/reset", json=options).raise_for_status()

    def calls(self):
        response = self.http.get(self.url + "/_test/state")
        response.raise_for_status()
        return response.json()["calls"]

    def assert_ranked(self, result):
        self.assertEqual([d.page_content for d in result], ["首都在北京", "北京是首都"])
        self.assertEqual(
            [d.metadata for d in result],
            [
                {"id": 2, "source": "fixture", "relevance_score": 0.9},
                {"id": 0, "source": "fixture", "relevance_score": 0.4},
            ],
        )

    def test_v2_preserves_rank_scores_metadata_and_input(self):
        before = deepcopy(self.documents)
        self.assert_ranked(self.model.compress_documents(self.documents, "哪个是首都？"))
        self.assertEqual(self.documents, before)
        calls = self.calls()
        self.assertEqual([c["path"] for c in calls], ["/v2/rerank"])
        self.assertEqual(
            calls[0]["body"],
            {
                "model": "fixture-reranker",
                "query": "哪个是首都？",
                "documents": [d.page_content for d in self.documents],
                "top_n": 2,
            },
        )

    def test_only_v2_404_falls_back_once_with_the_same_request(self):
        self.configure(v2_status=404)
        self.assert_ranked(self.model.compress_documents(self.documents, "哪个是首都？"))
        calls = self.calls()
        self.assertEqual([c["path"] for c in calls], ["/v2/rerank", "/v1/rerank"])
        self.assertEqual(calls[0]["body"], calls[1]["body"])

    def test_other_http_errors_do_not_fall_back(self):
        for status in (400, 401, 429, 500):
            with self.subTest(status=status):
                self.configure(v2_status=status)
                with self.assertRaises(ApiError) as error:
                    self.model.compress_documents(self.documents, "query")
                self.assertEqual(error.exception.status_code, status)
                self.assertEqual([c["path"] for c in self.calls()], ["/v2/rerank"])

    def test_v1_failure_propagates_without_another_fallback(self):
        self.configure(v2_status=404, v1_status=404)
        with self.assertRaises(cohere.NotFoundError):
            self.model.compress_documents(self.documents, "query")
        self.assertEqual([c["path"] for c in self.calls()], ["/v2/rerank", "/v1/rerank"])

    def test_empty_input_makes_no_request(self):
        for documents in (None, []):
            self.assertEqual(self.model.compress_documents(documents, "query"), [])
        self.assertEqual(self.calls(), [])

    def test_out_of_range_result_indices_are_rejected(self):
        for index in (-1, len(self.documents)):
            with self.subTest(index=index):
                self.configure(results=[{"index": index, "relevance_score": 0.9}])
                with self.assertRaisesRegex(ValueError, "out of range"):
                    self.model.compress_documents(self.documents, "query")

    def test_empty_results_are_accepted(self):
        self.configure(results=[])
        self.assertEqual(self.model.compress_documents(self.documents, "query"), [])
