"""Milvus REST v2 contract and failure propagation through the real HTTP client."""

import os
import socket
from types import SimpleNamespace
from unittest import skipUnless
from unittest.mock import MagicMock, patch
from uuid import UUID

import requests
from django.test import SimpleTestCase

from common.event.listener_manage import ListenerManagement
from common.exception.app_exception import AppApiException
from knowledge.models import SourceType, State, Status, TaskType
from knowledge.vector.milvus_vector import MilvusVector
from maxkb.const import CONFIG


class MilvusWriteTests(SimpleTestCase):
    """Core regressions also run without the optional HTTP simulation."""

    def setUp(self):
        self.enterContext(patch.object(MilvusVector, "_existing", set()))
        self.enterContext(patch.object(MilvusVector, "_loaded", set()))
        self.enterContext(patch("knowledge.vector.milvus_vector.maxkb_logger"))
        self.post = self.enterContext(patch.object(MilvusVector, "_post"))
        self.store = MilvusVector()
        self.responses = [
            (True, {"code": 0, "data": {"has": False}}),
            (True, {"code": 0}),
            (True, {"code": 0}),
            (True, {"code": 0}),
        ]

    def test_collection_field_parameters_follow_rest_v2_schema(self):
        self.post.side_effect = self.responses
        self.store._upsert_records("knowledge", [{"id": "entity", "embedding": [1.0, 0.0]}])

        create_body = next(
            call.args[1] for call in self.post.call_args_list if call.args[0].endswith("/collections/create")
        )
        fields = {field["fieldName"]: field for field in create_body["schema"]["fields"]}
        self.assertEqual(fields["embedding"]["elementTypeParams"], {"dim": 2})
        for field in fields.values():
            if field["dataType"] == "VarChar":
                self.assertEqual(field["elementTypeParams"], {"max_length": 128})
            self.assertNotIn("dim", field)
            self.assertNotIn("maxLength", field)

    def test_write_failure_raises_and_stops_subsequent_requests(self):
        operations = ["collections/has", "collections/create", "collections/load", "entities/upsert"]
        for index, operation in enumerate(operations):
            with self.subTest(operation=operation):
                MilvusVector._existing.clear()
                MilvusVector._loaded.clear()
                self.post.reset_mock()
                self.post.side_effect = self.responses[:index] + [(False, {"code": 65535, "message": "rejected"})]

                with self.assertRaises(AppApiException) as error:
                    self.store._upsert_records("knowledge", [{"id": "entity", "embedding": [1.0, 0.0]}])

                self.assertIn(operation, error.exception.message)
                self.assertEqual(self.post.call_count, index + 1)


@skipUnless(os.environ.get("MILVUS_TEST_URL"), "Start the local Milvus Postman simulation")
class MilvusWriteHTTPTests(SimpleTestCase):
    knowledge_id = "00000000-0000-0000-0000-000000000001"

    def setUp(self):
        self.base_url = os.environ["MILVUS_TEST_URL"].rstrip("/")
        self.enterContext(patch.dict(CONFIG, MILVUS_URI=self.base_url, MILVUS_TOKEN="regression-token"))
        self.enterContext(patch.object(MilvusVector, "_session", None))
        self.enterContext(patch.object(MilvusVector, "_uri", ""))
        self.enterContext(patch.object(MilvusVector, "_existing", set()))
        self.enterContext(patch.object(MilvusVector, "_loaded", set()))
        self.enterContext(patch("knowledge.vector.milvus_vector.maxkb_logger"))
        self.addCleanup(self.close_session)
        self.store = MilvusVector()
        self.name = self.store._collection_name(self.knowledge_id)
        self.reset()

    def close_session(self):
        if MilvusVector._session is not None:
            MilvusVector._session.close()

    def reset(self, failure=None, existing=False):
        MilvusVector._existing.clear()
        MilvusVector._loaded.clear()
        collections = {self.name: {"dim": 2, "loaded": False, "records": {}}} if existing else {}
        response = requests.post(
            self.base_url + "/__test/reset", json={"failure": failure, "collections": collections}, timeout=5
        )
        response.raise_for_status()

    def state(self):
        response = requests.get(self.base_url + "/__test/state", timeout=5)
        response.raise_for_status()
        return response.json()

    def records(self, count=1):
        return [
            {
                "id": str(index),
                "embedding": [1.0, 0.0],
                "document_id": "document",
                "paragraph_id": "paragraph",
                "is_active": True,
                "source_id": "paragraph",
                "source_type": SourceType.PARAGRAPH.value,
            }
            for index in range(count)
        ]

    def test_custom_schema_creates_loads_and_upserts_entities(self):
        self.store._upsert_records(self.knowledge_id, self.records())

        state = self.state()
        self.assertEqual(
            [call["operation"] for call in state["calls"]],
            [
                "collections/has",
                "collections/create",
                "collections/load",
                "entities/upsert",
            ],
        )
        collection = state["collections"][self.name]
        self.assertTrue(collection["loaded"])
        self.assertEqual(collection["records"]["0"], self.records()[0])
        fields = {field["fieldName"]: field for field in collection["schema"]["fields"]}
        self.assertEqual(int(fields["embedding"]["elementTypeParams"]["dim"]), 2)
        for field in fields.values():
            if field["dataType"] == "VarChar":
                self.assertEqual(int(field["elementTypeParams"]["max_length"]), 128)
        self.assertEqual(state["calls"][1]["body"]["indexParams"][0]["indexType"], "HNSW")

    def test_collection_failures_stop_before_upsert(self):
        operations = ["collections/has", "collections/create", "collections/load"]
        for index, operation in enumerate(operations):
            with self.subTest(operation=operation):
                self.reset({"operation": operation, "body": {"code": 65535, "message": "collection unavailable"}})
                with self.assertRaises(AppApiException) as error:
                    self.store._upsert_records(self.knowledge_id, self.records())
                self.assertIn(operation, error.exception.message)
                self.assertEqual([call["operation"] for call in self.state()["calls"]], operations[: index + 1])

    def test_failed_load_is_retried_for_an_existing_collection(self):
        self.reset({"operation": "collections/load", "body": {"code": 65535, "message": "loading failed"}})
        with self.assertRaises(AppApiException):
            self.store._upsert_records(self.knowledge_id, self.records())

        self.store._upsert_records(self.knowledge_id, self.records())

        state = self.state()
        operations = [call["operation"] for call in state["calls"]]
        self.assertEqual(operations.count("collections/create"), 1)
        self.assertEqual(operations.count("collections/load"), 2)
        self.assertTrue(state["collections"][self.name]["loaded"])
        self.assertEqual(len(state["collections"][self.name]["records"]), 1)

    def test_upsert_rejects_http_business_and_malformed_responses(self):
        cases = [
            (200, {"code": 65535, "message": "write rejected"}, False),
            (401, {"message": "Unauthorized"}, False),
            (429, {"code": 0}, False),
            (503, {"code": 0}, False),
            (502, "<html>Bad gateway</html>", True),
            (200, "not JSON", True),
            (200, {}, False),
            (200, [], False),
            (200, None, False),
            (200, {"code": False}, False),
            (200, {"code": "0"}, False),
        ]
        for status, body, raw in cases:
            with self.subTest(status=status, body=body):
                self.reset({"operation": "entities/upsert", "status": status, "body": body, "raw": raw}, existing=True)
                with self.assertRaises(AppApiException) as error:
                    self.store._upsert_records(self.knowledge_id, self.records())
                self.assertIn("entities/upsert", error.exception.message)

    def test_connection_loss_is_propagated(self):
        self.reset({"operation": "entities/upsert", "disconnect": True}, existing=True)
        with self.assertRaises(AppApiException):
            self.store._upsert_records(self.knowledge_id, self.records())

    def test_unreachable_service_is_propagated(self):
        # Reserve an unused local port without listening; no external service is contacted.
        with socket.socket() as unavailable:
            unavailable.bind(("127.0.0.1", 0))
            uri = f"http://127.0.0.1:{unavailable.getsockname()[1]}"
            with patch.dict(CONFIG, MILVUS_URI=uri), self.assertRaises(AppApiException) as error:
                self.store._upsert_records(self.knowledge_id, self.records())
            self.assertIn("collections/has", error.exception.message)

    def test_malformed_has_result_does_not_trigger_create(self):
        for payload in (None, [], {}, {"has": "false"}):
            with self.subTest(payload=payload):
                self.reset({"operation": "collections/has", "body": {"code": 0, "data": payload}})
                with self.assertRaises(AppApiException):
                    self.store._upsert_records(self.knowledge_id, self.records())
                self.assertEqual([call["operation"] for call in self.state()["calls"]], ["collections/has"])

    def test_drop_invalidates_loaded_cache_for_uuid_and_string_ids(self):
        self.store._upsert_records(self.knowledge_id, self.records())
        self.store.drop_knowledge_index(UUID(self.knowledge_id))
        self.store._upsert_records(self.knowledge_id, self.records())
        operations = [call["operation"] for call in self.state()["calls"]]
        self.assertEqual(operations.count("collections/create"), 2)
        self.assertEqual(operations.count("collections/load"), 2)

    @patch("knowledge.vector.milvus_vector.pg_vector_recall")
    def test_read_failure_keeps_pg_fallback(self, pg_recall):
        self.reset({"operation": "collections/has", "status": 503, "body": {"message": "unavailable"}})
        pg_recall.return_value = [{"paragraph_id": "paragraph", "similarity": 0.9}]
        result = self.store._search_embedding([1.0, 0.0], [self.knowledge_id], None, [], [], True, 3, 0.5)
        self.assertEqual([row["paragraph_id"] for row in result], ["paragraph"])
        pg_recall.assert_called_once()

    def test_later_upsert_failure_stops_remaining_batches(self):
        self.reset(
            {"operation": "entities/upsert", "at": 2, "body": {"code": 65535, "message": "write rejected"}},
            existing=True,
        )
        with self.assertRaises(AppApiException):
            self.store._upsert_records(self.knowledge_id, self.records(1001))

        state = self.state()
        batches = [call for call in state["calls"] if call["operation"] == "entities/upsert"]
        self.assertEqual([len(call["body"]["data"]) for call in batches], [500, 500])
        self.assertEqual(len(state["collections"][self.name]["records"]), 500)

    def test_paragraph_embedding_failure_is_not_reported_as_success(self):
        self.reset(
            {"operation": "entities/upsert", "body": {"code": 65535, "message": "write rejected"}}, existing=True
        )
        model = MagicMock()
        model.embed_documents.side_effect = lambda texts: [[1.0, 0.0] for _ in texts]
        data = [
            {
                "text": "paragraph text",
                "knowledge_id": self.knowledge_id,
                "document_id": "document",
                "paragraph_id": "paragraph",
                "source_id": "paragraph",
                "source_type": SourceType.PARAGRAPH.value,
            }
        ]
        with (
            patch("common.event.listener_manage.VectorStore.get_embedding_vector", return_value=self.store),
            patch("common.event.listener_manage.process_pending_visual_assets"),
            patch("common.event.listener_manage.embed_paragraph_assets") as embed_assets,
            patch("common.event.listener_manage.native_search", return_value=data),
            patch("common.event.listener_manage.QuerySet") as listener_query,
            patch("knowledge.vector.milvus_vector.QuerySet") as vector_query,
            patch.object(ListenerManagement, "update_status") as update_status,
            patch("common.event.listener_manage.maxkb_logger") as logger,
        ):
            listener_query.return_value.filter.return_value.first.return_value = SimpleNamespace(status=str(Status()))
            vector_query.return_value.filter.return_value.values.return_value = []
            vector_query.return_value.filter.return_value.values_list.return_value = []

            ListenerManagement.embedding_by_paragraph("paragraph", model)

        self.assertEqual([call.args[2] for call in update_status.call_args_list], [State.STARTED, State.FAILURE])
        self.assertTrue(all(call.args[1] == TaskType.EMBEDDING for call in update_status.call_args_list))
        embed_assets.assert_not_called()
        self.assertTrue(
            any(call["operation"] == "entities/upsert" for call in self.state()["calls"]), logger.error.call_args
        )
