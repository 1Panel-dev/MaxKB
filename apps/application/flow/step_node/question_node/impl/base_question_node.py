# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_question_node.py
    @date：2024/6/4 14:30
    @desc:
"""
import re
import time
from functools import reduce
from typing import List, Dict

from django.db.models import QuerySet
from langchain.schema import HumanMessage, SystemMessage
from langchain_core.messages import BaseMessage

from application.flow.i_step_node import NodeResult, INode
from application.flow.step_node.question_node.i_question_node import IQuestionNode
from models_provider.models import Model
from models_provider.tools import get_model_instance_by_model_workspace_id, get_model_credential


def _write_context(node_variable: Dict, workflow_variable: Dict, node: INode, workflow, answer: str):
    chat_model = node_variable.get('chat_model')
    message_tokens = chat_model.get_num_tokens_from_messages(node_variable.get('message_list'))
    answer_tokens = chat_model.get_num_tokens(answer)
    node.context['message_tokens'] = message_tokens
    node.context['answer_tokens'] = answer_tokens
    node.context['answer'] = answer
    node.context['history_message'] = node_variable['history_message']
    node.context['question'] = node_variable['question']
    node.context['run_time'] = time.time() - node.context['start_time']
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
    for chunk in response:
        answer += chunk.content
        yield chunk.content
    _write_context(node_variable, workflow_variable, node, workflow, answer)


def write_context(node_variable: Dict, workflow_variable: Dict, node: INode, workflow):
    """
    写入上下文数据
    @param node_variable:      节点数据
    @param workflow_variable:  全局数据
    @param node:               节点实例对象
    @param workflow:           工作流管理器
    """
    response = node_variable.get('result')
    answer = response.content
    _write_context(node_variable, workflow_variable, node, workflow, answer)


def get_default_model_params_setting(model_id):
    model = QuerySet(Model).filter(id=model_id).first()
    credential = get_model_credential(model.provider, model.model_type, model.model_name)
    model_params_setting = credential.get_model_params_setting_form(
        model.model_name).get_default_form_data()
    return model_params_setting


class BaseQuestionNode(IQuestionNode):
    def save_context(self, details, workflow_manage):
        self.context['run_time'] = details.get('run_time')
        self.context['question'] = details.get('question')
        self.context['answer'] = details.get('answer')
        self.context['message_tokens'] = details.get('message_tokens')
        self.context['answer_tokens'] = details.get('answer_tokens')
        self.context['exception_message'] = details.get('err_message')
        if self.node_params.get('is_result', False):
            self.answer_text = details.get('answer')

    def execute(self, model_id, system, prompt, dialogue_number, history_chat_record, stream, chat_id, chat_record_id,
                model_params_setting=None,
                **kwargs) -> NodeResult:
        if model_params_setting is None:
            model_params_setting = get_default_model_params_setting(model_id)
        workspace_id = self.workflow_manage.get_body().get('workspace_id')
        chat_model = get_model_instance_by_model_workspace_id(model_id, workspace_id,
                                                              **model_params_setting)
        history_message = self.get_history_message(history_chat_record, dialogue_number)
        self.context['history_message'] = history_message
        question = self.generate_prompt_question(prompt)
        self.context['question'] = question.content
        system = self.workflow_manage.generate_prompt(system)
        self.context['system'] = system
        message_list = self.generate_message_list(system, prompt, history_message)
        self.context['message_list'] = message_list
        if stream:
            r = chat_model.stream(message_list)
            return NodeResult({'result': r, 'chat_model': chat_model, 'message_list': message_list,
                               'history_message': history_message, 'question': question.content}, {},
                              _write_context=write_context_stream)
        else:
            r = chat_model.invoke(message_list)
            return NodeResult({'result': r, 'chat_model': chat_model, 'message_list': message_list,
                               'history_message': history_message, 'question': question.content}, {},
                              _write_context=write_context)

    @staticmethod
    def get_history_message(history_chat_record, dialogue_number):
        start_index = len(history_chat_record) - dialogue_number
        history_message = reduce(lambda x, y: [*x, *y], [
            [history_chat_record[index].get_human_message(), history_chat_record[index].get_ai_message()]
            for index in
            range(start_index if start_index > 0 else 0, len(history_chat_record))], [])
        for message in history_message:
            if isinstance(message.content, str):
                message.content = re.sub('<form_rander>[\d\D]*?<\/form_rander>', '', message.content)
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
            'system': self.context.get('system'),
            'history_message': [{'content': message.content, 'role': message.type} for message in
                                (self.context.get('history_message') if self.context.get(
                                    'history_message') is not None else [])],
            'question': self.context.get('question'),
            'answer': self.context.get('answer'),
            'type': self.node.type,
            'message_tokens': self.context.get('message_tokens'),
            'answer_tokens': self.context.get('answer_tokens'),
            'status': self.status,
            'err_message': self.err_message,
            'enableException': self.node.properties.get('enableException'),
        }
