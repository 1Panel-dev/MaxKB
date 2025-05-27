# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： workflow_manage.py
    @date：2024/1/9 17:40
    @desc:
"""
import concurrent
import json
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor
from functools import reduce
from typing import List, Dict

from django.db import close_old_connections
from django.db.models import QuerySet
from django.utils import translation
from django.utils.translation import get_language
from django.utils.translation import gettext as _
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

executor = ThreadPoolExecutor(max_workers=200)


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


end_nodes = ['ai-chat-node', 'reply-node', 'function-node', 'function-lib-node', 'application-node',
             'image-understand-node', 'speech-to-text-node', 'text-to-speech-node', 'image-generate-node']


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
                                          _('The branch {branch} of the {node} node needs to be connected').format(
                                              node=node.properties.get("stepName"), branch=branch.get("type")))

        else:
            edge_list = [edge for edge in self.edges if edge.sourceNodeId == node.id]
            if len(edge_list) == 0 and not end_nodes.__contains__(node.type):
                raise AppApiException(500, _("{node} Nodes cannot be considered as end nodes").format(
                    node=node.properties.get("stepName")))

    def get_next_nodes(self, node: Node):
        edge_list = [edge for edge in self.edges if edge.sourceNodeId == node.id]
        node_list = reduce(lambda x, y: [*x, *y],
                           [[node for node in self.nodes if node.id == edge.targetNodeId] for edge in edge_list],
                           [])
        if len(node_list) == 0 and not end_nodes.__contains__(node.type):
            raise AppApiException(500,
                                  _("The next node that does not exist"))
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
            f_lib = QuerySet(FunctionLib).filter(id=function_lib_id).first()
            if f_lib is None:
                raise ValidationError(ErrorDetail(_("The function library for node {node} is not available").format(
                    node=node.properties.get("stepName"))))

    def is_valid_base_node(self):
        base_node_list = [node for node in self.nodes if node.id == 'base-node']
        if len(base_node_list) == 0:
            raise AppApiException(500, _('Basic information node is required'))
        if len(base_node_list) > 1:
            raise AppApiException(500, _('There can only be one basic information node'))


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
                    if self.work_flow.answer_is_not_empty():
                        chunk = self.work_flow.base_to_response.to_stream_chunk_response(
                            self.work_flow.params['chat_id'],
                            self.work_flow.params['chat_record_id'],
                            '\n\n', False, 0, 0)
                        self.work_flow.append_answer('\n\n')
                        return chunk
                    return self.pop()
        return None


class WorkflowManage:
    def __init__(self, flow: Flow, params, work_flow_post_handler: WorkFlowPostHandler,
                 base_to_response: BaseToResponse = SystemToResponse(), form_data=None, image_list=None,
                 document_list=None,
                 audio_list=None,
                 other_list=None,
                 start_node_id=None,
                 start_node_data=None, chat_record=None, child_node=None):
        if form_data is None:
            form_data = {}
        if image_list is None:
            image_list = []
        if document_list is None:
            document_list = []
        if audio_list is None:
            audio_list = []
        if other_list is None:
            other_list = []
        self.start_node_id = start_node_id
        self.start_node = None
        self.form_data = form_data
        self.image_list = image_list
        self.document_list = document_list
        self.audio_list = audio_list
        self.other_list = other_list
        self.params = params
        self.flow = flow
        self.context = {}
        self.node_chunk_manage = NodeChunkManage(self)
        self.work_flow_post_handler = work_flow_post_handler
        self.current_node = None
        self.current_result = None
        self.answer = ""
        self.answer_list = ['']
        self.status = 200
        self.base_to_response = base_to_response
        self.chat_record = chat_record
        self.child_node = child_node
        self.future_list = []
        self.lock = threading.Lock()
        self.field_list = []
        self.global_field_list = []
        self.init_fields()
        if start_node_id is not None:
            self.load_node(chat_record, start_node_id, start_node_data)
        else:
            self.node_context = []

    def init_fields(self):
        field_list = []
        global_field_list = []
        for node in self.flow.nodes:
            properties = node.properties
            node_name = properties.get('stepName')
            node_id = node.id
            node_config = properties.get('config')
            if node_config is not None:
                fields = node_config.get('fields')
                if fields is not None:
                    for field in fields:
                        field_list.append({**field, 'node_id': node_id, 'node_name': node_name})
                global_fields = node_config.get('globalFields')
                if global_fields is not None:
                    for global_field in global_fields:
                        global_field_list.append({**global_field, 'node_id': node_id, 'node_name': node_name})
        field_list.sort(key=lambda f: len(f.get('node_name')), reverse=True)
        global_field_list.sort(key=lambda f: len(f.get('node_name')), reverse=True)
        self.field_list = field_list
        self.global_field_list = global_field_list

    def append_answer(self, content):
        self.answer += content
        self.answer_list[-1] += content

    def answer_is_not_empty(self):
        return len(self.answer_list[-1]) > 0

    def load_node(self, chat_record, start_node_id, start_node_data):
        self.node_context = []
        self.answer = chat_record.answer_text
        self.answer_list = chat_record.answer_text_list
        self.answer_list.append('')
        for node_details in sorted(chat_record.details.values(), key=lambda d: d.get('index')):
            node_id = node_details.get('node_id')
            if node_details.get('runtime_node_id') == start_node_id:
                def get_node_params(n):
                    is_result = False
                    if n.type == 'application-node':
                        is_result = True
                    return {**n.properties.get('node_data'), 'form_data': start_node_data, 'node_data': start_node_data,
                            'child_node': self.child_node, 'is_result': is_result}

                self.start_node = self.get_node_cls_by_id(node_id, node_details.get('up_node_id_list'),
                                                          get_node_params=get_node_params)
                self.start_node.valid_args(
                    {**self.start_node.node_params, 'form_data': start_node_data}, self.start_node.workflow_params)
                if self.start_node.type == 'application-node':
                    application_node_dict = node_details.get('application_node_dict', {})
                    self.start_node.context['application_node_dict'] = application_node_dict
                self.node_context.append(self.start_node)
                continue

            node_id = node_details.get('node_id')
            node = self.get_node_cls_by_id(node_id, node_details.get('up_node_id_list'))
            node.valid_args(node.node_params, node.workflow_params)
            node.save_context(node_details, self)
            node.node_chunk.end()
            self.node_context.append(node)

    def run(self):
        close_old_connections()
        language = get_language()
        if self.params.get('stream'):
            return self.run_stream(self.start_node, None, language)
        return self.run_block(language)

    def run_block(self, language='zh'):
        """
        非流式响应
        @return: 结果
        """
        self.run_chain_async(None, None, language)
        while self.is_run():
            pass
        details = self.get_runtime_details()
        message_tokens = sum([row.get('message_tokens') for row in details.values() if
                              'message_tokens' in row and row.get('message_tokens') is not None])
        answer_tokens = sum([row.get('answer_tokens') for row in details.values() if
                             'answer_tokens' in row and row.get('answer_tokens') is not None])
        answer_text_list = self.get_answer_text_list()
        answer_text = '\n\n'.join(
            '\n\n'.join([a.get('content') for a in answer]) for answer in
            answer_text_list)
        answer_list = reduce(lambda pre, _n: [*pre, *_n], answer_text_list, [])
        self.work_flow_post_handler.handler(self.params['chat_id'], self.params['chat_record_id'],
                                            answer_text,
                                            self)
        return self.base_to_response.to_block_response(self.params['chat_id'],
                                                       self.params['chat_record_id'], answer_text, True
                                                       , message_tokens, answer_tokens,
                                                       _status=status.HTTP_200_OK if self.status == 200 else status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                       other_params={'answer_list': answer_list})

    def run_stream(self, current_node, node_result_future, language='zh'):
        """
        流式响应
        @return:
        """
        self.run_chain_async(current_node, node_result_future, language)
        return tools.to_stream_response_simple(self.await_result())

    def is_run(self, timeout=0.5):
        future_list_len = len(self.future_list)
        try:
            r = concurrent.futures.wait(self.future_list, timeout)
            if len(r.not_done) > 0:
                return True
            else:
                if future_list_len == len(self.future_list):
                    return False
                else:
                    return True
        except Exception as e:
            return True

    def await_result(self):
        try:
            while self.is_run():
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
            while self.is_run():
                pass
            details = self.get_runtime_details()
            message_tokens = sum([row.get('message_tokens') for row in details.values() if
                                  'message_tokens' in row and row.get('message_tokens') is not None])
            answer_tokens = sum([row.get('answer_tokens') for row in details.values() if
                                 'answer_tokens' in row and row.get('answer_tokens') is not None])
            self.work_flow_post_handler.handler(self.params['chat_id'], self.params['chat_record_id'],
                                                self.answer,
                                                self)
            yield self.base_to_response.to_stream_chunk_response(self.params['chat_id'],
                                                                 self.params['chat_record_id'],
                                                                 '',
                                                                 [],
                                                                 '', True, message_tokens, answer_tokens, {})

    def run_chain_async(self, current_node, node_result_future, language='zh'):
        future = executor.submit(self.run_chain_manage, current_node, node_result_future, language)
        self.future_list.append(future)

    def run_chain_manage(self, current_node, node_result_future, language='zh'):
        translation.activate(language)
        if current_node is None:
            start_node = self.get_start_node()
            current_node = get_node(start_node.type)(start_node, self.params, self)
        self.node_chunk_manage.add_node_chunk(current_node.node_chunk)
        # 添加节点
        self.append_node(current_node)
        result = self.run_chain(current_node, node_result_future)
        if result is None:
            return
        node_list = self.get_next_node_list(current_node, result)
        if len(node_list) == 1:
            self.run_chain_manage(node_list[0], None, language)
        elif len(node_list) > 1:
            sorted_node_run_list = sorted(node_list, key=lambda n: n.node.y)
            # 获取到可执行的子节点
            result_list = [{'node': node, 'future': executor.submit(self.run_chain_manage, node, None, language)} for
                           node in
                           sorted_node_run_list]
            for r in result_list:
                self.future_list.append(r.get('future'))

    def run_chain(self, current_node, node_result_future=None):
        if node_result_future is None:
            node_result_future = self.run_node_future(current_node)
        try:
            is_stream = self.params.get('stream', True)
            result = self.hand_event_node_result(current_node,
                                                 node_result_future) if is_stream else self.hand_node_result(
                current_node, node_result_future)
            return result
        except Exception as e:
            traceback.print_exc()
        return None

    def hand_node_result(self, current_node, node_result_future):
        try:
            current_result = node_result_future.result()
            result = current_result.write_context(current_node, self)
            if result is not None:
                # 阻塞获取结果
                list(result)
            return current_result
        except Exception as e:
            traceback.print_exc()
            self.status = 500
            current_node.get_write_error_context(e)
            self.answer += str(e)
        finally:
            current_node.node_chunk.end()

    def append_node(self, current_node):
        for index in range(len(self.node_context)):
            n = self.node_context[index]
            if current_node.id == n.node.id and current_node.runtime_node_id == n.runtime_node_id:
                self.node_context[index] = current_node
                return
        self.node_context.append(current_node)

    def hand_event_node_result(self, current_node, node_result_future):
        runtime_node_id = current_node.runtime_node_id
        real_node_id = current_node.runtime_node_id
        child_node = {}
        view_type = current_node.view_type
        try:
            current_result = node_result_future.result()
            result = current_result.write_context(current_node, self)
            if result is not None:
                if self.is_result(current_node, current_result):
                    for r in result:
                        reasoning_content = ''
                        content = r
                        child_node = {}
                        node_is_end = False
                        view_type = current_node.view_type
                        if isinstance(r, dict):
                            content = r.get('content')
                            child_node = {'runtime_node_id': r.get('runtime_node_id'),
                                          'chat_record_id': r.get('chat_record_id')
                                , 'child_node': r.get('child_node')}
                            if r.__contains__('real_node_id'):
                                real_node_id = r.get('real_node_id')
                            if r.__contains__('node_is_end'):
                                node_is_end = r.get('node_is_end')
                            view_type = r.get('view_type')
                            reasoning_content = r.get('reasoning_content')
                        chunk = self.base_to_response.to_stream_chunk_response(self.params['chat_id'],
                                                                               self.params['chat_record_id'],
                                                                               current_node.id,
                                                                               current_node.up_node_id_list,
                                                                               content, False, 0, 0,
                                                                               {'node_type': current_node.type,
                                                                                'runtime_node_id': runtime_node_id,
                                                                                'view_type': view_type,
                                                                                'child_node': child_node,
                                                                                'node_is_end': node_is_end,
                                                                                'real_node_id': real_node_id,
                                                                                'reasoning_content': reasoning_content})
                        current_node.node_chunk.add_chunk(chunk)
                    chunk = (self.base_to_response
                             .to_stream_chunk_response(self.params['chat_id'],
                                                       self.params['chat_record_id'],
                                                       current_node.id,
                                                       current_node.up_node_id_list,
                                                       '', False, 0, 0, {'node_is_end': True,
                                                                         'runtime_node_id': runtime_node_id,
                                                                         'node_type': current_node.type,
                                                                         'view_type': view_type,
                                                                         'child_node': child_node,
                                                                         'real_node_id': real_node_id,
                                                                         'reasoning_content': ''}))
                    current_node.node_chunk.add_chunk(chunk)
                else:
                    list(result)
            return current_result
        except Exception as e:
            # 添加节点
            traceback.print_exc()
            chunk = self.base_to_response.to_stream_chunk_response(self.params['chat_id'],
                                                                   self.params['chat_record_id'],
                                                                   current_node.id,
                                                                   current_node.up_node_id_list,
                                                                   'Exception:' + str(e), False, 0, 0,
                                                                   {'node_is_end': True,
                                                                    'runtime_node_id': current_node.runtime_node_id,
                                                                    'node_type': current_node.type,
                                                                    'view_type': current_node.view_type,
                                                                    'child_node': {},
                                                                    'real_node_id': real_node_id})
            current_node.node_chunk.add_chunk(chunk)
            current_node.get_write_error_context(e)
            self.status = 500
            return None
        finally:
            current_node.node_chunk.end()

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
            if self.chat_record is not None and self.chat_record.details is not None:
                details = self.chat_record.details.get(node.runtime_node_id)
                if details is not None and self.start_node.runtime_node_id != node.runtime_node_id:
                    details_result[node.runtime_node_id] = details
                    continue
            details = node.get_details(index)
            details['node_id'] = node.id
            details['up_node_id_list'] = node.up_node_id_list
            details['runtime_node_id'] = node.runtime_node_id
            details_result[node.runtime_node_id] = details
        return details_result

    def get_answer_text_list(self):
        result = []
        answer_list = reduce(lambda x, y: [*x, *y],
                             [n.get_answer_list() for n in self.node_context if n.get_answer_list() is not None],
                             [])
        up_node = None
        for index in range(len(answer_list)):
            current_answer = answer_list[index]
            if len(current_answer.content) > 0:
                if up_node is None or current_answer.view_type == 'single_view' or (
                        current_answer.view_type == 'many_view' and up_node.view_type == 'single_view'):
                    result.append([current_answer])
                else:
                    if len(result) > 0:
                        exec_index = len(result) - 1
                        if isinstance(result[exec_index], list):
                            result[exec_index].append(current_answer)
                    else:
                        result.insert(0, [current_answer])
                up_node = current_answer
        if len(result) == 0:
            # 如果没有响应 就响应一个空数据
            return [[]]
        return [[item.to_dict() for item in r] for r in result]

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

    @staticmethod
    def dependent_node(up_node_id, node):
        if not node.node_chunk.is_end():
            return False
        if node.id == up_node_id:
            if node.type == 'form-node':
                if node.context.get('form_data', None) is not None:
                    return True
                return False
            return True

    def dependent_node_been_executed(self, node_id):
        """
        判断依赖节点是否都已执行
        @param node_id: 需要判断的节点id
        @return:
        """
        up_node_id_list = [edge.sourceNodeId for edge in self.flow.edges if edge.targetNodeId == node_id]
        return all([any([self.dependent_node(up_node_id, node) for node in self.node_context]) for up_node_id in
                    up_node_id_list])

    def get_up_node_id_list(self, node_id):
        up_node_id_list = [edge.sourceNodeId for edge in self.flow.edges if edge.targetNodeId == node_id]
        return up_node_id_list

    def get_next_node_list(self, current_node, current_node_result):
        """
        获取下一个可执行节点列表
        @param current_node:         当前可执行节点
        @param current_node_result:  当前可执行节点结果
        @return:  可执行节点列表
        """
        # 判断是否中断执行
        if current_node_result.is_interrupt_exec(current_node):
            return []
        node_list = []
        if current_node_result is not None and current_node_result.is_assertion_result():
            for edge in self.flow.edges:
                if (edge.sourceNodeId == current_node.id and
                        f"{edge.sourceNodeId}_{current_node_result.node_variable.get('branch_id')}_right" == edge.sourceAnchorId):
                    next_node = [node for node in self.flow.nodes if node.id == edge.targetNodeId]
                    if len(next_node) == 0:
                        continue
                    if next_node[0].properties.get('condition', "AND") == 'AND':
                        if self.dependent_node_been_executed(edge.targetNodeId):
                            node_list.append(
                                self.get_node_cls_by_id(edge.targetNodeId,
                                                        [*current_node.up_node_id_list, current_node.node.id]))
                    else:
                        node_list.append(
                            self.get_node_cls_by_id(edge.targetNodeId,
                                                    [*current_node.up_node_id_list, current_node.node.id]))
        else:
            for edge in self.flow.edges:
                if edge.sourceNodeId == current_node.id:
                    next_node = [node for node in self.flow.nodes if node.id == edge.targetNodeId]
                    if len(next_node) == 0:
                        continue
                    if next_node[0].properties.get('condition', "AND") == 'AND':
                        if self.dependent_node_been_executed(edge.targetNodeId):
                            node_list.append(
                                self.get_node_cls_by_id(edge.targetNodeId,
                                                        [*current_node.up_node_id_list, current_node.node.id]))
                    else:
                        node_list.append(
                            self.get_node_cls_by_id(edge.targetNodeId,
                                                    [*current_node.up_node_id_list, current_node.node.id]))
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

    def get_workflow_content(self):
        context = {
            'global': self.context,
        }

        for node in self.node_context:
            context[node.id] = node.context
        return context

    def reset_prompt(self, prompt: str):
        placeholder = "{}"
        for field in self.field_list:
            globeLabel = f"{field.get('node_name')}.{field.get('value')}"
            globeValue = f"context.get('{field.get('node_id')}',{placeholder}).get('{field.get('value', '')}','')"
            prompt = prompt.replace(globeLabel, globeValue)
        for field in self.global_field_list:
            globeLabel = f"全局变量.{field.get('value')}"
            globeLabelNew = f"global.{field.get('value')}"
            globeValue = f"context.get('global').get('{field.get('value', '')}','')"
            prompt = prompt.replace(globeLabel, globeValue).replace(globeLabelNew, globeValue)
        return prompt

    def generate_prompt(self, prompt: str):
        """
        格式化生成提示词
        @param prompt: 提示词信息
        @return: 格式化后的提示词
        """
        context = self.get_workflow_content()
        prompt = self.reset_prompt(prompt)
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

    def get_node_cls_by_id(self, node_id, up_node_id_list=None,
                           get_node_params=lambda node: node.properties.get('node_data')):
        for node in self.flow.nodes:
            if node.id == node_id:
                node_instance = get_node(node.type)(node,
                                                    self.params, self, up_node_id_list, get_node_params)
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
