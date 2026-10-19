# coding=utf-8
"""
@project: MaxKB
@file： chat_completion_serializers.py
@desc: 通用流式补全（支持 function calling），供前端工作流 AI 生成的 agent 循环逐轮调用
"""

import json

from common.config.embedding_config import ModelManage
from common.exception.app_exception import AppApiException
from common.utils.common import to_stream_response_simple
from common.utils.logger import maxkb_logger
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from langchain_core.messages import convert_to_messages
from models_provider.base_model_provider import ModelTypeConst
from models_provider.models import Model
from models_provider.tools import (
    get_model,
    get_model_default_params,
    get_model_instance_by_model_workspace_id,
    reset_model_params,
)
from rest_framework import serializers

# messages 条数护栏，迭代上限由前端 agent 循环控制
MAX_MESSAGES = 400


class ChatCompletionSerializers(serializers.Serializer):
    workspace_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Workspace ID"))
    model_id = serializers.CharField(required=True, label=_("Model"))
    model_params_setting = serializers.JSONField(required=False, default=dict, label=_("Model params setting"))
    # OpenAI 格式消息：role 为 system/user/assistant/tool，assistant 可带 tool_calls 与 reasoning_content
    messages = serializers.ListField(child=serializers.DictField(), required=True, label=_("Chat context"))
    # OpenAI function 定义：[{type:'function', function:{name, description, parameters}}]
    tools = serializers.ListField(child=serializers.DictField(), required=False, default=list, label=_("Tools"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        messages = self.data.get("messages") or []
        if not messages:
            raise AppApiException(400, _("Messages cannot be empty"))
        if len(messages) > MAX_MESSAGES:
            raise AppApiException(400, _("Too many messages"))
        for message in messages:
            if message.get("role") not in ("system", "user", "assistant", "tool"):
                raise AppApiException(400, _("Authentication failed. Please verify that the parameters are correct."))
        model = QuerySet(Model).filter(id=self.data.get("model_id")).first()
        if model is None:
            raise AppApiException(500, _("Model does not exist"))
        if model.model_type != ModelTypeConst.LLM.name:
            raise AppApiException(400, _("Model does not exists or is not an LLM model"))
        # 共享/系统级模型:workspace_id 为字符串 "None",不校验传入的工作空间;否则必须属于传入的工作空间
        if (
            model.workspace_id != "None"
            and self.data.get("workspace_id")
            and self.data.get("workspace_id") != model.workspace_id
        ):
            raise AppApiException(403, _("Model is not visible to the workspace"))
        return model

    def _get_model_instance(self, model):
        model_id = self.data.get("model_id")
        model_params_setting = self.data.get("model_params_setting") or {}
        if model.workspace_id == "None":
            default_model_params = get_model_default_params(model)
            model_params = reset_model_params(default_model_params, **model_params_setting)
            return ModelManage.get_model(model_id, lambda _id: get_model(model, **model_params))
        return get_model_instance_by_model_workspace_id(
            model_id=model_id, workspace_id=model.workspace_id, **model_params_setting
        )

    def chat_completion(self):
        model = self.is_valid(raise_exception=True)
        messages = convert_to_messages([dict(m) for m in self.data.get("messages")])
        tools = [dict(t) for t in self.data.get("tools") or []]

        def event(payload: dict) -> str:
            return "data: " + json.dumps(payload, ensure_ascii=False) + "\n\n"

        def process():
            try:
                model_instance = self._get_model_instance(model)
                llm = model_instance.bind_tools(tools) if tools else model_instance
                content = ""
                reasoning = ""
                finish_reason = None
                usage = None
                # 按流式 index 聚合工具调用：id/name 只在首片出现，arguments 逐片拼接
                tool_calls_by_index: dict = {}
                for chunk in llm.stream(messages):
                    text = chunk.content if isinstance(chunk.content, str) else ""
                    if text:
                        content += text
                        yield event({"type": "delta", "content": text})
                    reasoning_delta = (chunk.additional_kwargs or {}).get("reasoning_content")
                    if reasoning_delta:
                        reasoning += reasoning_delta
                        yield event({"type": "reasoning", "content": reasoning_delta})
                    for tool_chunk in getattr(chunk, "tool_call_chunks", None) or []:
                        index = tool_chunk.get("index") or 0
                        call = tool_calls_by_index.setdefault(index, {"id": "", "name": "", "arguments": ""})
                        if tool_chunk.get("id"):
                            call["id"] = tool_chunk["id"]
                        if tool_chunk.get("name"):
                            call["name"] = call["name"] or tool_chunk["name"]
                        args_delta = tool_chunk.get("args") or ""
                        call["arguments"] += args_delta
                        if call["id"]:
                            yield event(
                                {"type": "tool_call", "id": call["id"], "name": call["name"], "arguments": args_delta}
                            )
                    metadata = chunk.response_metadata or {}
                    if metadata.get("finish_reason"):
                        finish_reason = metadata["finish_reason"]
                    if getattr(chunk, "usage_metadata", None):
                        usage = dict(chunk.usage_metadata)
                tool_calls = [
                    {
                        "id": call["id"],
                        "type": "function",
                        "function": {"name": call["name"], "arguments": call["arguments"] or "{}"},
                    }
                    for _index, call in sorted(tool_calls_by_index.items())
                    if call["id"] and call["name"]
                ]
                yield event(
                    {
                        "type": "completion",
                        "content": content,
                        "reasoningKey": "reasoning_content" if reasoning else None,
                        "reasoningContent": reasoning or None,
                        "toolCalls": tool_calls,
                        "finishReason": finish_reason or ("tool_calls" if tool_calls else "stop"),
                        "usage": usage,
                    }
                )
            except Exception as e:
                maxkb_logger.error(f"chat completion error: {e}", exc_info=True)
                yield event({"type": "error", "message": str(e)})
            yield "data: [DONE]\n\n"

        return to_stream_response_simple(process())
