# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： loop_node.py
    @date：2026/7/2 10:00
    @desc:
"""
import time

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.workflow.common import WorkflowType, new_instance
from application.workflow.i_node import INode

from application.workflow.message.struct.content import NodeInfo
from application.workflow.message.struct.text_content import TextContent
from application.workflow.status import Status

from common.exception.app_exception import AppApiException

MAX_LOOP_COUNT = 500


class LoopNodeSerializer(serializers.Serializer):
    loop_type = serializers.CharField(required=True, label=_("loop_type"))
    array = serializers.ListField(required=False, allow_null=True, label=_("array"))
    number = serializers.IntegerField(required=False, allow_null=True, label=_("number"))
    loop_body = serializers.DictField(required=True, label="循环体")

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        loop_type = self.data.get('loop_type')
        if loop_type == 'ARRAY':
            array = self.data.get('array')
            if array is None or len(array) == 0:
                message = _('{field}, this field is required.', field='array')
                raise AppApiException(500, message)
        elif loop_type == 'NUMBER':
            number = self.data.get('number')
            if number is None:
                message = _('{field}, this field is required.', field='number')
                raise AppApiException(500, message)


def _generate_loop_number(number):
    return iter([(i, i) for i in range(number)])


def _generate_loop_array(array):
    return iter([(item, i) for i, item in enumerate(array)])


def _generate_while_loop(number):
    return iter([(i, i) for i in range(number)])


class LoopNode(INode):
    serializer_class = LoopNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = 'loop-node'

    def _run(self):
        self.execute()

    def execute(self):
        node_params = self.get_parameters()
        workflow_params = self.get_workflow_parameters()

        loop_type = node_params.get('loop_type')
        array = node_params.get('array')
        number = node_params.get('number')
        loop_body = node_params.get('loop_body')

        if loop_type == 'ARRAY' and isinstance(array, list) and len(array) >= 2:
            array = self.workflow_manage.get_reference_field(array[0], array[1:])

        self.write_context('params', {'loop_type': loop_type, 'array': array, 'number': number})

        if loop_type == 'ARRAY':
            iterator = _generate_loop_array(array)
        elif loop_type == 'LOOP':
            iterator = _generate_while_loop(number or MAX_LOOP_COUNT)
        else:
            iterator = _generate_loop_number(number)

        self._loop_node_data = []
        self._loop_answer_data = []
        self._answer_text = ''
        self._workflow_params = workflow_params
        self._loop_body = loop_body
        self._iterator = iterator

        self._run_next()

    def _run_next(self):
        try:
            item, index = next(self._iterator)
        except StopIteration:
            self.write_context('answer', self._answer_text)
            self.write_context('run_time', time.time() - self.data.get('start_time', time.time()))
            self.complete(Status.SUCCESS)
            return
        loop_context = {'index': index, 'item': item}
        workflow = new_instance(self._loop_body, self.get_workflow_type())

        chunk_list = []

        def on_next(wf_manage, content):
            chunk_list.append(content)
            if hasattr(content, 'content'):
                self._answer_text += content.content
                self.write(content)

        def on_complete(wf_manage, error):
            self._loop_node_data.append(wf_manage.context)
            self._loop_answer_data.append(chunk_list)
            self.write_context('loop_node_data', self._loop_node_data)
            self.write_context('loop_answer_data', self._loop_answer_data)
            self.write_context('index', index)
            self.write_context('item', item)

            if error:
                self.write_context('error_message', str(error))
                return

            self._run_next()

        from application.workflow.workflow_manage import CallBack
        from application.workflow.loop_workflow_manage import LoopWorkFlowManage
        from application.workflow.nodes import get_node_class
        call_back = CallBack(on_next, on_complete)

        loop_start_class = get_node_class('loop-start-node', self.get_workflow_type())

        def get_start_node_fn(wf, wf_manage):
            start_node = wf.get_node('loop-start-node')
            return loop_start_class(start_node, wf_manage, lambda n: n.properties.get('node_data', {}))

        loop_manage = LoopWorkFlowManage(
            workflow=workflow,
            parameters=self._workflow_params,
            workflow_type=self.get_workflow_type(),
            call_back=call_back,
            get_start_node=get_start_node_fn,
            parent_workflow_manage=self.workflow_manage,
            loop_context=loop_context,
        )
        loop_manage.start_node.workflow_manage = loop_manage
        loop_manage.run()
