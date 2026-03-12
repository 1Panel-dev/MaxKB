# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： tool_workflow_manage.py
    @date：2026/3/12 15:17
    @desc:
"""
from concurrent.futures import ThreadPoolExecutor

from application.flow.common import Workflow
from application.flow.i_step_node import WorkFlowPostHandler
from application.flow.workflow_manage import WorkflowManage
from common.handle.base_to_response import BaseToResponse
from common.handle.impl.response.system_to_response import SystemToResponse

executor = ThreadPoolExecutor(max_workers=200)


class ToolWorkflowManage(WorkflowManage):
    def __init__(self, flow: Workflow, params, work_flow_post_handler: WorkFlowPostHandler,
                 base_to_response: BaseToResponse = SystemToResponse(), form_data=None,
                 start_node_id=None,
                 start_node_data=None, chat_record=None, child_node=None, is_the_task_interrupted=lambda: False):
        super().__init__(flow, params, work_flow_post_handler, base_to_response, form_data, None, None, None,
                         None, None, start_node_id, start_node_data, chat_record, child_node, is_the_task_interrupted)

    def get_start_node(self):
        return self.flow.get_node('tool-start-node')
