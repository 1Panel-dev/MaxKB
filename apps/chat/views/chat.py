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

from chat.api.chat_api import ChatAPI
from chat.api.chat_authentication_api import ChatAuthenticationAPI, ChatAuthenticationProfileAPI, ChatOpenAPI
from chat.serializers.chat import OpenChatSerializers, ChatSerializers
from chat.serializers.chat_authentication import AnonymousAuthenticationSerializer, ApplicationProfileSerializer, \
    AuthProfileSerializer
from common.auth import TokenAuth
from common.constants.permission_constants import ChatAuth
from common.exception.app_exception import AppAuthenticationFailed
from common.result import result


class AnonymousAuthentication(APIView):
    def options(self, request, *args, **kwargs):
        return HttpResponse(
            headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": "true",
                     "Access-Control-Allow-Methods": "POST",
                     "Access-Control-Allow-Headers": "Origin,Content-Type,Cookie,Accept,Token"}, )

    @extend_schema(
        methods=['POST'],
        description=_('Application Anonymous Certification'),
        summary=_('Application Anonymous Certification'),
        operation_id=_('Application Anonymous Certification'),  # type: ignore
        request=ChatAuthenticationAPI.get_request(),
        responses=None,
        tags=[_('Chat')]  # type: ignore
    )
    def post(self, request: Request):
        return result.success(
            AnonymousAuthenticationSerializer(data={'access_token': request.data.get("access_token")}).auth(
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
        if isinstance(request.auth, ChatAuth):
            return result.success(ApplicationProfileSerializer(
                data={'application_id': request.auth.application_id}).profile())
        raise AppAuthenticationFailed(401, "身份异常")


class AuthProfile(APIView):
    @extend_schema(
        methods=['GET'],
        description=_("Get application authentication information"),
        summary=_("Get application authentication information"),
        operation_id=_("Get application authentication information"),  # type: ignore
        parameters=ChatAuthenticationProfileAPI.get_parameters(),
        responses=None,
        tags=[_('Chat')]  # type: ignore
    )
    def get(self, request: Request):
        return result.success(
            AuthProfileSerializer(data={'access_token': request.query_params.get("access_token")}).profile())


class ChatView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_("dialogue"),
        summary=_("dialogue"),
        operation_id=_("dialogue"),  # type: ignore
        request=ChatAPI.get_request(),
        parameters=ChatAPI.get_parameters(),
        responses=None,
        tags=[_('Chat')]  # type: ignore
    )
    def post(self, request: Request, chat_id: str):
        return ChatSerializers(data={'chat_id': chat_id,
                                     'chat_user_id': request.auth.chat_user_id,
                                     'chat_user_type': request.auth.chat_user_type,
                                     'application_id': request.auth.application_id}
                               ).chat(request.data)


class OpenView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_("Get the session id according to the application id"),
        summary=_("Get the session id according to the application id"),
        operation_id=_("Get the session id according to the application id"),  # type: ignore
        parameters=ChatOpenAPI.get_parameters(),
        responses=None,
        tags=[_('Chat')]  # type: ignore
    )
    def get(self, request: Request, workspace_id: str, application_id: str):
        return result.success(OpenChatSerializers(
            data={'workspace_id': workspace_id, 'application_id': application_id,
                  'chat_user_id': request.auth.chat_user_id, 'chat_user_type': request.auth.chat_user_type}).open())
