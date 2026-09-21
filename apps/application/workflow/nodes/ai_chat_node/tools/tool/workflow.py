# coding=utf-8
"""
@project: MaxKB
@Author:  虎虎虎
@file:    workflow.py
@date:    2026/9/15
@desc:
"""

import threading
import time

import uuid_utils.compat as uuid
from django.db.models import OuterRef, QuerySet, Subquery
from langchain_core.tools import StructuredTool
from pydantic import Field

from application.workflow.message.aggregator import AggregationManager
from application.workflow.status import Status
from knowledge.models.knowledge_action import State
from tools.models import Tool, ToolRecord, ToolType, ToolWorkflowVersion

from ..base import build_schema, get_type


def get_workflow_args(tool, qv):
    for node in qv.work_flow.get("nodes"):
        if node.get("type") == "tool-base-node":
            input_field_list = node.get("properties").get("user_input_field_list")
            return build_schema(
                {
                    field.get("field"): (
                        get_type(field.get("type")),
                        Field(..., required=True, description=field.get("desc"))
                        if field.get("is_required")
                        else Field(default=None, required=False, description=field.get("desc")),
                    )
                    for field in input_field_list
                }
            )

    return build_schema({})


def _save_workflow_tool_record(
    tool_record_id, tool_id, workspace_id, source_type, source_id, wf_manage, aggregation, parameters, start_time, error
):
    """
    工具工作流执行结束后落库执行记录（替代旧引擎 ToolWorkflowPostHandler.handler）。
    实实行（非调试）直接插入 ToolRecord，字段与工具记录查询端点保持一致。
    """
    workflow = wf_manage.workflow
    base_node = workflow.get_node("tool-base-node")
    input_field_list = base_node.properties.get("user_input_field_list", []) if base_node else []
    output_field_list = base_node.properties.get("user_output_field_list", []) if base_node else []
    input_data = {f.get("field"): parameters.get(f.get("field")) for f in input_field_list}
    # 新引擎工具输出统一收口于全局 output 上下文（tool-start-node 初始化、变量赋值节点写入）
    output = wf_manage.context.get("output", {})
    details = wf_manage.get_details()
    if error:
        state = State.FAILURE
    else:
        has_fail = any((d or {}).get("status") == Status.FAIL.value for d in (details or []))
        state = State.FAILURE if has_fail else State.SUCCESS
    ToolRecord(
        id=tool_record_id,
        tool_id=tool_id,
        workspace_id=workspace_id,
        source_type=source_type,
        source_id=source_id,
        state=state,
        run_time=time.time() - start_time,
        meta={
            "input_field_list": input_field_list,
            "output_field_list": output_field_list,
            "input": input_data,
            "output": output,
            "details": details,
            "answer_text_list": aggregation.get_contents(),
        },
    ).save()


def get_workflow_func(source_type, source_id, tool, qv, workspace_id, workflow_params=None):
    from knowledge.services.retrieval_access import inherited_retrieval_context

    tool_id = tool.id

    def inner(**kwargs):
        # 使用新工作流引擎执行工具工作流，方式与 tool_workflow_lib_node 保持一致。
        from application.workflow.common import WorkflowType, new_instance
        from application.workflow.nodes import get_node_class
        from application.workflow.workflow_manage import CallBack, WorkflowManage

        tool_record_id = str(uuid.uuid7())
        sub_workflow = new_instance(qv.work_flow, WorkflowType.TOOL)
        start_time = time.time()
        sub_parameters = {
            "chat_record_id": tool_record_id,
            "tool_id": str(tool_id),
            "stream": True,
            "workspace_id": workspace_id,
            "default_model_setting": qv.default_model_setting or {},
            **kwargs,
            **inherited_retrieval_context({"workspace_id": workspace_id, **(workflow_params or {})}),
        }

        # WorkflowManage.run() 在后台线程异步执行节点，完成时机由 on_complete 回调驱动，
        # 而 inner 作为 LangChain 同步工具函数必须阻塞到子工作流结束再返回其输出。
        aggregation = AggregationManager()
        done_event = threading.Event()
        result_holder = {"output": {}, "error": None}

        def on_next(wf_manage, content):
            # 逐块聚合，用于执行记录的 answer_text_list（不直接转发给上游）
            aggregation.aggregate(content)

        def on_complete(wf_manage, error):
            try:
                # 工具工作流输出统一写入 context['output']
                result_holder["output"] = dict(wf_manage.context.get("output", {}) or {})
                # 执行结束落库工具执行记录
                _save_workflow_tool_record(
                    tool_record_id,
                    tool_id,
                    workspace_id,
                    source_type,
                    source_id,
                    wf_manage,
                    aggregation,
                    sub_parameters,
                    start_time,
                    error,
                )
            finally:
                result_holder["error"] = error
                done_event.set()

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
        sub_manage.run()
        done_event.wait()
        if result_holder["error"]:
            raise result_holder["error"]
        return result_holder["output"]

    return inner


def get_workflow_tools(source_type, source_id, tool_workflow_ids, workspace_id, workflow_params=None):
    tools = QuerySet(Tool).filter(
        id__in=tool_workflow_ids, is_active=True, tool_type=ToolType.WORKFLOW, workspace_id=workspace_id
    )
    latest_subquery = ToolWorkflowVersion.objects.filter(tool_id=OuterRef("tool_id")).order_by("-create_time")

    qs = ToolWorkflowVersion.objects.filter(
        tool_id__in=[t.id for t in tools], id=Subquery(latest_subquery.values("id")[:1])
    )
    qd = {q.tool_id: q for q in qs}
    results = []
    for tool in tools:
        qv = qd.get(tool.id)
        func = get_workflow_func(source_type, source_id, tool, qv, workspace_id, workflow_params)
        args = get_workflow_args(tool, qv)
        tool = StructuredTool.from_function(
            func=func,
            name=tool.name,
            description=tool.desc,
            args_schema=args,
        )
        results.append(tool)

    return results
