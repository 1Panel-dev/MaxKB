# coding=utf-8
"""
@project: MaxKB
@Author:  虎虎虎
@file:    custom.py
@date:    2026/9/15
@desc:
"""

import json
import time

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from langchain_core.tools import StructuredTool
from pydantic import Field

from knowledge.models.knowledge_action import State
from tools.models import Tool, ToolRecord, ToolType

from ..base import build_schema, get_type


def get_custom_args(tool):
    """
    从 CUSTOM 工具的 input_field_list 显式构建给模型的 args_schema。

    input_field_list 项结构：{name, is_required, type(string|int|dict|array|float), source}
    """
    input_field_list = tool.input_field_list or []
    return build_schema(
        {
            field.get("name"): (
                get_type(field.get("type")),
                Field(..., required=True, description=field.get("desc"))
                if field.get("is_required")
                else Field(default=None, required=False, description=field.get("desc")),
            )
            for field in input_field_list
        }
    )


def _save_custom_tool_record(tool_id, workspace_id, source_type, source_id, input_params, output, start_time, error):
    """
    CUSTOM 工具执行结束后落库执行记录（替代原 MCP 路径的 save_tool_record）。

    input 仅记录业务入参（不含 init 参数），避免密文/密钥进入记录。
    """
    state = State.FAILURE if error else State.SUCCESS
    ToolRecord(
        id=uuid.uuid7(),
        tool_id=tool_id,
        workspace_id=workspace_id,
        source_type=source_type,
        source_id=source_id,
        state=state,
        run_time=time.time() - start_time,
        meta={
            "input": input_params,
            "output": str(error) if error else output,
        },
    ).save()


def get_custom_func(source_type, source_id, tool, workspace_id):
    tool_id = tool.id
    code = tool.code
    init_field_list = tool.init_field_list or []
    init_params_ciphertext = tool.init_params

    def inner(**kwargs):
        # 在进程内直接跑沙箱代码（无 MCP 子进程），方式与工具调试执行 ToolExecutor.exec_code 一致。
        from common.utils.rsa_util import rsa_long_decrypt
        from common.utils.tool_code import ToolExecutor

        start_time = time.time()
        # 合并初始化参数（默认值 → 已保存的启动参数），服务端注入，模型不可见
        init_params_default_value = {i["field"]: i.get("default_value") for i in init_field_list}
        if init_params_ciphertext is not None:
            init_params = init_params_default_value | json.loads(rsa_long_decrypt(init_params_ciphertext))
        else:
            init_params = init_params_default_value
        all_params = init_params | kwargs

        error = None
        result = None
        try:
            result = ToolExecutor().exec_code(code, all_params)
        except Exception as e:
            error = e
        finally:
            _save_custom_tool_record(tool_id, workspace_id, source_type, source_id, kwargs, result, start_time, error)
        if error:
            raise error
        return result

    return inner


def get_custom_tools(source_type, source_id, tool_ids, workspace_id):
    if not tool_ids:
        return []
    tools = QuerySet(Tool).filter(id__in=tool_ids, is_active=True, tool_type=ToolType.CUSTOM)
    results = []
    for tool in tools:
        func = get_custom_func(source_type, source_id, tool, workspace_id)
        args = get_custom_args(tool)
        structured_tool = StructuredTool.from_function(
            func=func,
            name=tool.name,
            description=tool.desc,
            args_schema=args,
        )
        results.append(structured_tool)

    return results
