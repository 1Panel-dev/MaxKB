"""Knowledge equivalent of the application's MCPToolHandler."""

import json
import uuid

from django.db.models import QuerySet
from rest_framework.exceptions import ValidationError

from chat.mcp.common import initialize_result, json_result, tool_error
from knowledge.models import Knowledge
from knowledge.services.external_retrieval import retrieve
from knowledge.services.retrieval_access import RetrievalError, authorized_ids

# 检索参数，单知识库 MCP 与全局知识库 MCP 的 search_knowledge 共用
RETRIEVAL_INPUT_PROPERTIES = {
    "query_text": {"type": "string", "minLength": 1, "maxLength": 8000},
    "top_number": {"type": "integer", "minimum": 1, "maximum": 50, "default": 5},
    "similarity": {"type": "number", "minimum": 0, "maximum": 1, "default": 0},
    "search_mode": {
        "type": "string",
        "enum": ["embedding", "keywords", "blend"],
        "default": "embedding",
    },
}

# 全局知识库 MCP 地址：先列出可检索的知识库，再按 knowledge_id 检索
LIST_KNOWLEDGE_TOOL = "list_knowledge"

SEARCH_KNOWLEDGE_TOOL = "search_knowledge"


def initialize_knowledge(params):
    if (
        not isinstance(params.get("protocolVersion"), str)
        or not isinstance(params.get("capabilities"), dict)
        or not isinstance(params.get("clientInfo"), dict)
    ):
        raise ValidationError("Invalid initialization parameters.")
    return initialize_result(params, "maxkb-knowledge-mcp")


def retrieve_result(knowledge_id, identity, arguments):
    """
    执行检索并组装工具结果。参数不合法、开关关闭或授权被撤销等以工具错误返回并附原因，
    调用方模型可据此修正后重试，而不是让 MCP 会话因 HTTP 错误中断。
    """
    try:
        output = retrieve(knowledge_id, identity, arguments)
    except RetrievalError as e:
        return tool_error(e.message)
    except ValidationError as e:
        return tool_error(json.dumps(e.detail, ensure_ascii=False, default=str))
    except Exception:
        return tool_error("Knowledge retrieval failed.")
    return json_result(output)


class KnowledgeMCPToolHandler:
    def __init__(self, knowledge, identity):
        self.knowledge, self.identity = knowledge, identity
        self.tool_name = f"knowledge_{knowledge.id}"

    def initialize(self, params):
        return initialize_knowledge(params)

    def list_tools(self):
        # 带上知识库描述，调用方模型才能判断什么问题该检索该知识库
        description = f"检索知识库：{self.knowledge.name}"
        if self.knowledge.desc:
            description = f"{description}\n{self.knowledge.desc}"
        return {
            "tools": [
                {
                    "name": self.tool_name,
                    "description": description,
                    "inputSchema": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["query_text"],
                        "properties": RETRIEVAL_INPUT_PROPERTIES,
                    },
                }
            ]
        }

    def call_tool(self, params):
        if params.get("name") != self.tool_name:
            raise ValidationError("Unknown tool.")
        return retrieve_result(self.knowledge.id, self.identity, params.get("arguments", {}))


class ChatUserKnowledgeMCPToolHandler:
    """
    全局知识库 MCP：以对话用户 API Key 的身份列出并检索其可访问的知识库，知识库再多工具数量也固定。
    可访问与单知识库 MCP 地址的判定一致：外部检索服务已开启，且未开启身份认证或当前对话用户已获授权。
    """

    def __init__(self, identity):
        self.identity = identity

    def initialize(self, params):
        return initialize_knowledge(params)

    def list_tools(self):
        return {
            "tools": [
                {
                    "name": LIST_KNOWLEDGE_TOOL,
                    "description": "List the knowledge bases you can search, with their id, name and description. "
                    f"Pick the one that fits the question and search it with {SEARCH_KNOWLEDGE_TOOL}.",
                    "inputSchema": {"type": "object", "properties": {}},
                },
                {
                    "name": SEARCH_KNOWLEDGE_TOOL,
                    "description": f"Search a knowledge base from {LIST_KNOWLEDGE_TOOL} by knowledge_id. "
                    "Returns the matching paragraphs with similarity scores and citations.",
                    "inputSchema": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["knowledge_id", "query_text"],
                        "properties": {
                            "knowledge_id": {
                                "type": "string",
                                "description": f"Id of the knowledge base to search, from {LIST_KNOWLEDGE_TOOL}.",
                            },
                            **RETRIEVAL_INPUT_PROPERTIES,
                        },
                    },
                },
            ]
        }

    def get_knowledge(self):
        knowledge = list(QuerySet(Knowledge).filter(external_service__enabled=True).order_by("name"))
        restricted = [str(item.id) for item in knowledge if item.external_service.get("authentication", False)]
        authorized = authorized_ids(self.identity.user_id, restricted) if restricted else set()
        return [
            item
            for item in knowledge
            if not item.external_service.get("authentication", False) or str(item.id) in authorized
        ]

    def list_knowledge(self):
        knowledge = [
            {"knowledge_id": str(item.id), "name": item.name, "desc": item.desc or ""} for item in self.get_knowledge()
        ]
        return json_result(knowledge, {"knowledge": knowledge})

    def search_knowledge(self, arguments):
        arguments = dict(arguments)
        knowledge_id = arguments.pop("knowledge_id", None)
        try:
            knowledge_id = str(uuid.UUID(str(knowledge_id)))
        except ValueError:
            return tool_error(f"Unknown knowledge_id: {knowledge_id}")
        # retrieve 内部会再次校验开关与授权，并在检索前后复核 API Key
        return retrieve_result(knowledge_id, self.identity, arguments)

    def call_tool(self, params):
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if name == LIST_KNOWLEDGE_TOOL:
            return self.list_knowledge()
        if name == SEARCH_KNOWLEDGE_TOOL:
            if not isinstance(arguments, dict):
                raise ValidationError("Invalid arguments.")
            return self.search_knowledge(arguments)
        raise ValidationError("Unknown tool.")
