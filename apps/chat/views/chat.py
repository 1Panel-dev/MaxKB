# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： chat.py
    @date：2025/6/6 11:18
    @desc:
"""
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from chat.api.chat_authentication_api import ChatAuthenticationAPI
from chat.serializers.chat_authentication import AuthenticationSerializer, ApplicationProfileSerializer
from common.auth import TokenAuth
from common.exception.app_exception import AppAuthenticationFailed
from common.result import result


class Authentication(APIView):
    def options(self, request, *args, **kwargs):
        return HttpResponse(
            headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true",
                     "Access-Control-Allow-Methods": "POST",
                     "Access-Control-Allow-Headers": "Origin,Content-Type,Cookie,Accept,Token"}, )

    @extend_schema(
        methods=['POST'],
        description=_('Application Certification'),
        summary=_('Application Certification'),
        operation_id=_('Application Certification'),  # type: ignore
        request=ChatAuthenticationAPI.get_request(),
        responses=None,
        tags=[_('Chat')]  # type: ignore
    )
    def post(self, request: Request):
        return result.success(
            AuthenticationSerializer(data={'access_token': request.data.get("access_token"),
                                           'authentication_value': request.data.get(
                                               'authentication_value')}).auth(
                request),
            headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true",
                     "Access-Control-Allow-Methods": "POST",
                     "Access-Control-Allow-Headers": "Origin,Content-Type,Cookie,Accept,Token"}
        )


class ApplicationProfile(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_("Get application related information"),
        summary=_("Get application related information"),
        operation_id=_("Get application related information"),  # type: ignore
        request=None,
        responses=None,
        tags=[_('Chat')]  # type: ignore
    )
    def get(self, request: Request):
        if 'application_id' in request.auth.keywords:
            return result.success(ApplicationProfileSerializer(
                data={'application_id': request.auth.keywords.get('application_id')}).profile())
        raise AppAuthenticationFailed(401, "身份异常")


class ChatView(APIView):
    pass
