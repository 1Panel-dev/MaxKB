# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： workflow_manage.py
    @date：2024/1/9 17:40
    @desc:
"""
from concurrent.futures import ThreadPoolExecutor
from typing import List

from django.db import close_old_connections
from django.utils.translation import get_language
from langchain_core.prompts import PromptTemplate

from application.flow.common import Workflow
from application.flow.i_step_node import WorkFlowPostHandler, INode
from application.flow.step_node import get_node
from application.flow.workflow_manage import WorkflowManage
from common.handle.base_to_response import BaseToResponse
from common.handle.impl.response.system_to_response import SystemToResponse

executor = ThreadPoolExecutor(max_workers=200)


class NodeResultFuture:
    def __init__(self, r, e, status=200):
        self.r = r
        self.e = e
        self.status = status

    def result(self):
        if self.status == 200:
            return self.r
        else:
            raise self.e


def await_result(result, timeout=1):
    try:
        result.result(timeout)
        return False
    except Exception as e:
        return True


class NodeChunkManage:

    def __init__(self, work_flow):
        self.node_chunk_list = []
        self.current_node_chunk = None
        self.work_flow = work_flow

    def add_node_chunk(self, node_chunk):
        self.node_chunk_list.append(node_chunk)

    def contains(self, node_chunk):
        return self.node_chunk_list.__contains__(node_chunk)

    def pop(self):
        if self.current_node_chunk is None:
            try:
                current_node_chunk = self.node_chunk_list.pop(0)
                self.current_node_chunk = current_node_chunk
            except IndexError as e:
                pass
        if self.current_node_chunk is not None:
            try:
                chunk = self.current_node_chunk.chunk_list.pop(0)
                return chunk
            except IndexError as e:
                if self.current_node_chunk.is_end():
                    self.current_node_chunk = None
                    if self.work_flow.answer_is_not_empty():
                        chunk = self.work_flow.base_to_response.to_stream_chunk_response(
                            self.work_flow.params['chat_id'],
                            self.work_flow.params['chat_record_id'],
                            '\n\n', False, 0, 0)
                        self.work_flow.append_answer('\n\n')
                        return chunk
                    return self.pop()
        return None


class LoopWorkflowManage(WorkflowManage):

    def __init__(self, flow: Workflow,
                 params,
                 work_flow_post_handler: WorkFlowPostHandler,
                 parentWorkflowManage,
                 loop_params,
                 get_loop_context,
                 base_to_response: BaseToResponse = SystemToResponse(),
                 start_node_id=None,
                 start_node_data=None, chat_record=None, child_node=None):
        self.parentWorkflowManage = parentWorkflowManage
        self.loop_params = loop_params
        self.get_loop_context = get_loop_context
        self.loop_field_list = []
        super().__init__(flow, params, work_flow_post_handler, base_to_response, None, None, None,
                         None,
                         None, start_node_id, start_node_data, chat_record, child_node)

    def get_node_cls_by_id(self, node_id, up_node_id_list=None,
                           get_node_params=lambda node: node.properties.get('node_data')):
        for node in self.flow.nodes:
            if node.id == node_id:
                node_instance = get_node(node.type)(node,
                                                    self.params, self, up_node_id_list,
                                                    get_node_params,
                                                    salt=self.get_index())
                return node_instance
        return None

    def stream(self):
        close_old_connections()
        language = get_language()
        self.run_chain_async(self.start_node, None, language)
        return self.await_result()

    def get_index(self):
        return self.loop_params.get('index')

    def get_start_node(self):
        start_node_list = [node for node in self.flow.nodes if
                           ['loop-start-node'].__contains__(node.type)]
        return start_node_list[0]

    def get_reference_field(self, node_id: str, fields: List[str]):
        """
        @param node_id: 节点id
        @param fields:  字段
        @return:
        """
        if node_id == 'global':
            return self.parentWorkflowManage.get_reference_field(node_id, fields)
        elif node_id == 'chat':
            return self.parentWorkflowManage.get_reference_field(node_id, fields)
        elif node_id == 'loop':
            loop_context = self.get_loop_context()
            return INode.get_field(loop_context, fields)
        else:
            node = self.get_node_by_id(node_id)
            if node:
                return node.get_reference_field(fields)
            return self.parentWorkflowManage.get_reference_field(node_id, fields)

    def get_workflow_content(self):
        context = {
            'global': self.context,
            'chat': self.chat_context,
            'loop': self.get_loop_context(),
        }

        for node in self.node_context:
            context[node.id] = node.context
        return context

    def init_fields(self):
        super().init_fields()
        loop_field_list = []
        loop_start_node = self.flow.get_node('loop-start-node')
        loop_input_field_list = loop_start_node.properties.get('loop_input_field_list')
        node_name = loop_start_node.properties.get('stepName')
        node_id = loop_start_node.id
        if loop_input_field_list is not None:
            for f in loop_input_field_list:
                loop_field_list.append(
                    {'label': f.get('label'), 'value': f.get('field'), 'node_id': node_id, 'node_name': node_name})
        self.loop_field_list = loop_field_list

    def reset_prompt(self, prompt: str):
        prompt = super().reset_prompt(prompt)
        for field in self.loop_field_list:
            chatLabel = f"loop.{field.get('value')}"
            chatValue = f"context.get('loop').get('{field.get('value', '')}','')"
            prompt = prompt.replace(chatLabel, chatValue)

        prompt = self.parentWorkflowManage.reset_prompt(prompt)
        return prompt

    def generate_prompt(self, prompt: str):
        """
        格式化生成提示词
        @param prompt: 提示词信息
        @return: 格式化后的提示词
        """

        context = {**self.get_workflow_content(), **self.parentWorkflowManage.get_workflow_content()}
        prompt = self.reset_prompt(prompt)
        prompt_template = PromptTemplate.from_template(prompt, template_format='jinja2')
        value = prompt_template.format(context=context)
        return value
