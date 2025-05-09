# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： workflow_manage.py
    @date：2025/5/9 10:30
    @desc:
"""
from builtins import function
from enum import Enum
from typing import List, Dict

from workflow.workflow.common import Workflow, Channel, Chunk


class WorkflowType(Enum):
    # 应用
    APPLICATION = "APPLICATION"
    # 知识库
    KNOWLEDGE = "KNOWLEDGE"
    # ....


class WorkflowManage:
    channel = Channel()

    def __init__(self,
                 workflow: Workflow,
                 chunk_list: List[Chunk],
                 start_node: Chunk,
                 workflow_type: WorkflowType,
                 body: Dict,
                 consumer: function):
        self.workflow = workflow
        self.chunk_list = chunk_list
        self.start_node = start_node
        self.workflow_type = workflow_type
        self.body = body
        self.consumer = consumer

    def stream(self):
        pass

    def invoke(self):
        pass
