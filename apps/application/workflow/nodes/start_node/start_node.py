# coding=utf-8
"""
@project: MaxKB
@Author：虎虎虎
@file： start_node.py
@date：2026/7/1 16:59
@desc:
"""

import time
from typing import List

from django.db.models import QuerySet
from django.utils import timezone
from rest_framework import serializers

from application.models.application_chat import ApplicationLongTermMemory
from application.workflow.common import WorkflowType
from application.workflow.i_node import INode
from application.workflow.status import Status


def get_field_key(item: dict):
    return item.get("variable") or item.get("field")


def get_default_global_variable(input_field_list: List):
    return {
        get_field_key(item): item.get("default_value")
        for item in input_field_list
        if item.get("default_value", None) is not None
    }


def get_input_global_variable(input_field_list: List, form_data: dict):
    """默认值打底，再用本次提交的表单值覆盖；没有默认值的字段及 False / 0 等取值同样生效。"""
    variable = get_default_global_variable(input_field_list)
    for item in input_field_list:
        key = get_field_key(item)
        if key and form_data.get(key) is not None:
            variable[key] = form_data[key]
    return variable


class ApplicationSerializer(serializers.Serializer):
    chat_id = serializers.UUIDField(required=True, label="对话id")
    user_id = serializers.UUIDField(required=True, label="用户id")
    chat_record_id = serializers.UUIDField(required=True, label="对话记录id")
    messages = serializers.ListField(required=True, label="上下文数据")


class StarNode(INode):
    supported_workflow_type_list = [WorkflowType.APPLICATION]
    type = "start-node"

    def execute(self):
        workflow_params = self.get_workflow_parameters()
        base_node = self.workflow_manage.workflow.get_node("base-node")

        user_input_field_list = base_node.properties.get("user_input_field_list", []) if base_node else []
        api_input_field_list = base_node.properties.get("api_input_field_list", []) if base_node else []
        form_data = workflow_params.get("form_data") or {}
        default_global = get_input_global_variable(user_input_field_list, form_data)
        default_api_global = get_input_global_variable(api_input_field_list, form_data)
        history_chat_record = workflow_params.get("history_chat_record", [])
        history_context = [{"question": r.problem_text, "answer": r.answer_text} for r in history_chat_record]

        chat_id = workflow_params.get("chat_id")
        chat_user_id = workflow_params.get("chat_user_id")

        memory = ""
        if chat_user_id:
            long_term_memory = (
                QuerySet(ApplicationLongTermMemory)
                .filter(chat_user_id=chat_user_id, application_id=workflow_params.get("application_id"))
                .first()
            )
            if long_term_memory:
                memory = long_term_memory.memory

        workflow_variable = {
            **default_global,
            **default_api_global,
            "time": timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S"),
            "start_time": time.time(),
            "history_context": history_context,
            "chat_id": str(chat_id) if chat_id else None,
            "chat_user_id": chat_user_id,
            "chat_user_type": workflow_params.get("chat_user_type"),
            "chat_user": workflow_params.get("chat_user"),
            "chat_user_group": workflow_params.get("chat_user_group"),
            "memory": memory,
        }

        question = workflow_params.get("question", "")
        node_variable = {
            "question": question,
            "image": workflow_params.get("image_list", []),
            "document": workflow_params.get("document_list", []),
            "audio": workflow_params.get("audio_list", []),
            "video": workflow_params.get("video_list", []),
            "other": workflow_params.get("other_list", []),
            "memory": memory,
        }

        for key, value in node_variable.items():
            self.write_context(key, value)

        # 全局变量统一放进 context['global']，与 reset_variable / get_reference_field 的引用约定一致
        for key, value in workflow_variable.items():
            self.workflow_manage.write_context("global", key, value)

        config = self.node.properties.get("config", {})
        if config:
            for field in config.get("globalFields", []):
                key = field.get("value")
                if key:
                    self.workflow_manage.write_context("global", key, workflow_variable.get(key, ""))

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        global_fields = []
        for field in (self.node.properties.get("config") or {}).get("globalFields", []) or []:
            key = field.get("value")
            value = self.workflow_manage.get_context("global", key) or ""
            global_fields.append(
                {
                    "label": field.get("label"),
                    "key": key,
                    "value": value,
                }
            )
        details.update(
            {
                "question": self.get_context("question"),
                "image": self.get_context("image"),
                "document": self.get_context("document"),
                "audio": self.get_context("audio"),
                "video": self.get_context("video"),
                "global_fields": global_fields,
            }
        )
        return details
