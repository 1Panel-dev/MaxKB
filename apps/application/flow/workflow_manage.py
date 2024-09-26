# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： workflow_manage.py
    @date：2024/1/9 17:40
    @desc:
"""
import json
import traceback
from functools import reduce
from typing import List, Dict

from django.db.models import QuerySet
from langchain_core.prompts import PromptTemplate
from rest_framework import status
from rest_framework.exceptions import ErrorDetail, ValidationError

from application.flow import tools
from application.flow.i_step_node import INode, WorkFlowPostHandler, NodeResult
from application.flow.step_node import get_node
from common.exception.app_exception import AppApiException
from common.handle.base_to_response import BaseToResponse
from common.handle.impl.response.system_to_response import SystemToResponse
from function_lib.models.function import FunctionLib
from setting.models import Model
from setting.models_provider import get_model_credential


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


end_nodes = ['ai-chat-node', 'reply-node', 'function-node', 'function-lib-node']


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

    def get_start_node(self):
        start_node_list = [node for node in self.nodes if node.id == 'start-node']
        return start_node_list[0]

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
                                          f'{node.properties.get("stepName")} 节点的{branch.get("type")}分支需要连接')
                elif len(edge_list) > 1:
                    raise AppApiException(500,
                                          f'{node.properties.get("stepName")} 节点的{branch.get("type")}分支不能连接俩个节点')

        else:
            edge_list = [edge for edge in self.edges if edge.sourceNodeId == node.id]
            if len(edge_list) == 0 and not end_nodes.__contains__(node.type):
                raise AppApiException(500, f'{node.properties.get("stepName")} 节点不能当做结束节点')
            elif len(edge_list) > 1:
                raise AppApiException(500,
                                      f'{node.properties.get("stepName")} 节点不能连接俩个节点')

    def get_next_nodes(self, node: Node):
        edge_list = [edge for edge in self.edges if edge.sourceNodeId == node.id]
        node_list = reduce(lambda x, y: [*x, *y],
                           [[node for node in self.nodes if node.id == edge.targetNodeId] for edge in edge_list],
                           [])
        if len(node_list) == 0 and not end_nodes.__contains__(node.type):
            raise AppApiException(500,
                                  f'不存在的下一个节点')
        return node_list

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
            raise AppApiException(500, '开始节点必填')
        if len(start_node_list) > 1:
            raise AppApiException(500, '开始节点只能有一个')

    def is_valid_model_params(self):
        node_list = [node for node in self.nodes if (node.type == 'ai-chat-node' or node.type == 'question-node')]
        for node in node_list:
            model = QuerySet(Model).filter(id=node.properties.get('node_data', {}).get('model_id')).first()
            if model is None:
                raise ValidationError(ErrorDetail(f'节点{node.properties.get("stepName")} 模型不存在'))
            credential = get_model_credential(model.provider, model.model_type, model.model_name)
            model_params_setting = node.properties.get('node_data', {}).get('model_params_setting')
            model_params_setting_form = credential.get_model_params_setting_form(
                model.model_name)
            if model_params_setting is None:
                model_params_setting = model_params_setting_form.get_default_form_data()
                node.properties.get('node_data', {})['model_params_setting'] = model_params_setting
            model_params_setting_form.valid_form(model_params_setting)
            if node.properties.get('status', 200) != 200:
                raise ValidationError(ErrorDetail(f'节点{node.properties.get("stepName")} 不可用'))
        node_list = [node for node in self.nodes if (node.type == 'function-lib-node')]
        for node in node_list:
            function_lib_id = node.properties.get('node_data', {}).get('function_lib_id')
            if function_lib_id is None:
                raise ValidationError(ErrorDetail(f'节点{node.properties.get("stepName")} 函数库id不能为空'))
            f_lib = QuerySet(FunctionLib).filter(id=function_lib_id).first()
            if f_lib is None:
                raise ValidationError(ErrorDetail(f'节点{node.properties.get("stepName")} 函数库不可用'))

    def is_valid_base_node(self):
        base_node_list = [node for node in self.nodes if node.id == 'base-node']
        if len(base_node_list) == 0:
            raise AppApiException(500, '基本信息节点必填')
        if len(base_node_list) > 1:
            raise AppApiException(500, '基本信息节点只能有一个')


class WorkflowManage:
    def __init__(self, flow: Flow, params, work_flow_post_handler: WorkFlowPostHandler,
                 base_to_response: BaseToResponse = SystemToResponse(), form_data=None):
        if form_data is None:
            form_data = {}
        self.form_data = form_data
        self.params = params
        self.flow = flow
        self.context = {}
        self.node_context = []
        self.work_flow_post_handler = work_flow_post_handler
        self.current_node = None
        self.current_result = None
        self.answer = ""
        self.base_to_response = base_to_response

    def run(self):
        if self.params.get('stream'):
            return self.run_stream()
        return self.run_block()

    def run_block(self):
        try:
            while self.has_next_node(self.current_result):
                self.current_node = self.get_next_node()
                self.current_node.valid_args(self.current_node.node_params, self.current_node.workflow_params)
                self.node_context.append(self.current_node)
                self.current_result = self.current_node.run()
                result = self.current_result.write_context(self.current_node, self)
                if result is not None:
                    list(result)
                if not self.has_next_node(self.current_result):
                    details = self.get_runtime_details()
                    message_tokens = sum([row.get('message_tokens') for row in details.values() if
                                          'message_tokens' in row and row.get('message_tokens') is not None])
                    answer_tokens = sum([row.get('answer_tokens') for row in details.values() if
                                         'answer_tokens' in row and row.get('answer_tokens') is not None])
                    self.work_flow_post_handler.handler(self.params['chat_id'], self.params['chat_record_id'],
                                                        self.answer,
                                                        self)
                    return self.base_to_response.to_block_response(self.params['chat_id'],
                                                                   self.params['chat_record_id'], self.answer, True
                                                                   , message_tokens, answer_tokens)
        except Exception as e:
            traceback.print_exc()
            self.current_node.get_write_error_context(e)
            self.work_flow_post_handler.handler(self.params['chat_id'], self.params['chat_record_id'],
                                                self.answer,
                                                self)
            return self.base_to_response.to_block_response(self.params['chat_id'], self.params['chat_record_id'],
                                                           str(e), True,
                                                           0, 0, _status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def run_stream(self):
        return tools.to_stream_response_simple(self.stream_event())

    def stream_event(self):
        try:
            while self.has_next_node(self.current_result):
                self.current_node = self.get_next_node()
                self.node_context.append(self.current_node)
                self.current_node.valid_args(self.current_node.node_params, self.current_node.workflow_params)
                self.current_result = self.current_node.run()
                result = self.current_result.write_context(self.current_node, self)
                has_next_node = self.has_next_node(self.current_result)
                if result is not None:
                    if self.is_result():
                        for r in result:
                            yield self.base_to_response.to_stream_chunk_response(self.params['chat_id'],
                                                                                 self.params['chat_record_id'],
                                                                                 r, False, 0, 0)
                        if has_next_node:
                            yield self.base_to_response.to_stream_chunk_response(self.params['chat_id'],
                                                                                 self.params['chat_record_id'],
                                                                                 '\n', False, 0, 0)
                            self.answer += '\n'
                    else:
                        list(result)
                if not has_next_node:
                    details = self.get_runtime_details()
                    message_tokens = sum([row.get('message_tokens') for row in details.values() if
                                          'message_tokens' in row and row.get('message_tokens') is not None])
                    answer_tokens = sum([row.get('answer_tokens') for row in details.values() if
                                         'answer_tokens' in row and row.get('answer_tokens') is not None])
                    yield self.base_to_response.to_stream_chunk_response(self.params['chat_id'],
                                                                         self.params['chat_record_id'],
                                                                         '', True, message_tokens, answer_tokens)
                    break
            self.work_flow_post_handler.handler(self.params['chat_id'], self.params['chat_record_id'],
                                                self.answer,
                                                self)
        except Exception as e:
            self.current_node.get_write_error_context(e)
            self.answer += str(e)
            self.work_flow_post_handler.handler(self.params['chat_id'], self.params['chat_record_id'],
                                                self.answer,
                                                self)
            yield self.base_to_response.to_stream_chunk_response(self.params['chat_id'], self.params['chat_record_id'],
                                                                 str(e), True, 0, 0)

    def is_result(self):
        """
        判断是否是返回节点
        @return:
        """
        return self.current_node.node_params.get('is_result', not self.has_next_node(
            self.current_result)) if self.current_node.node_params is not None else False

    def get_chunk_content(self, chunk, is_end=False):
        return 'data: ' + json.dumps(
            {'chat_id': self.params['chat_id'], 'id': self.params['chat_record_id'], 'operate': True,
             'content': chunk, 'is_end': is_end}, ensure_ascii=False) + "\n\n"

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
            details = node.get_details(index)
            details_result[node.id] = details
        return details_result

    def get_next_node(self):
        """
        获取下一个可运行的所有节点
        """
        if self.current_node is None:
            node = self.get_start_node()
            node_instance = get_node(node.type)(node, self.params, self)
            return node_instance
        if self.current_result is not None and self.current_result.is_assertion_result():
            for edge in self.flow.edges:
                if (edge.sourceNodeId == self.current_node.id and
                        f"{edge.sourceNodeId}_{self.current_result.node_variable.get('branch_id')}_right" == edge.sourceAnchorId):
                    return self.get_node_cls_by_id(edge.targetNodeId)
        else:
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
        context = {
            'global': self.context,
        }

        for node in self.node_context:
            properties = node.node.properties
            node_config = properties.get('config')
            if node_config is not None:
                fields = node_config.get('fields')
                if fields is not None:
                    for field in fields:
                        globeLabel = f"{properties.get('stepName')}.{field.get('value')}"
                        globeValue = f"context['{node.id}'].{field.get('value')}"
                        prompt = prompt.replace(globeLabel, globeValue)
                global_fields = node_config.get('globalFields')
                if global_fields is not None:
                    for field in global_fields:
                        globeLabel = f"全局变量.{field.get('value')}"
                        globeValue = f"context['global'].{field.get('value')}"
                        prompt = prompt.replace(globeLabel, globeValue)
                context[node.id] = node.context
        prompt_template = PromptTemplate.from_template(prompt, template_format='jinja2')

        value = prompt_template.format(context=context)
        return value

    def get_start_node(self):
        """
        获取启动节点
        @return:
        """
        start_node_list = [node for node in self.flow.nodes if node.type == 'start-node']
        return start_node_list[0]

    def get_base_node(self):
        """
        获取基础节点
        @return:
        """
        base_node_list = [node for node in self.flow.nodes if node.type == 'base-node']
        return base_node_list[0]

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
