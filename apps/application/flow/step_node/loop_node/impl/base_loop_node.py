# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： base_loop_node.py
    @date：2025/3/11 18:24
    @desc:
"""
import time
from typing import Dict, List

from django.utils.translation import gettext as _

from application.flow.common import Answer
from application.flow.i_step_node import NodeResult, WorkFlowPostHandler, INode
from application.flow.step_node.loop_node.i_loop_node import ILoopNode
from application.flow.tools import Reasoning
from application.models import ChatRecord
from common.handle.impl.response.loop_to_response import LoopToResponse
from maxkb.const import CONFIG

max_loop_count = int(CONFIG.get("WORKFLOW_LOOP_NODE_MAX_LOOP_COUNT", 500))


def _is_interrupt_exec(node, node_variable: Dict, workflow_variable: Dict):
    return node.context.get('is_interrupt_exec', False)


def _write_context(node_variable: Dict, workflow_variable: Dict, node: INode, workflow, answer: str,
                   reasoning_content: str):
    node.context['answer'] = answer
    node.context['run_time'] = time.time() - node.context['start_time']
    node.context['reasoning_content'] = reasoning_content
    if workflow.is_result(node, NodeResult(node_variable, workflow_variable)):
        node.answer_text = answer


def write_context_stream(node_variable: Dict, workflow_variable: Dict, node: INode, workflow):
    """
    写入上下文数据 (流式)
    @param node_variable:      节点数据
    @param workflow_variable:  全局数据
    @param node:               节点
    @param workflow:           工作流管理器
    """

    response = node_variable.get('result')
    workflow_manage = node_variable.get('workflow_manage')
    answer = ''
    reasoning_content = ''
    for chunk in response:
        content_chunk = chunk.get('content', '')
        reasoning_content_chunk = chunk.get('reasoning_content', '')
        reasoning_content += reasoning_content_chunk
        answer += content_chunk
        yield {'content': content_chunk,
               'reasoning_content': reasoning_content_chunk}
    runtime_details = workflow_manage.get_runtime_details()
    _write_context(node_variable, workflow_variable, node, workflow, answer, reasoning_content)


def write_context(node_variable: Dict, workflow_variable: Dict, node: INode, workflow):
    """
    写入上下文数据
    @param node_variable:      节点数据
    @param workflow_variable:  全局数据
    @param node:               节点实例对象
    @param workflow:           工作流管理器
    """
    response = node_variable.get('result')
    model_setting = node.context.get('model_setting',
                                     {'reasoning_content_enable': False, 'reasoning_content_end': '</think>',
                                      'reasoning_content_start': '<think>'})
    reasoning = Reasoning(model_setting.get('reasoning_content_start'), model_setting.get('reasoning_content_end'))
    reasoning_result = reasoning.get_reasoning_content(response)
    reasoning_result_end = reasoning.get_end_reasoning_content()
    content = reasoning_result.get('content') + reasoning_result_end.get('content')
    if 'reasoning_content' in response.response_metadata:
        reasoning_content = response.response_metadata.get('reasoning_content', '')
    else:
        reasoning_content = reasoning_result.get('reasoning_content') + reasoning_result_end.get('reasoning_content')
    _write_context(node_variable, workflow_variable, node, workflow, content, reasoning_content)


def get_answer_list(instance, child_node_node_dict, runtime_node_id):
    answer_list = instance.get_record_answer_list()
    for a in answer_list:
        _v = child_node_node_dict.get(a.get('runtime_node_id'))
        if _v:
            a['runtime_node_id'] = runtime_node_id
            a['child_node'] = _v
    return answer_list


def insert_or_replace(arr, index, value):
    if index < len(arr):
        arr[index] = value  # 替换
    else:
        # 在末尾插入足够多的None，然后替换最后一个
        arr.extend([None] * (index - len(arr) + 1))
        arr[index] = value
    return arr


def generate_loop_number(number: int):
    def i(current_index: int):
        return iter([(index, index) for index in range(current_index, number)])

    return i


def generate_loop_array(array):
    def i(current_index: int):
        return iter([(array[index], index) for index in range(current_index, len(array))])

    return i


def generate_while_loop(current_index: int):
    index = current_index
    while True:
        yield index, index
        index += 1


def loop(workflow_manage_new_instance, node: INode, generate_loop):
    loop_global_data = {}
    break_outer = False
    is_interrupt_exec = False
    loop_node_data = node.context.get('loop_node_data') or []
    loop_answer_data = node.context.get("loop_answer_data") or []
    start_index = node.context.get("current_index") or 0
    current_index = start_index
    node_params = node.node_params
    start_node_id = node_params.get('child_node', {}).get('runtime_node_id')
    loop_type = node_params.get('loop_type')
    start_node_data = None
    chat_record = None
    child_node = None
    if start_node_id:
        chat_record_id = node_params.get('child_node', {}).get('chat_record_id')
        child_node = node_params.get('child_node', {}).get('child_node')
        start_node_data = node_params.get('node_data')
        chat_record = ChatRecord(id=chat_record_id, answer_text_list=[], answer_text='',
                                 details=loop_node_data[current_index])

    for item, index in generate_loop(current_index):
        if 0 < max_loop_count <= index - start_index and loop_type == 'LOOP':
            raise Exception(_('Exceeding the maximum number of cycles'))
        """
        指定次数循环
        @return:
        """
        instance = workflow_manage_new_instance({'index': index, 'item': item}, loop_global_data, start_node_id,
                                                start_node_data, chat_record, child_node)
        response = instance.stream()
        answer = ''
        current_index = index
        reasoning_content = ''
        child_node_node_dict = {}
        for chunk in response:
            if chunk.get('node_type') == 'loop-break-node' and chunk.get('content', '') == 'BREAK':
                break_outer = True
                continue
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
                insert_or_replace(loop_node_data, index, instance.get_runtime_details())
                insert_or_replace(loop_answer_data, index,
                                  get_answer_list(instance, child_node_node_dict, node.runtime_node_id))
                node.context['is_interrupt_exec'] = is_interrupt_exec
                node.context['loop_node_data'] = loop_node_data
                node.context['loop_answer_data'] = loop_answer_data
                node.context["index"] = current_index
                node.context["item"] = current_index
                node.status = 500
                node.err_message = chunk.get('content')
                return
            node_type = chunk.get('node_type')
            if node_type == 'form-node':
                break_outer = True
                is_interrupt_exec = True
        start_node_id = None
        start_node_data = None
        chat_record = None
        child_node = None
        insert_or_replace(loop_node_data, index, instance.get_runtime_details())
        insert_or_replace(loop_answer_data, index,
                          get_answer_list(instance, child_node_node_dict, node.runtime_node_id))
        if break_outer:
            break
    node.context['is_interrupt_exec'] = is_interrupt_exec
    node.context['loop_node_data'] = loop_node_data
    node.context['loop_answer_data'] = loop_answer_data
    node.context["index"] = current_index
    node.context["item"] = current_index


def get_write_context(loop_type, array, number, loop_body, stream):
    def inner_write_context(node_variable: Dict, workflow_variable: Dict, node: INode, workflow):
        if loop_type == 'ARRAY':
            return loop(node_variable['workflow_manage_new_instance'], node, generate_loop_array(array))
        if loop_type == 'LOOP':
            return loop(node_variable['workflow_manage_new_instance'], node, generate_while_loop)
        return loop(node_variable['workflow_manage_new_instance'], node, generate_loop_number(number))

    return inner_write_context


class LoopWorkFlowPostHandler(WorkFlowPostHandler):
    def handler(self, workflow):
        pass


class BaseLoopNode(ILoopNode):
    def save_context(self, details, workflow_manage):
        self.context['loop_context_data'] = details.get('loop_context_data')
        self.context['loop_answer_data'] = details.get('loop_answer_data')
        self.context['loop_node_data'] = details.get('loop_node_data')
        self.context['result'] = details.get('result')
        self.context['params'] = details.get('params')
        self.context['run_time'] = details.get('run_time')
        self.context['index'] = details.get('current_index')
        self.context['item'] = details.get('current_item')
        for key, value in (details.get('loop_context_data') or {}).items():
            self.context[key] = value
        self.answer_text = ""

    def get_answer_list(self) -> List[Answer] | None:
        result = []
        for answer_list in (self.context.get("loop_answer_data") or []):
            for a in answer_list:
                if isinstance(a, dict):
                    result.append(Answer(**a))

        return result

    def get_loop_context(self):
        return self.context

    def execute(self, loop_type, array, number, loop_body, stream, **kwargs) -> NodeResult:
        from application.flow.loop_workflow_manage import LoopWorkflowManage, Workflow
        def workflow_manage_new_instance(loop_data, global_data, start_node_id=None,
                                         start_node_data=None, chat_record=None, child_node=None):
            workflow_manage = LoopWorkflowManage(Workflow.new_instance(loop_body), self.workflow_manage.params,
                                                 LoopWorkFlowPostHandler(
                                                     self.workflow_manage.work_flow_post_handler.chat_info),
                                                 self.workflow_manage,
                                                 loop_data,
                                                 self.get_loop_context,
                                                 base_to_response=LoopToResponse(),
                                                 start_node_id=start_node_id,
                                                 start_node_data=start_node_data,
                                                 chat_record=chat_record,
                                                 child_node=child_node
                                                 )

            return workflow_manage

        return NodeResult({'workflow_manage_new_instance': workflow_manage_new_instance}, {},
                          _write_context=get_write_context(loop_type, array, number, loop_body, stream),
                          _is_interrupt=_is_interrupt_exec)

    def get_loop_context_data(self):
        fields = self.node.properties.get('config', []).get('fields', []) or []
        return {f.get('value'): self.context.get(f.get('value')) for f in fields if
                self.context.get(f.get('value')) is not None}

    def get_details(self, index: int, **kwargs):

        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            "result": self.context.get('result'),
            'array': self.node_params_serializer.data.get('array'),
            'number': self.node_params_serializer.data.get('number'),
            "params": self.context.get('params'),
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'current_index': self.context.get("index"),
            "current_item": self.context.get("item"),
            'loop_type': self.node_params_serializer.data.get('loop_type'),
            'status': self.status,
            'loop_context_data': self.get_loop_context_data(),
            'loop_node_data': self.context.get("loop_node_data"),
            'loop_answer_data': self.context.get("loop_answer_data"),
            'err_message': self.err_message
        }
