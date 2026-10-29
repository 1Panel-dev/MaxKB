# coding=utf-8
"""
@project: MaxKB
@Author：虎虎虎
@file： llm_node.py
@date：2026/10/16
@desc: LLM 节点:单次调用大模型(不执行工具),输出 content/reasoning_content/refusal/is_refusal/usage/tool_calls/finish_reason
"""

import asyncio
import contextlib
import json

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage, SystemMessage
from rest_framework import serializers

from application.workflow.common import AsyncRunner, CancelledException, WorkflowType
from application.workflow.i_node import INode
from application.workflow.message.aggregator import AggregationManager
from application.workflow.message.struct.content import Content, NodeInfo, Position
from application.workflow.message.struct.reasoning_content import ReasoningContent
from application.workflow.message.struct.text_content import TextContent
from application.workflow.message.struct.tool_content import ToolContent
from application.workflow.nodes.llm_node.message_converter import to_messages
from application.workflow.status import Status
from common.exception.app_exception import AppApiException
from common.utils.count_tokens import count_local_tokens
from common.utils.partial_json import complete_json
from models_provider.models import Model
from models_provider.tools import get_model_credential, get_model_instance_by_model_workspace_id


class LLMNodeSerializer(serializers.Serializer):
    model_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Model id"))
    model_id_type = serializers.CharField(required=False, default="custom", label=_("Model id type"))
    model_id_reference = serializers.ListField(
        required=False, child=serializers.CharField(), allow_empty=True, label=_("Reference Field")
    )
    model_params_setting = serializers.DictField(required=False, label=_("Model parameter settings"))
    system = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Role Setting"))
    prompt = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Prompt word"))
    # 上下文:enable_context 为真时从 context_variable 引用的变量取消息列表,否则不带上下文
    enable_context = serializers.BooleanField(required=False, default=False, label=_("Custom context"))
    context_variable = serializers.ListField(
        required=False, child=serializers.CharField(), allow_empty=True, label=_("Context variable")
    )
    # 工具定义(OpenAI function 格式),只交给模型做决策,不在本节点执行
    tools = serializers.DictField(required=False, allow_null=True, label=_("Tools"))
    is_result = serializers.BooleanField(required=False, default=False, label=_("Whether to return content"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        # reference / default 在运行时才解析,此处只校验自定义模型
        if (self.data.get("model_id_type") or "custom") in ("reference", "default"):
            return
        model_id = self.data.get("model_id")
        if not model_id or not QuerySet(Model).filter(id=model_id).exists():
            raise AppApiException(500, _("The model of the node does not exist"))


def _get_default_model_params_setting(model_id):
    model = QuerySet(Model).filter(id=model_id).first()
    if model is None:
        # 模型已删除或不可见(如默认模型/引用变量指向了失效的模型)
        raise AppApiException(500, _("The model of the node does not exist"))
    credential = get_model_credential(model.provider, model.model_type, model.model_name)
    return credential.get_model_params_setting_form(model.model_name).get_default_form_data()


class ToolCallAccumulator:
    """
    流式工具调用累积:为每个调用分配一个 uuid7,流式 ToolContent 与 tool_calls 输出共用,原始 id 另存为 original_id。
    响应 id 只出现在调用的首个分片:按 index 识别同一调用,无 index 时按原始 id,两者都没有时归属最近一次调用。
    不依赖 LangChain 的分片合并(无 index 时其会把后续分片误判为新调用)。
    """

    def __init__(self):
        self._key_to_id = {}
        self._calls = {}
        self._last_id = None

    def append(self, index, original_id, name, args):
        """累积一个分片,返回该调用的 uuid7;无法归属时返回 None"""
        original_id = original_id or None
        key = index if index is not None else original_id
        if key is None:
            tool_call_id = self._last_id
        else:
            if key not in self._key_to_id:
                self._key_to_id[key] = str(uuid.uuid7())
                self._calls[self._key_to_id[key]] = {"original_id": None, "name": "", "arguments": ""}
            tool_call_id = self._key_to_id[key]
        if tool_call_id is None:
            return None
        call = self._calls[tool_call_id]
        call["original_id"] = call["original_id"] or original_id
        call["name"] = call["name"] or name or ""
        call["arguments"] += args or ""
        self._last_id = tool_call_id
        return tool_call_id

    def name_of(self, tool_call_id):
        """调用名只在首个分片返回,后续分片输出时用累积到的名称补齐"""
        return self._calls[tool_call_id]["name"]

    def tool_calls(self):
        return [
            {
                "index": index,
                "id": tool_call_id,
                "original_id": call["original_id"],
                "type": "function",
                "name": call["name"],
                "arguments": _complete_arguments(call["arguments"]),
            }
            for index, (tool_call_id, call) in enumerate(self._calls.items())
        ]


def _complete_arguments(arguments):
    """输出被截断(达到最大 token)或含非法转义时补全为合法 JSON,无法补全时原样返回"""
    if not arguments:
        return "{}"
    try:
        return complete_json(arguments)
    except ValueError:
        return arguments


def _message_to_dict(message):
    """执行详情中展示的消息,保留工具调用信息便于排查上下文"""
    result = {"content": message.content, "role": message.type}
    if getattr(message, "tool_calls", None):
        result["tool_calls"] = [
            {
                "id": tc.get("id"),
                "name": tc.get("name"),
                "arguments": json.dumps(tc.get("args") or {}, ensure_ascii=False),
            }
            for tc in message.tool_calls
        ]
    if getattr(message, "tool_call_id", None):
        result["tool_call_id"] = message.tool_call_id
    return result


def _to_openai_tool(tool):
    function = tool.get("function") or {}
    result = {"name": function.get("name"), "description": function.get("description") or ""}
    if function.get("parameters"):
        result["parameters"] = function.get("parameters")
    return {"type": tool.get("type") or "function", "function": result}


class LLMNode(INode):
    serializer_class = LLMNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = "llm-node"

    def __init__(self, node, workflow_manage, get_node_parameters):
        super().__init__(node, workflow_manage, get_node_parameters)
        self.async_runner = AsyncRunner()
        self.is_result = False

    def cancel(self):
        self.async_runner.cancel()
        super().cancel()

    def write(self, message: Content):
        super().write(message)
        self.data.setdefault("messages", []).append(message)

    def _output(self, message: Content):
        """仅在开启返回内容时输出给用户"""
        if self.is_result:
            self.write(message)

    def execute(self):
        workflow_params = self.get_workflow_parameters()
        node_params = self.get_parameters()
        self.is_result = node_params.get("is_result", False)

        model_id = node_params.get("model_id")
        model_params_setting = node_params.get("model_params_setting")
        model_id_type = node_params.get("model_id_type", "custom")
        model_id_reference = node_params.get("model_id_reference")
        if model_id_type == "reference" and model_id_reference:
            reference_data = self.workflow_manage.get_reference_field(model_id_reference[0], model_id_reference[1:])
            if reference_data and isinstance(reference_data, dict):
                model_id = reference_data.get("model_id", model_id)
                model_params_setting = reference_data.get("model_params_setting")
        if model_id_type == "default":
            default_model_setting = (workflow_params.get("default_model_setting") or {}).get("LLM") or {}
            if isinstance(default_model_setting, dict):
                model_id = default_model_setting.get("model_id", model_id)
                model_params_setting = default_model_setting.get("model_params_setting")
        if not model_id:
            raise Exception(_("Model is not allowed to be empty"))
        if model_params_setting is None:
            model_params_setting = _get_default_model_params_setting(model_id)
        chat_model = get_model_instance_by_model_workspace_id(
            model_id, workflow_params.get("workspace_id"), **(model_params_setting or {})
        )

        message_list = self._build_messages(node_params)
        self.write_context("message_list", [_message_to_dict(m) for m in message_list])

        tools = self._get_tools(node_params.get("tools"))
        model = chat_model.bind_tools(tools) if tools else chat_model

        self._check_cancelled()
        self.async_runner.run_async(lambda: self._stream_response(model, chat_model, message_list))

    def _build_messages(self, node_params):
        if node_params.get("enable_context") and node_params.get("context_variable"):
            context_variable = node_params.get("context_variable")
            messages = to_messages(self.workflow_manage.get_reference_field(context_variable[0], context_variable[1:]))
        else:
            messages = []

        system = self.workflow_manage.generate_prompt(node_params.get("system") or "")
        if system:
            # 上下文首条已是 system 时合并为一条,避免出现多条 system(部分模型要求 system 唯一)
            if messages and isinstance(messages[0], SystemMessage):
                existing = messages[0].content if isinstance(messages[0].content, str) else ""
                messages[0] = SystemMessage(f"{system}\n\n{existing}" if existing.strip() else system)
            else:
                messages.insert(0, SystemMessage(system))

        prompt = self.workflow_manage.generate_prompt(node_params.get("prompt") or "")
        if prompt:
            messages.append(HumanMessage(prompt))
        return messages

    def _get_tools(self, tools_config):
        if not tools_config:
            return []
        if tools_config.get("location") == "reference":
            reference = tools_config.get("reference") or []
            tools = self.workflow_manage.get_reference_field(reference[0], reference[1:]) if reference else None
        else:
            tools = tools_config.get("tools")
        if isinstance(tools, str):
            tools = json.loads(tools)
        return [_to_openai_tool(t) for t in (tools or []) if isinstance(t, dict)]

    async def _stream_response(self, model, chat_model, message_list):
        node_info = NodeInfo(self.get_node_id(), self.get_node_name(), Status.RUNNING)
        position = Position(self.get_node_id())
        reasoning_content_id = str(uuid.uuid7())
        text_content_id = str(uuid.uuid7())
        tool_call_accumulator = ToolCallAccumulator()
        reasoning_content = ""
        reasoning_end = False
        full = None
        finish_reason = "error"
        response = model.astream(message_list)
        try:
            async for chunk in response:
                self._check_cancelled()
                # astream() falls back to a complete message when streaming is disabled.
                # Normalize a copy so tool arguments follow the same accumulation path.
                if isinstance(chunk, AIMessage) and not isinstance(chunk, AIMessageChunk):
                    chunk = AIMessageChunk(**chunk.model_dump(exclude={"type"}))
                full = chunk if full is None else full + chunk
                reasoning_chunk = chunk.additional_kwargs.get("reasoning_content")
                if reasoning_chunk and not reasoning_end:
                    reasoning_content += reasoning_chunk
                    self._output(
                        ReasoningContent(reasoning_content_id, reasoning_chunk, Status.RUNNING, node_info, position)
                    )
                if text := chunk.text:
                    if reasoning_content and not reasoning_end:
                        reasoning_end = True
                        self._output(ReasoningContent(reasoning_content_id, "", Status.SUCCESS, node_info, position))
                    self._output(TextContent(text_content_id, text, Status.RUNNING, node_info, position))
                for tc in chunk.tool_call_chunks or []:
                    tool_call_id = tool_call_accumulator.append(
                        tc.get("index"), tc.get("id"), tc.get("name"), tc.get("args")
                    )
                    if not tool_call_id:
                        continue
                    if tc.get("name") or tc.get("args"):
                        self._output(
                            ToolContent(
                                tool_call_id,
                                tool_call_accumulator.name_of(tool_call_id),
                                tc.get("args") or "",
                                "",
                                Status.RUNNING,
                                node_info,
                                position,
                            )
                        )
            finish_reason = None
        except CancelledException:
            finish_reason = "cancelled"
            raise
        finally:
            self._output(
                TextContent(
                    text_content_id,
                    "",
                    Status.SUCCESS,
                    NodeInfo(self.get_node_id(), self.get_node_name(), Status.SUCCESS),
                    position,
                )
            )
            # 无论正常结束、抛异常还是被取消中断,都落盘已累积内容并关闭 LLM 流式响应底层连接
            await asyncio.to_thread(
                self._write_final_context,
                chat_model,
                message_list,
                full,
                reasoning_content,
                finish_reason,
                tool_call_accumulator.tool_calls(),
            )
            with contextlib.suppress(Exception):
                await response.aclose()

    def _write_final_context(self, chat_model, message_list, message, reasoning_content, finish_reason, tool_calls):
        content = str(message.text) if message is not None else ""
        additional_kwargs = message.additional_kwargs if message is not None else {}
        response_metadata = message.response_metadata if message is not None else {}
        refusal = additional_kwargs.get("refusal")

        usage_metadata = message.usage_metadata if message is not None else None
        if usage_metadata:
            prompt_tokens = usage_metadata.get("input_tokens", 0)
            completion_tokens = usage_metadata.get("output_tokens", 0)
        elif self.async_runner.cancel_event.is_set():
            # 中断时模型已不可用，只能走本地 tokenizer 计算
            prompt_tokens, completion_tokens = count_local_tokens(message_list, content)
        else:
            prompt_tokens = chat_model.get_num_tokens_from_messages(message_list)
            completion_tokens = chat_model.get_num_tokens(content)

        if finish_reason is None:
            finish_reason = response_metadata.get("finish_reason") or response_metadata.get("stop_reason")
            if not finish_reason:
                finish_reason = "tool_calls" if tool_calls else "stop"
        self.write_context("content", content)
        self.write_context("reasoning_content", reasoning_content)
        self.write_context("refusal", refusal)
        self.write_context("is_refusal", bool(refusal))
        self.write_context(
            "usage",
            {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
        )
        self.write_context("tool_calls", tool_calls)
        self.write_context("finish_reason", finish_reason)
        self.data["message_tokens"] = prompt_tokens
        self.data["answer_tokens"] = completion_tokens

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        aggregation = AggregationManager()
        for m in self.data.get("messages") or []:
            aggregation.aggregate(m)
        details.update(
            {
                "message_list": self.get_context("message_list"),
                "content": self.get_context("content"),
                "reasoning_content": self.get_context("reasoning_content"),
                "refusal": self.get_context("refusal"),
                "is_refusal": self.get_context("is_refusal"),
                "usage": self.get_context("usage"),
                "tool_calls": self.get_context("tool_calls"),
                "finish_reason": self.get_context("finish_reason"),
                "message_tokens": self.data.get("message_tokens"),
                "answer_tokens": self.data.get("answer_tokens"),
                "messages": aggregation.get_contents(),
            }
        )
        return details
