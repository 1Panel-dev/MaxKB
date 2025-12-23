# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： chat_record.py
    @date：2025/6/23 10:42
    @desc:
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.serializers.application_chat_record import ChatRecordOperateSerializer
from chat.api.chat_api import HistoricalConversationAPI, PageHistoricalConversationAPI, \
    PageHistoricalConversationRecordAPI, HistoricalConversationRecordAPI, HistoricalConversationOperateAPI
from chat.api.vote_api import VoteAPI
from chat.serializers.chat_record import VoteSerializer, HistoricalConversationSerializer, \
    HistoricalConversationRecordSerializer, HistoricalConversationOperateSerializer
from common import result
from common.auth import ChatTokenAuth


class VoteView(APIView):
    authentication_classes = [ChatTokenAuth]

    @extend_schema(
        methods=['PUT'],
        description=_("Like, Dislike"),
        summary=_("Like, Dislike"),
        operation_id=_("Like, Dislike"),  # type: ignore
        parameters=VoteAPI.get_parameters(),
        request=VoteAPI.get_request(),
        responses=VoteAPI.get_response(),
        tags=[_('Chat')]  # type: ignore
    )
    def put(self, request: Request, chat_id: str, chat_record_id: str):
        return result.success(VoteSerializer(
            data={'chat_id': chat_id,
                  'chat_record_id': chat_record_id
                  }).vote(request.data))


class HistoricalConversationView(APIView):
    authentication_classes = [ChatTokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_("Get historical conversation"),
        summary=_("Get historical conversation"),
        operation_id=_("Get historical conversation"),  # type: ignore
        parameters=HistoricalConversationAPI.get_parameters(),
        responses=HistoricalConversationAPI.get_response(),
        tags=[_('Chat')]  # type: ignore
    )
    def get(self, request: Request):
        return result.success(HistoricalConversationSerializer(
            data={
                'application_id': request.auth.application_id,
                'chat_user_id': request.auth.chat_user_id,
            }).list())

    class Operate(APIView):
        authentication_classes = [ChatTokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_("Modify conversation about"),
            summary=_("Modify conversation about"),
            operation_id=_("Modify conversation about"),  # type: ignore
            parameters=HistoricalConversationOperateAPI.get_parameters(),
            request=HistoricalConversationOperateAPI.get_request(),
            responses=HistoricalConversationOperateAPI.get_response(),
            tags=[_('Chat')]  # type: ignore
        )
        def put(self, request: Request, chat_id: str):
            return result.success(HistoricalConversationOperateSerializer(
                data={
                    'application_id': request.auth.application_id,
                    'chat_user_id': request.auth.chat_user_id,
                    'chat_id': chat_id,
                }).edit_abstract(request.data)
                                  )

        @extend_schema(
            methods=['DELETE'],
            description=_("Delete history conversation"),
            summary=_("Delete history conversation"),
            operation_id=_("Delete history conversation"),  # type: ignore
            parameters=HistoricalConversationOperateAPI.get_parameters(),
            responses=HistoricalConversationOperateAPI.get_response(),
            tags=[_('Chat')]  # type: ignore
        )
        def delete(self, request: Request, chat_id: str):
            return result.success(HistoricalConversationOperateSerializer(
                data={
                    'application_id': request.auth.application_id,
                    'chat_user_id': request.auth.chat_user_id,
                    'chat_id': chat_id,
                }).logic_delete())

    class BatchDelete(APIView):
        authentication_classes = [ChatTokenAuth]

        @extend_schema(
            methods=['DELETE'],
            description=_("Batch delete history conversation"),
            summary=_("Batch delete history conversation"),
            operation_id=_("Batch delete history conversation"),  # type: ignore
            parameters=HistoricalConversationOperateAPI.get_parameters(),
            responses=HistoricalConversationOperateAPI.get_response(),
            tags=[_('Chat')]  # type: ignore
        )
        def delete(self, request: Request):
            return result.success(HistoricalConversationOperateSerializer.Clear(data={
                'application_id': request.auth.application_id,
                'chat_user_id': request.auth.chat_user_id,
            }).batch_logic_delete())

    class PageView(APIView):
        authentication_classes = [ChatTokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_("Get historical conversation by page"),
            summary=_("Get historical conversation by page"),
            operation_id=_("Get historical conversation by page"),  # type: ignore
            parameters=PageHistoricalConversationAPI.get_parameters(),
            responses=PageHistoricalConversationAPI.get_response(),
            tags=[_('Chat')]  # type: ignore
        )
        def get(self, request: Request, current_page: int, page_size: int):
            return result.success(HistoricalConversationSerializer(
                data={
                    'application_id': request.auth.application_id,
                    'chat_user_id': request.auth.chat_user_id,
                }).page(current_page, page_size))


class HistoricalConversationRecordView(APIView):
    authentication_classes = [ChatTokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_("Get historical conversation records"),
        summary=_("Get historical conversation records"),
        operation_id=_("Get historical conversation records"),  # type: ignore
        parameters=HistoricalConversationRecordAPI.get_parameters(),
        responses=HistoricalConversationRecordAPI.get_response(),
        tags=[_('Chat')]  # type: ignore
    )
    def get(self, request: Request, chat_id: str):
        return result.success(HistoricalConversationRecordSerializer(
            data={
                'chat_id': chat_id,
                'application_id': request.auth.application_id,
                'chat_user_id': request.auth.chat_user_id,
            }).list())

    class PageView(APIView):
        authentication_classes = [ChatTokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_("Get historical conversation records by page "),
            summary=_("Get historical conversation records by page"),
            operation_id=_("Get historical conversation records by page"),  # type: ignore
            parameters=PageHistoricalConversationRecordAPI.get_parameters(),
            responses=PageHistoricalConversationRecordAPI.get_response(),
            tags=[_('Chat')]  # type: ignore
        )
        def get(self, request: Request, chat_id: str, current_page: int, page_size: int):
            return result.success(HistoricalConversationRecordSerializer(
                data={
                    'chat_id': chat_id,
                    'application_id': request.auth.application_id,
                    'chat_user_id': request.auth.chat_user_id,
                }).page(current_page, page_size))


class ChatRecordView(APIView):
    authentication_classes = [ChatTokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_("Get conversation details"),
        summary=_("Get conversation details"),
        operation_id=_("Get conversation details"),  # type: ignore
        parameters=PageHistoricalConversationRecordAPI.get_parameters(),
        responses=PageHistoricalConversationRecordAPI.get_response(),
        tags=[_('Chat')]  # type: ignore
    )
    def get(self, request: Request, chat_id: str, chat_record_id: str):
        return result.success(ChatRecordOperateSerializer(
            data={
                'chat_id': chat_id,
                'chat_record_id': chat_record_id,
                'application_id': request.auth.application_id,
                'chat_user_id': request.auth.chat_user_id,
            }).one(False))
