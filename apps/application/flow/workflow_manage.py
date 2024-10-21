# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： workflow_manage.py
    @date：2024/1/9 17:40
    @desc:
"""
import json
import threading
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
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

executor = ThreadPoolExecutor(max_workers=50)


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

        else:
            edge_list = [edge for edge in self.edges if edge.sourceNodeId == node.id]
            if len(edge_list) == 0 and not end_nodes.__contains__(node.type):
                raise AppApiException(500, f'{node.properties.get("stepName")} 节点不能当做结束节点')

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


class NodeResultFuture:
    def __init__(self, r, e, status=200):
        self.r = r
        self.e = e
        self.status = status

    def result(self):
        if self.status == 200:
            return self.r
        else:
            raise self.e


def await_result(result, timeout=1):
    try:
        result.result(timeout)
        return False
    except Exception as e:
        return True


class NodeChunkManage:

    def __init__(self, work_flow):
        self.node_chunk_list = []
        self.current_node_chunk = None
        self.work_flow = work_flow

    def add_node_chunk(self, node_chunk):
        self.node_chunk_list.append(node_chunk)

    def contains(self, node_chunk):
        return self.node_chunk_list.__contains__(node_chunk)

    def pop(self):
        if self.current_node_chunk is None:
            try:
                current_node_chunk = self.node_chunk_list.pop(0)
                self.current_node_chunk = current_node_chunk
            except IndexError as e:
                pass
        if self.current_node_chunk is not None:
            try:
                chunk = self.current_node_chunk.chunk_list.pop(0)
                return chunk
            except IndexError as e:
                if self.current_node_chunk.is_end():
                    self.current_node_chunk = None
                    if len(self.work_flow.answer) > 0:
                        chunk = self.work_flow.base_to_response.to_stream_chunk_response(
                            self.work_flow.params['chat_id'],
                            self.work_flow.params['chat_record_id'],
                            '\n\n', False, 0, 0)
                        self.work_flow.answer += '\n\n'
                        return chunk
                    return self.pop()
        return None


class NodeChunk:
    def __init__(self):
        self.status = 0
        self.chunk_list = []

    def add_chunk(self, chunk):
        self.chunk_list.append(chunk)

    def end(self):
        self.status = 200

    def is_end(self):
        return self.status == 200


class WorkflowManage:
    def __init__(self, flow: Flow, params, work_flow_post_handler: WorkFlowPostHandler,
                 base_to_response: BaseToResponse = SystemToResponse(), form_data=None):
        if form_data is None:
            form_data = {}
        self.form_data = form_data
        self.params = params
        self.flow = flow
        self.lock = threading.Lock()
        self.context = {}
        self.node_context = []
        self.node_chunk_manage = NodeChunkManage(self)
        self.work_flow_post_handler = work_flow_post_handler
        self.current_node = None
        self.current_result = None
        self.answer = ""
        self.status = 0
        self.base_to_response = base_to_response

    def run(self):
        if self.params.get('stream'):
            return self.run_stream()
        return self.run_block()

    def run_block(self):
        """
        非流式响应
        @return: 结果
        """
        result = self.run_chain_async(None)
        result.result()
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
                                                       , message_tokens, answer_tokens,
                                                       _status=status.HTTP_200_OK if self.status == 200 else status.HTTP_500_INTERNAL_SERVER_ERROR)

    def run_stream(self):
        """
        流式响应
        @return:
        """
        result = self.run_chain_async(None)
        return tools.to_stream_response_simple(self.await_result(result))

    def await_result(self, result):
        try:
            while await_result(result):
                while True:
                    chunk = self.node_chunk_manage.pop()
                    if chunk is not None:
                        yield chunk
                    else:
                        break
            while True:
                chunk = self.node_chunk_manage.pop()
                if chunk is None:
                    break
                yield chunk
        finally:
            self.work_flow_post_handler.handler(self.params['chat_id'], self.params['chat_record_id'],
                                                self.answer,
                                                self)

    def run_chain_async(self, current_node):
        future = executor.submit(self.run_chain, current_node)
        return future

    def run_chain(self, current_node):
        if current_node is None:
            start_node = self.get_start_node()
            current_node = get_node(start_node.type)(start_node, self.params, self)
        node_result_future = self.run_node_future(current_node)
        try:
            is_stream = self.params.get('stream', True)
            # 处理节点响应
            result = self.hand_event_node_result(current_node,
                                                 node_result_future) if is_stream else self.hand_node_result(
                current_node, node_result_future)
            with self.lock:
                if current_node.status == 500:
                    return
                node_list = self.get_next_node_list(current_node, result)
            # 获取到可执行的子节点
            result_list = []
            for node in node_list:
                result = self.run_chain_async(node)
                result_list.append(result)
            [r.result() for r in result_list]
            if self.status == 0:
                self.status = 200
        except Exception as e:
            traceback.print_exc()

    def hand_node_result(self, current_node, node_result_future):
        try:
            current_result = node_result_future.result()
            result = current_result.write_context(current_node, self)
            if result is not None:
                # 阻塞获取结果
                list(result)
            # 添加节点
            self.node_context.append(current_node)
            return current_result
        except Exception as e:
            # 添加节点
            self.node_context.append(current_node)
            traceback.print_exc()
            self.status = 500
            current_node.get_write_error_context(e)
            self.answer += str(e)

    def hand_event_node_result(self, current_node, node_result_future):
        node_chunk = NodeChunk()
        try:
            current_result = node_result_future.result()
            result = current_result.write_context(current_node, self)
            if result is not None:
                if self.is_result(current_node, current_result):
                    self.node_chunk_manage.add_node_chunk(node_chunk)
                    for r in result:
                        chunk = self.base_to_response.to_stream_chunk_response(self.params['chat_id'],
                                                                               self.params['chat_record_id'],
                                                                               r, False, 0, 0)
                        node_chunk.add_chunk(chunk)
                    node_chunk.end()
                else:
                    list(result)
            # 添加节点
            self.node_context.append(current_node)
            return current_result
        except Exception as e:
            # 添加节点
            self.node_context.append(current_node)
            traceback.print_exc()
            self.answer += str(e)
            chunk = self.base_to_response.to_stream_chunk_response(self.params['chat_id'],
                                                                   self.params['chat_record_id'],
                                                                   str(e), False, 0, 0)
            if not self.node_chunk_manage.contains(node_chunk):
                self.node_chunk_manage.add_node_chunk(node_chunk)
            node_chunk.add_chunk(chunk)
            node_chunk.end()
            current_node.get_write_error_context(e)
            self.status = 500

    def run_node_async(self, node):
        future = executor.submit(self.run_node, node)
        return future

    def run_node_future(self, node):
        try:
            node.valid_args(node.node_params, node.workflow_params)
            result = self.run_node(node)
            return NodeResultFuture(result, None, 200)
        except Exception as e:
            return NodeResultFuture(None, e, 500)

    def run_node(self, node):
        result = node.run()
        result.write_context(node, self)
        return result

    def is_result(self, current_node, current_node_result):
        return current_node.node_params.get('is_result', not self._has_next_node(
            current_node, current_node_result)) if current_node.node_params is not None else False

    def get_chunk_content(self, chunk, is_end=False):
        return 'data: ' + json.dumps(
            {'chat_id': self.params['chat_id'], 'id': self.params['chat_record_id'], 'operate': True,
             'content': chunk, 'is_end': is_end}, ensure_ascii=False) + "\n\n"

    def _has_next_node(self, current_node, node_result: NodeResult | None):
        """
        是否有下一个可运行的节点
        """
        if node_result is not None and node_result.is_assertion_result():
            for edge in self.flow.edges:
                if (edge.sourceNodeId == current_node.id and
                        f"{edge.sourceNodeId}_{node_result.node_variable.get('branch_id')}_right" == edge.sourceAnchorId):
                    return True
        else:
            for edge in self.flow.edges:
                if edge.sourceNodeId == current_node.id:
                    return True

    def has_next_node(self, node_result: NodeResult | None):
        """
        是否有下一个可运行的节点
        """
        return self._has_next_node(self.get_start_node() if self.current_node is None else self.current_node,
                                   node_result)

    def get_runtime_details(self):
        details_result = {}
        for index in range(len(self.node_context)):
            node = self.node_context[index]
            details = node.get_details(index)
            details_result[str(uuid.uuid1())] = details
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

    def dependent_node_been_executed(self, node_id):
        """
        判断依赖节点是否都已执行
        @param node_id: 需要判断的节点id
        @return:
        """
        up_node_id_list = [edge.sourceNodeId for edge in self.flow.edges if edge.targetNodeId == node_id]
        return all([any([node.id == up_node_id for node in self.node_context]) for up_node_id in up_node_id_list])

    def get_next_node_list(self, current_node, current_node_result):
        """
        获取下一个可执行节点列表
        @param current_node:         当前可执行节点
        @param current_node_result:  当前可执行节点结果
        @return:  可执行节点列表
        """
        node_list = []
        if current_node_result is not None and current_node_result.is_assertion_result():
            for edge in self.flow.edges:
                if (edge.sourceNodeId == current_node.id and
                        f"{edge.sourceNodeId}_{current_node_result.node_variable.get('branch_id')}_right" == edge.sourceAnchorId):
                    if self.dependent_node_been_executed(edge.targetNodeId):
                        node_list.append(self.get_node_cls_by_id(edge.targetNodeId))
        else:
            for edge in self.flow.edges:
                if edge.sourceNodeId == current_node.id and self.dependent_node_been_executed(edge.targetNodeId):
                    node_list.append(self.get_node_cls_by_id(edge.targetNodeId))
        return node_list

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
