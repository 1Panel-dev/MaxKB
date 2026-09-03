# coding=utf-8
"""
@project: MaxKB
@Author:  虎虎虎
@file:    tool_workflow_lib_node.py
@date:    2026/9/3 17:20
@desc:
"""

import uuid_utils.compat as uuid
from django.db import connection
from django.db.models import QuerySet
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.workflow.common import WorkflowType, new_instance
from application.workflow.i_node import INode, Signal
from application.workflow.message.struct.content import Position
from application.workflow.status import Status
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.exception.app_exception import ChatException
from common.field.common import ObjectField
from tools.models import Tool, ToolType, ToolWorkflowVersion


class InputField(serializers.Serializer):
    field = serializers.CharField(required=True, label=_("Variable Name"))
    label = serializers.CharField(required=True, label=_("Variable Label"))
    source = serializers.CharField(required=True, label=_("Variable Source"))
    type = serializers.CharField(required=True, label=_("Variable Type"))
    value = ObjectField(required=True, label=_("Variable Value"), model_type_list=[str, list, bool, dict, int, float])


class ToolWorkflowLibNodeSerializer(serializers.Serializer):
    tool_lib_id = serializers.UUIDField(required=True, label=_("Library ID"))
    input_field_list = InputField(required=True, many=True)
    is_result = serializers.BooleanField(required=False, label=_("Whether to return content"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        f_lib = QuerySet(Tool).filter(id=self.data.get("tool_lib_id"), tool_type=ToolType.WORKFLOW).first()
        # 归还链接到连接池
        connection.close()
        if f_lib is None:
            raise Exception(_("The function has been deleted"))


def valid_function(tool_lib, workspace_id):
    if tool_lib is None:
        raise Exception(gettext("Tool does not exist"))
    get_authorized_tool = DatabaseModelManage.get_model("get_authorized_tool")
    if tool_lib and tool_lib.workspace_id != workspace_id and get_authorized_tool is not None:
        tool_lib = get_authorized_tool(QuerySet(Tool).filter(id=tool_lib.id), workspace_id).first()
    if tool_lib is None:
        raise Exception(gettext("Tool does not exist"))
    if not tool_lib.is_active:
        raise Exception(gettext("Tool is not active"))


def _sum_tokens(context, key):
    total = 0
    for node_context in (context or {}).values():
        if isinstance(node_context, dict) and isinstance(node_context.get(key), (int, float)):
            total += node_context.get(key)
    return total


class ToolWorkflowLibNode(INode):
    serializer_class = ToolWorkflowLibNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = "tool-workflow-lib-node"

    def _run(self):
        # 完成时机由子工作流的 on_complete 回调驱动，这里不自动 complete
        self.execute()

    def execute(self):
        node_params = self.get_parameters()
        workflow_params = self.get_workflow_parameters()
        tool_lib_id = node_params.get("tool_lib_id")
        input_field_list = node_params.get("input_field_list", [])
        workspace_id = workflow_params.get("workspace_id")

        tool_workflow_version = (
            QuerySet(ToolWorkflowVersion).filter(tool_id=tool_lib_id).order_by("-create_time")[0:1].first()
        )
        if tool_workflow_version is None:
            raise ChatException(500, _("The tool has not been published. Please use it after publishing."))
        tool_lib = QuerySet(Tool).filter(id=tool_lib_id).first()
        valid_function(tool_lib, workspace_id)

        parameters = self._resolve_parameters(input_field_list)
        # 入参映射属于调试数据，不需要给下游引用
        self.data["params"] = parameters

        sub_workflow = new_instance(tool_workflow_version.work_flow, WorkflowType.TOOL)
        tool_record_id = str(uuid.uuid7())
        sub_parameters = {
            "chat_record_id": tool_record_id,
            "tool_id": str(tool_lib_id),
            "stream": True,
            "workspace_id": workspace_id,
            **parameters,
        }

        node_id = self.get_node_id()

        def on_next(wf_manage, content):
            # 把子工作流的输出位置嵌套到当前节点下，再转发给父工作流
            content.position = Position(node_id, None, content.position)
            self.write(content)

        def on_complete(wf_manage, error):
            # 收集工具工作流输出（tool-start-node 初始化、变量赋值节点覆写）
            output = dict(wf_manage.context.get("output", {}) or {})
            # 只有需要给下游引用的数据才写 context：各输出字段
            for key, value in output.items():
                self.write_context(key, value)
            # 调试/详情数据放 self.data，不进可引用 context（run_time 由基类 complete 写入）
            self.data["output"] = output
            self.data["details"] = wf_manage.get_details()
            self.data["message_tokens"] = _sum_tokens(wf_manage.context, "message_tokens")
            self.data["answer_tokens"] = _sum_tokens(wf_manage.context, "answer_tokens")

            if error:
                self.complete(Status.FAIL, error=error)
                return
            # 子工作流命中表单：向上传播中断，暂停父工作流
            if wf_manage.signal == Signal.FORM:
                self.complete(Status.SUCCESS, signal=Signal.FORM)
                return
            self.complete(Status.SUCCESS)

        from application.workflow.nodes import get_node_class
        from application.workflow.workflow_manage import CallBack, WorkflowManage

        call_back = CallBack(on_next, on_complete)

        def get_start_node_fn(wf, wm):
            start_node = wf.get_node("tool-start-node")
            node_class = get_node_class("tool-start-node", WorkflowType.TOOL)
            return node_class(start_node, wm, lambda n: n.properties.get("node_data", {}))

        sub_manage = WorkflowManage(
            workflow=sub_workflow,
            parameters=sub_parameters,
            workflow_type=WorkflowType.TOOL,
            call_back=call_back,
            get_start_node=get_start_node_fn,
        )
        sub_manage.start_node.workflow_manage = sub_manage
        # 子工作流的输出已在 on_next 中逐块转发给父工作流，无需按 is_result 重复输出
        sub_manage.run()

    def _resolve_parameters(self, input_field_list):
        result = {}
        for item in input_field_list:
            source = item.get("source")
            value = item.get("value")
            if source == "reference" and isinstance(value, list) and len(value) >= 2:
                value = self.workflow_manage.get_reference_field(value[0], value[1:])
            result[item.get("field")] = value
        return result

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        details.update(
            {
                "params": self.data.get("params"),
                "output": self.data.get("output"),
                "message_tokens": self.data.get("message_tokens"),
                "answer_tokens": self.data.get("answer_tokens"),
                "details": self.data.get("details"),
                "enableException": self.node.properties.get("enableException"),
            }
        )
        return details
