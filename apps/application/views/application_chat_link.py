"""
    @project: MaxKB
    @Author: niu
    @file: application_chat_link.py
    @date: 2026/2/9 10:44
    @desc:
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.api.application_chat_link import ChatRecordLinkAPI, ChatRecordDetailShareAPI
from application.serializers.application_chat_link import ChatRecordShareLinkSerializer, ChatShareLinkDetailSerializer
from common import result
from common.auth import ChatTokenAuth


class ChatRecordLinkView(APIView):
    authentication_classes = [ChatTokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_("Generate share link"),
        summary=_("Generate share link"),
        operation_id=_("Generate share link"),  # type: ignore
        request=ChatRecordLinkAPI.get_request(),
        parameters=ChatRecordLinkAPI.get_parameters(),
        responses=ChatRecordLinkAPI.get_response(),
        tags=[_("Chat record link")]  # type: ignore
    )

    def post(self, request: Request, application_id: str, chat_id: str):
        return result.success(ChatRecordShareLinkSerializer(data={
            "application_id": application_id,
            "chat_id": chat_id,
            "user_id": request.auth.chat_user_id
        }).generate_link(request.data))


class ChatRecordDetailView(APIView):

    @extend_schema(
        methods=['GET'],
        description=_("Get chat record by share link"),
        summary=_("Get chat record by share link"),
        operation_id=_("Get chat record by share link"),  # type: ignore
        parameters=ChatRecordDetailShareAPI.get_parameters(),
        responses=ChatRecordDetailShareAPI.get_response(),
        tags=[_("Chat record link")]  # type: ignore
    )
    def get(self, request, link: str):
        return result.success(
            ChatShareLinkDetailSerializer(data={'link':link}).get_record_list()
        )
