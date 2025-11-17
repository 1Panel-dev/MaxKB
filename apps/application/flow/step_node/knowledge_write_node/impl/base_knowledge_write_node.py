# coding=utf-8
"""
    @project: MaxKB
    @Author：niu
    @file： base_knowledge_write_node.py
    @date：2025/11/13 11:19
    @desc:
"""
from application.flow.i_step_node import NodeResult
from application.flow.step_node.knowledge_write_node.i_knowledge_write_node import IKnowledgeWriteNode


class BaseKnowledgeWriteNode(IKnowledgeWriteNode):

    def save_context(self, details, workflow_manage):
        pass

    def execute(self, paragraph_list, chunk_length, **kwargs) -> NodeResult:
        pass