# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： reply_node.py
    @date：2026/7/2 10:00
    @desc:
"""
from typing import List
import uuid_utils.compat as uuid
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode
from application.workflow.message.struct.content import NodeInfo, Position
from application.workflow.message.struct.text_content import TextContent
from application.workflow.status import Status


class ReplyNodeSerializer(serializers.Serializer):
    reply_type = serializers.CharField(required=True, label=_("Response Type"))
    fields = serializers.ListField(required=False, label=_("Reference Field"))
    content = serializers.CharField(required=False, allow_blank=True, allow_null=True,
                                    label=_("Direct answer content"))
    is_result = serializers.BooleanField(required=False, label=_('Whether to return content'))


class ReplyNode(INode):
    serializer_class = ReplyNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = 'reply-node'

    def execute(self):
        node_params = self.get_parameters()
        chunk_id = uuid.uuid7()

        reply_type = node_params.get('reply_type')
        fields = node_params.get('fields')
        content = node_params.get('content')
        is_result = node_params.get('is_result', False)

        if reply_type == 'referencing':
            result = self._get_reference_content(fields)
        else:
            result = self._generate_reply_content(content)

        self.write_context('answer', result)

        if is_result:
            node_info = NodeInfo(self.get_node_id(), self.get_node_name(), Status.SUCCESS)
            self.write(TextContent(str(chunk_id), result, Status.SUCCESS, node_info, Position(self.get_node_id())))

    def _generate_reply_content(self, prompt):
        if prompt is None:
            return ''
        return self.workflow_manage.generate_prompt(prompt)

    def _get_reference_content(self, fields: List[str]):
        if fields and len(fields) >= 2:
            return str(self.workflow_manage.get_reference_field(fields[0], fields[1:]))
        return ''
