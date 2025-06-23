# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： chat_record.py
    @date：2025/6/23 10:42
    @desc:
"""
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _

from chat.api.vote_api import VoteAPI
from chat.serializers.chat_record import VoteSerializer
from common import result
from common.auth import TokenAuth


class VoteView(APIView):
    authentication_classes = [TokenAuth]

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
