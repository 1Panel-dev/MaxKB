# coding=utf-8
"""
@project: MaxKB
@Author：虎
@file： tool_node.py
@date：2026/9/3 15:09
@desc:
"""

import json
import re

import uuid_utils.compat as uuid
from django.core import validators
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from rest_framework import serializers
from rest_framework.utils.formatting import lazy_format

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode
from application.workflow.message.struct.content import NodeInfo, Position
from application.workflow.message.struct.text_content import TextContent
from application.workflow.status import Status
from common.exception.app_exception import AppApiException
from common.field.common import ObjectField
from common.utils.common import common_convert_value
from common.utils.logger import maxkb_logger
from common.utils.tool_code import ToolExecutor

function_executor = ToolExecutor()


class InputField(serializers.Serializer):
    name = serializers.CharField(required=True, label=_("Variable Name"))
    is_required = serializers.BooleanField(required=True, label=_("Is this field required"))
    type = serializers.CharField(
        required=True,
        label=_("type"),
        validators=[
            validators.RegexValidator(
                regex=re.compile("^string|int|dict|array|float|boolean$"),
                message=_("The field only supports string|int|dict|array|float"),
                code=500,
            )
        ],
    )
    source = serializers.CharField(
        required=True,
        label=_("source"),
        validators=[
            validators.RegexValidator(
                regex=re.compile("^custom|reference$"),
                message=_("The field only supports custom|reference"),
                code=500,
            )
        ],
    )
    value = ObjectField(required=True, label=_("Variable Value"), model_type_list=[str, list])

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        is_required = self.data.get("is_required")
        if is_required and self.data.get("value") is None:
            message = lazy_format(_("{field}, this field is required."), field=self.data.get("name"))
            raise AppApiException(500, message)


class ToolNodeSerializer(serializers.Serializer):
    input_field_list = InputField(required=True, many=True)
    code = serializers.CharField(required=True, label=_("function"))
    is_result = serializers.BooleanField(required=False, label=_("Whether to return content"))


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


class ToolNode(INode):
    serializer_class = ToolNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = "tool-node"

    def execute(self):
        node_params = self.get_parameters()
        input_field_list = node_params.get("input_field_list", [])
        code = node_params.get("code")
        is_result = node_params.get("is_result", False)

        params = {
            field.get("name"): convert_value(
                field.get("name"),
                field.get("value"),
                field.get("type"),
                field.get("is_required"),
                field.get("source"),
                self,
            )
            for field in input_field_list
        }

        # 合并启动参数默认值（如果有 init_field_list 定义）
        init_field_list = node_params.get("init_field_list", [])
        if init_field_list:
            init_params_default_value = {i["field"]: i.get("default_value") for i in init_field_list}
            init_params = self.get_workflow_parameters().get("init_params")
            if init_params is not None:
                all_params = init_params_default_value | init_params | params
            else:
                all_params = init_params_default_value | params
        else:
            all_params = params

        result = function_executor.exec_code(code, all_params)
        self.write_context("params", all_params)
        self.write_context("result", result)

        if is_result:
            chunk_id = str(uuid.uuid7())
            node_info = NodeInfo(self.get_node_id(), self.get_node_name(), Status.SUCCESS)
            self.write(TextContent(chunk_id, str(result), Status.SUCCESS, node_info, Position(self.get_node_id())))

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        details.update(
            {
                "result": self.get_context("result"),
                "params": self.get_context("params"),
                "enableException": self.node.properties.get("enableException"),
            }
        )
        return details
