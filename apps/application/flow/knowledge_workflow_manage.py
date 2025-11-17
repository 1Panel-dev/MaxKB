# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： Knowledge_workflow_manage.py
    @date：2025/11/13 19:02
    @desc:
"""

from application.flow.common import Workflow
from application.flow.i_step_node import WorkFlowPostHandler, KnowledgeFlowParamsSerializer
from application.flow.workflow_manage import WorkflowManage
from common.handle.base_to_response import BaseToResponse
from common.handle.impl.response.system_to_response import SystemToResponse


class KnowledgeWorkflowManage(WorkflowManage):

    def __init__(self, flow: Workflow,
                 params,
                 work_flow_post_handler: WorkFlowPostHandler,
                 base_to_response: BaseToResponse = SystemToResponse(),
                 start_node_id=None,
                 start_node_data=None, chat_record=None, child_node=None):
        super().__init__(flow, params, work_flow_post_handler, base_to_response, None, None, None,
                         None,
                         None, None, start_node_id, start_node_data, chat_record, child_node)

    def get_params_serializer_class(self):
        return KnowledgeFlowParamsSerializer

    def get_start_node(self):
        start_node_list = [node for node in self.flow.nodes if
                           self.params.get('data_source', {}).get('node_id') == node.id]
        return start_node_list[0]
