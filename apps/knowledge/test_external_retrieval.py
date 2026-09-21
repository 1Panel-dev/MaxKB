import importlib
import json
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import UUID

from django.test import RequestFactory, SimpleTestCase
from django.urls import resolve

from chat.views.v3 import knowledge as views
from knowledge.models import Knowledge, SourceType
from knowledge.serializers.external_retrieval import (
    ExternalServiceSerializer,
    ExternalServiceSettings,
    RetrievalRequest,
    service_settings,
)
from knowledge.services import external_retrieval as core
from knowledge.services import retrieval_access as access

KID = "10000000-0000-0000-0000-000000000001"
DID = "20000000-0000-0000-0000-000000000001"
PID = "30000000-0000-0000-0000-000000000001"
UID = "40000000-0000-0000-0000-000000000001"
KEY = "50000000-0000-0000-0000-000000000001"


def knowledge(**settings):
    return SimpleNamespace(id=KID, name="manual", workspace_id="default", external_service=settings)


class RetrievalSettingsTests(SimpleTestCase):
    def test_new_default_and_existing_migration_default_differ(self):
        self.assertEqual(Knowledge().external_service, {"enabled": False, "authentication": False})
        migration = importlib.import_module("knowledge.migrations.0015_knowledge_external_service").Migration
        self.assertEqual(migration.operations[0].field.get_default(), {})
        self.assertEqual(migration.operations[1].field.get_default(), Knowledge().external_service)
        self.assertFalse(service_settings(knowledge())["enabled"])
        self.assertFalse(service_settings(Knowledge())["authentication"])

    def test_only_two_settings_can_be_changed(self):
        self.assertTrue(ExternalServiceSettings(data={"enabled": True}).is_valid())
        for data in ({}, [], {"knowledge_id": KID}, {"authentication": None}):
            self.assertFalse(ExternalServiceSettings(data=data).is_valid())

    def test_enabling_old_service_preserves_legacy_auth_until_explicitly_changed(self):
        item = knowledge()
        item.save = Mock()
        serializer = ExternalServiceSerializer(data={"workspace_id": "default", "knowledge_id": KID})
        with patch.object(serializer, "get_knowledge", return_value=item) as get_knowledge:
            # Exercise the update without opening a database transaction in this isolated unit test.
            update = ExternalServiceSerializer.update_settings.__wrapped__
            settings = update(serializer, {"enabled": True})
            self.assertEqual(item.external_service, {"enabled": True})
            self.assertTrue(settings["enabled"])
            self.assertFalse(settings["authentication"])
            get_knowledge.assert_called_once_with(lock=True)
            settings = update(serializer, {"authentication": True})
            self.assertEqual(item.external_service, {"enabled": True, "authentication": True})
            self.assertTrue(settings["enabled"])
            self.assertTrue(settings["authentication"])
        item.save.assert_called_with(update_fields=["external_service"])

    @patch("knowledge.serializers.external_retrieval.Knowledge.objects")
    def test_settings_cannot_cross_workspace_boundary(self, manager):
        from common.exception.app_exception import NotFound404

        manager.all.return_value.filter.return_value.first.return_value = None
        serializer = ExternalServiceSerializer(data={"workspace_id": "other", "knowledge_id": KID})
        with self.assertRaises(NotFound404):
            serializer.get_settings()
        manager.all.return_value.filter.assert_called_once_with(id=UUID(KID), workspace_id="other")

    def test_request_validation(self):
        self.assertTrue(RetrievalRequest(data={"query_text": "hello"}).is_valid())
        for extra in (
            {"query_text": 5},
            {"query_text": " "},
            {"query_text": "x" * 8001},
            {"top_number": 0},
            {"top_number": 51},
            {"similarity": float("nan")},
            {"knowledge_id": KID},
            {"user_id": UID},
            {"debug": True},
            {"search_mode": "bad"},
        ):
            with self.subTest(extra=extra):
                self.assertFalse(RetrievalRequest(data={"query_text": "hello", **extra}).is_valid())

    def test_config_uses_deployment_prefix_and_key_placeholder(self):
        with patch("knowledge.serializers.external_retrieval.CONFIG.get_chat_path", return_value="/custom/chat"):
            settings = service_settings(
                knowledge(authentication=True), RequestFactory().get("/", HTTP_HOST="testserver")
            )
        self.assertIn("/custom/chat/api/v3/knowledge/", settings["api_url"])
        connection = settings["mcp_config"][f"knowledge_{KID}"]
        self.assertEqual(connection["transport"], "streamable_http")
        self.assertEqual(connection["headers"]["Authorization"], "Bearer <CHAT_USER_API_KEY>")
        self.assertNotIn("headers", service_settings(knowledge())["mcp_config"][f"knowledge_{KID}"])

    def test_routes_resolve_to_knowledge_and_preserve_application_mcp(self):
        self.assertIs(resolve(f"/chat/api/v3/knowledge/{KID}/mcp").func, views.knowledge_mcp_view)
        self.assertIs(resolve(f"/chat/api/v3/knowledge/{KID}/retrieve").func, views.retrieve_view)
        self.assertEqual(
            resolve(f"/admin/api/workspace/default/knowledge/{KID}/external_service").kwargs["workspace_id"], "default"
        )
        self.assertEqual(resolve("/chat/api/v3/mcp").func.__module__, "chat.views.v3.mcp")


class RetrievalAccessTests(SimpleTestCase):
    def setUp(self):
        self.key = SimpleNamespace(id=KEY, user_id=UID, is_active=True, user=SimpleNamespace(is_active=True))

    @patch.object(access, "QuerySet")
    def test_existing_api_key_uses_original_secret_without_writes(self, queryset):
        queryset.return_value.select_related.return_value.filter.return_value.first.return_value = self.key
        raw = "0123456789abcdef0123456789abcdef"
        self.assertEqual(access.authenticate_key("Bearer " + raw), access.RetrievalIdentity(UID, KEY))
        queryset.return_value.select_related.return_value.filter.assert_called_once_with(secret_key=raw)
        queryset.return_value.update.assert_not_called()

    def test_invalid_credentials_never_become_anonymous(self):
        self.assertIsNone(access.authenticate_key(None).user_id)
        for header in ("", "Basic x", "Bearer short", "Bearer a b"):
            with self.assertRaises(access.RetrievalError):
                access.authenticate_key(header)
        for key in (
            None,
            SimpleNamespace(**{**vars(self.key), "is_active": False}),
            SimpleNamespace(**{**vars(self.key), "user": SimpleNamespace(is_active=False)}),
        ):
            with self.assertRaises(access.RetrievalError):
                access.key_identity(key)

    @patch.object(access, "QuerySet")
    def test_refresh_rechecks_revoked_key(self, queryset):
        queryset.return_value.select_related.return_value.filter.return_value.first.return_value = None
        with self.assertRaises(access.RetrievalError):
            access.refresh_identity(access.RetrievalIdentity(UID, KEY))
        queryset.return_value.select_related.return_value.filter.assert_called_once_with(id=KEY)

    @patch.object(access, "authorized_ids", return_value={KID})
    @patch.object(access, "QuerySet")
    def test_external_switch_and_authorization_matrix(self, queryset, authorized):
        for enabled, authentication in ((False, False), (False, True), (True, False), (True, True)):
            queryset.return_value.filter.return_value.first.return_value = knowledge(
                enabled=enabled, authentication=authentication
            )
            for identity in (access.RetrievalIdentity(), access.RetrievalIdentity(UID, KEY)):
                denied = not enabled or (authentication and not identity.user_id)
                if denied:
                    with self.assertRaises(access.RetrievalError) as error:
                        access.authorize_external(KID, identity)
                    self.assertEqual(error.exception.status, 404 if not enabled else 401)
                else:
                    self.assertEqual(access.authorize_external(KID, identity).id, KID)
        authorized.return_value = set()
        with self.assertRaises(access.RetrievalError) as error:
            access.authorize_external(KID, access.RetrievalIdentity(UID))
        self.assertEqual(error.exception.status, 403)

    @patch.object(access.DatabaseModelManage, "get_model", return_value=None)
    @patch.object(access, "QuerySet")
    def test_missing_handler_or_inactive_user_denies(self, queryset, handler):
        queryset.return_value.filter.return_value.exists.return_value = True
        self.assertEqual(access.authorized_ids(UID, [KID]), set())
        handler.return_value = lambda *a: [KID]
        queryset.return_value.filter.return_value.exists.return_value = False
        self.assertEqual(access.authorized_ids(UID, [KID]), set())

    @patch.object(access.DatabaseModelManage, "get_model")
    @patch.object(access, "authorized_ids", return_value={KID})
    @patch.object(access, "QuerySet")
    def test_old_rules_new_auth_and_anonymous_setting(self, queryset, authorized, handler):
        queryset.return_value.filter.return_value = [knowledge()]
        self.assertEqual(access.filter_workflow_knowledge([KID], {}), [KID])
        handler.return_value.return_value = []
        self.assertEqual(
            access.filter_workflow_knowledge([KID], {"chat_user_id": UID, "chat_user_type": "CHAT_USER"}), []
        )
        queryset.return_value.filter.return_value = [knowledge(enabled=False, authentication=True)]
        identity = access.identity_from_server(UID, "CHAT_USER")
        self.assertEqual(access.filter_workflow_knowledge([KID], {"retrieval_identity": identity}), [KID])
        authorized.return_value = set()
        self.assertEqual(
            access.filter_workflow_knowledge(
                [KID], {"form_data": {"asker": {"id": UID}}, "retrieval_identity": {"user_id": UID}}
            ),
            [],
        )
        authorized.assert_called_with(None, [KID])
        queryset.return_value.filter.return_value = [knowledge(authentication=False)]
        self.assertEqual(access.filter_workflow_knowledge([KID], {}), [KID])

    def test_child_tools_cannot_override_trusted_identity(self):
        parent = {
            "retrieval_identity": access.identity_from_server(UID, "CHAT_USER"),
            "workspace_id": "default",
            "debug": False,
        }
        child = {
            "retrieval_identity": {"admin_user_id": UID},
            "debug": True,
            **access.inherited_retrieval_context(parent),
        }
        self.assertEqual(child["retrieval_identity"].user_id, UID)
        self.assertFalse(child["debug"])
        self.assertIsNone(access.identity_from_server(UID, "APPLICATION_API_KEY", True).admin_user_id)

    @patch("oss.serializers.file._check_workspace_resource_permission")
    @patch("common.auth.handle.impl.user_token.get_auth")
    @patch.object(access, "QuerySet")
    def test_admin_debug_uses_resource_permissions(self, queryset, get_auth, check):
        from common.exception.app_exception import AppUnauthorizedFailed

        queryset.return_value.filter.return_value.first.return_value = SimpleNamespace(id=UID)
        self.assertEqual(access.filter_admin_knowledge([knowledge()], UID), [KID])
        self.assertEqual(check.call_args.kwargs["read_permission"], "KNOWLEDGE:READ")
        check.side_effect = AppUnauthorizedFailed(403, "denied")
        self.assertEqual(access.filter_admin_knowledge([knowledge()], UID), [])


class RetrievalCoreTests(SimpleTestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.authorize = self.stack.enter_context(
            patch.object(core, "authorize_external", return_value=knowledge(enabled=True))
        )
        self.stack.enter_context(patch.object(core, "refresh_identity", side_effect=lambda i: i))
        self.model = self.stack.enter_context(patch.object(core, "get_embedding_model_by_knowledge_id"))
        self.vector = self.stack.enter_context(patch.object(core.VectorStore, "get_embedding_vector"))
        self.documents = self.stack.enter_context(patch.object(core.Document, "objects"))
        self.paragraphs = self.stack.enter_context(patch.object(core.Paragraph, "objects"))
        self.paragraphs.select_related.return_value.filter.return_value = [
            SimpleNamespace(
                id=PID,
                document_id=DID,
                knowledge_id=KID,
                title="title",
                content="answer",
                document=SimpleNamespace(name="document"),
            )
        ]
        self.match = {"paragraph_id": PID, "source_type": SourceType.PARAGRAPH, "source_id": PID, "similarity": 0.9}
        self.vector.return_value.hit_test.return_value = [self.match]
        self.stats = self.stack.enter_context(patch.object(core, "record_recall_safely"))

    def retrieve(self, **data):
        return core.retrieve(KID, access.RetrievalIdentity(), {"query_text": "hello", **data})

    def test_keyword_search_and_scoped_citations(self):
        result = self.retrieve(search_mode="keywords")
        self.model.assert_not_called()
        self.assertEqual(result["hits"][0]["citation"]["document_name"], "document")
        self.assertEqual(self.vector.return_value.hit_test.call_args.args[1], [KID])
        self.paragraphs.select_related.return_value.filter.assert_called_once_with(
            id__in=[PID], knowledge_id=KID, document__knowledge_id=KID, is_active=True, document__is_active=True
        )
        self.stats.assert_called_once_with([self.match])

    def test_stale_foreign_or_inactive_paragraph_not_returned(self):
        self.paragraphs.select_related.return_value.filter.return_value = []
        self.assertEqual(self.retrieve()["hits"], [])
        self.stats.assert_called_once_with([])

    def test_foreign_source_not_returned_or_counted(self):
        self.match["source_id"] = DID
        self.assertEqual(self.retrieve()["hits"], [])
        self.stats.assert_called_once_with([])

    def test_revoke_or_close_while_model_runs_discards_result(self):
        self.authorize.side_effect = [knowledge(), access.RetrievalError("access_denied", "denied", 403)]
        with self.assertRaises(access.RetrievalError):
            self.retrieve()
        self.stats.assert_not_called()


class RetrievalTransportTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.auth = self.stack.enter_context(
            patch.object(views, "authenticate_key", return_value=access.RetrievalIdentity())
        )
        self.authorize = self.stack.enter_context(
            patch.object(views, "authorize_external", return_value=knowledge(enabled=True))
        )
        self.output = {"knowledge_id": KID, "hits": [{"content": "answer"}]}
        self.rest = self.stack.enter_context(patch.object(views, "retrieve", return_value=self.output))
        self.mcp = self.stack.enter_context(patch("chat.mcp.knowledge.retrieve", return_value=self.output))

    def rpc(self, data, **headers):
        request = self.factory.post(
            "/mcp",
            json.dumps(data),
            content_type="application/json",
            HTTP_ACCEPT="application/json, text/event-stream",
            **headers,
        )
        return views.knowledge_mcp_view(request, KID)

    def test_rest_mcp_share_retrieval_output(self):
        rest = views.retrieve_view(
            self.factory.post("/retrieve", '{"query_text":"hello"}', content_type="application/json"), KID
        )
        mcp = self.rpc(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": f"knowledge_{KID}", "arguments": {"query_text": "hello"}},
            }
        )
        self.assertEqual(json.loads(json.loads(mcp.content)["result"]["content"][0]["text"]), json.loads(rest.content))
        self.assertEqual(rest["Cache-Control"], "no-store")

    def test_notifications_do_not_execute_tools(self):
        response = self.rpc({"jsonrpc": "2.0", "method": "tools/call", "params": {"name": f"knowledge_{KID}"}})
        self.assertEqual(response.status_code, 202)
        self.mcp.assert_not_called()

    def test_mcp_rechecks_auth_on_every_request(self):
        self.assertEqual(self.rpc({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}).status_code, 200)
        self.auth.side_effect = access.RetrievalError("invalid_api_key", "Invalid API key.", 401)
        response = self.rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response["WWW-Authenticate"], "Bearer")

    def test_protocol_validation(self):
        for data, code in (
            ([], -32600),
            ({"jsonrpc": "2.0", "method": "ping", "id": True}, -32600),
            ({"jsonrpc": "2.0", "method": "unknown", "id": 1}, -32601),
            ({"jsonrpc": "2.0", "method": "initialize", "id": 1}, -32602),
        ):
            self.assertEqual(json.loads(self.rpc(data).content)["error"]["code"], code)
        self.assertEqual(
            self.rpc({"jsonrpc": "2.0", "method": "ping", "id": 1}, HTTP_MCP_PROTOCOL_VERSION="bad").status_code, 400
        )

    def test_origin_size_content_type_and_method(self):
        self.assertEqual(self.rpc({}, HTTP_ORIGIN="https://foreign.example").status_code, 403)
        for request, status in (
            (self.factory.post("/", "x" * 65537, content_type="application/json"), 413),
            (self.factory.post("/", "{}", content_type="text/plain"), 415),
            (self.factory.get("/"), 405),
        ):
            self.assertEqual(views.retrieve_view(request, KID).status_code, status)

    def test_errors_do_not_leak_provider_details(self):
        self.rest.side_effect = RuntimeError("private credentials")
        response = views.retrieve_view(
            self.factory.post("/", '{"query_text":"hello"}', content_type="application/json"), KID
        )
        self.assertEqual(response.status_code, 503)
        self.assertNotIn(b"private", response.content)
        self.mcp.side_effect = RuntimeError("private credentials")
        response = self.rpc({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": f"knowledge_{KID}"}})
        self.assertTrue(json.loads(response.content)["result"]["isError"])
        self.assertNotIn(b"private", response.content)

    async def test_real_mcp_sdk_initialize_discover_and_call(self):
        import httpx
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        async def dispatch(request):
            django_request = self.factory.generic(
                request.method, "/mcp", request.content, content_type="application/json", headers=dict(request.headers)
            )
            response = views.knowledge_mcp_view(django_request, KID)
            return httpx.Response(response.status_code, headers=dict(response.headers), content=response.content)

        async with httpx.AsyncClient(transport=httpx.MockTransport(dispatch)) as client:
            async with streamable_http_client("http://testserver/mcp", http_client=client) as (read, write, _):
                async with ClientSession(read, write) as session:
                    initialized = await session.initialize()
                    self.assertEqual(initialized.serverInfo.name, "maxkb-knowledge-mcp")
                    tools = await session.list_tools()
                    self.assertEqual(tools.tools[0].name, f"knowledge_{KID}")
                    result = await session.call_tool(tools.tools[0].name, {"query_text": "hello"})
                    self.assertEqual(json.loads(result.content[0].text), self.output)
