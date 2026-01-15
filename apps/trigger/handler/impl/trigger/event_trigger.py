# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： event_trigger.py
    @date：2026/1/15 11:08
    @desc:
"""

from django.db.models import QuerySet
from django.utils.translation import gettext as _, gettext_lazy
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.views import APIView

from common import result
from common.exception.app_exception import AppApiException
from common.result import Result
from trigger.handler.base_trigger import BaseTrigger
from trigger.models import TriggerTask, Trigger
from trigger.serializers.trigger import TriggerResponse
from trigger.serializers.trigger_task import TriggerTaskResponse


def valid_parameter_type(value, _type, desc):
    try:
        if _type == 'int':
            instance_type = int | float
        elif _type == 'boolean':
            instance_type = bool
        elif _type == 'float':
            instance_type = float | int
        elif _type == 'dict':
            instance_type = dict
        elif _type == 'array':
            instance_type = list
        elif _type == 'string':
            instance_type = str
        else:
            raise Exception(_(
                'Field: {name} Type: {_type} Value: {value} Unsupported types'
            ).format(name=desc, _type=_type))
    except:
        return value
    if not isinstance(value, instance_type):
        raise Exception(_(
            'Field: {name} Type: {_type} Value: {value} Type error'
        ).format(name=desc, _type=_type, value=value))
    return value


def get_parameters(body_setting, request: Request):
    parameters = {}
    for body in body_setting:
        value = request.data.get(body.get('field'))
        if value is None and body.get('required'):
            raise AppApiException(500, f'{body.get("desc")} is required')
        _type = body.get('type')
        valid_parameter_type(value, _type, body.get("desc"))
        parameters[body.get('field')] = value
    return parameters


class EventTriggerRequest(serializers.Serializer):
    pass


class EventTriggerView(APIView):
    @extend_schema(
        methods=['POST'],
        description=gettext_lazy('Event Trigger WebHook'),
        summary=gettext_lazy('Event Trigger WebHook'),
        operation_id=gettext_lazy('Event Trigger WebHook'),  # type: ignore
        request={
            'application/json': {
                'schema': {
                    'type': 'object',
                    'example': {}
                }
            }
        },
        tags=[gettext_lazy('Trigger')],  # type: ignore
        examples=[
            OpenApiExample(
                'Example Request',
                description='Send an empty JSON object as request body',
                value={},
                request_only=True,  # 仅用于请求示例
                response_only=False,
            )
        ]

    )
    def post(self, request: Request, trigger_id: str):
        trigger = QuerySet(Trigger).filter(id=trigger_id).first()
        if trigger:
            return EventTrigger.execute(TriggerResponse(trigger).data, request)
        return Result(code=404, message="404")


class EventTrigger(BaseTrigger):
    """
    事件触发器
    """

    @staticmethod
    def execute(trigger, request=None, **kwargs):
        is_active = trigger.get('is_active')
        if not is_active:
            return Result(code=404, message="404", status=404)
        trigger_setting = trigger.get('trigger_setting')
        body = trigger_setting.get('body')
        parameters = get_parameters(body, request)
        trigger_task_list = [TriggerTaskResponse(trigger_task).data for trigger_task in
                             QuerySet(TriggerTask).filter(trigger__id=trigger.get('id'), is_active=True)]
        from trigger.handler.simple_tools import execute
        for trigger_task in trigger_task_list:
            execute(trigger_task, parameters=parameters)
        return result.success(True)

    def support(self, trigger, **kwargs):
        return trigger.get('trigger_type') == 'EVENT'

    def deploy(self, trigger, **kwargs):
        return True

    def undeploy(self, trigger, **kwargs):
        return True
