# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： i_node.py
    @date：2026/6/29  16:41
    @desc:
"""
import time
from typing import Optional, Type, Callable

from rest_framework import serializers

from application.workflow.common import Node
from application.workflow.message.struct.content import Content
from application.workflow.status import Status


class INode:
    # 当前节点支持的工作流类型
    supported_workflow_type_list = []
    # 节点类型
    type = None
    # 序列化校验器
    serializer_class: Optional[Type[serializers.Serializer]] = None

    @staticmethod
    def is_valid(data):
        INode.serializer_class(data=data).is_valid(raise_exception=True)

    def __init__(self, node, workflow_manage, get_node_parameters: Callable[[Node], dict]):
        self.node = node
        self.status = Status.BEFORE_RUNNING
        self.workflow_manage = workflow_manage
        # 节点参数
        self.parameters = get_node_parameters(node)
        # 节点运行时产生的数据
        self.data = {}

    def next_success_nodes(self):
        edge_node_list = self.workflow_manage.workflow.get_next_edge_nodes(self.node.id)
        if edge_node_list is None:
            self.workflow_manage.next_nodes([])
            return
        self.workflow_manage.next_nodes(
            [en.node for en in edge_node_list if en.edge.sourceAnchorId == self.node.id + '_right'])

    def next_fail_nodes(self):
        edge_node_list = self.workflow_manage.workflow.get_next_edge_nodes(self.node.id)
        if edge_node_list is None:
            self.workflow_manage.next_nodes([])
            return
        self.workflow_manage.next_nodes(
            [en.node for en in edge_node_list if en.edge.sourceAnchorId == self.node.id + '_exception_right'])

    def execute(self):
        pass

    def run(self):
        """
        运行节点
        @return: 不响应数据
        """
        start_time = time.time()
        self.status = Status.RUNNING
        self.data['start_time'] = start_time
        self._run()
        self.data['run_time'] = time.time() - start_time

    def _run(self):
        """
        执行节点
        @return:
        """
        return self.execute()

    def get_node_id(self):
        """
        获取节点id
        @return: 节点id
        """
        return self.node.id

    def get_node_name(self):
        """
        获取节点名称
        @return: 节点名称
        """
        return self.node.properties.get("stepName")

    def write_context(self, key, value, append=False):
        """
        将数据写入节点上下文
        @param key:   数据key
        @param value: 数据value
        @param append: 是否追加
        @return: None
        """
        self.workflow_manage.write_context(self.node.id, key, value, append)

    def get_context(self, key):
        """
        获取上下文数据 根据key
        @param key: key
        @return: 数据
        """
        return self.workflow_manage.get_context(self.node.id, key)

    def get_workflow_type(self):
        """
        获取工作流类型
        @return: 工作流类型
        """
        return self.workflow_manage.workflow_type

    def get_workflow_parameters(self):
        """
        获取工作流body
        @return: 工作流body数据
        """
        return self.workflow_manage.get_parameters()

    def get_parameters(self):
        """
        获取节点参数数据
        @return: 节点参数数据
        """
        return self.parameters

    def get_next_nodes(self, wf):
        """
        获取下n个基点
        @param wf: 工作流对象
        @return:  下n个节点
        """
        return wf.get_next_nodes(self.get_node_id())

    def write(self, message: Content):
        self.workflow_manage.write(message)
