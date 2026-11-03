import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import RequestFactory, SimpleTestCase
from django.urls import resolve

from application.models import ChatSourceChoices, ChatUserType
from chat.mcp.application import ChatUserMCPToolHandler, InvalidParamsError, chat_application, get_chat_file_field
from chat.views.v3.mcp import mcp_view
from common.auth.struct.auth import Auth
from common.exception.app_exception import AppAuthenticationFailed


APP_ID = "01a17d06-3bd0-7661-91dc-9d990282d863"

AGENT_PARAMS = {
    "message",
    "chat_id",
    "form_data",
    "image_list",
    "document_list",
    "audio_list",
    "video_list",
    "other_list",
}


class ChatApplicationTest(SimpleTestCase):
    @patch("common.init.init_template.run")
    @patch("chat.mcp.application.ChatSerializers")
    def test_chats_as_given_chat_user_in_a_new_chat(self, chat_serializers, _init):
        chat_serializers.return_value.chat.return_value = SimpleNamespace(
            content=json.dumps({"data": {"content": "answer<tool_calls_render>tool</tool_calls_render>"}}).encode()
        )

        result = chat_application(
            "app-id", "user-id", ChatUserType.CHAT_USER.value, "hello", {"a": 1}, {"image_list": [{"file_id": "f"}]}
        )

        chat_info = chat_serializers.call_args.kwargs["data"]
        self.assertEqual(chat_info["chat_user_id"], "user-id")
        self.assertEqual(chat_info["chat_user_type"], ChatUserType.CHAT_USER.value)
        self.assertEqual(chat_info["source"], {"type": ChatSourceChoices.API_CALL.value})
        self.assertTrue(chat_info["chat_id"])
        payload = chat_serializers.return_value.chat.call_args.args[0]
        self.assertEqual(payload["message"], {"content": "hello", "image_list": [{"file_id": "f"}]})
        self.assertEqual(payload["form_data"], {"a": 1})
        self.assertFalse(payload["stream"])
        self.assertEqual(result, ("answer", chat_info["chat_id"]))

    @patch("common.init.init_template.run")
    @patch("chat.mcp.application.ChatSerializers")
    def test_continues_given_chat(self, chat_serializers, _init):
        chat_serializers.return_value.chat.return_value = SimpleNamespace(content=b'{"data": {"content": "a"}}')

        result = chat_application("app-id", "user-id", ChatUserType.CHAT_USER.value, "hi", chat_id="chat-1")

        self.assertEqual(chat_serializers.call_args.kwargs["data"]["chat_id"], "chat-1")
        self.assertEqual(result, ("a", "chat-1"))

    def test_classifies_files_by_extension(self):
        self.assertEqual(get_chat_file_field("a.PNG"), "image_list")
        self.assertEqual(get_chat_file_field("a.pdf"), "document_list")
        self.assertEqual(get_chat_file_field("a.mp3"), "audio_list")
        self.assertEqual(get_chat_file_field("a.mp4"), "video_list")
        self.assertEqual(get_chat_file_field("a.zip"), "other_list")
        self.assertEqual(get_chat_file_field("noext"), "other_list")


class ChatUserMCPToolHandlerTest(SimpleTestCase):
    def setUp(self):
        self.handler = ChatUserMCPToolHandler(
            SimpleNamespace(id="user-id"),
            Auth(set(), {"CHAT_USER:r:app-1": 1, "CHAT_USER:r:app-2": 0, "OTHER:r:app-3": 1}),
        )

    def test_only_permitted_applications_are_queried(self):
        self.assertEqual(self.handler.get_application_ids(), ["app-1"])

    def test_application_scoped_handler_only_exposes_that_application(self):
        auth = Auth(set(), {"CHAT_USER:r:app-1": 1, "CHAT_USER:r:app-4": 1})
        self.assertEqual(
            ChatUserMCPToolHandler(SimpleNamespace(id="u"), auth, "app-4").get_application_ids(), ["app-4"]
        )
        self.assertEqual(ChatUserMCPToolHandler(SimpleNamespace(id="u"), auth, "app-9").get_application_ids(), [])

    def scoped_handler(self):
        return ChatUserMCPToolHandler(SimpleNamespace(id="user-id"), Auth(set(), {f"CHAT_USER:r:{APP_ID}": 1}), APP_ID)

    @patch("chat.mcp.application.QuerySet")
    def test_scoped_list_tools_exposes_the_agent_and_upload(self, query_set):
        query_set.return_value.filter.return_value.order_by.return_value = [
            SimpleNamespace(id=APP_ID, name="Agent", desc="desc")
        ]

        tools = self.scoped_handler().list_tools()["tools"]

        self.assertEqual([tool["name"] for tool in tools], [f"agent_{APP_ID}", "upload_file"])
        self.assertTrue(tools[0]["description"].startswith("Agent desc\nAn AI agent."))
        self.assertEqual(set(tools[0]["inputSchema"]["properties"]), AGENT_PARAMS)
        self.assertEqual(tools[0]["inputSchema"]["required"], ["message"])

    def test_global_list_tools_exposes_list_and_call_agent(self):
        tools = self.handler.list_tools()["tools"]

        self.assertEqual([tool["name"] for tool in tools], ["list_agents", "call_agent", "upload_file"])
        self.assertEqual(set(tools[1]["inputSchema"]["properties"]), {"application_id", *AGENT_PARAMS})
        self.assertEqual(tools[1]["inputSchema"]["required"], ["application_id", "message"])

    @patch.object(ChatUserMCPToolHandler, "get_applications")
    def test_list_agents_returns_accessible_applications(self, get_applications):
        get_applications.return_value = [SimpleNamespace(id=APP_ID, name="Agent", desc=None)]

        result = self.handler.call_tool({"name": "list_agents", "arguments": {}})

        self.assertEqual(
            result["structuredContent"], {"agents": [{"application_id": APP_ID, "name": "Agent", "desc": ""}]}
        )
        self.assertEqual(json.loads(result["content"][0]["text"]), result["structuredContent"]["agents"])

    @patch("chat.mcp.application.chat_application", return_value=("answer", "chat-id"))
    @patch.object(ChatUserMCPToolHandler, "get_applications")
    def test_call_agent_tool_chats_as_chat_user_and_returns_chat_id(self, get_applications, chat_app):
        get_applications.return_value.filter.return_value.exists.return_value = True

        result = self.scoped_handler().call_tool({"name": f"agent_{APP_ID}", "arguments": {"message": "hi"}})

        get_applications.return_value.filter.assert_called_once_with(id=APP_ID)
        chat_app.assert_called_once_with(APP_ID, "user-id", ChatUserType.CHAT_USER.value, "hi", {}, {}, None)
        self.assertEqual(result["content"][0], {"type": "text", "text": "answer"})
        self.assertEqual(result["structuredContent"], {"answer": "answer", "chat_id": "chat-id"})

    @patch("chat.mcp.application.chat_application", return_value=("answer", "chat-id"))
    @patch.object(ChatUserMCPToolHandler, "get_applications")
    def test_global_call_agent_uses_application_id(self, get_applications, chat_app):
        get_applications.return_value.filter.return_value.exists.return_value = True

        self.handler.call_tool({"name": "call_agent", "arguments": {"application_id": APP_ID, "message": "hi"}})

        chat_app.assert_called_once_with(APP_ID, "user-id", ChatUserType.CHAT_USER.value, "hi", {}, {}, None)

    @patch.object(ChatUserMCPToolHandler, "get_applications")
    def test_call_tool_rejects_unknown_tools_and_applications(self, get_applications):
        get_applications.return_value.filter.return_value.exists.return_value = False
        cases = [
            (self.handler, "call_agent", {"application_id": APP_ID, "message": "hi"}),
            (self.handler, "call_agent", {"application_id": "not-a-uuid", "message": "hi"}),
            (self.handler, f"agent_{APP_ID}", {"message": "hi"}),
            (self.scoped_handler(), "list_agents", {}),
            (self.scoped_handler(), "call_agent", {"application_id": APP_ID, "message": "hi"}),
            (self.scoped_handler(), "agent_not-a-uuid", {"message": "hi"}),
        ]
        for handler, name, arguments in cases:
            with self.subTest(name=name, scoped=bool(handler.application_id)), self.assertRaises(InvalidParamsError):
                handler.call_tool({"name": name, "arguments": arguments})

    @patch("chat.mcp.application.QuerySet")
    def test_check_chat_id(self, query_set):
        chat_id = "01a17d06-3bd0-7661-91dc-9d990282d863"
        query_set.return_value.filter.return_value.first.return_value = None
        self.assertEqual(self.handler.check_chat_id(chat_id, "app-1"), chat_id)

        query_set.return_value.filter.return_value.first.return_value = SimpleNamespace(
            chat_user_id="other-user", application_id="app-1"
        )
        with self.assertRaises(InvalidParamsError):
            self.handler.check_chat_id(chat_id, "app-1")

        query_set.return_value.filter.return_value.first.return_value = SimpleNamespace(
            chat_user_id="user-id", application_id="app-2"
        )
        self.assertEqual(self.handler.check_chat_id(chat_id), chat_id)
        with self.assertRaises(InvalidParamsError):
            self.handler.check_chat_id(chat_id, "app-1")

        with self.assertRaises(InvalidParamsError):
            self.handler.check_chat_id("not-a-uuid")

    @patch("chat.mcp.application.QuerySet")
    def test_chat_files_keep_caller_fields_and_infer_chat_id(self, query_set):
        query_set.return_value.filter.return_value = [
            SimpleNamespace(id="f1", file_name="a.png", source_id="chat-1"),
            SimpleNamespace(id="f2", file_name="b.pdf", source_id="chat-1"),
        ]

        chat_id, chat_files = self.handler.get_chat_files(
            None, {"image_list": [{"file_id": "f1"}], "other_list": [{"file_id": "f2", "name": "ignored"}]}
        )

        self.assertEqual(chat_id, "chat-1")
        self.assertEqual(
            chat_files,
            {
                "image_list": [{"name": "a.png", "url": "./oss/file/f1", "file_id": "f1"}],
                "other_list": [{"name": "b.pdf", "url": "./oss/file/f2", "file_id": "f2"}],
            },
        )

    def test_chat_files_without_attachments(self):
        self.assertEqual(self.handler.get_chat_files("chat-1", {"message": "hi"}), ("chat-1", {}))

    @patch("chat.mcp.application.QuerySet")
    def test_chat_files_must_belong_to_the_chat(self, query_set):
        query_set.return_value.filter.return_value = [SimpleNamespace(id="f1", file_name="a.png", source_id="chat-1")]

        with self.assertRaises(InvalidParamsError):
            self.handler.get_chat_files("chat-2", {"image_list": [{"file_id": "f1"}]})
        with self.assertRaises(InvalidParamsError):
            self.handler.get_chat_files(None, {"image_list": [{"file_id": "f1"}, {"file_id": "missing"}]})

    def test_chat_files_reject_invalid_format(self):
        for attachments in (["f1"], {"file_id": "f1"}, [{"name": "a.png"}]):
            with self.subTest(attachments=attachments), self.assertRaises(InvalidParamsError):
                self.handler.get_chat_files(None, {"image_list": attachments})

    @patch("oss.serializers.file.FileSerializer")
    def test_upload_file_returns_file_and_new_chat_id(self, file_serializer):
        file_serializer.return_value.upload.return_value = "./oss/file/file-1"

        result = self.handler.upload_file({"file_name": "a.txt", "content": "aGVsbG8="})["structuredContent"]

        data = file_serializer.call_args.kwargs["data"]
        self.assertEqual(data["file"].read(), b"hello")
        self.assertEqual(data["source_id"], result["chat_id"])
        file_serializer.return_value.upload.assert_called_once_with(user_id="user-id")
        self.assertEqual(result["file_id"], "file-1")
        self.assertEqual(result["field"], "document_list")

    def test_upload_file_rejects_invalid_content(self):
        with self.assertRaises(InvalidParamsError):
            self.handler.upload_file({"file_name": "a.txt", "content": "not base64!"})
        with self.assertRaises(InvalidParamsError):
            self.handler.upload_file({"content": "aGVsbG8="})


class MCPViewTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post(self, body, token="chat-key"):
        request = self.factory.post(
            "/chat/api/v3/mcp",
            data=json.dumps(body),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        return mcp_view(request)

    def test_rejects_non_chat_user_key(self):
        response = self.post({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}, token="application-key")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.content)["error"]["code"], -32001)

    @patch("chat.views.v3.mcp.ChatUserKey.handle", side_effect=AppAuthenticationFailed(500, "Secret key is invalid"))
    def test_rejects_invalid_chat_user_key(self, _handle):
        response = self.post({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})

        self.assertEqual(response.status_code, 401)

    @patch("chat.views.v3.mcp.ChatUserMCPToolHandler")
    @patch("chat.views.v3.mcp.ChatUserKey.handle")
    def test_routes_tools_list_with_chat_user(self, handle, handler_class):
        chat_user = SimpleNamespace(id="user-id")
        auth = Auth(set(), {})
        handle.return_value = (SimpleNamespace(profile=chat_user), auth)
        handler_class.return_value.list_tools.return_value = {"tools": []}

        response = self.post({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})

        handler_class.assert_called_once_with(chat_user, auth, None)
        self.assertEqual(json.loads(response.content), {"jsonrpc": "2.0", "id": 1, "result": {"tools": []}})

    @patch("chat.views.v3.mcp.ChatUserKey.handle", return_value=(SimpleNamespace(profile=None), MagicMock()))
    def test_notification_is_accepted_without_body(self, _handle):
        response = self.post({"jsonrpc": "2.0", "method": "notifications/initialized"})

        self.assertEqual(response.status_code, 202)

    def test_application_scoped_route(self):
        match = resolve("/chat/api/v3/application/app-1/mcp")

        self.assertIs(match.func, mcp_view)
        self.assertEqual(match.kwargs, {"application_id": "app-1"})

    def post_sse(self, body):
        request = self.factory.post(
            "/chat/api/v3/mcp",
            data=json.dumps(body),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer chat-key",
            HTTP_ACCEPT="application/json, text/event-stream",
        )
        return mcp_view(request)

    @staticmethod
    def read_sse(response):
        return b"".join(response.streaming_content).decode()

    @patch("chat.views.v3.mcp.SSE_HEARTBEAT_SECONDS", 0.01)
    @patch("chat.views.v3.mcp.ChatUserMCPToolHandler")
    @patch("chat.views.v3.mcp.ChatUserKey.handle", return_value=(SimpleNamespace(profile=None), MagicMock()))
    def test_tool_call_streams_progress_then_result(self, _handle, handler_class):
        import time

        def slow_call(params):
            time.sleep(0.05)
            return {"content": [{"type": "text", "text": "done"}]}

        handler_class.return_value.call_tool.side_effect = slow_call

        response = self.post_sse(
            {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "tools/call",
                "params": {"name": "agent_x", "arguments": {}, "_meta": {"progressToken": "p1"}},
            }
        )

        self.assertEqual(response["Content-Type"], "text/event-stream; charset=utf-8")
        events = [json.loads(line[6:]) for line in self.read_sse(response).splitlines() if line.startswith("data: ")]
        self.assertEqual(events[0]["method"], "notifications/progress")
        self.assertEqual(events[0]["params"]["progressToken"], "p1")
        self.assertEqual(
            events[-1], {"jsonrpc": "2.0", "id": 7, "result": {"content": [{"type": "text", "text": "done"}]}}
        )

    @patch("chat.views.v3.mcp.SSE_HEARTBEAT_SECONDS", 0.01)
    @patch("chat.views.v3.mcp.ChatUserMCPToolHandler")
    @patch("chat.views.v3.mcp.ChatUserKey.handle", return_value=(SimpleNamespace(profile=None), MagicMock()))
    def test_tool_call_stream_sends_ping_without_progress_token_and_maps_errors(self, _handle, handler_class):
        import time

        def failing_call(params):
            time.sleep(0.05)
            raise InvalidParamsError("Unknown tool: x")

        handler_class.return_value.call_tool.side_effect = failing_call

        body = self.read_sse(
            self.post_sse({"jsonrpc": "2.0", "id": 8, "method": "tools/call", "params": {"name": "x"}})
        )

        self.assertIn(": ping", body)
        last = json.loads([line for line in body.splitlines() if line.startswith("data: ")][-1][6:])
        self.assertEqual(last["error"], {"code": -32602, "message": "Unknown tool: x"})
