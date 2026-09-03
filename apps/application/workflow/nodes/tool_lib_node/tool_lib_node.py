# coding=utf-8
"""
@project: MaxKB
@Author：虎
@file： tool_lib_node.py
@date：2026/9/3 16:21
@desc:
"""

import base64
import io
import json
import mimetypes
import traceback

import uuid_utils.compat as uuid
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import connection
from django.db.models import QuerySet
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode
from application.workflow.message.struct.content import NodeInfo, Position
from application.workflow.message.struct.text_content import TextContent
from application.workflow.status import Status
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.exception.app_exception import AppApiException
from common.field.common import ObjectField
from common.utils.common import common_convert_value
from common.utils.logger import maxkb_logger
from common.utils.rsa_util import rsa_long_decrypt
from common.utils.tool_code import ToolExecutor
from knowledge.models import FileSourceType
from knowledge.models.knowledge_action import State
from oss.serializers.file import FileSerializer
from tools.models import Tool, ToolRecord, ToolTaskTypeChoices

function_executor = ToolExecutor()


class InputField(serializers.Serializer):
    name = serializers.CharField(required=True, label=_("Variable Name"))
    value = ObjectField(required=True, label=_("Variable Value"), model_type_list=[str, list])


class ToolLibNodeSerializer(serializers.Serializer):
    tool_lib_id = serializers.UUIDField(required=True, label=_("Library ID"))
    input_field_list = InputField(required=True, many=True)
    is_result = serializers.BooleanField(required=False, label=_("Whether to return content"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        f_lib = QuerySet(Tool).filter(id=self.data.get("tool_lib_id")).first()
        # 归还链接到连接池
        connection.close()
        if f_lib is None:
            raise Exception(_("The function has been deleted"))


def get_field_value(debug_field_list, name, is_required):
    result = [field for field in debug_field_list if field.get("name") == name]
    if len(result) > 0:
        return result[-1]["value"]
    if is_required:
        raise AppApiException(500, gettext("Field: {name} No value set").format(name=name))
    return None


def valid_reference_value(_type, value, name):
    if _type == "int":
        instance_type = int | float
    elif _type == "boolean":
        instance_type = bool
    elif _type == "float":
        instance_type = float | int
    elif _type == "dict":
        value = json.loads(value) if isinstance(value, str) else value
        instance_type = dict
    elif _type == "array":
        value = json.loads(value) if isinstance(value, str) else value
        instance_type = list
    elif _type == "string":
        instance_type = str
    else:
        maxkb_logger.error(
            gettext("Field: {name} Type: {_type} Value: {value} Unsupported this type").format(
                name=name, _type=_type, value=value
            )
        )
        return value
    if not isinstance(value, instance_type):
        raise Exception(
            gettext("Field: {name} Type: {_type} Value: {value} Type error").format(name=name, _type=_type, value=value)
        )
    return value


def convert_value(name: str, value, _type, is_required, source, node):
    if not is_required and (value is None or ((isinstance(value, str) or isinstance(value, list)) and len(value) == 0)):
        return None
    if source == "reference":
        value = node.workflow_manage.get_reference_field(value[0], value[1:])
        if value is None:
            if not is_required:
                return None
            else:
                raise Exception(gettext("Field: {name} Type: {_type} is required").format(name=name, _type=_type))
        value = valid_reference_value(_type, value, name)
        if _type == "int":
            return int(value)
        if _type == "float":
            return float(value)
        return value
    try:
        value = node.workflow_manage.generate_prompt(value)
        return common_convert_value(_type, value)
    except Exception:
        raise Exception(
            gettext("Field: {name} Type: {_type} Value: {value} Type error").format(name=name, _type=_type, value=value)
        )


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


def _filter_file_bytes(data):
    """递归过滤掉所有层级的 file_bytes"""
    if isinstance(data, dict):
        return {k: _filter_file_bytes(v) for k, v in data.items() if k != "file_bytes"}
    elif isinstance(data, list):
        return [_filter_file_bytes(item) for item in data]
    else:
        return data


def bytes_to_uploaded_file(file_bytes, file_name="unknown"):
    content_type, _ = mimetypes.guess_type(file_name)
    if content_type is None:
        # 如果未能识别，设置为默认的二进制文件类型
        content_type = "application/octet-stream"
    # 创建一个内存中的字节流对象
    file_stream = io.BytesIO(file_bytes)

    # 获取文件大小
    file_size = len(file_bytes)

    uploaded_file = InMemoryUploadedFile(
        file=file_stream,
        field_name=None,
        name=file_name,
        content_type=content_type,
        size=file_size,
        charset=None,
    )
    return uploaded_file


def _get_result_detail(result):
    if isinstance(result, dict):
        result_dict = {k: (str(v)[:500] if len(str(v)) > 500 else v) for k, v in result.items()}
    elif isinstance(result, list):
        result_dict = [str(item)[:500] if len(str(item)) > 500 else item for item in result]
    elif isinstance(result, str):
        result_dict = result[:500] if len(result) > 500 else result
    else:
        result_dict = result
    return result_dict


class ToolLibNode(INode):
    serializer_class = ToolLibNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = "tool-lib-node"

    def execute(self):
        node_params = self.get_parameters()
        workflow_params = self.get_workflow_parameters()
        tool_lib_id = node_params.get("tool_lib_id")
        input_field_list = node_params.get("input_field_list", [])
        is_result = node_params.get("is_result", False)

        workspace_id = workflow_params.get("workspace_id")
        tool_lib = QuerySet(Tool).filter(id=tool_lib_id).first()
        valid_function(tool_lib, workspace_id)
        params = {
            field.get("name"): convert_value(
                field.get("name"),
                field.get("value"),
                field.get("type"),
                field.get("is_required"),
                field.get("source"),
                self,
            )
            for field in [
                {"value": get_field_value(input_field_list, field.get("name"), field.get("is_required")), **field}
                for field in tool_lib.input_field_list
            ]
        }

        self.write_context("params", params)
        # 合并初始化参数
        init_params_default_value = {i["field"]: i.get("default_value") for i in tool_lib.init_field_list}
        if tool_lib.init_params is not None:
            all_params = init_params_default_value | json.loads(rsa_long_decrypt(tool_lib.init_params)) | params
        else:
            all_params = init_params_default_value | params

        if self.node.properties.get("kind") == "data-source":
            exist = function_executor.exec_code(
                f"{tool_lib.code}\ndef function_exist(function_name): return callable(globals().get(function_name))",
                {"function_name": "get_download_file_list"},
            )
            all_params = {**all_params, **(workflow_params.get("data_source") or {})}
            if exist:
                download_file_list = []
                download_list = function_executor.exec_code(
                    tool_lib.code, all_params, function_name="get_download_file_list"
                )
                for item in download_list:
                    self._check_cancelled()
                    file_result = function_executor.exec_code(
                        tool_lib.code, {**all_params, "download_item": item}, function_name="download"
                    )
                    file_bytes = file_result.get("file_bytes", [])
                    chunks = []
                    for chunk in file_bytes:
                        chunks.append(base64.b64decode(chunk))
                    file = bytes_to_uploaded_file(b"".join(chunks), file_result.get("name"))
                    file_url = self.upload_knowledge_file(file)
                    download_file_list.append({"file_id": file_url.split("/")[-1], "name": file_result.get("name")})
                result = download_file_list
            else:
                result = function_executor.exec_code(tool_lib.code, all_params)
        else:
            result = self.tool_exec_record(tool_lib, all_params)

        self.write_context("result", result)

        if is_result:
            chunk_id = str(uuid.uuid7())
            node_info = NodeInfo(self.get_node_id(), self.get_node_name(), Status.SUCCESS)
            self.write(TextContent(chunk_id, str(result), Status.SUCCESS, node_info, Position(self.get_node_id())))

    def tool_exec_record(self, tool_lib, all_params):
        import time

        task_record_id = uuid.uuid7()
        start_time = time.time()
        filtered_args = all_params
        try:
            # 过滤掉 tool_init_params 中的参数
            tool_init_params = json.loads(rsa_long_decrypt(tool_lib.init_params)) if tool_lib.init_params else {}
            if tool_init_params:
                filtered_args = {k: v for k, v in all_params.items() if k not in tool_init_params}
            workflow_params = self.get_workflow_parameters()
            workflow_type = self.get_workflow_type()
            if workflow_type == WorkflowType.KNOWLEDGE:
                source_id = workflow_params.get("knowledge_id")
                source_type = ToolTaskTypeChoices.KNOWLEDGE.value
            elif workflow_type == WorkflowType.TOOL:
                source_id = workflow_params.get("tool_id")
                source_type = ToolTaskTypeChoices.TOOL.value
            else:
                source_id = workflow_params.get("application_id")
                source_type = ToolTaskTypeChoices.APPLICATION.value

            ToolRecord(
                id=task_record_id,
                workspace_id=tool_lib.workspace_id,
                tool_id=tool_lib.id,
                source_type=source_type,
                source_id=source_id,
                meta={"input": filtered_args, "output": {}},
                state=State.STARTED,
            ).save()

            result = function_executor.exec_code(tool_lib.code, all_params)
            result_dict = _get_result_detail(result)
            QuerySet(ToolRecord).filter(id=task_record_id).update(
                state=State.SUCCESS,
                run_time=time.time() - start_time,
                meta={"input": filtered_args, "output": result_dict},
            )

            return result
        except Exception as e:
            maxkb_logger.error(f"Tool execution error: {traceback.format_exc()}")
            QuerySet(ToolRecord).filter(id=task_record_id).update(
                state=State.FAILURE,
                run_time=time.time() - start_time,
                meta={"input": filtered_args, "output": "Error: " + str(e)},
            )
            raise e

    def upload_knowledge_file(self, file):
        knowledge_id = self.get_workflow_parameters().get("knowledge_id")
        meta = {
            "debug": False,
            "knowledge_id": knowledge_id,
        }
        file_url = (
            FileSerializer(
                data={
                    "file": file,
                    "meta": meta,
                    "source_id": knowledge_id,
                    "source_type": FileSourceType.KNOWLEDGE.value,
                }
            )
            .upload()
            .replace("./oss/file/", "")
        )
        file.close()
        return file_url

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        details.update(
            {
                "result": _filter_file_bytes(self.get_context("result")),
                "params": self.get_context("params"),
                "enableException": self.node.properties.get("enableException"),
            }
        )
        return details
