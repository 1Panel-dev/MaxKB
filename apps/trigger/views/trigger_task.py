# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： trigger_task.py
    @date：2026/1/14 16:01
    @desc:
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.api.application_api import ApplicationCreateAPI
from common import result
from trigger.serializers.trigger_task import TriggerTaskQuerySerializer


class TriggerTaskView(APIView):
    @extend_schema(
        methods=['GET'],
        description=_('Get the task list of triggers'),
        summary=_('Get the task list of triggers'),
        operation_id=_('Get the task list of triggers'),  # type: ignore
        parameters=ApplicationCreateAPI.get_parameters(),
        request=ApplicationCreateAPI.get_request(),
        responses=ApplicationCreateAPI.get_response(),
        tags=[_('Trigger')]  # type: ignore
    )
    def get(self, request: Request, workspace_id: str, trigger_id: str):
        return result.success(
            TriggerTaskQuerySerializer(data={'workspace_id': workspace_id, 'trigger_id': trigger_id}).list())
