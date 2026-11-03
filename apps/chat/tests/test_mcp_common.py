from django.test import SimpleTestCase

from chat.mcp.common import DEFAULT_PROTOCOL_VERSION, initialize_result, json_result, tool_error


class MCPCommonTest(SimpleTestCase):
    def test_initialize_negotiates_protocol_version(self):
        self.assertEqual(initialize_result({"protocolVersion": "2025-11-25"}, "s")["protocolVersion"], "2025-11-25")
        for params in ({"protocolVersion": "1999-01-01"}, {}, None):
            self.assertEqual(initialize_result(params, "s")["protocolVersion"], DEFAULT_PROTOCOL_VERSION)
        self.assertEqual(initialize_result({}, "maxkb-mcp")["serverInfo"]["name"], "maxkb-mcp")

    def test_json_result_and_tool_error(self):
        self.assertEqual(
            json_result(["中文"], {"items": ["中文"]}),
            {"content": [{"type": "text", "text": '["中文"]'}], "structuredContent": {"items": ["中文"]}},
        )
        self.assertEqual(json_result({"a": 1})["structuredContent"], {"a": 1})
        self.assertEqual(tool_error("bad"), {"isError": True, "content": [{"type": "text", "text": "bad"}]})
