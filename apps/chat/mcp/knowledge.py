"""Knowledge equivalent of the application's MCPToolHandler."""

import json

from rest_framework.exceptions import ValidationError

from knowledge.services.external_retrieval import retrieve
from knowledge.services.retrieval_access import RetrievalError

PROTOCOL_VERSIONS = ("2025-03-26", "2025-06-18", "2025-11-25")


class KnowledgeMCPToolHandler:
    def __init__(self, knowledge, identity):
        self.knowledge, self.identity = knowledge, identity
        self.tool_name = f"knowledge_{knowledge.id}"

    def initialize(self, params):
        version = params.get("protocolVersion")
        if (
            not isinstance(version, str)
            or not isinstance(params.get("capabilities"), dict)
            or not isinstance(params.get("clientInfo"), dict)
        ):
            raise ValidationError("Invalid initialization parameters.")
        return {
            "protocolVersion": version if version in PROTOCOL_VERSIONS else "2025-06-18",
            "serverInfo": {"name": "maxkb-knowledge-mcp", "version": "1.0.0"},
            "capabilities": {"tools": {}},
        }

    def list_tools(self):
        return {
            "tools": [
                {
                    "name": self.tool_name,
                    "description": f"检索知识库：{self.knowledge.name}",
                    "inputSchema": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["query_text"],
                        "properties": {
                            "query_text": {"type": "string", "minLength": 1, "maxLength": 8000},
                            "top_number": {"type": "integer", "minimum": 1, "maximum": 50, "default": 5},
                            "similarity": {"type": "number", "minimum": 0, "maximum": 1, "default": 0},
                            "search_mode": {
                                "type": "string",
                                "enum": ["embedding", "keywords", "blend"],
                                "default": "embedding",
                            },
                        },
                    },
                }
            ]
        }

    def call_tool(self, params):
        if params.get("name") != self.tool_name:
            raise ValidationError("Unknown tool.")
        try:
            output = retrieve(self.knowledge.id, self.identity, params.get("arguments", {}))
        except (RetrievalError, ValidationError):
            raise
        except Exception:
            return {"isError": True, "content": [{"type": "text", "text": "Knowledge retrieval failed."}]}
        return {"content": [{"type": "text", "text": json.dumps(output, ensure_ascii=False)}]}
