import json

import uuid_utils.compat as uuid
from django.db.models import QuerySet

from application.models import ApplicationApiKey, Application, ChatUserType, ChatSourceChoices
from chat.serializers.chat import ChatSerializers


class MCPToolHandler:
    def __init__(self, auth_header):
        app_key = QuerySet(ApplicationApiKey).filter(secret_key=auth_header, is_active=True).first()
        if not app_key:
            raise PermissionError("Invalid API Key")

        self.application = QuerySet(Application).filter(id=app_key.application_id, is_publish=True).first()
        if not self.application:
            raise PermissionError("Application is not found or not published")

    def initialize(self):
        return {
            "protocolVersion": "2025-06-18",
            "serverInfo": {
                "name": "maxkb-mcp",
                "version": "1.0.0"
            },
            "capabilities": {
                "tools": {}
            }
        }

    def list_tools(self):
        return {
            "tools": [
                {
                    "name": 'ai_chat',
                    "description": f'{self.application.name} {self.application.desc}',
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string", "description": "The message to send to the AI."},
                        },
                        "required": ["message"]
                    }
                }
            ]
        }

    def _get_chat_id(self):
        from application.models import ChatUserType
        from chat.serializers.chat import OpenChatSerializers
        from common.init import init_template

        init_template.run()

        return OpenChatSerializers(data={
            'application_id': self.application.id,
            'chat_user_id': str(uuid.uuid7()),
            'chat_user_type': ChatUserType.ANONYMOUS_USER,
            'ip_address': '-',
            'source': {"type": ChatSourceChoices.ONLINE.value},
            'debug': False
        }).open()

    def call_tool(self, params):
        name = params["name"]
        args = params.get("arguments", {})
        # print(params)

        payload = {
            'message': args.get('message'),
            'stream': False,
            're_chat': False
        }
        resp = ChatSerializers(data={
            'chat_id': self._get_chat_id(),
            'chat_user_id': str(uuid.uuid7()),
            'chat_user_type': ChatUserType.ANONYMOUS_USER,
            'application_id': self.application.id,
            'ip_address': '-',
            'source': {"type": ChatSourceChoices.ONLINE.value},
            'debug': False,
        }).chat(payload)
        data = json.loads(str(resp.text))

        return {"content": [{"type": "text", "text": data.get('data', {}).get('content')}]}
