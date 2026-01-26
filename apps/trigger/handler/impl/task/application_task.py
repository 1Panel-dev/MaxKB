# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_task.py
    @date：2026/1/14 19:14
    @desc:
"""

import uuid_utils.compat as uuid
from django.db.models import QuerySet

from application.models import ChatUserType, Chat, ChatRecord, ChatSourceChoices
from chat.serializers.chat import ChatSerializers
from knowledge.models.knowledge_action import State

from trigger.handler.base_task import BaseTriggerTask
from trigger.models import TaskRecord


def get_reference(fields, obj):
    for field in fields:
        value = obj.get(field)
        if value is None:
            return None
        else:
            obj = value
    return obj


def get_field_value(value, kwargs):
    source = value.get('source')
    if source == 'custom':
        return value.get('value')
    else:
        return get_reference(value.get('value'), kwargs)


def get_application_execute_parameters(parameter_setting, kwargs):
    parameters = {'form_data': {}}
    question_setting = parameter_setting.get('question')
    if question_setting:
        parameters['message'] = get_field_value(question_setting, kwargs)
    filed_list = ['image_list', 'document_list', 'audio_list', 'video_list', 'other_list']
    for field in filed_list:
        field_setting = parameter_setting.get(field)
        if field_setting:
            parameters[field] = get_field_value(field_setting, kwargs)
    api_input_field_list = parameter_setting.get('api_input_field_list')
    if api_input_field_list:
        for key, value in api_input_field_list.items():
            parameters['form_data'][key] = get_field_value(value, kwargs)
    user_input_field_list = parameter_setting.get('user_input_field_list')
    if user_input_field_list:
        for key, value in user_input_field_list.items():
            parameters['form_data'][key] = get_field_value(value, kwargs)
    return parameters


def get_loop_workflow_node(node_list):
    result = []
    for item in node_list:
        if item.get('type') == 'loop-node':
            for loop_item in item.get('loop_node_data') or []:
                for inner_item in loop_item.values():
                    result.append(inner_item)
    return result


def get_workflow_state(details):
    node_list = details.values()
    all_node = [*node_list, *get_loop_workflow_node(node_list)]
    err = any([True for value in all_node if value.get('status') == 500 and not value.get('enableException')])
    if err:
        return State.FAILURE
    return State.SUCCESS


class ApplicationTask(BaseTriggerTask):
    def support(self, trigger_task, **kwargs):
        return trigger_task.get('source_type') == 'APPLICATION'

    def execute(self, trigger_task, **kwargs):
        parameter_setting = trigger_task.get('parameter')
        parameters = get_application_execute_parameters(parameter_setting, kwargs)
        parameters['re_chat'] = False
        parameters['stream'] = True
        chat_id = uuid.uuid7()
        chat_user_id = str(uuid.uuid7())
        chat_record_id = str(uuid.uuid7())
        parameters['chat_record_id'] = chat_record_id
        application_id = trigger_task.get('source_id')
        message = parameters.get('message')
        Chat.objects.get_or_create(id=chat_id, defaults={
            'application_id': application_id,
            'abstract': message,
            'chat_user_id': chat_user_id,
            'chat_user_type': ChatUserType.ANONYMOUS_USER.value,
            'asker': {'username': "游客"},
            'source': {
                'type': ChatSourceChoices.TRIGGER.value
            },
        })
        task_record_id = uuid.uuid7()
        TaskRecord(id=task_record_id, trigger_id=trigger_task.get('trigger'), trigger_task_id=trigger_task.get('id'),
                   source_type="APPLICATION",
                   source_id=application_id,
                   task_record_id=chat_record_id,
                   meta={'chat_id': chat_id},
                   state=State.STARTED).save()
        try:
            list(ChatSerializers(data={
                "chat_id": chat_id,
                "chat_user_id": chat_user_id,
                'chat_user_type': ChatUserType.ANONYMOUS_USER.value,
                'application_id': application_id,
                'source': {
                    'type': ChatSourceChoices.TRIGGER.value
                },
                'debug': False
            }).chat(instance=parameters))
            chat_record = QuerySet(ChatRecord).filter(id=chat_record_id).first()
            state = get_workflow_state(chat_record.details)
            QuerySet(TaskRecord).filter(id=task_record_id).update(state=state, run_time=chat_record.run_time)
        except Exception as e:
            state = State.FAILURE
            QuerySet(TaskRecord).filter(id=task_record_id).update(state=state, run_time=0)
