# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_reply_node.py
    @date：2024/6/11 17:25
    @desc:
"""
from typing import List, Dict

from langchain_core.messages import AIMessage, AIMessageChunk

from application.flow import tools
from application.flow.i_step_node import NodeResult, INode
from application.flow.step_node.direct_reply_node.i_reply_node import IReplyNode


def get_to_response_write_context(node_variable: Dict, node: INode):
    def _write_context(answer, status=200):
        node.context['answer'] = answer

    return _write_context


def to_stream_response(chat_id, chat_record_id, node_variable: Dict, workflow_variable: Dict, node, workflow,
                       post_handler):
    """
    将流式数据 转换为 流式响应
    @param chat_id:           会话id
    @param chat_record_id:    对话记录id
    @param node_variable:     节点数据
    @param workflow_variable: 工作流数据
    @param node:              节点
    @param workflow:          工作流管理器
    @param post_handler:      后置处理器 输出结果后执行
    @return: 流式响应
    """
    response = node_variable.get('result')
    _write_context = get_to_response_write_context(node_variable, node)
    return tools.to_stream_response(chat_id, chat_record_id, response, workflow, _write_context, post_handler)


def to_response(chat_id, chat_record_id, node_variable: Dict, workflow_variable: Dict, node, workflow,
                post_handler):
    """
    将结果转换
    @param chat_id:           会话id
    @param chat_record_id:    对话记录id
    @param node_variable:     节点数据
    @param workflow_variable: 工作流数据
    @param node:              节点
    @param workflow:          工作流管理器
    @param post_handler:      后置处理器
    @return: 响应
    """
    response = node_variable.get('result')
    _write_context = get_to_response_write_context(node_variable, node)
    return tools.to_response(chat_id, chat_record_id, response, workflow, _write_context, post_handler)


class BaseReplyNode(IReplyNode):
    def execute(self, reply_type, stream, fields=None, content=None, **kwargs) -> NodeResult:
        if reply_type == 'referencing':
            result = self.get_reference_content(fields)
        else:
            result = self.generate_reply_content(content)
        if stream:
            return NodeResult({'result': iter([AIMessageChunk(content=result)]), 'answer': result}, {},
                              _to_response=to_stream_response)
        else:
            return NodeResult({'result': AIMessage(content=result), 'answer': result}, {}, _to_response=to_response)

    def generate_reply_content(self, prompt):
        return self.workflow_manage.generate_prompt(prompt)

    def get_reference_content(self, fields: List[str]):
        return str(self.workflow_manage.get_reference_field(
            fields[0],
            fields[1:]))

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'answer': self.context.get('answer'),
            'status': self.status,
            'err_message': self.err_message
        }
