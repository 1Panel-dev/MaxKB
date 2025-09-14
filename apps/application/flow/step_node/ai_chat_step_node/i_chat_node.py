# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： i_chat_node.py
    @date：2024/6/4 13:58
    @desc:
"""
from typing import Type

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult


class ChatNodeSerializer(serializers.Serializer):
    model_id = serializers.CharField(required=True, label=_("Model id"))
    system = serializers.CharField(required=False, allow_blank=True, allow_null=True,
                                   label=_("Role Setting"))
    prompt = serializers.CharField(required=True, label=_("Prompt word"))
    # 多轮对话数量
    dialogue_number = serializers.IntegerField(required=True, label=_("Number of multi-round conversations"))

    is_result = serializers.BooleanField(required=False,
                                         label=_('Whether to return content'))

    model_params_setting = serializers.DictField(required=False,
                                                 label=_("Model parameter settings"))
    model_setting = serializers.DictField(required=False,
                                          label='Model settings')
    dialogue_type = serializers.CharField(required=False, allow_blank=True, allow_null=True,
                                          label=_("Context Type"))
    mcp_enable = serializers.BooleanField(required=False, label=_("Whether to enable MCP"))
    mcp_servers = serializers.JSONField(required=False, label=_("MCP Server"))
    mcp_tool_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("MCP Tool ID"))
    mcp_tool_ids = serializers.ListField(child=serializers.UUIDField(), required=False, allow_empty=True, label=_("MCP Tool IDs"), )
    mcp_source = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("MCP Source"))

    tool_enable = serializers.BooleanField(required=False, default=False, label=_("Whether to enable tools"))
    tool_ids = serializers.ListField(child=serializers.UUIDField(), required=False, allow_empty=True,
                                     label=_("Tool IDs"), )
    mcp_output_enable = serializers.BooleanField(required=False, default=True, label=_("Whether to enable MCP output"))

class IChatNode(INode):
    type = 'ai-chat-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return ChatNodeSerializer

    def _run(self):
        return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, model_id, system, prompt, dialogue_number, history_chat_record, stream, chat_id,
                chat_record_id,
                model_params_setting=None,
                dialogue_type=None,
                model_setting=None,
                mcp_enable=False,
                mcp_servers=None,
                mcp_tool_id=None,
                mcp_tool_ids=None,
                mcp_source=None,
                tool_enable=False,
                tool_ids=None,
                mcp_output_enable=True,
                **kwargs) -> NodeResult:
        pass
