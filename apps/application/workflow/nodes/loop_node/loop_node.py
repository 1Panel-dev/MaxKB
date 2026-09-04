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
from application.workflow.i_node import INode, Signal

from application.workflow.message.struct.content import NodeInfo, Position
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
        loop_type = self.data.get("loop_type")
        if loop_type == "ARRAY":
            array = self.data.get("array")
            if array is None or len(array) == 0:
                message = _("{field}, this field is required.", field="array")
                raise AppApiException(500, message)
        elif loop_type == "NUMBER":
            number = self.data.get("number")
            if number is None:
                message = _("{field}, this field is required.", field="number")
                raise AppApiException(500, message)


def _generate_loop_number(number, start_index=0):
    return iter([(i, i) for i in range(start_index, number)])


def _generate_loop_array(array, start_index=0):
    return iter([(item, i) for i, item in enumerate(array) if i >= start_index])


def _generate_while_loop(number, start_index=0):
    return iter([(i, i) for i in range(start_index, number)])


class LoopNode(INode):
    serializer_class = LoopNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = "loop-node"

    def _run(self):
        self.execute()

    def execute(self):
        node_params = self.get_parameters()
        workflow_params = self.get_workflow_parameters()

        loop_type = node_params.get("loop_type")
        array = node_params.get("array")
        number = node_params.get("number")
        loop_body = node_params.get("loop_body")

        # 从 position 获取 start_index
        position = workflow_params.get("position") or {}
        start_index = position.get("index") or 0 if position.get("id") == self.node.id else 0

        if loop_type == "ARRAY" and isinstance(array, list) and len(array) >= 2:
            array = self.workflow_manage.get_reference_field(array[0], array[1:])

        self.write_context("params", {"loop_type": loop_type, "array": array, "number": number})

        # 根据 start_index 构建迭代器
        if loop_type == "ARRAY":
            iterator = _generate_loop_array(array, start_index=start_index)
        elif loop_type == "LOOP":
            iterator = _generate_while_loop(number or MAX_LOOP_COUNT, start_index=start_index)
        else:
            iterator = _generate_loop_number(number, start_index=start_index)

        self._loop_node_data = self.get_context("loop_node_data") or []
        self._loop_answer_data = self.get_context("loop_answer_data") or []
        self._answer_text = self.get_context("answer") or ""
        self._workflow_params = workflow_params
        self._loop_body = loop_body
        self._iterator = iterator

        self._run_next()

    def _run_next(self):
        try:
            item, index = next(self._iterator)
        except StopIteration:
            self.write_context("answer", self._answer_text)
            self.write_context("run_time", time.time() - self.data.get("start_time", time.time()))
            self.complete(Status.SUCCESS)
            return
        loop_context = {"index": index, "item": item}
        workflow = new_instance(self._loop_body, self.get_workflow_type())

        chunk_list = []

        def on_next(wf_manage, content):
            chunk_list.append(content)
            if hasattr(content, "content"):
                self._answer_text += content.content
            content.position = Position(self.get_node_id(), index, content.position)
            self.write(content)

        def on_complete(wf_manage, error):
            self._loop_node_data.append(wf_manage.context)
            self._loop_answer_data.append([c.to_dict() for c in chunk_list])
            self.write_context("loop_node_data", self._loop_node_data)
            self.write_context("loop_answer_data", self._loop_answer_data)
            self.write_context("index", index)
            self.write_context("item", item)

            if wf_manage.signal == Signal.BREAK or wf_manage.signal == Signal.FORM:
                self.write_context("answer", self._answer_text)
                self.write_context("run_time", time.time() - self.data.get("start_time", time.time()))
                self.complete(Status.SUCCESS)
                return

            if wf_manage.signal == Signal.CONTINUE:
                self._run_next()
                return

            if error:
                self.write_context("error_message", str(error))
                return

            self._run_next()

        from application.workflow.workflow_manage import CallBack
        from application.workflow.loop_workflow_manage import LoopWorkFlowManage
        from application.workflow.nodes import get_node_class

        call_back = CallBack(on_next, on_complete)

        loop_start_class = get_node_class("loop-start-node", self.get_workflow_type())

        # 获取 position，当前 index 和 position.index 一致时传入 children
        position = self._workflow_params.get("position") or {}
        child_position = None
        if position.get("id") == self.node.id and position.get("index") == index:
            child_position = position.get("children")

        def get_start_node_fn(wf, wf_manage):
            # 如果有 child_position，从指定节点开始
            if child_position and child_position.get("id"):
                node_id = child_position.get("id")
                node = wf.get_node(node_id)
                if node:
                    node_class = get_node_class(node.type, self.get_workflow_type())
                    return node_class(node, wf_manage, lambda n: n.properties.get("node_data", {}))

            # 默认从 loop-start-node 开始
            start_node = wf.get_node("loop-start-node")
            return loop_start_class(start_node, wf_manage, lambda n: n.properties.get("node_data", {}))

        # 构建子工作流参数，第一次迭代传入 child_position
        loop_workflow_params = dict(self._workflow_params)
        if child_position:
            loop_workflow_params["position"] = child_position
        else:
            loop_workflow_params.pop("position", None)

        loop_manage = LoopWorkFlowManage(
            workflow=workflow,
            parameters=loop_workflow_params,
            workflow_type=self.get_workflow_type(),
            call_back=call_back,
            get_start_node=get_start_node_fn,
            parent_workflow_manage=self.workflow_manage,
            loop_context=loop_context,
        )
        loop_manage.start_node.workflow_manage = loop_manage
        loop_manage.run()

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        details.update(
            {
                "params": self.get_context("params"),
                "index": self.get_context("index"),
                "item": self.get_context("item"),
                "answer": self.get_context("answer"),
            }
        )

        loop_node_data = self.get_context("loop_node_data") or []
        loop_details = []
        position_index = 0

        # 从 old_details 获取之前的迭代详情
        old_iteration_details = []
        if old_details and isinstance(old_details, dict):
            old_iteration_details = old_details.get("iteration_details", [])

        # 1. 先把 old_iteration_details 全部复制过来，记录断点位置
        if old_iteration_details and position and position.get("id") == self.node.id:
            for i, value in enumerate(old_iteration_details):
                loop_details.append(value)
                if position.get("index") == i:
                    position_index = i

        # 2. 遍历当前新执行的迭代
        for new_iter_index, iteration_context in enumerate(loop_node_data):
            iteration_result = []

            # 第一个新迭代且是断点：传入旧详情
            if new_iter_index == 0 and position and position.get("id") == self.node.id:
                # 续跑迭代：先复制旧详情
                if position_index < len(old_iteration_details):
                    for old_item in old_iteration_details[position_index]:
                        iteration_result.append(old_item)

            # 遍历当前迭代的节点 context
            child_position = (
                position.get("children")
                if new_iter_index == 0 and position and position.get("id") == self.node.id
                else None
            )
            child_position_index = 0
            for node_id, node_context in iteration_context.items():
                node_details = {
                    "node_id": node_id,
                    **node_context,
                }
                # 断点节点：插入到 child_position_index 位置
                if child_position and child_position.get("id") == node_id:
                    iteration_result.insert(child_position_index, node_details)
                else:
                    iteration_result.append(node_details)

            # 第一个新迭代且是断点：插入到 position_index，否则追加
            if new_iter_index == 0 and position and position.get("id") == self.node.id:
                loop_details.insert(position_index, iteration_result)
            else:
                loop_details.append(iteration_result)

        details["iteration_details"] = loop_details
        return details
