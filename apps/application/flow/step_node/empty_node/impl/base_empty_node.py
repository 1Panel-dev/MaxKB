# coding=utf-8
"""
    @project: MaxKB
    @Author：AI Assistant
    @file： base_empty_node.py
    @date：2026/06/10
    @desc: 空节点实现 - 用于流程判断的ELSE分支占位
"""
from application.flow.i_step_node import NodeResult
from application.flow.step_node.empty_node.i_empty_node import IEmptyNode


class BaseEmptyNode(IEmptyNode):
    """空节点实现类"""

    def save_context(self, details, workflow_manage):
        """保存上下文 - 空节点无需保存任何内容"""
        self.context['exception_message'] = details.get('err_message')

    def execute(self, **kwargs) -> NodeResult:
        """
        执行空节点
        空节点不产生任何输出，仅作为流程占位符
        """
        return NodeResult({}, {})

    def get_details(self, index: int, **kwargs):
        """获取节点执行详情"""
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message,
            'enableException': self.node.properties.get('enableException'),
        }
