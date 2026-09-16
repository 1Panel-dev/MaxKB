"""MCP backend honoring the application's sandbox switch."""

from langchain_mcp_adapters.client import MultiServerMCPClient
from mcp.types import CallToolResult

from common.mcp.config import InternalMCPConfig, remote_connection, validate_mcp_servers
from common.mcp.sandbox import sandbox_connection
from maxkb.const import CONFIG


class SandboxMCPBackend(MultiServerMCPClient):
    """Provide MCP tools and sessions using the configured sandbox mode.

    With SANDBOX enabled, inherited get_tools() creates tools whose later
    invocations also open sandbox workers. When explicitly disabled, use remote
    SDK connections directly for local development. This backend supplies the
    agent's tools; SandboxShellBackend handles skill files and shell commands.
    """

    def __init__(self, servers: dict):
        super().__init__(connections=self._build_connections(servers))

    @staticmethod
    def _build_connections(servers: dict) -> dict:
        if not isinstance(servers, dict):
            raise ValueError("MCP servers must be an object")
        connections = {}
        for name, config in servers.items():
            if not isinstance(config, dict):
                raise ValueError("MCP server configuration must be an object")
            internal = isinstance(config, InternalMCPConfig)
            if internal and config.get("transport") == "stdio":
                connections[name] = dict(config)
                continue
            validate_mcp_servers({name: config})
            if internal:
                connections[name] = dict(config)
            elif bool(int(CONFIG.get("SANDBOX", 1))):
                connections[name] = sandbox_connection(config)
            else:
                connections[name] = remote_connection(config)
        return connections

    async def call_tool(self, server_name: str, tool_name: str, arguments: dict | None = None) -> CallToolResult:
        """Call one tool and close its session/worker, preserving the MCP result."""
        async with self.session(server_name) as session:
            return await session.call_tool(tool_name, arguments)
