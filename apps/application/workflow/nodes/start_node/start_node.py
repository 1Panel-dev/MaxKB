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


def get_default_global_variable(input_field_list: List):
    return {
        item.get('variable') or item.get('field'): item.get('default_value')
        for item in input_field_list
        if item.get('default_value', None) is not None
    }


class ApplicationSerializer(serializers.Serializer):
    chat_id = serializers.UUIDField(required=True, label="对话id")
    user_id = serializers.UUIDField(required=True, label="用户id")
    chat_record_id = serializers.UUIDField(required=True, label="对话记录id")
    messages = serializers.ListField(required=True, label="上下文数据")


class StarNode(INode):
    serializer_class = ApplicationSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION]
    type = 'start-node'

    def execute(self):
        workflow_params = self.get_workflow_parameters()
        base_node = self.workflow_manage.workflow.get_node('base-node')

        user_input_field_list = base_node.properties.get('user_input_field_list', []) if base_node else []
        api_input_field_list = base_node.properties.get('api_input_field_list', []) if base_node else []
        default_global = get_default_global_variable(user_input_field_list)
        default_api_global = get_default_global_variable(api_input_field_list)

        history_chat_record = workflow_params.get('history_chat_record', [])
        history_context = [
            {'question': r.problem_text, 'answer': r.answer_text}
            for r in history_chat_record
        ]

        chat_id = workflow_params.get('chat_id')
        chat_user_id = workflow_params.get('chat_user_id')

        memory = ''
        if chat_user_id:
            long_term_memory = (
                QuerySet(ApplicationLongTermMemory)
                .filter(
                    chat_user_id=chat_user_id,
                    application_id=workflow_params.get('application_id')
                )
                .first()
            )
            if long_term_memory:
                memory = long_term_memory.memory

        workflow_variable = {
            **default_global,
            **default_api_global,
            'time': timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M:%S'),
            'start_time': time.time(),
            'history_context': history_context,
            'chat_id': str(chat_id) if chat_id else None,
            'chat_user_id': chat_user_id,
            'chat_user_type': workflow_params.get('chat_user_type'),
            'chat_user': workflow_params.get('chat_user'),
            'chat_user_group': workflow_params.get('chat_user_group'),
            'memory': memory,
        }

        question = workflow_params.get('question', '')
        node_variable = {
            'question': question,
            'image': workflow_params.get('image_list', []),
            'document': workflow_params.get('document_list', []),
            'audio': workflow_params.get('audio_list', []),
            'video': workflow_params.get('video_list', []),
            'other': workflow_params.get('other_list', []),
            'memory': memory,
        }

        for key, value in node_variable.items():
            self.write_context(key, value)

        for key, value in workflow_variable.items():
            self.workflow_manage.context[key] = value

        config = self.node.properties.get('config', {})
        if config:
            for field in config.get('globalFields', []):
                key = field.get('value')
                if key:
                    self.workflow_manage.context[key] = workflow_variable.get(key, '')
