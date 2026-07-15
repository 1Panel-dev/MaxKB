# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： loop_workflow_manage.py
    @date：2026/7/2 10:00
    @desc:
"""
from typing import Dict, Optional, Callable

from application.workflow.common import Workflow, WorkflowType, Node
from application.workflow.i_node import INode
from application.workflow.workflow_manage import WorkflowManage, CallBack


class LoopWorkFlowManage(WorkflowManage):

    def __init__(self,
                 workflow: Workflow,
                 parameters: Dict,
                 workflow_type: WorkflowType,
                 call_back: CallBack,
                 get_start_node: Callable[[Workflow, WorkflowManage], INode],
                 parent_workflow_manage: WorkflowManage,
                 loop_context: Dict = None):
        self.parent_workflow_manage = parent_workflow_manage
        self.loop_context = loop_context or {}
        super().__init__(workflow, parameters, workflow_type, call_back, get_start_node)

    def get_parameters(self):
        return {**self.parameters, **self.loop_context}

    def get_parent_context(self, node_id, key):
        return self.parent_workflow_manage.get_context(node_id, key)

    def generate_prompt(self, prompt):
        prompt = self.workflow.reset_prompt(prompt)
        prompt = self.parent_workflow_manage.workflow.reset_prompt(prompt)
        context = {**self.context, **self.parent_workflow_manage.context}
        from langchain_core.prompts import PromptTemplate
        prompt_template = PromptTemplate.from_template(prompt, template_format='jinja2')
        return prompt_template.format(context=context)

    def get_reference_field(self, node_id, fields):
        """
        获取引用字段，先从当前工作流获取，获取不到再从父工作流获取
        @param node_id: 节点id
        @param fields:   字段
        @return: 引用数据
        """
        # 先从当前工作流获取
        result = super().get_reference_field(node_id, fields)
        if result is not None:
            return result

        # 从父工作流获取
        return self.parent_workflow_manage.get_reference_field(node_id, fields)
