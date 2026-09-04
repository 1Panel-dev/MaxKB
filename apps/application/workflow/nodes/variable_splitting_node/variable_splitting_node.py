# coding=utf-8
"""
@project: MaxKB
@Author: 虎虎虎
@file: variable_splitting_node.py
@desc: 变量拆分节点
"""

import json

from django.utils.translation import gettext_lazy as _
from jsonpath_ng.ext import parse
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode
from common.cache.mem_cache import MemCache

jsonpath_expr_cache = MemCache(
    "parse_path",
    {
        "TIMEOUT": 3600,  # 缓存有效期为 1 小时
        "OPTIONS": {
            "MAX_ENTRIES": 1000,  # 最多缓存 1000 个条目
            "CULL_FREQUENCY": 10,  # 达到上限时，删除约 1/10 的缓存
        },
    },
)


class VariableSplittingNodeParamsSerializer(serializers.Serializer):
    input_variable = serializers.ListField(required=True, label=_("input variable"))
    variable_list = serializers.ListField(required=True, label=_("Split variables"))


def parse_and_cache(path):
    jsonpath_expr = jsonpath_expr_cache.get(path)
    if not jsonpath_expr:
        jsonpath_expr = parse(path)
        jsonpath_expr_cache.set(path, jsonpath_expr)
    return jsonpath_expr


def smart_jsonpath_search(data: dict, path: str):
    """智能 JSON Path 搜索。

    - 单个匹配: 直接返回值
    - 多个匹配: 返回值的列表
    - 无匹配: 返回 None
    """
    jsonpath_expr = parse_and_cache(path)
    matches = jsonpath_expr.find(data)

    if not matches:
        return None
    elif len(matches) == 1:
        return matches[0].value
    else:
        return [match.value for match in matches]


class VariableSplittingNode(INode):
    serializer_class = VariableSplittingNodeParamsSerializer
    supported_workflow_type_list = [
        WorkflowType.APPLICATION,
        WorkflowType.KNOWLEDGE,
        WorkflowType.TOOL,
    ]
    type = "variable-splitting-node"

    def execute(self):
        node_params = self.get_parameters()

        input_variable = self.workflow_manage.get_reference_field(
            node_params.get("input_variable")[0],
            node_params.get("input_variable")[1:],
        )
        variable_list = node_params.get("variable_list", [])

        if isinstance(input_variable, str):
            try:
                input_variable = json.loads(input_variable)
            except Exception:
                pass

        self.write_context("request", input_variable)
        response = {v["field"]: smart_jsonpath_search(input_variable, v["expression"]) for v in variable_list}
        self.write_context("result", response)
        for key, value in response.items():
            self.write_context(key, value)

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        details.update(
            {
                "request": self.get_context("request"),
                "result": self.get_context("result"),
                "status": self.status.value if self.status else None,
            }
        )
        return details
