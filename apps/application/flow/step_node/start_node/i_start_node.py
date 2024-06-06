# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： i_start_node.py
    @date：2024/6/3 16:54
    @desc:
"""
from typing import Type

from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult


class IStarNode(INode):
    type = 'start-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer] | None:
        return None

    def _run(self):
        return self.execute(**self.flow_params_serializer.data)

    def execute(self, question, **kwargs) -> NodeResult:
        pass
