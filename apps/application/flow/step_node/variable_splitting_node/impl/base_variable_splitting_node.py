# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： base_variable_splitting_node.py
    @date：2025/10/13 15:02
    @desc:
"""
from jsonpath_ng import parse

from application.flow.i_step_node import NodeResult
from application.flow.step_node.variable_splitting_node.i_variable_splitting_node import IVariableSplittingNode


def smart_jsonpath_search(data: dict, path: str):
    """
    智能JSON Path搜索
    返回:
    - 单个匹配: 直接返回值
    - 多个匹配: 返回值的列表
    - 无匹配: 返回None
    """
    jsonpath_expr = parse(path)
    matches = jsonpath_expr.find(data)

    if not matches:
        return None
    elif len(matches) == 1:
        return matches[0].value
    else:
        return [match.value for match in matches]


class BaseVariableSplittingNode(IVariableSplittingNode):
    def save_context(self, details, workflow_manage):
        for key, value in details.get('result').items():
            self.context[key] = value
        self.context['result'] = details.get('result')
        self.context['request'] = details.get('request')

    def execute(self, input_variable, variable_list, **kwargs) -> NodeResult:
        self.context['request'] = input_variable
        response = {v['field']: smart_jsonpath_search(input_variable, v['expression']) for v in variable_list}
        return NodeResult({'result': response, **response}, {})

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'request': self.context.get('request'),
            'result': self.context.get('result'),
            'status': self.status,
            'err_message': self.err_message
        }
