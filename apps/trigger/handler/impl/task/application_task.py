# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_task.py
    @date：2026/1/14 19:14
    @desc:
"""
import json
import time
import traceback

import uuid_utils.compat as uuid
from django.db.models import QuerySet

from application.models import ChatUserType, Chat, ChatRecord, ChatSourceChoices, Application
from chat.serializers.chat import ChatSerializers
from common.utils.logger import maxkb_logger
from knowledge.models.knowledge_action import State
from trigger.handler.base_task import BaseTriggerTask
from trigger.models import TaskRecord, TriggerTask


def get_reference(fields, obj):
    for field in fields:
        value = obj.get(field)
        if value is None:
            return None
        else:
            obj = value
    return obj


def conversion_custom_value(value, _type):
    if ['array', 'dict', 'float', 'int', 'boolean', 'any'].__contains__(_type):
        try:
            return json.loads(value)
        except Exception as e:
            pass
    return value


def valid_value_type(value, _type):
    if _type == 'array':
        return isinstance(value, list)
    if _type == 'dict':
        return isinstance(value, dict)
    if _type == 'float':
        return isinstance(value, float)
    if _type == 'int':
        return isinstance(value, int)
    if _type == 'boolean':
        return isinstance(value, bool)
    return isinstance(value, str)


def get_field_value(value, kwargs, _type, required, default_value, field):
    source = value.get('source')
    if source == 'custom':
        _value = value.get('value')
        if _value:
            _value = conversion_custom_value(_value, _type)
        else:
            if default_value:
                return default_value
            if required:
                raise Exception(f'{field} is required')
            else:
                return None
    else:
        _value = get_reference(value.get('value'), kwargs)
    valid = valid_value_type(_value, _type)
    if not valid:
        raise Exception(f'{field} type error')
    return _value


def get_application_execute_parameters(parameter_setting, application_parameters_setting, kwargs):
    many_field = ['api_input_field_list', 'user_input_field_list']
    parameters = {'form_data': {}}
    for key, value in application_parameters_setting.items():
        setting = parameter_setting.get(key)
        if setting:
            if many_field.__contains__(key):
                for ck, cv in value.items():
                    _setting = setting.get(ck)
                    if _setting:
                        _value = get_field_value(_setting, kwargs, cv.get('type'), cv.get('required'),
                                                 cv.get('default_value'), ck)
                        parameters['form_data'][ck] = _value
                    else:
                        if cv.get('default_value'):
                            parameters['form_data'][ck] = cv.get('default_value')
                        else:
                            if cv.get('required'):
                                raise Exception(f'{ck} is required')
            else:
                value = get_field_value(setting, kwargs, value.get('type'), value.get('required'),
                                        value.get('default_value'), key)
                parameters['message' if key == 'question' else key] = value
        else:
            if value.get('default_value'):
                parameters['message' if key == 'question' else key] = value.get('default_value')
            else:
                if value.get('required'):
                    raise Exception(f'{"message" if key == "question" else key} is required')

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


def get_user_field_component_input_type(input_type):
    if input_type == "MultiRow":
        return 'array'
    if input_type == "SwitchInput":
        return 'boolean'
    return 'string'


def get_application_parameters_setting(application):
    application_parameter_setting = {'question': {
        'required': True,
        'type': 'string'
    }}
    if application.type == 'SIMPLE':
        return application_parameter_setting
    else:
        base_node_list = [n for n in application.work_flow.get('nodes') if n.get('type') == "base-node"]
        if len(base_node_list) == 0:
            raise Exception('Incorrect application workflow information')
        base_node = base_node_list[0]
        api_input_field_list = base_node.get('properties').get('api_input_field_list') or []
        api_input_field_list = {user_field.get('variable'): {
            'required': user_field.get('is_required'),
            'default_value': user_field.get('default_value'),
            'type': 'string'
        } for user_field in api_input_field_list}
        user_input_field_list = base_node.get('properties').get('user_input_field_list') or []
        user_input_field_list = {user_field.get('field'): {
            'required': user_field.get('required'),
            'default_value': user_field.get('default_value'),
            'type': get_user_field_component_input_type(user_field.get('input_type'))
        } for user_field in user_input_field_list}
        application_parameter_setting['api_input_field_list'] = api_input_field_list
        application_parameter_setting['user_input_field_list'] = user_input_field_list
        node_data = base_node.get('properties').get('node_data') or {}
        file_upload_enable = node_data.get('file_upload_enable')
        if file_upload_enable:
            file_upload_setting = node_data.get('file_upload_setting') or {}
            for field in ['audio', 'document', 'image', 'other', 'video']:
                v = file_upload_setting.get(field)
                if v:
                    application_parameter_setting[field] = {'required': False, 'default_value': [], 'type': 'array'}
        return application_parameter_setting


class ApplicationTask(BaseTriggerTask):
    def support(self, trigger_task, **kwargs):
        return trigger_task.get('source_type') == 'APPLICATION'

    def execute(self, trigger_task, **kwargs):
        parameter_setting = trigger_task.get('parameter')
        task_record_id = uuid.uuid7()
        start_time = time.time()
        try:
            application = QuerySet(Application).filter(id=trigger_task.get('source_id')).only('type',
                                                                                              'work_flow').first()
            if application is None:
                QuerySet(TriggerTask).filter(id=trigger_task.get('id')).delete()
                return
            application_id = trigger_task.get('source_id')
            chat_id = uuid.uuid7()
            chat_user_id = str(uuid.uuid7())
            chat_record_id = str(uuid.uuid7())
            TaskRecord(id=task_record_id, trigger_id=trigger_task.get('trigger'),
                       trigger_task_id=trigger_task.get('id'),
                       source_type="APPLICATION",
                       source_id=application_id,
                       task_record_id=chat_record_id,
                       meta={'chat_id': chat_id},
                       state=State.STARTED).save()
            application_parameters_setting = get_application_parameters_setting(application)
            parameters = get_application_execute_parameters(parameter_setting, application_parameters_setting, kwargs)
            parameters['re_chat'] = False
            parameters['stream'] = True
            parameters['chat_record_id'] = chat_record_id
            message = parameters.get('message')
            ip_address = '-'
            if kwargs.get('body') is not None:
                ip_address = kwargs.get('body').get('ip_address')
            Chat.objects.get_or_create(id=chat_id, defaults={
                'application_id': application_id,
                'abstract': message,
                'chat_user_id': chat_user_id,
                'chat_user_type': ChatUserType.ANONYMOUS_USER.value,
                'asker': {'username': "游客"},
                'ip_address': ip_address,
                'source': {
                    'type': ChatSourceChoices.TRIGGER.value
                },
            })

            list(ChatSerializers(data={
                "chat_id": chat_id,
                "chat_user_id": chat_user_id,
                'chat_user_type': ChatUserType.ANONYMOUS_USER.value,
                'application_id': application_id,
                'ip_address': ip_address,
                'source': {
                    'type': ChatSourceChoices.TRIGGER.value
                },
                'debug': False
            }).chat(instance=parameters))
            chat_record = QuerySet(ChatRecord).filter(id=chat_record_id).first()
            if chat_record:
                state = get_workflow_state(chat_record.details)
                QuerySet(TaskRecord).filter(id=task_record_id).update(state=state, run_time=chat_record.run_time,
                                                                      meta={'parameter_setting': parameter_setting,
                                                                            'input': parameters, 'output': None})
            else:
                QuerySet(TaskRecord).filter(id=task_record_id).update(state=State.FAILURE,
                                                                      run_time=time.time() - start_time,
                                                                      meta={'parameter_setting': parameter_setting,
                                                                            'input': parameters, 'output': None,
                                                                            'err_message': 'Error: An unknown error occurred during the execution of the conversation'})
        except Exception as e:
            maxkb_logger.error(f"Application execution error: {traceback.format_exc()}")
            QuerySet(TaskRecord).filter(id=task_record_id).update(
                state=State.FAILURE,
                run_time=time.time() - start_time,
                meta={'input': {'parameter_setting': parameter_setting, **kwargs}, 'output': None,
                      'err_message': 'Error: ' + str(e)}
            )
