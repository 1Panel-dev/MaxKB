# coding=utf-8
"""
    @project: MaxKB
    @Author：niu
    @file： trigger.py
    @date：2026/1/14 11:44
    @desc:
"""
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.views import APIView

from application.api.application_api import ApplicationCreateAPI, ApplicationQueryAPI, ApplicationImportAPI, \
    ApplicationExportAPI, ApplicationOperateAPI, ApplicationEditAPI, TextToSpeechAPI, SpeechToTextAPI, PlayDemoTextAPI
from application.models import Application
from application.serializers.application import ApplicationSerializer, Query, ApplicationOperateSerializer
from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions, get_is_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants, ViewPermission, CompareConstants
from common.log.log import log
from tools.api.tool import GetInternalToolAPI
from trigger.serializers.trigger import TriggerSerializer


class TriggerApi(APIView):
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
            data={'workspace_id': workspace_id,'user_id': request.user.id}).insert(request.data))





