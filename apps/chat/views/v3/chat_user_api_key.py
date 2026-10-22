from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from common.auth import ChatTokenAuth
from common.log.log import log
from common.result import result
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from chat.serializers.chat_user_api_key_serializers import ChatUserApiKeyModelSerializer, ChatUserApiKeySerializer
from system_manage.models import ChatUserApiKey


class ChatUserApiKeyView(APIView):
    authentication_classes = [ChatTokenAuth]

    @extend_schema(
        methods=["POST"],
        description=_("Create ChatUserAPIKey"),
        summary=_("Create ChatUserAPIKey"),
        operation_id="V3 Create ChatUserAPIKey",
        responses=None,
        tags=[_("V3 Chat User API Key")],  # type: ignore
    )
    @log(menu="Chat User API Key", operate="Add chat user API key")
    def post(self, request: Request):
        return result.success(ChatUserApiKeySerializer(data={"user_id": request.user.id}).generate())

    @extend_schema(
        methods=["GET"],
        description=_("Get ChatUserAPIKey"),
        summary=_("Get ChatUserAPIKey"),
        operation_id="V3 Get ChatUserAPIKey",
        responses=None,
        tags=[_("V3 Chat User API Key")],  # type: ignore
    )
    @log(menu="Chat User API Key", operate="Get chat user API key")
    def get(self, request: Request):
        user_id = request.user.id
        api_key = QuerySet(ChatUserApiKey).filter(user_id=user_id).first()
        if api_key is None:
            # 用户还没有 API Key，直接调用生成逻辑
            return result.success(ChatUserApiKeySerializer(data={"user_id": user_id}).generate())
        return result.success(ChatUserApiKeyModelSerializer(api_key).data)
