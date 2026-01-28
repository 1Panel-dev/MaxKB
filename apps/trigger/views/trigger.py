# coding=utf-8
"""
    @project: MaxKB
    @Author：niu
    @file： trigger.py
    @date：2026/1/14 11:44
    @desc:
"""
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.api.application_api import ApplicationCreateAPI
from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants, ViewPermission, CompareConstants, \
    Permission, Group, Operate
from common.log.log import log
from common.result import DefaultResultSerializer
from trigger.models import Trigger
from trigger.serializers.task_source_trigger import TaskSourceTriggerListSerializer, TaskSourceTriggerOperateSerializer, \
    TaskSourceTriggerSerializer
from trigger.serializers.trigger import TriggerQuerySerializer, TriggerOperateSerializer

from trigger.api.trigger import TriggerCreateAPI, TriggerOperateAPI, TriggerEditAPI, TriggerBatchDeleteAPI, \
    TriggerBatchActiveAPI, TaskSourceTriggerOperateAPI, TaskSourceTriggerAPI, TaskSourceTriggerCreateAPI
from trigger.serializers.trigger import TriggerSerializer


def get_trigger_operation_object(trigger_id):
    trigger_model = QuerySet(model=Trigger).filter(id=trigger_id).first()
    if trigger_model is not None:
        return {
            "name": trigger_model.name
        }


def get_trigger_operation_object_batch(trigger_id_list):
    trigger_model_list = QuerySet(model=Trigger).filter(id__in=trigger_id_list)
    if trigger_model_list is not None:
        return {
            "name": f'[{",".join([trigger_model.name for trigger_model in trigger_model_list])}]',
            "trigger_list": [{'name': trigger_model.name, 'type': trigger_model.type} for trigger_model in
                             trigger_model_list]
        }


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
    @has_permissions(
        PermissionConstants.TRIGGER_CREATE.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    @log(
        menu="Trigger", operate="Create trigger",
        get_operation_object=lambda r, k: r.data.get('name'),
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
    @has_permissions(
        PermissionConstants.TRIGGER_READ.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
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
        @has_permissions(
            PermissionConstants.TRIGGER_READ.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        )
        @log(
            menu="Trigger", operate="Get trigger details",
            get_operation_object=lambda r, k: get_trigger_operation_object(k.get('trigger_id')),
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
        @has_permissions(
            PermissionConstants.TRIGGER_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        )
        @log(
            menu="Trigger", operate="Modify the trigger",
            get_operation_object=lambda r, k: get_trigger_operation_object(k.get('trigger_id')),
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
        @has_permissions(
            PermissionConstants.TRIGGER_DELETE.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        )
        @log(
            menu="Trigger", operate="Delete the trigger",
            get_operation_object=lambda r, k: get_trigger_operation_object(k.get('trigger_id')),
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
        @has_permissions(
            PermissionConstants.TRIGGER_DELETE.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        )
        @log(
            menu="Trigger", operate="Delete the trigger",
            get_operation_object=lambda r, k: get_trigger_operation_object_batch(r.data.get('id_list')),
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
        @has_permissions(
            PermissionConstants.TRIGGER_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        )
        @log(
            menu="Trigger", operate="Activate trigger in batches",
            get_operation_object=lambda r, k: get_trigger_operation_object_batch(r.data.get('id_list')),
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
        @has_permissions(
            PermissionConstants.TRIGGER_READ.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
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
        description=_('Create trigger in source'),
        summary=_('Create trigger in source'),
        operation_id=_('Create trigger in source'),  # type: ignore
        parameters=TaskSourceTriggerCreateAPI.get_parameters(),
        request=TaskSourceTriggerCreateAPI.get_request(),
        responses=TaskSourceTriggerCreateAPI.get_response(),
        tags=[_('Trigger')]  # type: ignore
    )
    @has_permissions(
        lambda r, kwargs: Permission(group=Group(kwargs.get("source_type")), operate=Operate.TRIGGER_CREATE,
                                     resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}:ROLE/WORKSPACE_MANAGE"
                                     ),
        lambda r, kwargs: Permission(group=Group(kwargs.get("source_type")), operate=Operate.TRIGGER_CREATE,
                                     resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}/{kwargs.get('source_type')}/{kwargs.get('source_id')}"
                                     ),
        ViewPermission([RoleConstants.USER.get_workspace_role()],
                       [lambda r, kwargs: Permission(group=Group(kwargs.get('source_type')),
                                                     operate=Operate.SELF,
                                                     resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}/{kwargs.get('source_type')}/{kwargs.get('source_id')}")],
                       CompareConstants.AND),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def post(self, request: Request, workspace_id: str, source_type: str, source_id: str):
        return result.success(TaskSourceTriggerSerializer(data={
            'workspace_id': workspace_id,
            'user_id': request.user.id
        }).insert({**request.data, 'source_id': source_id,
                   'workspace_id': workspace_id,
                   'is_active': True,
                   'source_type': source_type}))

    @extend_schema(
        methods=['GET'],
        description=_('Get the trigger list of source'),
        summary=_('Get the trigger list of source'),
        operation_id=_('Get the trigger list of source'),  # type: ignore
        parameters=TaskSourceTriggerAPI.get_parameters(),
        responses=DefaultResultSerializer,
        tags=[_('Trigger')]  # type: ignore
    )
    @has_permissions(
        lambda r, kwargs: Permission(group=Group(kwargs.get("source_type")), operate=Operate.TRIGGER_READ,
                                     resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}:ROLE/WORKSPACE_MANAGE"
                                     ),
        lambda r, kwargs: Permission(group=Group(kwargs.get("source_type")), operate=Operate.TRIGGER_READ,
                                     resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}/{kwargs.get('source_type')}/{kwargs.get('source_id')}"
                                     ),
        RoleConstants.USER.get_workspace_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
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
        @has_permissions(
            lambda r, kwargs: Permission(group=Group(kwargs.get("source_type")), operate=Operate.TRIGGER_READ,
                                         resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}:ROLE/WORKSPACE_MANAGE"
                                         ),
            lambda r, kwargs: Permission(group=Group(kwargs.get("source_type")), operate=Operate.TRIGGER_READ,
                                         resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}/{kwargs.get('source_type')}/{kwargs.get('source_id')}"
                                         ),
            RoleConstants.USER.get_workspace_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
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

        @has_permissions(
            lambda r, kwargs: Permission(group=Group(kwargs.get("source_type")), operate=Operate.TRIGGER_EDIT,
                                         resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}:ROLE/WORKSPACE_MANAGE"
                                         ),
            lambda r, kwargs: Permission(group=Group(kwargs.get("source_type")), operate=Operate.TRIGGER_EDIT,
                                         resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}/{kwargs.get('source_type')}/{kwargs.get('source_id')}"
                                         ),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [lambda r, kwargs: Permission(group=Group(kwargs.get('source_type')),
                                                         operate=Operate.SELF,
                                                         resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}/{kwargs.get('source_type')}/{kwargs.get('source_id')}")],
                           CompareConstants.AND),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
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
        @has_permissions(
            lambda r, kwargs: Permission(group=Group(kwargs.get("source_type")), operate=Operate.TRIGGER_DELETE,
                                         resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}:ROLE/WORKSPACE_MANAGE"
                                         ),
            lambda r, kwargs: Permission(group=Group(kwargs.get("source_type")), operate=Operate.TRIGGER_DELETE,
                                         resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}/{kwargs.get('source_type')}/{kwargs.get('source_id')}"
                                         ),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [lambda r, kwargs: Permission(group=Group(kwargs.get('source_type')),
                                                         operate=Operate.SELF,
                                                         resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}/{kwargs.get('source_type')}/{kwargs.get('source_id')}")],
                           CompareConstants.AND),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        def delete(self, request: Request, workspace_id: str, source_type: str, source_id: str, trigger_id: str):
            return result.success(TaskSourceTriggerOperateSerializer(
                data={'trigger_id': trigger_id, 'workspace_id': workspace_id,
                      'source_id': source_id, 'source_type': source_type}
            ).delete())
