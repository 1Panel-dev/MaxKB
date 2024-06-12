# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： workflow_manage.py
    @date：2024/1/9 17:40
    @desc:
"""
import json
import uuid
from typing import List, Dict

from langchain_core.prompts import PromptTemplate

from application.flow.i_step_node import INode, WorkFlowPostHandler, NodeResult
from application.flow.step_node import get_node


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


class WorkflowManage:
    def __init__(self, flow: Flow, params):
        self.params = params
        self.flow = flow
        self.context = {}
        self.node_context = []
        self.current_node = None
        self.current_result = None

    def run(self):
        """
        运行工作流
        """
        while self.has_next_node(self.current_result):
            self.current_node = self.get_next_node()
            self.node_context.append(self.current_node)
            self.current_result = self.current_node.run()
            if self.has_next_node(self.current_result):
                self.current_result.write_context(self.current_node, self)
            else:
                r = self.current_result.to_response(self.params['chat_id'], self.params['chat_record_id'],
                                                    self.current_node, self,
                                                    WorkFlowPostHandler(client_id=self.params['client_id'],
                                                                        chat_info=None,
                                                                        client_type='APPLICATION_ACCESS_TOKEN'))
                for row in r:
                    print(row)
        print(self)

    def has_next_node(self, node_result: NodeResult | None):
        """
        是否有下一个可运行的节点
        """
        if self.current_node is None:
            if self.get_start_node() is not None:
                return True
        else:
            if node_result is not None and node_result.is_assertion_result():
                for edge in self.flow.edges:
                    if (edge.sourceNodeId == self.current_node.id and
                            f"{edge.sourceNodeId}_{node_result.node_variable.get('branch_id')}_right" == edge.sourceAnchorId):
                        return True
            else:
                for edge in self.flow.edges:
                    if edge.sourceNodeId == self.current_node.id:
                        return True
        return False

    def get_runtime_details(self):
        details_result = {}
        for index in range(len(self.node_context)):
            node = self.node_context[index]
            details = node.get_details({'index': index})
            details_result[node.id] = details
        return details_result

    def get_next_node(self):
        """
        获取下一个可运行的所有节点
        """
        if self.current_node is None:
            node = self.get_start_node()
            node_instance = get_node(node.type)(node, self.params, self.context)
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

        for node in self.node_context:
            context[node.id] = node.context
        value = prompt_template.format(context=context)
        return value

    def get_start_node(self):
        """
        获取启动节点
        @return:
        """
        start_node_list = [node for node in self.flow.nodes if node.type == 'start-node']
        return start_node_list[0]

    def get_node_cls_by_id(self, node_id):
        for node in self.flow.nodes:
            if node.id == node_id:
                node_instance = get_node(node.type)(node,
                                                    self.params, self)
                return node_instance
        return None

    def get_node_by_id(self, node_id):
        for node in self.node_context:
            if node.id == node_id:
                return node
        return None

    def get_node_reference(self, reference_address: Dict):
        node = self.get_node_by_id(reference_address.get('node_id'))
        return node.context[reference_address.get('node_field')]


json_str = """
{
    "nodes": [
        {
            "id": "base-node",
            "type": "base-node",
            "x": 200,
            "y": 270,
            "properties": {
                "height": 200,
                "stepName": "基本信息",
                "node_data": {
                    "name": "",
                    "desc": "",
                    "prologue": "您好，我是 MaxKB 小助手，您可以向我提出 MaxKB 使用问题。"
                }
            }
        },
        {
            "id": "start-node",
            "type": "start-node",
            "x": 140,
            "y": 800,
            "properties": {
                "height": 200,
                "stepName": "开始",
                "output": [
                    {
                        "key": ""
                    }
                ],
                "fields": [
                    {
                        "label": "用户问题",
                        "value": "question"
                    }
                ]
            }
        },
        {
            "id": "34902d3d-a3ff-497f-b8e1-0c34a44d7dd5",
            "type": "search-dataset-node",
            "x": 1490,
            "y": 580,
            "properties": {
                "height": 200,
                "stepName": "知识库检索",
                "input": [
                    {
                        "key": "输入"
                    }
                ],
                "output": [
                    {
                        "key": "输出"
                    }
                ],
                "fields": [
                    {
                        "label": "检索结果",
                        "value": "data"
                    },
                    {
                        "label": "满足直接回答的分段内容",
                        "value": "paragraph"
                    }
                ],
                "node_data": {
                    "dataset_id_list": [
                        "e750b5f5-247a-11ef-8fc8-a8a1595801ab",
                        "1e42a226-1bfd-11ef-be5f-a8a1595801ab",
                        "e3b4ad8d-18f2-11ef-9a18-a8a1595801ab",
                        "861d1f5c-18f3-11ef-a40e-a8a1595801ab"
                    ],
                    "dataset_setting": {
                        "top_n": 3,
                        "similarity": 0.6,
                        "max_paragraph_char_number": 5000,
                        "search_mode": "embedding"
                    },
                    "question_reference_address": [
                        "start-node",
                        "question"
                    ]
                }
            }
        },
        {
            "id": "34902d3d-a3ff-497f-b8e1-0c34a44d7dd6",
            "type": "condition-node",
            "x": 1080,
            "y": 500,
            "properties": {
                "height": 200,
                "width": 600,
                "stepName": "判断器",
                "input": [
                    {
                        "key": "输入"
                    }
                ],
                "output": [
                    {
                        "key": "9208"
                    },
                    {
                        "key": "1143"
                    },
                    {
                        "key": "输出"
                    }
                ],
                "node_data": {
                    "branch": [
                        {
                            "conditions": [
                                {
                                    "field": [
                                        "03597cb0-ed4c-4bcb-b25b-3b358f72b266",
                                        "answer"
                                    ],
                                    "compare": "contain",
                                    "value": "打招呼"
                                }
                            ],
                            "id": "2391",
                            "type": "IF",
                            "condition": "and"
                        },
                        {
                            "conditions": [
                                {
                                    "field": [
                                        "03597cb0-ed4c-4bcb-b25b-3b358f72b266",
                                        "answer"
                                    ],
                                    "compare": "contain",
                                    "value": "售前咨询"
                                }
                            ],
                            "id": "1143",
                            "type": "IF ELSE 1",
                            "condition": "and"
                        },
                        {
                            "conditions": [

                            ],
                            "id": "9208",
                            "type": "ELSE",
                            "condition": "and"
                        }
                    ]
                }
            }
        },
        {
            "id": "03597cb0-ed4c-4bcb-b25b-3b358f72b266",
            "type": "ai-chat-node",
            "x": 580,
            "y": 400,
            "properties": {
                "height": "",
                "stepName": "AI 对话",
                "input": [
                    {
                        "key": "输入"
                    }
                ],
                "output": [
                    {
                        "key": "输出"
                    }
                ],
                "node_data": {
                    "model_id": "9bdd1ab3-135b-11ef-b688-a8a1595801ab",
                    "system": "你是问题分析大师",
                    "prompt": "请直接返回所属的问题分类，不要说推理过程。用户问题为：{{context['start-node'].question}} 问题分类是：打招呼 售前咨询 售后咨询其他咨询",
                    "dialogue_number": 1
                }
            }
        },
        {
            "id": "6649ee86-348c-4d68-9cad-71f0612beb05",
            "type": "ai-chat-node",
            "x": 2030,
            "y": 500,
            "properties": {
                "height": "",
                "stepName": "AI 对话",
                "input": [
                    {
                        "key": "输入"
                    }
                ],
                "output": [
                    {
                        "key": "输出"
                    }
                ],
                "node_data": {
                    "model_id": "9bdd1ab3-135b-11ef-b688-a8a1595801ab",
                    "system": "你是售前咨询工程师",
                    "prompt": "已知信息:{{context['34902d3d-a3ff-497f-b8e1-0c34a44d7dd5'].data}}回答用户问题:{{context['start-node'].question}}",
                    "dialogue_number": 0
                }
            }
        },
        {
            "id": "0004a9c9-e2fa-40ac-9215-2e1ad04f09c5",
            "type": "ai-chat-node",
            "x": 1360,
            "y": 1300,
            "properties": {
                "height": "",
                "stepName": "AI 对话",
                "input": [
                    {
                        "key": "输入"
                    }
                ],
                "output": [
                    {
                        "key": "输出"
                    }
                ],
                "node_data": {
                    "model_id": "9bdd1ab3-135b-11ef-b688-a8a1595801ab",
                    "system": "你是售后咨询工程师",
                    "prompt": "{{context['start-node'].question}}",
                    "dialogue_number": 0
                }
            }
        },
        {
            "id": "30c16d31-3881-48cd-991e-da3f99c45681",
            "type": "reply-node",
            "x": 1690,
            "y": 170,
            "properties": {
                "height": "",
                "stepName": "指定回复",
                "input": [
                    {
                        "key": ""
                    }
                ],
                "output": [
                    {
                        "key": ""
                    }
                ],
                "node_data": {
                    "reply_type": "content",
                    "content": "你好,有什么需要帮助的吗",
                    "fields": [

                    ]
                }
            }
        }
    ],
    "edges": [
        {
            "id": "214aa478-78ce-4c95-89aa-11f821bc65d2",
            "type": "app-edge",
            "sourceNodeId": "start-node",
            "targetNodeId": "03597cb0-ed4c-4bcb-b25b-3b358f72b266",
            "startPoint": {
                "x": 300,
                "y": 865.3335000000001
            },
            "endPoint": {
                "x": 420,
                "y": 677
            },
            "properties": {

            },
            "pointsList": [
                {
                    "x": 300,
                    "y": 865.3335000000001
                },
                {
                    "x": 410,
                    "y": 865.3335000000001
                },
                {
                    "x": 310,
                    "y": 677
                },
                {
                    "x": 420,
                    "y": 677
                }
            ],
            "sourceAnchorId": "start-node__right",
            "targetAnchorId": "03597cb0-ed4c-4bcb-b25b-3b358f72b266_输入_left"
        },
        {
            "id": "d56fb64a-4fc0-4779-911b-283a2238ef7b",
            "type": "app-edge",
            "sourceNodeId": "03597cb0-ed4c-4bcb-b25b-3b358f72b266",
            "targetNodeId": "34902d3d-a3ff-497f-b8e1-0c34a44d7dd6",
            "startPoint": {
                "x": 740,
                "y": 672
            },
            "endPoint": {
                "x": 790,
                "y": 678.6665
            },
            "properties": {

            },
            "pointsList": [
                {
                    "x": 740,
                    "y": 672
                },
                {
                    "x": 850,
                    "y": 672
                },
                {
                    "x": 680,
                    "y": 678.6665
                },
                {
                    "x": 790,
                    "y": 678.6665
                }
            ],
            "sourceAnchorId": "03597cb0-ed4c-4bcb-b25b-3b358f72b266_输出_right",
            "targetAnchorId": "34902d3d-a3ff-497f-b8e1-0c34a44d7dd6_输入_left"
        },
        {
            "id": "26fe01d6-8d41-4025-a637-e09f41c9b2c8",
            "type": "app-edge",
            "sourceNodeId": "34902d3d-a3ff-497f-b8e1-0c34a44d7dd6",
            "targetNodeId": "30c16d31-3881-48cd-991e-da3f99c45681",
            "startPoint": {
                "x": 1370,
                "y": 673.6665
            },
            "endPoint": {
                "x": 1530,
                "y": 286
            },
            "properties": {

            },
            "pointsList": [
                {
                    "x": 1370,
                    "y": 673.6665
                },
                {
                    "x": 1480,
                    "y": 673.6665
                },
                {
                    "x": 1420,
                    "y": 286
                },
                {
                    "x": 1530,
                    "y": 286
                }
            ],
            "sourceAnchorId": "34902d3d-a3ff-497f-b8e1-0c34a44d7dd6_9208_right",
            "targetAnchorId": "30c16d31-3881-48cd-991e-da3f99c45681__left"
        },
        {
            "id": "5c85d2bb-cb27-44ed-9e05-505f702381f6",
            "type": "app-edge",
            "sourceNodeId": "34902d3d-a3ff-497f-b8e1-0c34a44d7dd6",
            "targetNodeId": "34902d3d-a3ff-497f-b8e1-0c34a44d7dd5",
            "startPoint": {
                "x": 1370,
                "y": 697.6665
            },
            "endPoint": {
                "x": 1330,
                "y": 898.889
            },
            "properties": {

            },
            "pointsList": [
                {
                    "x": 1370,
                    "y": 697.6665
                },
                {
                    "x": 1480,
                    "y": 697.6665
                },
                {
                    "x": 1220,
                    "y": 898.889
                },
                {
                    "x": 1330,
                    "y": 898.889
                }
            ],
            "sourceAnchorId": "34902d3d-a3ff-497f-b8e1-0c34a44d7dd6_1143_right",
            "targetAnchorId": "34902d3d-a3ff-497f-b8e1-0c34a44d7dd5_输入_left"
        },
        {
            "id": "4d4b5740-910e-48b0-badd-8b9ce10e6e4e",
            "type": "app-edge",
            "sourceNodeId": "34902d3d-a3ff-497f-b8e1-0c34a44d7dd5",
            "targetNodeId": "6649ee86-348c-4d68-9cad-71f0612beb05",
            "startPoint": {
                "x": 1650,
                "y": 893.889
            },
            "endPoint": {
                "x": 1870,
                "y": 777
            },
            "properties": {

            },
            "pointsList": [
                {
                    "x": 1650,
                    "y": 893.889
                },
                {
                    "x": 1760,
                    "y": 893.889
                },
                {
                    "x": 1760,
                    "y": 777
                },
                {
                    "x": 1870,
                    "y": 777
                }
            ],
            "sourceAnchorId": "34902d3d-a3ff-497f-b8e1-0c34a44d7dd5_输出_right",
            "targetAnchorId": "6649ee86-348c-4d68-9cad-71f0612beb05_输入_left"
        },
        {
            "id": "9c446d4d-e500-4867-8d47-ed99f80b9b48",
            "type": "app-edge",
            "sourceNodeId": "34902d3d-a3ff-497f-b8e1-0c34a44d7dd6",
            "targetNodeId": "0004a9c9-e2fa-40ac-9215-2e1ad04f09c5",
            "startPoint": {
                "x": 1370,
                "y": 721.6665
            },
            "endPoint": {
                "x": 1200,
                "y": 1577
            },
            "properties": {

            },
            "pointsList": [
                {
                    "x": 1370,
                    "y": 721.6665
                },
                {
                    "x": 1480,
                    "y": 721.6665
                },
                {
                    "x": 1090,
                    "y": 1577
                },
                {
                    "x": 1200,
                    "y": 1577
                }
            ],
            "sourceAnchorId": "34902d3d-a3ff-497f-b8e1-0c34a44d7dd6_2391_right",
            "targetAnchorId": "0004a9c9-e2fa-40ac-9215-2e1ad04f09c5_输入_left"
        }
    ]
}
"""
f = Flow.new_instance(json.loads(json_str))
_id = str(uuid.uuid1())
w_manage = WorkflowManage(flow=f,
                          params={"history_chat_record": [], "question": "有企业版吗", "chat_id": _id,
                                  "chat_record_id": _id,
                                  "stream": True, "client_id": _id, "client_type": "xxxx"})
w_manage.run()
