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
from trigger.serializers.trigger_task import TriggerTaskQuerySerializer, TriggerTaskRecordQuerySerializer, \
    TriggerTaskRecordOperateSerializer


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


class TriggerTaskRecordView(APIView):
    pass


class TriggerTaskRecordExecutionDetailsView(APIView):
    @extend_schema(
        methods=['GET'],
        description=_('Retrieve detailed records of tasks executed by the trigger.'),
        summary=_('Retrieve detailed records of tasks executed by the trigger.'),
        operation_id=_('Retrieve detailed records of tasks executed by the trigger.'),  # type: ignore
        parameters=ApplicationCreateAPI.get_parameters(),
        request=ApplicationCreateAPI.get_request(),
        responses=ApplicationCreateAPI.get_response(),
        tags=[_('Trigger')]  # type: ignore
    )
    def get(self, request: Request, workspace_id: str, trigger_id: str, trigger_task_id: str,
            trigger_task_record_id: str):
        return result.success(
            TriggerTaskRecordOperateSerializer(
                data={'workspace_id': workspace_id, 'trigger_id': trigger_id, 'trigger_task_id': trigger_task_id,
                      'trigger_task_record_id': trigger_task_record_id})
            .get_execution_details())


class TriggerTaskRecordPageView(APIView):
    @extend_schema(
        methods=['GET'],
        description=_('Get a paginated list of execution records for trigger tasks.'),
        summary=_('Get a paginated list of execution records for trigger tasks.'),
        operation_id=_('Get a paginated list of execution records for trigger tasks.'),  # type: ignore
        parameters=ApplicationCreateAPI.get_parameters(),
        request=ApplicationCreateAPI.get_request(),
        responses=ApplicationCreateAPI.get_response(),
        tags=[_('Trigger')]  # type: ignore
    )
    def get(self, request: Request, workspace_id: str, trigger_id: str, current_page: int, page_size: int):
        return result.success(
            TriggerTaskRecordQuerySerializer(
                data={'workspace_id': workspace_id, 'trigger_id': trigger_id,
                      'state': request.query_params.get('state'),
                      'name': request.query_params.get('name')})
            .page(current_page, page_size))
