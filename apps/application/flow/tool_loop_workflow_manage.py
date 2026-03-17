# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： workflow_manage.py
    @date：2024/1/9 17:40
    @desc:
"""
from application.flow.i_step_node import ToolFlowParamsSerializer
from application.flow.loop_workflow_manage import LoopWorkflowManage


class ToolLoopWorkflowManage(LoopWorkflowManage):
    def get_params_serializer_class(self):
        return ToolFlowParamsSerializer

    def get_source_type(self):
        return "TOOL"

    def get_source_id(self):
        return self.params.get('tool_id')
