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
from trigger.serializers.trigger import TriggerSerializer, TriggerQuerySerializer


class TriggerView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Create trigger'),
        summary=_('Create trigger'),
        operation_id=_('Create trigger'),  # type: ignore
        parameters=ApplicationCreateAPI.get_parameters(),
        request=ApplicationCreateAPI.get_request(),
        responses=ApplicationCreateAPI.get_response(),
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
        return result.success(TriggerQuerySerializer(data={'workspace_id': workspace_id,
                                                           'name': request.query_params.get('name'),
                                                           'type': request.query_params.get('type')}).list())

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
                'type': request.query_params.get('type')
            }).page(current_page, page_size))
