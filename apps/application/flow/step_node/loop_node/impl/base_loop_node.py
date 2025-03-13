# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： base_loop_node.py
    @date：2025/3/11 18:24
    @desc:
"""
import time
from typing import Dict

from application.flow.i_step_node import NodeResult, WorkFlowPostHandler, INode
from application.flow.step_node.loop_node.i_loop_node import ILoopNode
from application.flow.tools import Reasoning
from common.handle.impl.response.loop_to_response import LoopToResponse


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
    answer = ''
    reasoning_content = ''
    for chunk in response:
        content_chunk = chunk.get('content', '')
        reasoning_content_chunk = chunk.get('reasoning_content', '')
        reasoning_content += reasoning_content_chunk
        answer += content_chunk
        yield {'content': content_chunk,
               'reasoning_content': reasoning_content_chunk}

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


def loop_number(number, loop_body):
    """
    指定次数循环
    @return:
    """
    pass


def loop_array(array, loop_body):
    """
    循环数组
    @return:
    """
    pass


def loop_loop(loop_body):
    """
    无线循环
    @return:
    """
    pass


class LoopWorkFlowPostHandler(WorkFlowPostHandler):
    def handler(self, chat_id,
                chat_record_id,
                answer,
                workflow):
        pass


class BaseLoopNode(ILoopNode):
    def save_context(self, details, workflow_manage):
        self.context['result'] = details.get('result')
        self.answer_text = str(details.get('result'))

    def execute(self, loop_type, array, number, loop_body, stream, **kwargs) -> NodeResult:
        from application.flow.workflow_manage import WorkflowManage, Flow
        workflow_manage = WorkflowManage(Flow.new_instance(loop_body), self.workflow_manage.params,
                                         LoopWorkFlowPostHandler(self.workflow_manage.work_flow_post_handler.chat_info
                                                                 ,
                                                                 self.workflow_manage.work_flow_post_handler.client_id,
                                                                 self.workflow_manage.work_flow_post_handler.client_type)
                                         , base_to_response=LoopToResponse())
        result = workflow_manage.stream()
        return NodeResult({"result": result}, {}, _write_context=write_context_stream)

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            "result": self.context.get('result'),
            "params": self.context.get('params'),
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message
        }
