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

from django.db import close_old_connections, connection
from django.utils import translation
from django.utils.translation import get_language
from langchain_core.prompts import PromptTemplate
from rest_framework import status

from application.flow import tools
from application.flow.common import Workflow
from application.flow.i_step_node import INode, WorkFlowPostHandler, NodeResult
from application.flow.step_node import get_node
from common.handle.base_to_response import BaseToResponse
from common.handle.impl.response.system_to_response import SystemToResponse

executor = ThreadPoolExecutor(max_workers=200)


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
    def __init__(self, flow: Workflow, params, work_flow_post_handler: WorkFlowPostHandler,
                 base_to_response: BaseToResponse = SystemToResponse(), form_data=None, image_list=None,
                 document_list=None,
                 audio_list=None,
                 video_list=None,
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
        if video_list is None:
            video_list = []
        if other_list is None:
            other_list = []
        self.start_node_id = start_node_id
        self.start_node = None
        self.form_data = form_data
        self.image_list = image_list
        self.video_list = video_list
        self.document_list = document_list
        self.audio_list = audio_list
        self.other_list = other_list
        self.params = params
        self.flow = flow
        self.context = {}
        self.chat_context = {}
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
        self.chat_field_list = []
        self.init_fields()
        if start_node_id is not None:
            self.load_node(chat_record, start_node_id, start_node_data)
        else:
            self.node_context = []

    def init_fields(self):
        field_list = []
        global_field_list = []
        chat_field_list = []
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
                chat_fields = node_config.get('chatFields')
                if chat_fields is not None:
                    for chat_field in chat_fields:
                        chat_field_list.append({**chat_field, 'node_id': node_id, 'node_name': node_name})
        field_list.sort(key=lambda f: len(f.get('node_name') + f.get('value')), reverse=True)
        global_field_list.sort(key=lambda f: len(f.get('node_name') + f.get('value')), reverse=True)
        chat_field_list.sort(key=lambda f: len(f.get('node_name') + f.get('value')), reverse=True)
        self.field_list = field_list
        self.global_field_list = global_field_list
        self.chat_field_list = chat_field_list

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
                    if n.type == 'loop-node':
                        is_result = True
                    return {**n.properties.get('node_data'), 'form_data': start_node_data, 'node_data': start_node_data,
                            'child_node': self.child_node, 'is_result': is_result}

                self.start_node = self.get_node_cls_by_id(node_id, node_details.get('up_node_id_list'),
                                                          get_node_params=get_node_params)
                self.start_node.valid_args(
                    {**self.start_node.node_params, 'form_data': start_node_data}, self.start_node.workflow_params)
                if self.start_node.type == 'loop-node':
                    loop_node_data = node_details.get('loop_node_data', {})
                    for k, v in node_details.get('loop_context_data').items():
                        if v is not None:
                            self.start_node.context[k] = v
                    self.start_node.context['loop_node_data'] = loop_node_data
                    self.start_node.context['current_index'] = node_details.get('current_index')
                    self.start_node.context['current_item'] = node_details.get('current_item')
                    self.start_node.context['loop_answer_data'] = node_details.get('loop_answer_data', {})
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
        self.work_flow_post_handler.handler(self)
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

    def get_body(self):
        return self.params

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
            self.work_flow_post_handler.handler(self)
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
                        node_type = current_node.type
                        if isinstance(r, dict):
                            content = r.get('content')
                            child_node = {'runtime_node_id': r.get('runtime_node_id'),
                                          'chat_record_id': r.get('chat_record_id')
                                , 'child_node': r.get('child_node')}
                            if r.__contains__('real_node_id'):
                                real_node_id = r.get('real_node_id')
                            if r.__contains__('node_is_end'):
                                node_is_end = r.get('node_is_end')
                            if r.__contains__('node_type'):
                                node_type = r.get("node_type")
                            view_type = r.get('view_type')
                            reasoning_content = r.get('reasoning_content')
                        chunk = self.base_to_response.to_stream_chunk_response(self.params['chat_id'],
                                                                               self.params['chat_record_id'],
                                                                               current_node.id,
                                                                               current_node.up_node_id_list,
                                                                               content, False, 0, 0,
                                                                               {'node_type': node_type,
                                                                                'runtime_node_id': runtime_node_id,
                                                                                'view_type': view_type,
                                                                                'child_node': child_node,
                                                                                'node_is_end': node_is_end,
                                                                                'real_node_id': real_node_id,
                                                                                'reasoning_content': reasoning_content,
                                                                                'node_status': "SUCCESS"})
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
                                                                         'reasoning_content': '',
                                                                         'node_status': "SUCCESS"}))
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
                                                                    'real_node_id': real_node_id,
                                                                    'node_status': 'ERROR'})
            current_node.node_chunk.add_chunk(chunk)
            current_node.get_write_error_context(e)
            self.status = 500
            return None
        finally:
            current_node.node_chunk.end()
            # 归还链接到连接池
            connection.close()

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

    def get_chat_info(self):
        return self.work_flow_post_handler.chat_info

    def get_chunk_content(self, chunk, is_end=False):
        return 'data: ' + json.dumps(
            {'chat_id': self.params['chat_id'], 'id': self.params['chat_record_id'], 'operate': True,
             'content': chunk, 'is_end': is_end}, ensure_ascii=False) + "\n\n"

    def _has_next_node(self, current_node, node_result: NodeResult | None):
        """
        是否有下一个可运行的节点
        """
        next_edge_node_list = self.flow.get_next_edge_nodes(current_node.id) or []
        for next_edge_node in next_edge_node_list:
            if node_result is not None and node_result.is_assertion_result():
                edge = next_edge_node.edge
                if (edge.sourceNodeId == current_node.id and
                        f"{edge.sourceNodeId}_{node_result.node_variable.get('branch_id')}_right" == edge.sourceAnchorId):
                    return True
        return len(next_edge_node_list) > 0

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

    def get_record_answer_list(self):
        answer_text_list = self.get_answer_text_list()
        return reduce(lambda pre, _n: [*pre, *_n], answer_text_list, [])

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

    @staticmethod
    def dependent_node(edge, node):
        up_node_id = edge.sourceNodeId
        if not node.node_chunk.is_end():
            return False
        if node.id == up_node_id:
            if node.context.get('branch_id', None):
                if edge.sourceAnchorId == f"{node.id}_{node.context.get('branch_id', None)}_right":
                    return True
                else:
                    return False
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
        up_edge_list = [edge for edge in self.flow.edges if edge.targetNodeId == node_id]
        return all(
            [any([self.dependent_node(edge, node) for node in self.node_context if node.id == edge.sourceNodeId]) for
             edge in
             up_edge_list])

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
        next_edge_node_list = self.flow.get_next_edge_nodes(current_node.id) or []
        if current_node_result is not None and current_node_result.is_assertion_result():
            for edge_node in next_edge_node_list:
                edge = edge_node.edge
                next_node = edge_node.node
                if (
                        f"{edge.sourceNodeId}_{current_node_result.node_variable.get('branch_id')}_right" == edge.sourceAnchorId):
                    if next_node.properties.get('condition', "AND") == 'AND':
                        if self.dependent_node_been_executed(edge.targetNodeId):
                            node_list.append(
                                self.get_node_cls_by_id(edge.targetNodeId,
                                                        [*current_node.up_node_id_list, current_node.node.id]))
                    else:
                        node_list.append(
                            self.get_node_cls_by_id(edge.targetNodeId,
                                                    [*current_node.up_node_id_list, current_node.node.id]))
        else:
            for edge_node in next_edge_node_list:
                edge = edge_node.edge
                next_node = edge_node.node
                if next_node.properties.get('condition', "AND") == 'AND':
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
        elif node_id == 'chat':
            return INode.get_field(self.chat_context, fields)
        else:
            node = self.get_node_by_id(node_id)
            if node:
                return node.get_reference_field(fields)
            return None

    def get_workflow_content(self):
        context = {
            'global': self.context,
            'chat': self.chat_context
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
        for field in self.chat_field_list:
            chatLabel = f"chat.{field.get('value')}"
            chatValue = f"context.get('chat').get('{field.get('value', '')}','')"
            prompt = prompt.replace(chatLabel, chatValue)

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
