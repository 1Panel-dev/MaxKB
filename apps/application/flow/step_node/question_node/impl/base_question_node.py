# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_question_node.py
    @date：2024/6/4 14:30
    @desc:
"""
import time
from functools import reduce
from typing import List, Dict

from langchain.schema import HumanMessage, SystemMessage
from langchain_core.messages import BaseMessage

from application.flow import tools
from application.flow.i_step_node import NodeResult, INode
from application.flow.step_node.question_node.i_question_node import IQuestionNode
from setting.models_provider.tools import get_model_instance_by_model_user_id


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
    for chunk in response:
        answer += chunk.content
    chat_model = node_variable.get('chat_model')
    message_tokens = chat_model.get_num_tokens_from_messages(node_variable.get('message_list'))
    answer_tokens = chat_model.get_num_tokens(answer)
    node.context['message_tokens'] = message_tokens
    node.context['answer_tokens'] = answer_tokens
    node.context['answer'] = answer
    node.context['history_message'] = node_variable['history_message']
    node.context['question'] = node_variable['question']
    node.context['run_time'] = time.time() - node.context['start_time']


def write_context(node_variable: Dict, workflow_variable: Dict, node: INode, workflow):
    """
    写入上下文数据
    @param node_variable:      节点数据
    @param workflow_variable:  全局数据
    @param node:               节点实例对象
    @param workflow:           工作流管理器
    """
    response = node_variable.get('result')
    chat_model = node_variable.get('chat_model')
    answer = response.content
    message_tokens = chat_model.get_num_tokens_from_messages(node_variable.get('message_list'))
    answer_tokens = chat_model.get_num_tokens(answer)
    node.context['message_tokens'] = message_tokens
    node.context['answer_tokens'] = answer_tokens
    node.context['answer'] = answer
    node.context['history_message'] = node_variable['history_message']
    node.context['question'] = node_variable['question']


def get_to_response_write_context(node_variable: Dict, node: INode):
    def _write_context(answer, status=200):
        chat_model = node_variable.get('chat_model')

        if status == 200:
            answer_tokens = chat_model.get_num_tokens(answer)
            message_tokens = chat_model.get_num_tokens_from_messages(node_variable.get('message_list'))
        else:
            answer_tokens = 0
            message_tokens = 0
        node.err_message = answer
        node.status = status
        node.context['message_tokens'] = message_tokens
        node.context['answer_tokens'] = answer_tokens
        node.context['answer'] = answer
        node.context['run_time'] = time.time() - node.context['start_time']

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


class BaseQuestionNode(IQuestionNode):
    def execute(self, model_id, system, prompt, dialogue_number, history_chat_record, stream, chat_id, chat_record_id,
                **kwargs) -> NodeResult:
        chat_model = get_model_instance_by_model_user_id(model_id, self.flow_params_serializer.data.get('user_id'))
        history_message = self.get_history_message(history_chat_record, dialogue_number)
        self.context['history_message'] = history_message
        question = self.generate_prompt_question(prompt)
        self.context['question'] = question.content
        message_list = self.generate_message_list(system, prompt, history_message)
        self.context['message_list'] = message_list
        if stream:
            r = chat_model.stream(message_list)
            return NodeResult({'result': r, 'chat_model': chat_model, 'message_list': message_list,
                               'get_to_response_write_context': get_to_response_write_context,
                               'history_message': history_message, 'question': question.content}, {},
                              _write_context=write_context_stream,
                              _to_response=to_stream_response)
        else:
            r = chat_model.invoke(message_list)
            return NodeResult({'result': r, 'chat_model': chat_model, 'message_list': message_list,
                               'history_message': history_message, 'question': question.content}, {},
                              _write_context=write_context, _to_response=to_response)

    @staticmethod
    def get_history_message(history_chat_record, dialogue_number):
        start_index = len(history_chat_record) - dialogue_number
        history_message = reduce(lambda x, y: [*x, *y], [
            [history_chat_record[index].get_human_message(), history_chat_record[index].get_ai_message()]
            for index in
            range(start_index if start_index > 0 else 0, len(history_chat_record))], [])
        return history_message

    def generate_prompt_question(self, prompt):
        return HumanMessage(self.workflow_manage.generate_prompt(prompt))

    def generate_message_list(self, system: str, prompt: str, history_message):
        if system is None or len(system) == 0:
            return [SystemMessage(self.workflow_manage.generate_prompt(system)), *history_message,
                    HumanMessage(self.workflow_manage.generate_prompt(prompt))]
        else:
            return [*history_message, HumanMessage(self.workflow_manage.generate_prompt(prompt))]

    @staticmethod
    def reset_message_list(message_list: List[BaseMessage], answer_text):
        result = [{'role': 'user' if isinstance(message, HumanMessage) else 'ai', 'content': message.content} for
                  message
                  in
                  message_list]
        result.append({'role': 'ai', 'content': answer_text})
        return result

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'system': self.node_params.get('system'),
            'history_message': [{'content': message.content, 'role': message.type} for message in
                                (self.context.get('history_message') if self.context.get(
                                    'history_message') is not None else [])],
            'question': self.context.get('question'),
            'answer': self.context.get('answer'),
            'type': self.node.type,
            'message_tokens': self.context.get('message_tokens'),
            'answer_tokens': self.context.get('answer_tokens'),
            'status': self.status,
            'err_message': self.err_message
        }
