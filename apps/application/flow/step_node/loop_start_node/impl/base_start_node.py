# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_start_node.py
    @date：2024/6/3 17:17
    @desc:
"""
from typing import Type

from rest_framework import serializers

from application.flow.i_step_node import NodeResult
from application.flow.step_node.loop_start_node.i_loop_start_node import ILoopStarNode


class BaseLoopStartStepNode(ILoopStarNode):
    def save_context(self, details, workflow_manage):
        self.context['index'] = details.get('current_index')
        self.context['item'] = details.get('current_item')

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        pass

    def execute(self, **kwargs) -> NodeResult:
        """
        开始节点 初始化全局变量
        """
        loop_params = self.workflow_manage.loop_params
        node_variable = {
            'index': loop_params.get("index"),
            'item': loop_params.get("item")
        }
        self.workflow_manage.chat_context = self.workflow_manage.get_chat_info().get_chat_variable()
        return NodeResult(node_variable, {})

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
            "current_index": self.context.get('index'),
            "current_item": self.context.get('item'),
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message,
        }
