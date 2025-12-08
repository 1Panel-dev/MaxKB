# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： common.py
    @date：2024/12/11 17:57
    @desc:
"""

from typing import List, Dict

from django.db.models import QuerySet
from django.utils.translation import gettext as _
from rest_framework.exceptions import ErrorDetail, ValidationError

from common.exception.app_exception import AppApiException
from common.utils.common import group_by
from models_provider.models import Model
from models_provider.tools import get_model_credential
from tools.models.tool import Tool

end_nodes = ['ai-chat-node', 'reply-node', 'function-node', 'function-lib-node', 'application-node',
             'image-understand-node', 'speech-to-text-node', 'text-to-speech-node', 'image-generate-node',
             'variable-assign-node']


class Answer:
    def __init__(self, content, view_type, runtime_node_id, chat_record_id, child_node, real_node_id,
                 reasoning_content):
        self.view_type = view_type
        self.content = content
        self.reasoning_content = reasoning_content
        self.runtime_node_id = runtime_node_id
        self.chat_record_id = chat_record_id
        self.child_node = child_node
        self.real_node_id = real_node_id

    def to_dict(self):
        return {'view_type': self.view_type, 'content': self.content, 'runtime_node_id': self.runtime_node_id,
                'chat_record_id': self.chat_record_id,
                'child_node': self.child_node,
                'reasoning_content': self.reasoning_content,
                'real_node_id': self.real_node_id}


class NodeChunk:
    def __init__(self):
        self.status = 0
        self.chunk_list = []

    def add_chunk(self, chunk):
        self.chunk_list.append(chunk)

    def end(self, chunk=None):
        if chunk is not None:
            self.add_chunk(chunk)
        self.status = 200

    def is_end(self):
        return self.status == 200


class Edge:
    def __init__(self, _id: str, _type: str, sourceNodeId: str, targetNodeId: str, **keywords):
        self.id = _id
        self.type = _type
        self.sourceNodeId = sourceNodeId
        self.targetNodeId = targetNodeId
        for keyword in keywords:
            self.__setattr__(keyword, keywords.get(keyword))


class Node:
    def __init__(self, _id: str, _type: str, x: int, y: int, properties: dict, **kwargs):
        self.id = _id
        self.type = _type
        self.x = x
        self.y = y
        self.properties = properties
        for keyword in kwargs:
            self.__setattr__(keyword, kwargs.get(keyword))


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

    @staticmethod
    def new_instance(flow_obj: Dict):
        nodes = flow_obj.get('nodes')
        edges = flow_obj.get('edges')
        nodes = [Node(node.get('id'), node.get('type'), **node)
                 for node in nodes]
        edges = [Edge(edge.get('id'), edge.get('type'), **edge) for edge in edges]
        return Workflow(nodes, edges)

    def get_start_node(self):
        return self.get_node('start-node')

    def get_search_node(self):
        return [node for node in self.nodes if node.type == 'search-dataset-node']

    def is_valid(self):
        """
        校验工作流数据
        """
        self.is_valid_model_params()
        self.is_valid_start_node()
        self.is_valid_base_node()
        self.is_valid_work_flow()

    @staticmethod
    def is_valid_node_params(node: Node):
        from application.flow.step_node import get_node
        get_node(node.type)(node, None, None)

    def is_valid_node(self, node: Node):
        self.is_valid_node_params(node)
        if node.type == 'condition-node':
            branch_list = node.properties.get('node_data').get('branch')
            for branch in branch_list:
                source_anchor_id = f"{node.id}_{branch.get('id')}_right"
                edge_list = [edge for edge in self.edges if edge.sourceAnchorId == source_anchor_id]
                if len(edge_list) == 0:
                    raise AppApiException(500,
                                          _('The branch {branch} of the {node} node needs to be connected').format(
                                              node=node.properties.get("stepName"), branch=branch.get("type")))

        else:
            edge_list = [edge for edge in self.edges if edge.sourceNodeId == node.id]
            if len(edge_list) == 0 and not end_nodes.__contains__(node.type):
                raise AppApiException(500, _("{node} Nodes cannot be considered as end nodes").format(
                    node=node.properties.get("stepName")))

    def is_valid_work_flow(self, up_node=None):
        if up_node is None:
            up_node = self.get_start_node()
        self.is_valid_node(up_node)
        next_nodes = self.get_next_nodes(up_node)
        for next_node in next_nodes:
            self.is_valid_work_flow(next_node)

    def is_valid_start_node(self):
        start_node_list = [node for node in self.nodes if node.id == 'start-node']
        if len(start_node_list) == 0:
            raise AppApiException(500, _('The starting node is required'))
        if len(start_node_list) > 1:
            raise AppApiException(500, _('There can only be one starting node'))

    def is_valid_model_params(self):
        node_list = [node for node in self.nodes if (node.type == 'ai-chat-node' or node.type == 'question-node')]
        for node in node_list:
            model = QuerySet(Model).filter(id=node.properties.get('node_data', {}).get('model_id')).first()
            if model is None:
                raise ValidationError(ErrorDetail(
                    _('The node {node} model does not exist').format(node=node.properties.get("stepName"))))
            credential = get_model_credential(model.provider, model.model_type, model.model_name)
            model_params_setting = node.properties.get('node_data', {}).get('model_params_setting')
            model_params_setting_form = credential.get_model_params_setting_form(
                model.model_name)
            if model_params_setting is None:
                model_params_setting = model_params_setting_form.get_default_form_data()
                node.properties.get('node_data', {})['model_params_setting'] = model_params_setting
            if node.properties.get('status', 200) != 200:
                raise ValidationError(
                    ErrorDetail(_("Node {node} is unavailable").format(node.properties.get("stepName"))))
        node_list = [node for node in self.nodes if (node.type == 'function-lib-node')]
        for node in node_list:
            function_lib_id = node.properties.get('node_data', {}).get('function_lib_id')
            if function_lib_id is None:
                raise ValidationError(ErrorDetail(
                    _('The library ID of node {node} cannot be empty').format(node=node.properties.get("stepName"))))
            f_lib = QuerySet(Tool).filter(id=function_lib_id).first()
            if f_lib is None:
                raise ValidationError(ErrorDetail(_("The function library for node {node} is not available").format(
                    node=node.properties.get("stepName"))))

    def is_valid_base_node(self):
        base_node_list = [node for node in self.nodes if node.id == 'base-node']
        if len(base_node_list) == 0:
            raise AppApiException(500, _('Basic information node is required'))
        if len(base_node_list) > 1:
            raise AppApiException(500, _('There can only be one basic information node'))
