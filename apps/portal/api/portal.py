# coding=utf-8
"""
@project: MaxKB
@Author：MaxKB
@file： portal.py
@date：2026/8/3
@desc: 门户API文档
"""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import DefaultResultSerializer
from users.serializers.login import LoginRequest


class PortalAPI(APIMixin):
    class Get(APIMixin):
        @staticmethod
        def get_response():
            return DefaultResultSerializer

    class Save(APIMixin):
        @staticmethod
        def get_request():
            return {
                "multipart/form-data": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "门户名称"},
                        "description": {"type": "string", "description": "门户描述"},
                        "logo": {"type": "string", "format": "binary", "description": "门户Logo"},
                        "tab_logo": {"type": "string", "format": "binary", "description": "浏览器Tab Logo"},
                        "enable_public_access": {"type": "boolean", "description": "是否开启公开访问"},
                        "enable_api": {"type": "boolean", "description": "是否开启API服务"},
                        "enable_auth": {"type": "boolean", "description": "是否开启身份认证"},
                        "auth_config": {"type": "object", "description": "身份认证配置"},
                        "enable_cors": {"type": "boolean", "description": "是否开启跨域设置"},
                        "cors_config": {"type": "object", "description": "跨域配置"},
                    },
                }
            }

        @staticmethod
        def get_response():
            return DefaultResultSerializer

    class Application(APIMixin):
        @staticmethod
        def get_parameters():
            return [
                OpenApiParameter(
                    name="current_page",
                    description="当前页码",
                    type=OpenApiTypes.INT,
                    location="path",
                    required=True,
                ),
                OpenApiParameter(
                    name="page_size",
                    description="每页数量",
                    type=OpenApiTypes.INT,
                    location="path",
                    required=True,
                ),
                OpenApiParameter(
                    name="name",
                    description="应用名称搜索",
                    type=OpenApiTypes.STR,
                    location="query",
                    required=False,
                ),
            ]

        @staticmethod
        def get_response():
            return DefaultResultSerializer

    class Login(APIMixin):
        @staticmethod
        def get_request():
            return LoginRequest

        @staticmethod
        def get_response():
            return DefaultResultSerializer

    class Info(APIMixin):
        @staticmethod
        def get_response():
            return DefaultResultSerializer

    class Logout(APIMixin):
        @staticmethod
        def get_response():
            return DefaultResultSerializer

    class Conversation(APIMixin):
        @staticmethod
        def get_parameters():
            return [
                OpenApiParameter(
                    name="current_page",
                    description="当前页码",
                    type=OpenApiTypes.INT,
                    location="path",
                    required=True,
                ),
                OpenApiParameter(
                    name="page_size",
                    description="每页数量",
                    type=OpenApiTypes.INT,
                    location="path",
                    required=True,
                ),
                OpenApiParameter(
                    name="name",
                    description="应用名称搜索",
                    type=OpenApiTypes.STR,
                    location="query",
                    required=False,
                ),
            ]

        @staticmethod
        def get_response():
            return DefaultResultSerializer
