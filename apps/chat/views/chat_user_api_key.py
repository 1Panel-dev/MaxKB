from common.auth import ChatTokenAuth
from common.log.log import log
from common.result import result
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from chat.serializers.chat_user_api_key_serializers import ChatUserApiKeySerializer


class ChatUserApiKeyView(APIView):
    authentication_classes = [ChatTokenAuth]

    @extend_schema(
        methods=["POST"],
        description=_("Create ChatUserAPIKey"),
        summary=_("Create ChatUserAPIKey"),
        operation_id=_("Create ChatUserAPIKey"),
        responses=None,
        tags=[_("Chat User API Key")],
    )
    @log(menu="Chat User API Key", operate="Add chat user API key")
    def post(self, request: Request):
        return result.success(ChatUserApiKeySerializer(data={"user_id": request.user.id}).generate())

    class Page(APIView):
        authentication_classes = [ChatTokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Get ChatUserAPIKey List"),
            summary=_("Get ChatUserAPIKey List"),
            operation_id=_("Get ChatUserAPIKey List"),
            parameters=[
                OpenApiParameter(name='order_by', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
                                 description=_('order by'), required=False),
            ],
            responses=None,
            tags=[_("Chat User API Key")],
        )
        def get(self, request: Request, current_page, page_size):
            return result.success(
                ChatUserApiKeySerializer(
                    data={"user_id": request.user.id,"order_by": request.query_params.get("order_by")}
                ).page(current_page, page_size)
            )

    class Operate(APIView):
        authentication_classes = [ChatTokenAuth]

        @extend_schema(
            methods=["DELETE"],
            description=_("Delete ChatUserAPIKey"),
            summary=_("Delete ChatUserAPIKey"),
            operation_id=_("Delete ChatUserAPIKey"),
            responses=None,
            parameters=None,
            tags=[_("Chat User API Key")],
        )
        @log(menu="Chat User API Key", operate="Delete chat user API key")
        def delete(self, request: Request, api_key_id: str):
            return result.success(
                ChatUserApiKeySerializer.Operate(
                    data={"id": api_key_id, "user_id": request.user.id}
                ).destroy()
            )