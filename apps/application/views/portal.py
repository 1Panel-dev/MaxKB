# coding=utf-8
"""
@project: MaxKB
@Author：虎虎
@file： portal.py
@date：2026/7/30 16:51
@desc: 门户 - 跨工作空间展示用户可查看的所有智能体
"""

import uuid_utils.compat as uuid
import logging

from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.serializers.application import Query
from application.models import ChatUserType, ChatSourceChoices
from chat.serializers.chat import OpenChatSerializers
from common import result
from common.auth import TokenAuth
from common.log.log import _get_ip_address
from users.serializers.user import get_workspace_list_by_user

logger = logging.getLogger(__name__)


class PortalApplicationAPI(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        description="Portal - Get accessible applications across all workspaces",
        summary="Portal - Get accessible applications",
        operation_id="portal-accessible-applications",
        tags=["Portal"],
    )
    def get(self, request: Request):
        user_id = str(request.user.id)
        workspace_list = get_workspace_list_by_user(user_id)
        all_apps = []
        seen = set()
        for ws in workspace_list:
            ws_id = ws["id"]
            try:
                apps = Query(data={"workspace_id": ws_id, "user_id": user_id}).list({})
                if not apps:
                    continue
                for app in apps:
                    app_id = app.get("id")
                    if app_id and app_id not in seen:
                        seen.add(app_id)
                        app["workspace_name"] = ws.get("name", ws_id)
                        app["workspace_id"] = ws_id
                        all_apps.append(app)
            except Exception as e:
                logger.warning(f"Portal: failed to query apps for workspace {ws_id}: {e}")
                continue
        return result.success(all_apps)


class PortalChatAPI(APIView):
    """Portal chat: open a chat session using admin TokenAuth"""

    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["POST"],
        description="Portal - Open a chat session",
        summary="Portal - Open chat",
        operation_id="portal-chat-open",
        tags=["Portal"],
    )
    def post(self, request: Request, workspace_id: str, application_id: str):
        ip_address = _get_ip_address(request)
        chat_user_id = str(uuid.uuid7())

        open_result = OpenChatSerializers(
            data={
                "workspace_id": workspace_id,
                "application_id": application_id,
                "chat_user_id": chat_user_id,
                "chat_user_type": ChatUserType.ANONYMOUS_USER,
                "ip_address": ip_address,
                "source": {"type": ChatSourceChoices.ONLINE.value},
                "debug": True,
            }
        ).open()

        return result.success(open_result)
