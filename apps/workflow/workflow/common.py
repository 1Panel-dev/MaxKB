# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： workflow.py
    @date：2025/5/9 10:58
    @desc:
"""
from typing import List, Dict
from queue import Queue, Empty

from common.utils.common import group_by


class Content:
    def __init__(self, content: str, reasoning_content: str, **kwargs):
        """
        内容
        @param content:          ai响应内容
        @param reasoning_content:思考过程
        @param kwargs:           其他参数
        """
        self.content = content
        self.reasoning_content = reasoning_content
        for key in kwargs:
            self.__setattr__(key, kwargs.get(key))


class Chunk:

    def __init__(self, runtime_id: str, node_id: str, node_name: str, content: Content, node_data, children, loop_index,
                 **kwargs):
        """

        @param runtime_id: 运行时id
        @param node_id:    节点id
        @param node_name:  节点名称
        @param loop_index: 循环下标
        @param children:   子块
        @param node_data   节点数据
        @param content:    内容
        """
        self.runtime_id = runtime_id
        self.node_id = node_id
        self.node_name = node_name
        self.loop_index = loop_index
        self.children = children
        self.content = content
        self.node_data = node_data
        for key in kwargs:
            self.__setattr__(key, kwargs.get(key))


class Channel:
    """
    对话管道
    """
    messages = Queue()
    is_end = False

    def write(self, message):
        if isinstance(message, Channel) | isinstance(message, Chunk):
            if self.is_end:
                raise "通道已关闭"
            self.messages.put(message)
        else:
            raise "不支持的管道参数"

    def end(self):
        self.is_end = True
        return self.messages.put(None)

    def pop(self):
        if self.is_end:
            return self.messages.get_nowait()
        return self.messages.get()

    def generator(self):
        while True:
            try:
                message = self.pop()
                if message:
                    if isinstance(message, Channel):
                        for chunk in message.generator():
                            yield chunk
                    else:
                        yield message
            except Empty:
                return


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

    def __init__(self, nodes: List[Node], edges: List[Edge]):
        self.nodes = nodes
        self.edges = edges
        self.node_map = {node.id: node for node in nodes}

        self.up_node_map = {key: [EdgeNode(edge, self.node_map.get(edge.sourceNodeId)) for
                                  edge in edges] for
                            key, edges in
                            group_by(edges, key=lambda edge: edge.targetNodeId).items()}

        self.next_node_map = {key: [EdgeNode(edge, self.node_map.get(edge.targetNodeId)) for edge in edges] for
                              key, edges in
                              group_by(edges, key=lambda edge: edge.sourceNodeId).items()}

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
