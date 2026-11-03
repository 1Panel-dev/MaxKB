"""MCP protocol helpers shared by the application and knowledge MCP servers."""

import json

PROTOCOL_VERSIONS = ("2025-03-26", "2025-06-18", "2025-11-25")

DEFAULT_PROTOCOL_VERSION = "2025-06-18"


def initialize_result(params, server_name):
    # 客户端请求的版本受支持时原样返回，否则返回默认版本，由客户端决定是否继续
    version = (params or {}).get("protocolVersion")
    return {
        "protocolVersion": version if version in PROTOCOL_VERSIONS else DEFAULT_PROTOCOL_VERSION,
        "serverInfo": {"name": server_name, "version": "1.0.0"},
        "capabilities": {"tools": {}},
    }


def json_result(data, structured_content=None):
    """工具结果：文本内容为 data 的 JSON，structuredContent 默认与 data 相同"""
    return {
        "content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}],
        "structuredContent": data if structured_content is None else structured_content,
    }


def tool_error(text):
    return {"isError": True, "content": [{"type": "text", "text": text}]}
