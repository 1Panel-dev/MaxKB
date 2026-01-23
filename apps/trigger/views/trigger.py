# coding=utf-8
"""
    @project: MaxKB
    @Author：niu
    @file： trigger.py
    @date：2026/1/14 11:44
    @desc:
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.api.application_api import ApplicationCreateAPI
from common import result
from common.auth import TokenAuth
from trigger.serializers.task_source_trigger import TaskSourceTriggerListSerializer, TaskSourceTriggerOperateSerializer, \
    TaskSourceTriggerSerializer
from trigger.serializers.trigger import TriggerQuerySerializer, TriggerOperateSerializer

from trigger.api.trigger import TriggerCreateAPI, TriggerOperateAPI, TriggerEditAPI, TriggerBatchDeleteAPI, \
    TriggerBatchActiveAPI, TaskSourceTriggerOperateAPI, TaskSourceTriggerAPI
from trigger.serializers.trigger import TriggerSerializer


class TriggerView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Create trigger'),
        summary=_('Create trigger'),
        operation_id=_('Create trigger'),  # type: ignore
        parameters=TriggerCreateAPI.get_parameters(),
        request=TriggerCreateAPI.get_request(),
        responses=TriggerCreateAPI.get_response(),
        tags=[_('Trigger')]  # type: ignore
    )
    def post(self, request: Request, workspace_id: str):
        return result.success(TriggerSerializer(
            data={'workspace_id': workspace_id, 'user_id': request.user.id}).insert(request.data))

    @extend_schema(
        methods=['GET'],
        description=_('Get the trigger list'),
        summary=_('Get the trigger list'),
        operation_id=_('Get the trigger list'),  # type: ignore
        parameters=ApplicationCreateAPI.get_parameters(),
        request=ApplicationCreateAPI.get_request(),
        responses=ApplicationCreateAPI.get_response(),
        tags=[_('Trigger')]  # type: ignore
    )
    def get(self, request: Request, workspace_id: str):
        return result.success(TriggerQuerySerializer(data={
            'workspace_id': workspace_id,
            'name': request.query_params.get('name'),
            'type': request.query_params.get('type'),
            'task': request.query_params.get('task'),
            'is_active': request.query_params.get('is_active'),
            'create_user': request.query_params.get('create_user'),
        }).list())

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Get trigger details'),
            summary=_('Get trigger details'),
            operation_id=_('Get trigger details'),  # type: ignore
            parameters=TriggerOperateAPI.get_parameters(),
            responses=result.DefaultResultSerializer,
            tags=[_('Trigger')]  # type: ignore
        )
        def get(self, request: Request, workspace_id: str, trigger_id: str):
            return result.success(TriggerOperateSerializer(
                data={'trigger_id': trigger_id, 'workspace_id': workspace_id, 'user_id': request.user.id}
            ).one())

        @extend_schema(
            methods=['PUT'],
            description=_('Modify the trigger'),
            summary=_('Modify the trigger'),
            operation_id=_('Modify the trigger'),  # type: ignore
            parameters=TriggerOperateAPI.get_parameters(),
            request=TriggerEditAPI.get_request(),
            responses=result.DefaultResultSerializer,
            tags=[_('Trigger')]  # type: ignore
        )
        def put(self, request: Request, workspace_id: str, trigger_id: str):
            return result.success(TriggerOperateSerializer(
                data={'trigger_id': trigger_id, 'workspace_id': workspace_id, 'user_id': request.user.id}
            ).edit(request.data))

        @extend_schema(
            methods=['DELETE'],
            description=_('Delete the trigger'),
            summary=_('Delete the trigger'),
            operation_id=_('Delete the trigger'),  # type: ignore
            parameters=TriggerOperateAPI.get_parameters(),
            responses=result.DefaultResultSerializer,
            tags=[_('Trigger')]  # type: ignore
        )
        def delete(self, request: Request, workspace_id: str, trigger_id: str):
            return result.success(TriggerOperateSerializer(
                data={'trigger_id': trigger_id, 'workspace_id': workspace_id, 'user_id': request.user.id}
            ).delete())

    class BatchDelete(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_('Delete trigger in batches'),
            summary=_('Delete trigger in batches'),
            operation_id=_('Delete trigger in batches'),  # type: ignore
            parameters=TriggerBatchDeleteAPI.get_parameters(),
            request=TriggerBatchDeleteAPI.get_request(),
            responses=result.DefaultResultSerializer,
            tags=[_('Trigger')]  # type: ignore
        )
        def put(self, request: Request, workspace_id: str):
            return result.success(TriggerSerializer.Batch(
                data={'workspace_id': workspace_id, 'user_id': request.user.id}
            ).batch_delete(request.data))

    class BatchActivate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_('Activate trigger in batches'),
            summary=_('Activate trigger in batches'),
            operation_id=_('Activate trigger in batches'),  # type: ignore
            parameters=TriggerBatchDeleteAPI.get_parameters(),
            request=TriggerBatchActiveAPI.get_request(),
            responses=result.DefaultResultSerializer,
            tags=[_('Trigger')]  # type: ignore
        )
        def put(self, request: Request, workspace_id: str):
            return result.success(TriggerSerializer.Batch(
                data={'workspace_id': workspace_id, 'user_id': request.user.id}
            ).batch_switch(request.data))

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Get the trigger list by page'),
            summary=_('Get the trigger list by page'),
            operation_id=_('Get the trigger list by page'),  # type: ignore
            parameters=ApplicationCreateAPI.get_parameters(),
            request=ApplicationCreateAPI.get_request(),
            responses=ApplicationCreateAPI.get_response(),
            tags=[_('Trigger')]  # type: ignore
        )
        def get(self, request: Request, workspace_id: str, current_page: int, page_size: int):
            return result.success(TriggerQuerySerializer(data={
                'workspace_id': workspace_id,
                'name': request.query_params.get('name'),
                'task': request.query_params.get('task'),
                'type': request.query_params.get('type'),
                'is_active': request.query_params.get('is_active'),
                'create_user': request.query_params.get('create_user'),
            }).page(current_page, page_size))


class TaskSourceTriggerView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Create trigger of source'),
        summary=_('Create trigger of source'),
        operation_id=_('Create trigger of source'),  # type: ignore
        parameters=TaskSourceTriggerAPI.get_parameters(),
        request=TaskSourceTriggerAPI.get_request(),
        responses=TaskSourceTriggerAPI.get_response(),
        tags=[_('Trigger')]  # type: ignore
    )
    def post(self, request: Request, workspace_id: str, source_type: str, source_id: str):
        return result.success(TaskSourceTriggerSerializer(data={
            'workspace_id': workspace_id,
            'user_id': request.user.id
        }).insert({**request.data, 'source_id': source_id,
                   'source_type': source_type}))

    @extend_schema(
        methods=['GET'],
        description=_('Get the trigger list of source'),
        summary=_('Get the trigger list of source'),
        operation_id=_('Get the trigger list of source'),  # type: ignore
        parameters=TaskSourceTriggerAPI.get_parameters(),
        responses=result.DefaultResultSerializer,
        tags=[_('Trigger')]  # type: ignore
    )
    def get(self, request: Request, workspace_id: str, source_type: str, source_id: str):
        return result.success(TaskSourceTriggerListSerializer(data={
            'workspace_id': workspace_id,
            'source_id': source_id,
            'source_type': source_type,
        }).list())

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Get Task source trigger details'),
            summary=_('Get Task source trigger details'),
            operation_id=_('Get Task source trigger details'),  # type: ignore
            parameters=TaskSourceTriggerOperateAPI.get_parameters(),
            responses=result.DefaultResultSerializer,
            tags=[_('Trigger')]  # type: ignore
        )
        def get(self, request: Request, workspace_id: str, source_type: str, source_id: str, trigger_id: str):
            return result.success(TaskSourceTriggerOperateSerializer(
                data={'trigger_id': trigger_id, 'workspace_id': workspace_id,
                      'source_id': source_id, 'source_type': source_type}
            ).one())


        @extend_schema(
            methods=['PUT'],
            description=_('Modify the task source trigger'),
            summary=_('Modify the task source trigger'),
            operation_id=_('Modify the task source trigger'),  # type: ignore
            parameters=TaskSourceTriggerOperateAPI.get_parameters(),
            request=TaskSourceTriggerOperateAPI.get_request(),
            responses=result.DefaultResultSerializer,
            tags=[_('Trigger')]  # type: ignore
        )
        def put(self, request: Request, workspace_id: str, source_type: str, source_id: str, trigger_id: str):
            return result.success(TaskSourceTriggerOperateSerializer(
                data={'trigger_id': trigger_id, 'workspace_id': workspace_id,
                      'source_id': source_id, 'source_type': source_type}
            ).edit(request.data))

        @extend_schema(
            methods=['DELETE'],
            description=_('Delete the task source trigger'),
            summary=_('Delete the task source trigger'),
            operation_id=_('Delete the task source trigger'),  # type: ignore
            parameters=TaskSourceTriggerOperateAPI.get_parameters(),
            responses=result.DefaultResultSerializer,
            tags=[_('Trigger')]  # type: ignore
        )
        def delete(self, request: Request, workspace_id: str, source_type: str, source_id: str, trigger_id: str):
            return result.success(TaskSourceTriggerOperateSerializer(
                data={'trigger_id': trigger_id, 'workspace_id': workspace_id,
                      'source_id': source_id, 'source_type': source_type}
            ).delete())











