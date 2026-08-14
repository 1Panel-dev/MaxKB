# coding=utf-8
"""
@project: maxkb
@Author：虎
@file： init_doc.py
@date：2024/5/24 14:11
@desc:
"""

import hashlib

from django.urls import path, URLPattern, URLResolver
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from maxkb.const import CONFIG

chat_api_prefix = CONFIG.get_chat_path()[1:] + "/api/"


def flatten_url_patterns(patterns, prefix=""):
    """
    递归展开 urlpatterns，遇到 include() 产生的 URLResolver 时向下钻取，
    累加各层路由前缀，最终产出 (完整路由字符串, URLPattern) 元组。
    """
    for entry in patterns:
        if isinstance(entry, URLResolver):
            yield from flatten_url_patterns(entry.url_patterns, prefix + str(entry.pattern))
        elif isinstance(entry, URLPattern):
            yield prefix + str(entry.pattern), entry


def init_app_doc(system_urlpatterns):
    system_urlpatterns += [
        path(f"{CONFIG.get_admin_path()[1:]}/api-doc/schema/", SpectacularAPIView.as_view(), name="schema"),
        # schema的配置文件的路由，下面两个ui也是根据这个配置文件来生成的
        path(
            f"{CONFIG.get_admin_path()[1:]}/api-doc/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),  # swagger-ui的路由
    ]


class ChatSpectacularSwaggerView(SpectacularSwaggerView):
    @staticmethod
    def _swagger_ui_resource(filename):
        return f"{CONFIG.get_chat_path()}/api-doc/swagger-ui-dist/{filename}"

    @staticmethod
    def _swagger_ui_favicon():
        return f"{CONFIG.get_chat_path()}/api-doc/swagger-ui-dist/favicon-32x32.png"


def build_curated_patterns(chat_urlpatterns, doc_names):
    """按 name 集合从（递归展开后的）chat 路由里挑出 curated 端点，重建为带完整 path 的 URLPattern。"""
    return [
        URLPattern(
            pattern=f"{chat_api_prefix}{full_path}", callback=url.callback, default_args=url.default_args, name=url.name
        )
        for full_path, url in flatten_url_patterns(chat_urlpatterns)
        if doc_names.__contains__(getattr(url, "name", None))
    ]


def init_chat_doc(system_urlpatterns, chat_urlpatterns):
    chat_path = CONFIG.get_chat_path()[1:]
    v3_patterns = build_curated_patterns(
        chat_urlpatterns,
        ["v3_chat", "v3_open", "v3_profile", "v3_portal_application", "v3_portal_historical_conversation"],
    )
    v2_patterns = build_curated_patterns(chat_urlpatterns, ["chat", "open", "profile", "anonymous"])
    system_urlpatterns += [
        # v3 curated 文档（主路径）
        path(
            f"{chat_path}/api-doc/schema/", SpectacularAPIView.as_view(patterns=v3_patterns), name="chat_schema"
        ),  # schema的配置文件的路由，下面ui根据它生成
        path(
            f"{chat_path}/api-doc/", ChatSpectacularSwaggerView.as_view(url_name="chat_schema"), name="swagger-ui"
        ),  # swagger-ui的路由
        # v2 curated 文档（保留）
        path(
            f"{chat_path}/api-doc/v2/schema/", SpectacularAPIView.as_view(patterns=v2_patterns), name="chat_schema_v2"
        ),
        path(
            f"{chat_path}/api-doc/v2/",
            ChatSpectacularSwaggerView.as_view(url_name="chat_schema_v2"),
            name="swagger-ui-v2",
        ),
    ]


def encrypt(text):
    md5 = hashlib.md5()
    md5.update(text.encode())
    result = md5.hexdigest()
    return result


def get_call(application_urlpatterns, patterns, params, func):
    def run():
        if params["valid"]():
            func(*params["get_params"](application_urlpatterns, patterns))

    return run


init_list = [
    (
        init_app_doc,
        {
            "valid": lambda: (
                CONFIG.get("DOC_PASSWORD") is not None
                and encrypt(CONFIG.get("DOC_PASSWORD")) == "d4fc097197b4b90a122b92cbd5bbe867"
            ),
            "get_call": get_call,
            "get_params": lambda application_urlpatterns, patterns: (application_urlpatterns,),
        },
    ),
    (
        init_chat_doc,
        {
            "valid": lambda: (
                CONFIG.get("DOC_PASSWORD") is not None
                and encrypt(CONFIG.get("DOC_PASSWORD")) == "d4fc097197b4b90a122b92cbd5bbe867"
                or True
            ),
            "get_call": get_call,
            "get_params": lambda application_urlpatterns, patterns: (application_urlpatterns, patterns),
        },
    ),
]


def init_doc(system_urlpatterns, chat_patterns):
    for init, params in init_list:
        if params["valid"]():
            get_call(system_urlpatterns, chat_patterns, params, init)()
