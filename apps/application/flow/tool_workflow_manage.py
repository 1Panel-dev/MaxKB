# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： tool_workflow_manage.py
    @date：2026/3/12 15:17
    @desc:
"""
import time
from concurrent.futures import ThreadPoolExecutor

from django.db import close_old_connections
from django.utils.translation import get_language

from application.flow.common import Workflow
from application.flow.i_step_node import WorkFlowPostHandler, ToolFlowParamsSerializer
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
        self.out_context = {}

    def get_params_serializer_class(self):
        return ToolFlowParamsSerializer

    def run(self):
        self.context['start_time'] = time.time()
        close_old_connections()
        language = get_language()
        if self.params.get('stream'):
            return self.run_stream(self.start_node, None, language)
        return self.run_block(language)

    def stream(self):
        close_old_connections()
        language = get_language()
        self.run_chain_async(self.start_node, None, language)
        return self.await_result(is_cleanup=False)

    def get_start_node(self):
        return self.flow.get_node('tool-start-node')

    def get_base_node(self):
        """
        获取基础节点
        @return:
        """
        return self.flow.get_node('tool-base-node')

    def get_input_field_list(self):
        """
        获取输入字段列表
        @return: 输入字段配置
        """
        base_node = self.get_base_node()
        return base_node.properties.get("user_input_field_list") or []

    def get_output_field_list(self):
        """
        获取输出字段列表配置
        @return:  输出字段列表配置
        """
        base_node = self.get_base_node()
        return base_node.properties.get("user_output_field_list") or []

    def get_input(self):
        """
        获取用户输入
        @return: 用户输入
        """
        input_field_list = self.get_input_field_list()
        return {f.get('field'): self.params.get(f.get('field')) for f in input_field_list}

    def get_source_type(self):
        return "TOOL"

    def get_source_id(self):
        return self.params.get('tool_id')
