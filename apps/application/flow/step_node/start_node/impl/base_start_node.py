# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_start_node.py
    @date：2024/6/3 17:17
    @desc:
"""
import time
from datetime import datetime
from typing import List, Type

from rest_framework import serializers

from application.flow.i_step_node import NodeResult
from application.flow.step_node.start_node.i_start_node import IStarNode


def get_default_global_variable(input_field_list: List):
    return {item.get('variable'): item.get('default_value') for item in input_field_list if
            item.get('default_value', None) is not None}


def get_global_variable(node):
    history_chat_record = node.flow_params_serializer.data.get('history_chat_record', [])
    history_context = [{'question': chat_record.problem_text, 'answer': chat_record.answer_text} for chat_record in
                       history_chat_record]
    chat_id = node.flow_params_serializer.data.get('chat_id')
    return {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'start_time': time.time(),
            'history_context': history_context, 'chat_id': str(chat_id), **node.workflow_manage.form_data}


class BaseStartStepNode(IStarNode):
    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        pass

    def execute(self, question, **kwargs) -> NodeResult:
        base_node = self.workflow_manage.get_base_node()
        default_global_variable = get_default_global_variable(base_node.properties.get('input_field_list', []))
        workflow_variable = {**default_global_variable, **get_global_variable(self)}
        """
        开始节点 初始化全局变量
        """
        return NodeResult({'question': question},
                          workflow_variable)

    def get_details(self, index: int, **kwargs):
        global_fields = []
        for field in self.node.properties.get('config')['globalFields']:
            key = field['value']
            global_fields.append({
                'label': field['label'],
                'key': key,
                'value': self.workflow_manage.context[key] if key in self.workflow_manage.context else ''
            })
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            "question": self.context.get('question'),
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message,
            'global_fields': global_fields
        }
