# coding=utf-8
"""
@project: maxkb
@Author：虎
@file： static_headers_middleware.py
@date：2024/3/13 18:26
@desc:
"""

import re
from html import escape

from django.utils.deprecation import MiddlewareMixin

from common.cache_data.application_access_token_cache import get_application_access_token
from maxkb.const import CONFIG
from portal.models import get_portal_setting
from portal.serializers.portal import PortalSerializer

# 路由白名单与前端 ui/src/router/chat/routes.ts 保持一致（路径不含 chat 前缀）
# 门户页路由
PORTAL_PAGE_ROUTES = [
    re.compile(r"/portal"),  # /portal
    re.compile(r"/portal/login"),  # /portal/login
    re.compile(r"/portal/applications"),  # /portal/applications
    re.compile(r"/portal/a/[^/]+"),  # /portal/a/:applicationId
    re.compile(r"/portal/a/[^/]+/c/[^/]+"),  # /portal/a/:applicationId/c/:chatId
]

# 单应用对话页路由
CHAT_PAGE_ROUTES = [
    re.compile(r"/(?P<access_token>[^/]+)"),  # /:accessToken
    re.compile(r"/(?P<access_token>[^/]+)/"),  # /:accessToken/
    re.compile(r"/(?P<access_token>[^/]+)/login"),  # /:accessToken/login
    re.compile(r"/(?P<access_token>[^/]+)/c/[^/]+"),  # /:accessToken/c/:chatId
]


def is_portal_page(route_path: str):
    return any(route.fullmatch(route_path) for route in PORTAL_PAGE_ROUTES)


def get_chat_page_access_token(route_path: str):
    """从单应用对话页地址中取出 access_token，不在白名单内时返回 None。"""
    for route in CHAT_PAGE_ROUTES:
        matched = route.fullmatch(route_path)
        if matched:
            access_token = matched.group("access_token")
            return None if access_token in ("api", "undefined") else access_token
    return None


def to_absolute_icon(icon: str, chat_path: str):
    """图标以 ./ 相对地址保存，深层地址下会解析到错误目录，改为 chat 前缀下的绝对地址。"""
    return chat_path + icon[1:] if icon.startswith("./") else icon


def replace_head(response, chat_path: str, icon=None, title=None):
    """替换页面默认图标与标题，为空时保留默认值。"""
    content = response.content.decode("utf-8")
    if icon:
        content = content.replace(
            f'<link rel="icon" href="{chat_path}/favicon.ico" />',
            f'<link rel="icon" href="{escape(to_absolute_icon(icon, chat_path))}" />',
        )
    if title:
        content = content.replace("<title>MaxKB</title>", f"<title>{escape(title)}</title>")
    response.content = content.encode("utf-8")


class ChatHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        chat_path = CONFIG.get_chat_path()
        if not request.path.startswith(chat_path + "/"):
            return response
        route_path = request.path[len(chat_path) :]
        if is_portal_page(route_path):
            if PortalSerializer._is_license_valid():
                replace_head(response, chat_path, icon=get_portal_setting("logo"))
            return response
        access_token = get_chat_page_access_token(route_path)
        if access_token is None:
            return response
        application_access_token = get_application_access_token(access_token, True)
        if application_access_token is None:
            return response
        if application_access_token.get("white_active", False):
            # 添加自定义的响应头
            white_list = application_access_token.get("white_list", [])
            response["Content-Security-Policy"] = f"frame-ancestors {' '.join(white_list)}"
        replace_head(
            response,
            chat_path,
            icon=application_access_token.get("application_icon"),
            title=application_access_token.get("application_name"),
        )
        return response
