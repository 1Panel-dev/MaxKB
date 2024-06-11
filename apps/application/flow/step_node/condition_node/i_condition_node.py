# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： i_condition_node.py
    @date：2024/6/7 9:54
    @desc:
"""
import json
from typing import Type

from rest_framework import serializers

from application.flow.i_step_node import INode
from common.util.field_message import ErrMessage


class ConditionSerializer(serializers.Serializer):
    compare = serializers.CharField(required=True, error_messages=ErrMessage.char("比较器"))
    value = serializers.CharField(required=True, error_messages=ErrMessage.char(""))
    field = serializers.ListField(required=True, error_messages=ErrMessage.char("字段"))


class ConditionBranchSerializer(serializers.Serializer):
    id = serializers.CharField(required=True, error_messages=ErrMessage.char("分支id"))
    condition = serializers.CharField(required=True, error_messages=ErrMessage.char("条件or|and"))
    conditions = ConditionSerializer(many=True)


class ConditionNodeParamsSerializer(serializers.Serializer):
    branch = ConditionBranchSerializer(many=True)


j = """
     {  "branch": [
                        {
                            "conditions": [
                                {
                                    "field": [
                                    "34902d3d-a3ff-497f-b8e1-0c34a44d7dd5",
                                    "paragraph_list"
                                    ],
                                    "compare": "len_eq",
                                    "value": "0"
                                }
                            ],
                            "id": "2391",
                            "condition": "and"
                        },
                        {
                            "conditions": [
                                {
                                    "field": [
                                        "34902d3d-a3ff-497f-b8e1-0c34a44d7dd5",
                                        "paragraph_list"
                                        ],
                                        "compare": "len_eq",
                                        "value": "1"
                                }
                            ],
                            "id": "1143",
                            "condition": "and"
                        },
                        {
                            "conditions": [
                                
                            ],
                            "id": "9208", 
                            "condition": "and"
                        }
                    ]}
"""
a = json.loads(j)
c = ConditionNodeParamsSerializer(data=a)
c.is_valid(raise_exception=True)
print(c.data)


class IConditionNode(INode):
    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return ConditionNodeParamsSerializer

    type = 'condition-node'
