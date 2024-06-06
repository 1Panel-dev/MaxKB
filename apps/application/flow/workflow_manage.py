# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： workflow_manage.py
    @date：2024/1/9 17:40
    @desc:
"""
from typing import List, Dict

from langchain_core.prompts import PromptTemplate

from application.flow.i_step_node import INode, WorkFlowPostHandler
from application.flow.step_node.ai_chat_step_node.impl.base_chat_node import BaseChatNode
from application.flow.step_node.search_dataset_node.impl.base_search_dataset_node import BaseSearchDatasetNode
from application.flow.step_node.start_node.impl.base_start_node import BaseStartStepNode


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


class Flow:
    def __init__(self, nodes: List[Node], edges: List[Edge]):
        self.nodes = nodes
        self.edges = edges

    @staticmethod
    def new_instance(flow_obj: Dict):
        nodes = flow_obj.get('nodes')
        edges = flow_obj.get('edges')
        nodes = [Node(node.get('id'), node.get('type'), **node)
                 for node in nodes]
        edges = [Edge(edge.get('id'), edge.get('type'), **edge) for edge in edges]
        return Flow(nodes, edges)


flow_node_dict = {
    'start-node': BaseStartStepNode,
    'search-dataset-node': BaseSearchDatasetNode,
    'chat-node': BaseChatNode
}


class WorkflowManage:
    def __init__(self, flow: Flow, params):
        self.params = params
        self.flow = flow
        self.context = {}
        self.node_dict = {}
        self.runtime_nodes = []
        self.current_node = None

    def run(self):
        """
        运行工作流
        """
        while self.has_next_node():
            self.current_node = self.get_next_node()
            self.node_dict[self.current_node.id] = self.current_node
            result = self.current_node.run()
            if self.has_next_node():
                result.write_context(self.current_node, self)
            else:
                r = result.to_response(self.params['chat_id'], self.params['chat_record_id'], self.current_node, self,
                                       WorkFlowPostHandler(client_id=self.params['client_id'], chat_info=None,
                                                           client_type='ss'))
                for row in r:
                    print(row)
        print(self)

    def has_next_node(self):
        """
        是否有下一个可运行的节点
        """
        if self.current_node is None:
            if self.get_start_node() is not None:
                return True
        else:
            for edge in self.flow.edges:
                if edge.sourceNodeId == self.current_node.id:
                    return True
        return False

    def get_runtime_details(self):
        return {}

    def get_next_node(self):
        """
        获取下一个可运行的所有节点
        """
        if self.current_node is None:
            node = self.get_start_node()
            node_instance = flow_node_dict[node.type](node.id, node.properties.get('node_data'),
                                                      self.params, self.context)
            return node_instance
        for edge in self.flow.edges:
            if edge.sourceNodeId == self.current_node.id:
                return self.get_node_cls_by_id(edge.targetNodeId)
        return None

    def get_reference_field(self, node_id: str, fields: List[str]):
        """

        @param node_id: 节点id
        @param fields:  字段
        @return:
        """
        if node_id == 'global':
            return INode.get_field(self.context, fields)
        else:
            return self.get_node_by_id(node_id).get_reference_field(fields)

    def generate_prompt(self, prompt: str):
        """
        格式化生成提示词
        @param prompt: 提示词信息
        @return: 格式化后的提示词
        """
        prompt_template = PromptTemplate.from_template(prompt, template_format='jinja2')
        context = {
            'global': self.context,
        }
        for key in self.node_dict:
            context[key] = self.node_dict[key].context
        value = prompt_template.format(context=context)
        return value

    def get_start_node(self):
        """
        获取启动节点
        @return:
        """
        return self.flow.nodes[0]

    def get_node_cls_by_id(self, node_id):
        for node in self.flow.nodes:
            if node.id == node_id:
                node_instance = flow_node_dict[node.type](node.id, node.properties.get('node_data'),
                                                          self.params, self)
                return node_instance
        return None

    def get_node_by_id(self, node_id):
        return self.node_dict[node_id]

    def get_node_reference(self, reference_address: Dict):
        node = self.get_node_by_id(reference_address.get('node_id'))
        return node.context[reference_address.get('node_field')]
