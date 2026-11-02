import base64
import binascii
import json
import re
import uuid as std_uuid

import uuid_utils.compat as uuid
from application.models import Application, ApplicationApiKey, Chat, ChatSourceChoices, ChatUserType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import QuerySet
from django.utils import timezone

from chat.serializers.chat import ChatSerializers
from common.auth.constants.group_constants import Group
from knowledge.models import File, FileSourceType

CHAT_FILE_LIST_FIELDS = ("image_list", "document_list", "audio_list", "video_list", "other_list")

CHAT_FILE_TYPE_LABELS = {
    "image_list": "image",
    "document_list": "document",
    "audio_list": "audio",
    "video_list": "video",
    "other_list": "file",
}

# 与前端 ui/src/constants/file-type.ts 保持一致，按后缀把文件归到对应的消息附件字段
CHAT_FILE_EXTENSIONS = {
    "image_list": ("JPG", "JPEG", "PNG", "GIF", "BMP"),
    "document_list": ("PDF", "DOCX", "TXT", "XLS", "XLSX", "MD", "HTML", "CSV"),
    "audio_list": ("MP3", "WAV", "OGG", "AAC", "M4A"),
    "video_list": ("MP4", "AVI", "MKV", "MOV", "FLV", "WMV"),
}

MCP_PROTOCOL_VERSION = "2025-06-18"

AGENT_TOOL_PREFIX = "agent_"

UPLOAD_FILE_TOOL = "upload_file"


class InvalidParamsError(Exception):
    """工具参数不合法，对应 JSON-RPC -32602"""


def get_chat_file_field(file_name):
    extension = file_name.rsplit(".", 1)[-1].upper() if "." in file_name else ""
    for field, extensions in CHAT_FILE_EXTENSIONS.items():
        if extension in extensions:
            return field
    return "other_list"


def build_tool(application, description=None):
    return {
        "name": f"{AGENT_TOOL_PREFIX}{str(application.id)}",
        "description": description or f"{application.name} {application.desc or ''}".strip(),
        "inputSchema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "The message to send to the AI."},
            },
            "required": ["message"],
        },
    }


def build_form_data(message, form_data=None):
    """
    合并父应用透传参数与提示词中的 JSON 参数，提示词参数优先。
    """
    try:
        message_form_data = json.loads(message or "{}")
    except (TypeError, json.JSONDecodeError):
        message_form_data = {}
    if not isinstance(message_form_data, dict):
        message_form_data = {}
    return {**(form_data or {}), **message_form_data}


def chat_application(
    application_id, chat_user_id, chat_user_type, message, form_data=None, chat_files=None, chat_id=None
):
    """
    以指定对话用户身份同步调用应用，返回 (回答, chat_id)。
    不传 chat_id 时新建会话；会话行由 ChatSerializers 惰性创建（标题取用户问题），无需先 open。
    """
    from common.init import init_template

    init_template.run()
    chat_id = chat_id or str(uuid.uuid7())
    resp = ChatSerializers(
        data={
            "chat_id": chat_id,
            "application_id": application_id,
            "chat_user_id": chat_user_id,
            "chat_user_type": chat_user_type,
            "ip_address": "-",
            "source": {"type": ChatSourceChoices.API_CALL.value},
            "debug": False,
        }
    ).chat(
        {
            "message": {"content": message or "", **(chat_files or {})},
            "stream": False,
            "re_chat": False,
            "form_data": build_form_data(message, form_data),
        }
    )
    data = (json.loads(resp.content).get("data") or {}).get("content") or ""
    # 排除<tool_calls_render></tool_calls_render>标签
    data = re.sub(r"<tool_calls_render>.*?</tool_calls_render>", "", data, flags=re.DOTALL)
    return data, chat_id


class MCPToolHandler:
    def __init__(self, auth_header, chat_files_header=None, form_data=None):
        app_key = QuerySet(ApplicationApiKey).filter(secret_key=auth_header, is_active=True).first()
        if not app_key:
            raise PermissionError("Invalid API Key")
        if app_key.is_permanent is False and app_key.expire_time < timezone.now():
            raise PermissionError("API Key is expired")

        self.app_key = app_key
        self.application = QuerySet(Application).filter(id=app_key.application_id, is_publish=True).first()
        if not self.application:
            raise PermissionError("Application is not found or not published")
        self.chat_files = self.decode_chat_files(chat_files_header)
        self.form_data = self.decode_form_data(form_data)

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

    @staticmethod
    def decode_form_data(form_data):
        """
        解析上层应用透传过来的表单数据
        """
        if not form_data:
            return {}
        try:
            form_data = json.loads(base64.b64decode(form_data).decode("utf-8"))
        except Exception:
            return {}
        if not isinstance(form_data, dict):
            return {}
        return form_data

    def initialize(self):
        return {
            "protocolVersion": MCP_PROTOCOL_VERSION,
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
        return {"tools": [build_tool(self.application, self.build_description())]}

    def call_tool(self, params):
        args = params.get("arguments", {})
        answer, _ = chat_application(
            self.application.id,
            str(self.app_key.id),
            ChatUserType.APPLICATION_API_KEY.value,
            args.get("message"),
            self.form_data,
            self.chat_files,
        )
        return {"content": [{"type": "text", "text": answer}]}


class ChatUserMCPToolHandler:
    """
    对话用户 API Key（chat-xxx）的 MCP 接口：Key 不绑定应用，
    以对话用户身份暴露其有权限访问的所有已发布应用，每个应用一个工具，另加一个上传文件工具。
    传入上一次返回的 chat_id 即可续聊；上传的文件挂在 chat_id 下，调用应用时通过 file_ids 携带。
    """

    def __init__(self, chat_user, auth, application_id=None):
        self.chat_user = chat_user
        self.auth = auth
        # 单应用 MCP 地址只暴露该应用
        self.application_id = application_id

    def initialize(self):
        return {
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "serverInfo": {"name": "maxkb-mcp", "version": "1.0.0"},
            "capabilities": {"tools": {}},
        }

    def get_application_ids(self):
        prefix = f"{Group.CHAT_USER}:r:"
        application_ids = [
            key[len(prefix) :] for key, value in self.auth.permissions.items() if key.startswith(prefix) and value
        ]
        if self.application_id:
            return [app_id for app_id in application_ids if app_id == str(self.application_id)]
        return application_ids

    def get_applications(self):
        return QuerySet(Application).filter(id__in=self.get_application_ids(), is_publish=True).order_by("name")

    @staticmethod
    def build_agent_tool(application):
        return {
            "name": f"{AGENT_TOOL_PREFIX}{str(application.id)}",
            "description": f"{application.name} {application.desc or ''}".strip(),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "The message to send to the AI."},
                    "chat_id": {
                        "type": "string",
                        "description": "Conversation id returned by a previous call or by upload_file. "
                        "Pass it to continue the same conversation with history; omit it to start a new one.",
                    },
                    "file_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Ids of files uploaded with upload_file to attach to this message.",
                    },
                    "form_data": {
                        "type": "object",
                        "description": "Values for the application's input parameters.",
                    },
                },
                "required": ["message"],
            },
        }

    @staticmethod
    def build_upload_tool():
        return {
            "name": UPLOAD_FILE_TOOL,
            "description": "Upload a file to attach to a conversation. Returns file_id and chat_id; "
            "pass both to an agent tool (file_ids, chat_id) so the AI can read the file.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_name": {"type": "string", "description": "File name with extension, e.g. report.pdf."},
                    "content": {"type": "string", "description": "Base64 encoded file content."},
                    "chat_id": {
                        "type": "string",
                        "description": "Conversation to attach the file to; omit it to start a new conversation.",
                    },
                },
                "required": ["file_name", "content"],
            },
        }

    def list_tools(self):
        return {
            "tools": [
                *[self.build_agent_tool(application) for application in self.get_applications()],
                self.build_upload_tool(),
            ]
        }

    def check_chat_id(self, chat_id, application_id=None):
        """
        校验调用方传入的 chat_id：已存在的会话必须属于当前对话用户（及当前应用），不存在则视为新会话。
        """
        if not chat_id:
            return None
        try:
            chat_id = str(std_uuid.UUID(str(chat_id)))
        except ValueError:
            raise InvalidParamsError(f"Invalid chat_id: {chat_id}")
        chat = QuerySet(Chat).filter(id=chat_id).first()
        if chat is not None and (
            str(chat.chat_user_id) != str(self.chat_user.id)
            or (application_id and str(chat.application_id) != str(application_id))
        ):
            raise InvalidParamsError(f"Invalid chat_id: {chat_id}")
        return chat_id

    def get_chat_files(self, chat_id, file_ids):
        """
        根据 file_ids 查出当前用户上传到该会话的文件，按类型组装成消息附件；未传 chat_id 时取文件所在会话。
        """
        if not file_ids:
            return chat_id, {}
        if not isinstance(file_ids, list):
            raise InvalidParamsError("file_ids must be an array")
        files = list(
            QuerySet(File).filter(
                id__in=[str(file_id) for file_id in file_ids],
                source_type=FileSourceType.CHAT,
                meta__user_id=str(self.chat_user.id),
            )
        )
        source_ids = {str(file.source_id) for file in files}
        if len(files) != len(set(map(str, file_ids))) or len(source_ids) != 1 or chat_id not in (None, *source_ids):
            raise InvalidParamsError("file_ids must be files uploaded to the same chat_id")
        chat_files = {}
        for file in files:
            chat_files.setdefault(get_chat_file_field(file.file_name), []).append(
                {"name": file.file_name, "url": f"./oss/file/{file.id}", "file_id": str(file.id)}
            )
        return source_ids.pop(), chat_files

    def upload_file(self, args):
        from oss.serializers.file import FileSerializer

        file_name = str(args.get("file_name") or "").strip()
        content = args.get("content")
        if not file_name or not isinstance(content, str) or not content:
            raise InvalidParamsError("file_name and content are required")
        try:
            file_bytes = base64.b64decode(content, validate=True)
        except (binascii.Error, ValueError):
            raise InvalidParamsError("content must be base64 encoded")
        chat_id = self.check_chat_id(args.get("chat_id")) or str(uuid.uuid7())
        file_url = FileSerializer(
            data={
                "file": SimpleUploadedFile(file_name, file_bytes),
                "meta": {},
                "source_id": chat_id,
                "source_type": FileSourceType.CHAT,
            }
        ).upload(user_id=str(self.chat_user.id))
        result = {"file_id": file_url.split("/")[-1], "name": file_name, "url": file_url, "chat_id": chat_id}
        return {
            "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
            "structuredContent": result,
        }

    def call_tool(self, params):
        name = str(params.get("name") or "")
        args = params.get("arguments") or {}
        if name == UPLOAD_FILE_TOOL:
            return self.upload_file(args)
        application_id = name[len(AGENT_TOOL_PREFIX) :] if name.startswith(AGENT_TOOL_PREFIX) else ""
        if not application_id or not self.get_applications().filter(id=application_id).exists():
            raise InvalidParamsError(f"Unknown tool: {name}")
        form_data = args.get("form_data") or {}
        if not isinstance(form_data, dict):
            raise InvalidParamsError("form_data must be an object")
        chat_id, chat_files = self.get_chat_files(
            self.check_chat_id(args.get("chat_id"), application_id), args.get("file_ids")
        )
        # 文件可能先上传到别的应用的会话，这里再按当前应用校验一次
        chat_id = self.check_chat_id(chat_id, application_id)
        answer, chat_id = chat_application(
            application_id,
            str(self.chat_user.id),
            ChatUserType.CHAT_USER.value,
            args.get("message"),
            form_data,
            chat_files,
            chat_id,
        )
        return {
            "content": [
                {"type": "text", "text": answer},
                {"type": "text", "text": json.dumps({"chat_id": chat_id})},
            ],
            "structuredContent": {"answer": answer, "chat_id": chat_id},
        }
