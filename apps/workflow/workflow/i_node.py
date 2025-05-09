# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： i_node.py
    @date：2025/5/7 16:41
    @desc:
"""
import time
from abc import abstractmethod

from common.utils.common import get_sha256_hash
from workflow.workflow.common import Channel, Chunk


class INode:
    # 当前节点支持的工作流类型
    supported_workflow_type_list = []
    # 节点类型
    type = None
    # 节点管道
    channel = Channel()

    def __init__(self, node, workflow_manage, chunk: Chunk = None, up_node_id_list=None, loop_index=None):
        self.node = node
        self.chunk = chunk
        if chunk is not None:
            self.context = chunk.node_data | {}
        else:
            self.context = {}
        # 运行时id
        self.runtime_node_id = get_sha256_hash("".join(up_node_id_list | []) + node.id + str(loop_index | ""))
        self.workflow_manage = workflow_manage
        self.node_serializer = self.get_node_serializer()(data=node.properties.get('node_data'))
        self.is_valid()

    def is_valid(self):
        self.node_serializer.is_valid(raise_exception=True)

    def execute(self, **kwargs):
        pass

    def run(self):
        start_time = time.time()
        self.context['start_time'] = start_time
        self._run()
        self.context['run_time'] = time.time() - start_time

    def _run(self):
        return self.execute(**self.node_serializer.data)

    @abstractmethod
    def get_node_serializer(self):
        pass
