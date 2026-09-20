# coding=utf-8
"""
@project: MaxKB
@Author：虎虎虎
@file： workflow.py
@date：2026/6/29 10:58
@desc:
"""

from enum import Enum
from typing import List, Dict

from django.utils.translation import gettext as _
from common.exception.app_exception import AppApiException
from common.utils.common import group_by


class Node:
    def __init__(self, _id: str, _type: str, x: int, y: int, properties: dict, **kwargs):
        """

        @param _id:     节点id
        @param _type:   类型
        @param x:       节点x轴位置
        @param y:       节点y轴位置
        @param properties:
        @param kwargs:
        """
        self.id = _id
        self.type = _type
        self.x = x
        self.y = y
        self.properties = properties
        for keyword in kwargs:
            self.__setattr__(keyword, kwargs.get(keyword))


class Edge:
    def __init__(self, _id: str, _type: str, sourceNodeId: str, targetNodeId: str, **keywords):
        """
        线
        @param _id:     线id
        @param _type:   线类型
        @param sourceNodeId:
        @param targetNodeId:
        @param keywords:
        """
        self.id = _id
        self.type = _type
        self.sourceNodeId = sourceNodeId
        self.targetNodeId = targetNodeId
        for keyword in keywords:
            self.__setattr__(keyword, keywords.get(keyword))


class EdgeNode:
    edge: Edge
    node: Node

    def __init__(self, edge, node):
        self.edge = edge
        self.node = node


def init_fields(workflow):
    result = []
    for node in workflow.nodes:
        properties = node.properties
        node_name = properties.get("stepName")
        node_id = node.id
        node_config = properties.get("config")
        result.append(NodeField(node_id, node_name, "异常信息", "exception_message"))
        if node_config is not None:
            fields = node_config.get("fields")
            if fields is not None:
                for field in fields:
                    result.append(NodeField(node_id, node_name, field.get("label"), field.get("value")))
            global_fields = node_config.get("globalFields")
            if global_fields is not None:
                for global_field in global_fields:
                    result.append(NodeField("global", "全局变量", global_field.get("label"), global_field.get("value")))
            chat_fields = node_config.get("chatFields")
            if chat_fields is not None:
                for chat_field in chat_fields:
                    result.append(NodeField("chat", "chat", chat_field.get("label"), chat_field.get("value")))
    result.sort(key=lambda f: len(f.node_name + f.value), reverse=True)
    return result


def get_node_parameters(node):
    return node.properties.get("node_data", {})


class NodeField:
    def __init__(self, node_id, node_name, label, value):
        self.node_id = node_id
        self.node_name = node_name
        self.label = label
        self.value = value

    def reset_variable(self, prompt: str):
        userVariable = self.node_name + "." + self.value
        systemVariable = f"context.get('{self.node_id}').get('{self.value}','')"
        prompt = prompt.replace(userVariable, systemVariable)
        # 全局变量:前端用 global.xxx 引用,也要能解析到 context['global']
        if self.node_id == "global":
            prompt = prompt.replace(f"global.{self.value}", systemVariable)
        return prompt


class WorkflowType(Enum):
    # 应用
    APPLICATION = "APPLICATION"
    # 知识库
    KNOWLEDGE = "KNOWLEDGE"
    # 工具
    TOOL = "TOOL"


class Workflow:
    """
    节点列表
    """

    nodes: List[Node]
    """
    线列表
    """
    edges: List[Edge]
    """
    节点id:node
    """
    node_map: Dict[str, Node]
    """
    节点id:当前节点id上面的所有节点
    """
    up_node_map: Dict[str, List[EdgeNode]]
    """
     节点id:当前节点id下面的所有节点
    """
    next_node_map: Dict[str, List[EdgeNode]]
    """
    节点字段
    """
    node_field_list: List[NodeField]

    def __init__(self, nodes: List[Node], edges: List[Edge]):
        self.nodes = nodes
        self.edges = edges
        self.node_map = {node.id: node for node in nodes}

        self.up_node_map = {
            key: [EdgeNode(edge, self.node_map.get(edge.sourceNodeId)) for edge in edges]
            for key, edges in group_by(edges, key=lambda edge: edge.targetNodeId).items()
        }

        self.next_node_map = {
            key: [EdgeNode(edge, self.node_map.get(edge.targetNodeId)) for edge in edges]
            for key, edges in group_by(edges, key=lambda edge: edge.sourceNodeId).items()
        }
        self.node_field_list = init_fields(self)

    def get_node(self, node_id):
        """
        根据node_id 获取节点信息
        @param node_id: node_id
        @return: 节点信息
        """
        return self.node_map.get(node_id)

    def get_up_edge_nodes(self, node_id) -> List[EdgeNode]:
        """
        根据节点id 获取当前连接前置节点和连线
        @param node_id: 节点id
        @return: 节点连线列表
        """
        return self.up_node_map.get(node_id)

    def get_next_edge_nodes(self, node_id) -> List[EdgeNode]:
        """
        根据节点id 获取当前连接目标节点和连线
        @param node_id: 节点id
        @return: 节点连线列表
        """
        return self.next_node_map.get(node_id)

    def get_up_nodes(self, node_id) -> List[Node]:
        """
        根据节点id 获取当前连接前置节点
        @param node_id: 节点id
        @return: 节点列表
        """
        return [en.node for en in self.up_node_map.get(node_id)]

    def get_next_nodes(self, node_id) -> List[Node]:
        """
        根据节点id 获取当前连接目标节点
        @param node_id: 节点id
        @return: 节点列表
        """
        return [en.node for en in self.next_node_map.get(node_id, [])]

    def reset_prompt(self, prompt):
        for node_field in self.node_field_list:
            prompt = node_field.reset_variable(prompt)
        return prompt

    def is_valid(self, workflow_type: WorkflowType):
        """
        校验工作流数据:一趟遍历同时统计节点id出现次数、校验每个节点的参数
        """
        start_node_list = []
        for node in self.nodes:
            if node.id == "start-node":
                start_node_list.append(node)
            self.is_valid_node(node, workflow_type)
        self.is_valid_start_node(start_node_list)

    def is_valid_start_node(self, start_node_list: List[Node]):
        """
        校验开始节点:有且只有一个 start-node
        """
        if len(start_node_list) == 0:
            raise AppApiException(500, _("The starting node is required"))
        if len(start_node_list) > 1:
            raise AppApiException(500, _("There can only be one starting node"))

    def is_valid_node(self, node: Node, workflow_type: WorkflowType = WorkflowType.APPLICATION):
        """
        校验单个节点:交给该节点类型对应的序列化器
        """
        from application.workflow.nodes import node_map

        node_class = node_map.get(node.type, {}).get(workflow_type)
        if node_class is None or node_class.serializer_class is None:
            return
        try:
            node_class.serializer_class(data=get_node_parameters(node)).is_valid(raise_exception=True)
        except AppApiException as e:
            raise AppApiException(500, f"{node.properties.get('stepName')}:{e.message}")


def new_instance(flow_obj: Dict, workflow_type: WorkflowType = WorkflowType.APPLICATION):
    nodes = flow_obj.get("nodes")
    edges = flow_obj.get("edges")
    nodes = [Node(node.get("id"), node.get("type"), **node) for node in nodes]
    edges = [Edge(edge.get("id"), edge.get("type"), **edge) for edge in edges]
    return Workflow(nodes, edges)
