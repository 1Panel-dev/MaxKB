"""Compatibility exports and client factory for the dedicated MCP backend."""

from application.workflow.backend.sandbox_mcp import SandboxMCPBackend
from common.mcp.config import InternalMCPConfig, validate_mcp_servers


__all__ = ["InternalMCPConfig", "validate_mcp_servers", "create_mcp_client"]


def create_mcp_client(servers):
    """Keep existing callers compatible with the dedicated MCP backend."""
    return SandboxMCPBackend(servers)
