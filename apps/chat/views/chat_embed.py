# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： chat_embed.py
    @date：2025/5/30 15:22
    @desc:
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from chat.api.chat_embed_api import ChatEmbedAPI
from chat.serializers.chat_embed_serializers import ChatEmbedSerializer


class ChatEmbedView(APIView):

    @extend_schema(
        methods=['GET'],
        description=_('Get embedded js'),
        summary=_('Get embedded js'),
        operation_id=_('Get embedded js'),  # type: ignore
        parameters=ChatEmbedAPI.get_parameters(),
        responses=ChatEmbedAPI.get_response(),
        tags=[_('Chat')]  # type: ignore
    )
    def get(self, request: Request):
        return ChatEmbedSerializer(
            data={'protocol': request.query_params.get('protocol'), 'token': request.query_params.get('token'),
                  'host': request.query_params.get('host'), }).get_embed(params=request.query_params)
