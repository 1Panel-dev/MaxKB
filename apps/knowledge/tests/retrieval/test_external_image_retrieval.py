import base64
from unittest.mock import patch
from uuid import uuid4

from django.db import connection
from django.test import TestCase
from jsonschema import Draft202012Validator

from knowledge.models import Document, Embedding, File, FileSourceType, Knowledge, Paragraph, ParagraphAsset, SourceType
from knowledge.serializers.external_retrieval import RetrievalRequest
from knowledge.services import external_retrieval as retrieval
from knowledge.vector.pg_vector import PGVector
from system_manage.models import ChatUser, ChatUserApiKey


class ExternalImageRetrievalTests(TestCase):
    png = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGNgYPgPAAEDAQAIicLsAAAAAElFTkSuQmCC"

    def setUp(self):
        self.user = ChatUser.objects.create(username="image-retrieval")
        key = ChatUserApiKey.objects.create(user=self.user, secret_key=str(uuid4()))
        self.client.defaults.update(
            HTTP_AUTHORIZATION=f"Bearer {key.secret_key}", HTTP_ACCEPT="application/json, text/event-stream"
        )
        self.knowledge = Knowledge.objects.create(name="Images", external_service={"enabled": True})
        self.prefix = f"/chat/api/v3/knowledge/{self.knowledge.id}"
        with connection.cursor() as cursor:
            cursor.execute("SELECT lo_from_bytea(0, %s)", [base64.b64decode(self.png)])
            loid = cursor.fetchone()[0]
        self.upload = File(
            file_name="query.png", source_type=FileSourceType.CHAT, meta={"user_id": str(self.user.id)}, loid=loid
        )
        File.objects.bulk_create([self.upload])
        self.images = [{"file_id": str(self.upload.id), "name": "query.png", "url": f"./oss/file/{self.upload.id}"}]
        self.enterContext(patch("knowledge.services.retrieval_access.get_portal_setting", return_value=True))
        self.model = self.enterContext(patch.object(retrieval, "get_embedding_model_by_knowledge_id")).return_value
        self.model.supports_image_embedding.return_value = True
        self.model.embed_images.return_value = [[1.0, 0.0]]
        self.model.embed_query.return_value = [0.0, 1.0]
        self.enterContext(patch.object(retrieval.VectorStore, "get_embedding_vector", return_value=PGVector()))

    def rpc(self, path, method, params):
        response = self.client.post(
            path, {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["result"]

    def test_rest_and_both_mcp_tools_find_an_image_from_an_uploaded_attachment(self):
        doc = Document.objects.create(knowledge=self.knowledge, name="Gallery", char_length=0)
        paragraph = Paragraph.objects.create(document=doc, knowledge=self.knowledge, content="Image caption")
        asset = ParagraphAsset.objects.create(
            knowledge=self.knowledge, document=doc, paragraph=paragraph, file=self.upload
        )
        Embedding.objects.create(
            id=str(uuid4()),
            document=doc,
            knowledge=self.knowledge,
            paragraph=paragraph,
            source_type=SourceType.IMAGE,
            source_id=str(asset.id),
            embedding="[1,0]",
        )
        query = {"image_list": self.images}
        response = self.client.post(f"{self.prefix}/retrieve", query, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        hits = response.json()["hits"]
        self.assertEqual([hit["source_id"] for hit in hits], [str(asset.id)])
        self.model.embed_query.assert_not_called()
        self.model.embed_images.assert_called_once_with([f"data:image/png;base64,{self.png}"])

        for path, name, scope in (
            (f"{self.prefix}/mcp", f"knowledge_{self.knowledge.id}", {}),
            ("/chat/api/v3/knowledge_mcp", "search_knowledge", {"knowledge_id": str(self.knowledge.id)}),
        ):
            with self.subTest(path=path):
                tools = self.rpc(path, "tools/list", {})["tools"]
                schema = next(tool["inputSchema"] for tool in tools if tool["name"] == name)
                self.assertIn("image_list", schema["properties"])
                self.assertNotIn("query_text", schema["required"])
                arguments = {**scope, **query}
                Draft202012Validator(schema).validate(arguments)
                result = self.rpc(path, "tools/call", {"name": name, "arguments": arguments})
                self.assertEqual(result["structuredContent"]["hits"], hits)

        response = self.client.post(
            f"{self.prefix}/retrieve",
            {**query, "query_text": "caption", "search_mode": "blend"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["hits"][0]["source_id"], str(asset.id))
        self.model.embed_query.assert_called_once_with("caption")

    def test_rejects_files_outside_the_api_key_users_chat_uploads(self):
        for changes in (
            {"meta": {}},
            {"meta": {"user_id": str(uuid4())}},
            {"meta": {"user_id": str(self.user.id)}, "source_type": FileSourceType.KNOWLEDGE},
        ):
            with self.subTest(changes=changes):
                File.objects.filter(pk=self.upload.id).update(**changes)
                response = self.client.post(
                    f"{self.prefix}/retrieve", {"image_list": self.images}, content_type="application/json"
                )
                self.assertEqual(response.status_code, 400)
        self.model.embed_images.assert_not_called()

    def test_rejects_invalid_image_requests(self):
        for query in (
            {},
            {"image_list": []},
            {"image_list": [{"url": "https://example.com/query.png"}]},
            {"image_list": [{"file_id": "invalid"}]},
            {"image_list": self.images * 11},
            {"image_list": self.images, "search_mode": "keywords"},
        ):
            with self.subTest(query=query):
                self.assertFalse(RetrievalRequest(data=query).is_valid())
        self.model.supports_image_embedding.return_value = False
        response = self.client.post(
            f"{self.prefix}/retrieve", {"image_list": self.images}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.model.embed_images.assert_not_called()
