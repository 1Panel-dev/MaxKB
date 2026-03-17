# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： i_function_lib_node.py
    @date：2024/8/8 16:21
    @desc:
"""
from typing import Type

from django.db import connection
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.common import WorkflowMode
from application.flow.i_step_node import INode, NodeResult
from common.field.common import ObjectField
from tools.models.tool import Tool, ToolType


class InputField(serializers.Serializer):
    field = serializers.CharField(required=True, label=_('Variable Name'))
    label = serializers.CharField(required=True, label=_('Variable Label'))
    source = serializers.CharField(required=True, label=_('Variable Source'))
    type = serializers.CharField(required=True, label=_('Variable Type'))
    value = ObjectField(required=True, label=_("Variable Value"), model_type_list=[str, list, bool, dict, int, float])


class FunctionLibNodeParamsSerializer(serializers.Serializer):
    tool_lib_id = serializers.UUIDField(required=True, label=_('Library ID'))
    input_field_list = InputField(required=True, many=True)
    is_result = serializers.BooleanField(required=False,
                                         label=_('Whether to return content'))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        f_lib = QuerySet(Tool).filter(id=self.data.get('tool_lib_id'), tool_type=ToolType.WORKFLOW).first()
        # 归还链接到连接池
        connection.close()
        if f_lib is None:
            raise Exception(_('The function has been deleted'))


class IToolWorkflowLibNode(INode):
    type = 'tool-workflow-lib-node'
    support = [WorkflowMode.APPLICATION, WorkflowMode.APPLICATION_LOOP, WorkflowMode.KNOWLEDGE,
               WorkflowMode.KNOWLEDGE_LOOP, WorkflowMode.TOOL, WorkflowMode.TOOL_LOOP]

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return FunctionLibNodeParamsSerializer

    def _run(self):
        return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, tool_lib_id, input_field_list, **kwargs) -> NodeResult:
        pass
