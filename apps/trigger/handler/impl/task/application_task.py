# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_task.py
    @date：2026/1/14 19:14
    @desc:
"""
import uuid

from application.models import ChatUserType, Chat
from chat.serializers.chat import ChatSerializers
from trigger.handler.base_task import BaseTriggerTask


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
        for key, value in api_input_field_list.item():
            parameters['form_data'][key] = get_field_value(value, kwargs)
    user_input_field_list = parameter_setting.get('user_input_field_list')
    if user_input_field_list:
        for key, value in user_input_field_list.item():
            parameters['form_data'][key] = get_field_value(value, kwargs)
    return parameters


class ApplicationTask(BaseTriggerTask):
    def support(self, trigger_task, **kwargs):
        return trigger_task.get('source_type') == 'APPLICATION'

    def execute(self, trigger_task, **kwargs):
        parameter_setting = trigger_task.get('parameter')
        parameters = get_application_execute_parameters(parameter_setting, kwargs)
        parameters['re_chat'] = False
        parameters['stream'] = True
        chat_id = uuid.uuid1()
        chat_user_id = str(uuid.uuid1())
        application_id = trigger_task.get('source_id')
        message = parameters.get('message')
        Chat.objects.get_or_create(id=chat_id, defaults={
            'application_id': application_id,
            'abstract': message,
            'chat_user_id': chat_user_id,
            'chat_user_type': ChatUserType.ANONYMOUS_USER.value,
            'asker': {'username': "游客"}
        })

        list(ChatSerializers(data={
            "chat_id": chat_id,
            "chat_user_id": chat_user_id,
            'chat_user_type': ChatUserType.ANONYMOUS_USER.value,
            'application_id': application_id,
            'debug': False
        }).chat(instance=parameters))
