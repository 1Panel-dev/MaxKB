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
    def save_context(self, details, workflow_manage):
        base_node = self.workflow_manage.get_base_node()
        default_global_variable = get_default_global_variable(base_node.properties.get('input_field_list', []))
        workflow_variable = {**default_global_variable, **get_global_variable(self)}
        self.context['question'] = details.get('question')
        self.context['run_time'] = details.get('run_time')
        self.context['document'] = details.get('document_list')
        self.context['image'] = details.get('image_list')
        self.context['audio'] = details.get('audio_list')
        self.context['other'] = details.get('other_list')
        self.status = details.get('status')
        self.err_message = details.get('err_message')
        for key, value in workflow_variable.items():
            workflow_manage.context[key] = value

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        pass

    def execute(self, question, **kwargs) -> NodeResult:
        base_node = self.workflow_manage.get_base_node()
        default_global_variable = get_default_global_variable(base_node.properties.get('input_field_list', []))
        workflow_variable = {**default_global_variable, **get_global_variable(self)}
        """
        开始节点 初始化全局变量
        """
        node_variable = {
            'question': question,
            'image': self.workflow_manage.image_list,
            'document': self.workflow_manage.document_list,
            'audio': self.workflow_manage.audio_list,
            'other': self.workflow_manage.other_list,
        }
        return NodeResult(node_variable, workflow_variable)

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
            'image_list': self.context.get('image'),
            'document_list': self.context.get('document'),
            'audio_list': self.context.get('audio'),
            'other_list': self.context.get('other'),
            'global_fields': global_fields
        }
