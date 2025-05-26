# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application.py
    @date：2025/5/26 16:51
    @desc:
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.api.application_api import ApplicationCreateAPI
from application.serializers.application import ApplicationSerializer
from common import result


class Application(APIView):

    @extend_schema(
        methods=['POST'],
        description=_('Create an application'),
        summary=_('Create an application'),
        operation_id=_('Create an application'),  # type: ignore
        parameters=ApplicationCreateAPI.get_parameters(),
        request=ApplicationCreateAPI.get_request(),
        responses=ApplicationCreateAPI.get_response(),
        tags=[_('Application')]  # type: ignore
    )
    def post(self, request: Request):
        return result.success(ApplicationSerializer.insert(request.data))
