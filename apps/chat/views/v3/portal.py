# coding=utf-8
"""
@project: MaxKB
@Author：MaxKB
@file： portal.py
@date：2026/8/14
@desc: 门户视图
"""

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common import result
from common.auth import ChatTokenAuth
from common.utils.common import query_params_to_single_dict

from chat.api.portal_api import PortalAPI
from chat.serializers.portal import (
    PortalApplicationSerializer,
    PortalHistoricalConversationSerializer,
)


class PortalApplicationView(APIView):
    authentication_classes = [ChatTokenAuth]

    @extend_schema(
        methods=["GET"],
        description=_("Get published application list by page"),
        summary=_("Get published application list by page"),
        operation_id=_("Get published application list by page"),
        parameters=PortalAPI.Application.get_parameters(),
        responses=PortalAPI.Application.get_response(),
        tags=[_("V3 Chat")],
    )
    def get(self, request: Request, current_page: int, page_size: int):
        return result.success(
            PortalApplicationSerializer.Query(data={**query_params_to_single_dict(request.query_params)}).page(
                current_page, page_size, str(request.user.id)
            )
        )


class PortalHistoricalConversationView(APIView):
    authentication_classes = [ChatTokenAuth]

    @extend_schema(
        methods=["GET"],
        description=_("Get portal historical conversation by page"),
        summary=_("Get portal historical conversation by page"),
        operation_id=_("Get portal historical conversation by page"),
        parameters=PortalAPI.Conversation.get_parameters(),
        responses=PortalAPI.Conversation.get_response(),
        tags=[_("V3 Chat")],
    )
    def get(self, request: Request, current_page: int, page_size: int):
        return result.success(
            PortalHistoricalConversationSerializer.Query(
                data={**query_params_to_single_dict(request.query_params)}
            ).page(current_page, page_size, str(request.user.id))
        )
