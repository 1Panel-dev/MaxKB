# coding=utf-8
"""
@project: MaxKB
@Author：虎虎
@file： workflow_tool_task.py.py
@date：2026/3/27 18:47
@desc:
"""

import threading
import time
import traceback

import uuid_utils.compat as uuid
from django.db.models import QuerySet

from application.workflow.common import WorkflowType, get_node_parameters, new_instance
from application.workflow.nodes import get_node_class
from application.workflow.status import Status
from application.workflow.workflow_manage import CallBack, WorkflowManage
from common.utils.common import common_convert_value
from common.utils.logger import maxkb_logger
from common.utils.tool_code import ToolExecutor
from knowledge.models.knowledge_action import State
from tools.models import ToolRecord, ToolTaskTypeChoices, ToolWorkflowVersion, ToolType
from trigger.handler.impl.task.tool_task.common import BaseToolTriggerTask
from trigger.models import TaskRecord

executor = ToolExecutor()


def get_reference(fields, obj):
    for field in fields:
        value = obj.get(field)
        if value is None:
            return None
        else:
            obj = value
    return obj


def get_field_value(value, kwargs):
    source = value.get("source")
    if source == "custom":
        return value.get("value")
    else:
        return get_reference(value.get("value"), kwargs)


def get_tool_execute_parameters(input_field_list, parameter_setting, kwargs):
    type_map = {f.get("name"): f.get("type") for f in (input_field_list or []) if f.get("name")}

    parameters = {}
    if parameter_setting:
        for key, value in parameter_setting.items():
            raw = get_field_value(value, kwargs)
            parameters[key] = common_convert_value(type_map.get(key), raw)
    return parameters


class ToolTask(BaseToolTriggerTask):
    def support(self, tool, trigger_task, **kwargs):
        return tool.tool_type == ToolType.WORKFLOW

    def execute(self, tool, trigger_task, **kwargs):
        parameter_setting = trigger_task.get("parameter")
        tool_id = trigger_task.get("source_id")
        task_record_id = uuid.uuid7()
        start_time = time.time()
        try:
            TaskRecord(
                id=task_record_id,
                trigger_id=trigger_task.get("trigger"),
                trigger_task_id=trigger_task.get("id"),
                source_type="TOOL",
                source_id=tool_id,
                task_record_id=task_record_id,
                meta={"input": parameter_setting, "output": {}},
                state=State.STARTED,
            ).save()
            ToolRecord(
                id=task_record_id,
                workspace_id=tool.workspace_id,
                tool_id=tool.id,
                source_type=ToolTaskTypeChoices.TRIGGER,
                source_id=trigger_task.get("trigger"),
                meta={"input": parameter_setting, "output": {}},
                state=State.STARTED,
            ).save()
            tool_workflow_version = (
                QuerySet(ToolWorkflowVersion).filter(tool_id=tool.id).order_by("-create_time")[0:1].first()
            )
            if not tool_workflow_version:
                maxkb_logger.info(f"Tool with id {tool_id} not found or inactive.")
                return
            workflow = new_instance(tool_workflow_version.work_flow, WorkflowType.TOOL)
            base_node = workflow.get_node("tool-base-node")
            user_input_field_list = base_node.properties.get("user_input_field_list") or []
            field_parameters = get_tool_execute_parameters(
                user_input_field_list, parameter_setting.get("user_input_field_list"), kwargs
            )
            # 对齐旧引擎 body:输入字段值 + 运行身份;新引擎 tool-start-node 按 field 从这里取值
            parameters = {
                "tool_id": tool_id,
                "stream": True,
                "workspace_id": tool.workspace_id,
                **field_parameters,
            }

            # 后台任务:非流式,run() 起线程异步执行,完成后经 on_complete 通知,这里阻塞等结果
            done_event = threading.Event()
            run_result = {"error": None}

            def on_next(wf_manage, content):
                pass

            def on_complete(wf_manage, error):
                run_result["error"] = error
                done_event.set()

            call_back = CallBack(on_next, on_complete)

            def get_start_node_fn(wf, wm):
                start_node = wf.get_node("tool-start-node")
                if start_node is None:
                    raise Exception("The start node does not exist")
                node_class = get_node_class(start_node.type, WorkflowType.TOOL)
                return node_class(start_node, wm, get_node_parameters)

            work_flow_manage = WorkflowManage(workflow, parameters, WorkflowType.TOOL, call_back, get_start_node_fn)
            work_flow_manage.run()
            done_event.wait()

            if run_result["error"]:
                raise run_result["error"]

            # 新引擎工具输出收口于全局 output 上下文(tool-start-node 初始化、变量赋值节点写入)
            output = work_flow_manage.context.get("output", {})
            details = work_flow_manage.get_details()
            has_fail = any((d or {}).get("status") == Status.FAIL.value for d in (details or []))
            state = State.FAILURE if has_fail else State.SUCCESS
            QuerySet(TaskRecord).filter(id=task_record_id).update(
                state=state, run_time=time.time() - start_time, meta={"input": parameter_setting, "output": output}
            )
            QuerySet(ToolRecord).filter(id=task_record_id).update(
                state=state, run_time=time.time() - start_time, meta={"input": parameter_setting, "output": output}
            )
        except Exception as e:
            maxkb_logger.error(f"Tool execution error: {traceback.format_exc()}")
            QuerySet(TaskRecord).filter(id=task_record_id).update(
                state=State.FAILURE,
                run_time=time.time() - start_time,
                meta={"input": parameter_setting, "output": "Error: " + str(e), "err_message": "Error: " + str(e)},
            )
            QuerySet(ToolRecord).filter(id=task_record_id).update(
                state=State.FAILURE,
                run_time=time.time() - start_time,
                meta={"input": parameter_setting, "output": "Error: " + str(e), "err_message": "Error: " + str(e)},
            )
