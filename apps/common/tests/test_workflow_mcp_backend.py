from unittest.mock import AsyncMock, patch
from django.test import SimpleTestCase
from application.mcp_tools import get_mcp_tools
from common.mcp.client import create_mcp_client


class WorkflowMcpBackendTests(SimpleTestCase):
    def test_sandbox_mode_routes_remote_config_through_worker(self):
        config = {"transport": "sse", "url": "https://example.com/mcp"}
        worker = {"transport": "stdio", "command": "worker", "args": []}
        module = "application.workflow.backend.sandbox_mcp"
        with (
            patch(module + ".CONFIG.get", return_value=1),
            patch(module + ".sandbox_connection", return_value=worker) as build,
        ):
            client = create_mcp_client({"library": config})
        self.assertEqual(client.connections["library"], worker)
        build.assert_called_once_with(config)

    async def test_tool_discovery_uses_the_configured_backend(self):
        backend = AsyncMock()
        backend.get_tools.return_value = ["result"]
        with patch("application.mcp_tools.create_mcp_client", return_value=backend) as factory:
            self.assertEqual(await get_mcp_tools({}), ["result"])
        factory.assert_called_once_with({})
