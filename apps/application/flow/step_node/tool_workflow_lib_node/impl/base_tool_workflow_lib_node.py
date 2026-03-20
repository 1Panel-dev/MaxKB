# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： base_tool_workflow_lib_node.py.py
    @date：2026/3/16 13:55
    @desc:
"""

import time
from typing import Dict

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from application.flow.common import WorkflowMode, Workflow
from application.flow.i_step_node import NodeResult, ToolWorkflowPostHandler, INode
from application.flow.step_node.tool_workflow_lib_node.i_tool_workflow_lib_node import IToolWorkflowLibNode
from application.models import ChatRecord
from application.serializers.common import ToolExecute
from common.exception.app_exception import ChatException
from common.handle.impl.response.loop_to_response import LoopToResponse
from tools.models import ToolWorkflowVersion


def _write_context(node_variable: Dict, workflow_variable: Dict, node: INode, workflow, answer: str,
                   reasoning_content: str):
    result = node_variable.get('result')
    node.context['application_node_dict'] = node_variable.get('application_node_dict')
    node.context['node_dict'] = node_variable.get('node_dict', {})
    node.context['is_interrupt_exec'] = node_variable.get('is_interrupt_exec')
    node.context['message_tokens'] = result.get('usage', {}).get('prompt_tokens', 0)
    node.context['answer_tokens'] = result.get('usage', {}).get('completion_tokens', 0)
    node.context['answer'] = answer
    node.context['result'] = answer
    node.context['reasoning_content'] = reasoning_content
    node.context['run_time'] = time.time() - node.context['start_time']
    if workflow.is_result(node, NodeResult(node_variable, workflow_variable)):
        node.answer_text = answer


def get_answer_list(instance, child_node_node_dict, runtime_node_id):
    answer_list = instance.get_record_answer_list()
    for a in answer_list:
        _v = child_node_node_dict.get(a.get('runtime_node_id'))
        if _v:
            a['runtime_node_id'] = runtime_node_id
            a['child_node'] = _v
    return answer_list


def write_context_stream(node_variable: Dict, workflow_variable: Dict, node: INode, workflow):
    """
    写入上下文数据 (流式)
    @param node_variable:      节点数据
    @param workflow_variable:  全局数据
    @param node:               节点
    @param workflow:           工作流管理器
    """
    workflow_manage_new_instance = node_variable.get('workflow_manage_new_instance')
    node_params = node.node_params
    start_node_id = node_params.get('child_node', {}).get('runtime_node_id')
    child_node_data = node.context.get('child_node_data') or []
    start_node_data = None
    chat_record = None
    child_node = None
    if start_node_id:
        chat_record_id = node_params.get('child_node', {}).get('chat_record_id')
        child_node = node_params.get('child_node', {}).get('child_node')
        start_node_data = node_params.get('node_data')
        chat_record = ChatRecord(id=chat_record_id, answer_text_list=[], answer_text='',
                                 details=child_node_data)
    instance = workflow_manage_new_instance(start_node_id,
                                            start_node_data, chat_record, child_node)
    answer = ''
    reasoning_content = ''
    usage = {}
    node_child_node = {}
    is_interrupt_exec = False
    response = instance.stream()
    child_node_node_dict = {}
    for chunk in response:
        response_content = chunk
        content = (response_content.get('content', '') or '')
        runtime_node_id = response_content.get('runtime_node_id', '')
        chat_record_id = response_content.get('chat_record_id', '')
        child_node = response_content.get('child_node')
        node_type = response_content.get('node_type')
        _reasoning_content = (response_content.get('reasoning_content', '') or '')
        if node_type == 'form-node':
            is_interrupt_exec = True
        answer += content
        reasoning_content += _reasoning_content
        node_child_node = {'runtime_node_id': runtime_node_id, 'chat_record_id': chat_record_id,
                           'child_node': child_node}

        child_node = chunk.get('child_node')
        runtime_node_id = chunk.get('runtime_node_id', '')
        chat_record_id = chunk.get('chat_record_id', '')
        child_node_node_dict[runtime_node_id] = {
            'runtime_node_id': runtime_node_id,
            'chat_record_id': chat_record_id,
            'child_node': child_node}
        content_chunk = (chunk.get('content', '') or '')
        reasoning_content_chunk = (chunk.get('reasoning_content', '') or '')
        reasoning_content += reasoning_content_chunk
        answer += content_chunk
        yield chunk
        if chunk.get('node_status', "SUCCESS") == 'ERROR':
            is_interrupt_exec = True
            node.status = 500
            node.err_message = chunk.get('content')
        usage = response_content.get('usage', {})
    child_answer_data = get_answer_list(instance, child_node_node_dict, node.runtime_node_id)
    node.context['usage'] = {'usage': usage}
    node.context['child_node'] = node_child_node
    node.context['child_node_data'] = instance.get_runtime_details()
    node.context['is_interrupt_exec'] = is_interrupt_exec
    node.context['child_node_data'] = instance.get_runtime_details()
    node.context['child_answer_data'] = child_answer_data
    node.context['run_time'] = time.time() - node.context.get("start_time")
    for key, value in instance.out_context.items():
        node.context[key] = value


def _is_interrupt_exec(node, node_variable: Dict, workflow_variable: Dict):
    return node.context.get('is_interrupt_exec', False)


class BaseToolWorkflowLibNodeNode(IToolWorkflowLibNode):
    def get_parameters(self, input_field_list):
        result = {}
        for input in input_field_list:
            source = input.get('source')
            value = input.get('value')
            if source == 'reference':
                value = self.workflow_manage.get_reference_field(
                    value[0],
                    value[1:])
            result[input.get('field')] = value

        return result

    def save_context(self, details, workflow_manage):
        self.context['child_answer_data'] = details.get('child_answer_data')
        self.context['child_node_data'] = details.get('child_node_data')
        self.context['result'] = details.get('result')
        self.context['exception_message'] = details.get('err_message')
        if self.node_params.get('is_result'):
            self.answer_text = str(details.get('result'))

    @staticmethod
    def to_chat_record(record):
        if record is None:
            return None
        return ChatRecord(
            answer_text_list=record.meta.get('answer_text_list'),
            details=record.meta.get('details'),
            answer_text='',
        )

    def execute(self, tool_lib_id, input_field_list, **kwargs) -> NodeResult:
        from application.flow.tool_workflow_manage import ToolWorkflowManage
        workspace_id = self.workflow_manage.get_body().get('workspace_id')
        tool_workflow_version = QuerySet(ToolWorkflowVersion).filter(tool_id=tool_lib_id).order_by(
            '-create_time')[0:1].first()
        if tool_workflow_version is None:
            raise ChatException(500, _("The tool has not been published. Please use it after publishing."))
        parameters = self.get_parameters(input_field_list)
        tool_record_id = (self.node_params.get('child_node') or {}).get('chat_record_id') or str(uuid.uuid7())
        took_execute = ToolExecute(tool_lib_id, tool_record_id,
                                   workspace_id,
                                   self.workflow_manage.get_source_type(),
                                   self.workflow_manage.get_source_id(),
                                   False)

        def workflow_manage_new_instance(start_node_id=None,
                                         start_node_data=None, chat_record=None, child_node=None):
            work_flow_manage = ToolWorkflowManage(
                Workflow.new_instance(tool_workflow_version.work_flow, WorkflowMode.TOOL),
                {
                    'chat_record_id': tool_record_id,
                    'tool_id': tool_lib_id,
                    'stream': True,
                    'workspace_id': workspace_id,
                    **parameters},
                ToolWorkflowPostHandler(took_execute, tool_lib_id),
                base_to_response=LoopToResponse(),
                start_node_id=start_node_id,
                start_node_data=start_node_data,
                child_node=child_node,
                chat_record=self.to_chat_record(took_execute.get_record()),
                is_the_task_interrupted=lambda: False)

            return work_flow_manage

        return NodeResult({'workflow_manage_new_instance': workflow_manage_new_instance},
                          {}, _write_context=write_context_stream,
                          _is_interrupt=_is_interrupt_exec)

    def get_details(self, index: int, **kwargs):
        result = self.context.get('result')

        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            "result": result,
            "params": self.context.get('params'),
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'status': self.status,
            'child_node_data': self.context.get("child_node_data"),
            'child_answer_data': self.context.get("child_answer_data"),
            'err_message': self.err_message,
            'enableException': self.node.properties.get('enableException'),
        }
