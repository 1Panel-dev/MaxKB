# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： Knowledge_workflow_manage.py
    @date：2025/11/13 19:02
    @desc:
"""
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

from django.db.models import QuerySet
from django.utils.translation import get_language

from application.flow.common import Workflow
from application.flow.i_step_node import WorkFlowPostHandler, KnowledgeFlowParamsSerializer
from application.flow.workflow_manage import WorkflowManage
from common.handle.base_to_response import BaseToResponse
from common.handle.impl.response.system_to_response import SystemToResponse
from knowledge.models.knowledge_action import KnowledgeAction, State

executor = ThreadPoolExecutor(max_workers=200)


class KnowledgeWorkflowManage(WorkflowManage):

    def __init__(self, flow: Workflow,
                 params,
                 work_flow_post_handler: WorkFlowPostHandler,
                 base_to_response: BaseToResponse = SystemToResponse(),
                 start_node_id=None,
                 start_node_data=None, chat_record=None, child_node=None, is_the_task_interrupted=lambda: False):
        super().__init__(flow, params, work_flow_post_handler, base_to_response, None, None, None,
                         None,
                         None, None, start_node_id, start_node_data, chat_record, child_node, is_the_task_interrupted)

    def get_params_serializer_class(self):
        return KnowledgeFlowParamsSerializer

    def get_start_node(self):
        start_node_list = [node for node in self.flow.nodes if
                           self.params.get('data_source', {}).get('node_id') == node.id]
        return start_node_list[0]

    def run(self):
        self.context['start_time'] = time.time()
        executor.submit(self._run)

    def _run(self):
        QuerySet(KnowledgeAction).filter(id=self.params.get('knowledge_action_id')).update(
            state=State.STARTED)
        language = get_language()
        self.run_chain_async(self.start_node, None, language)
        while self.is_run():
            pass
        self.work_flow_post_handler.handler(self)

    @staticmethod
    def get_node_details(current_node, node, index):
        if current_node == node:
            return {
                'name': node.node.properties.get('stepName'),
                "index": index,
                'run_time': 0,
                'type': node.type,
                'status': 202,
                'err_message': ""
            }

        return node.get_details(index)

    def run_chain(self, current_node, node_result_future=None):
        QuerySet(KnowledgeAction).filter(id=self.params.get('knowledge_action_id')).update(
            details=self.get_runtime_details(lambda node, index: self.get_node_details(current_node, node, index)))
        if node_result_future is None:
            node_result_future = self.run_node_future(current_node)
        try:
            result = self.hand_node_result(current_node, node_result_future)
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
            if current_node.status == 500:
                return None
            if self.is_the_task_interrupted():
                current_node.status = 201
                return None
            return current_result
        except Exception as e:
            traceback.print_exc()
            self.status = 500
            current_node.get_write_error_context(e)
            self.answer += str(e)
            QuerySet(KnowledgeAction).filter(id=self.params.get('knowledge_action_id')).update(state=State.FAILURE)
        finally:
            current_node.node_chunk.end()
            QuerySet(KnowledgeAction).filter(id=self.params.get('knowledge_action_id')).update(
                details=self.get_runtime_details())
