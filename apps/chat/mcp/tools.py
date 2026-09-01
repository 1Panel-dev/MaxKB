import base64
import json
import re

import uuid_utils.compat as uuid
from application.models import Application, ApplicationApiKey, ChatSourceChoices, ChatUserType
from django.db.models import QuerySet
from django.utils import timezone

from chat.serializers.chat import ChatSerializers

CHAT_FILE_LIST_FIELDS = ("image_list", "document_list", "audio_list", "video_list", "other_list")

CHAT_FILE_TYPE_LABELS = {
    "image_list": "image",
    "document_list": "document",
    "audio_list": "audio",
    "video_list": "video",
    "other_list": "file",
}


class MCPToolHandler:
    def __init__(self, auth_header, chat_files_header=None, form_data=None):
        app_key = QuerySet(ApplicationApiKey).filter(secret_key=auth_header, is_active=True).first()
        if not app_key:
            raise PermissionError("Invalid API Key")
        if app_key.is_permanent is False and app_key.expire_time < timezone.now():
            raise PermissionError("API Key is expired")

        self.application = QuerySet(Application).filter(id=app_key.application_id, is_publish=True).first()
        if not self.application:
            raise PermissionError("Application is not found or not published")
        self.chat_files = self.decode_chat_files(chat_files_header)
        self.form_data = json.loads(base64.b64decode(form_data).decode("utf-8"))

    @staticmethod
    def decode_chat_files(chat_files_header):
        """
        解析上层应用透传过来的文件列表
        """
        if not chat_files_header:
            return {}
        try:
            chat_files = json.loads(base64.b64decode(chat_files_header).decode("utf-8"))
        except Exception:
            return {}
        if not isinstance(chat_files, dict):
            return {}
        return {
            key: value
            for key, value in chat_files.items()
            if key in CHAT_FILE_LIST_FIELDS and isinstance(value, list) and len(value) > 0
        }

    def initialize(self):
        return {
            "protocolVersion": "2025-06-18",
            "serverInfo": {"name": "maxkb-mcp", "version": "1.0.0"},
            "capabilities": {"tools": {}},
        }

    def build_description(self):
        """
        工具描述中带上当前对话已上传的文件, 否则上层模型不知道子应用可以处理这些文件
        """
        description = f"{self.application.name} {self.application.desc}"
        file_desc_list = []
        for field, file_list in self.chat_files.items():
            name_list = [
                str(file.get("name") or file.get("file_id"))
                for file in file_list
                if isinstance(file, dict) and (file.get("name") or file.get("file_id"))
            ]
            if name_list:
                file_desc_list.append(f"{CHAT_FILE_TYPE_LABELS.get(field, 'file')}: {', '.join(name_list)}")
        if not file_desc_list:
            return description
        return (
            f"{description}\n"
            "The user has attached the following files to the current conversation. "
            "They are forwarded to this AI automatically, so it can read and process them directly "
            "and you do NOT need to pass them as arguments: "
            f"{'; '.join(file_desc_list)}."
        )

    def list_tools(self):
        return {
            "tools": [
                {
                    "name": f"agent_{str(self.application.id)[:8]}",
                    "description": self.build_description(),
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string", "description": "The message to send to the AI."},
                        },
                        "required": ["message"],
                    },
                }
            ]
        }

    def _get_chat_id(self):
        from application.models import ChatUserType
        from common.init import init_template

        from chat.serializers.chat import OpenChatSerializers

        init_template.run()

        return OpenChatSerializers(
            data={
                "application_id": self.application.id,
                "chat_user_id": str(uuid.uuid7()),
                "chat_user_type": ChatUserType.ANONYMOUS_USER,
                "ip_address": "-",
                "source": {"type": ChatSourceChoices.ONLINE.value},
                "debug": False,
            }
        ).open()

    def call_tool(self, params):
        args = params.get("arguments", {})

        payload = {
            "message": args.get("message"),
            "stream": True,
            "re_chat": False,
            "form_data": self.form_data,
            **self.chat_files,
        }
        resp = ChatSerializers(
            data={
                "chat_id": self._get_chat_id(),
                "chat_user_id": str(uuid.uuid7()),
                "chat_user_type": ChatUserType.ANONYMOUS_USER,
                "application_id": self.application.id,
                "ip_address": "-",
                "source": {"type": ChatSourceChoices.ONLINE.value},
                "debug": False,
            }
        ).chat(payload)
        chunks = []
        for raw_line in resp:
            line = raw_line.decode("utf-8", errors="replace").rstrip("\r\n")
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if not payload or payload == "[DONE]":
                continue
            try:
                event = json.loads(payload)
            except json.JSONDecodeError:
                continue
            if event.get("operate") is True:
                chunks.append(event.get("content", ""))
                if event.get("is_end"):
                    break

        data = "".join(chunks)
        # 排除<tool_calls_render></tool_calls_render>标签
        data = re.sub(r"<tool_calls_render>.*?</tool_calls_render>", "", data, flags=re.DOTALL)
        return {"content": [{"type": "text", "text": data}]}
