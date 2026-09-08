# coding=utf-8
"""
@project: MaxKB
@Author：MaxKB
@file： portal.py
@date：2026/8/14
@desc: 门户配置序列化器
"""

from django.core.cache import cache
from django.db.models import Exists, OuterRef
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import Application, Chat
from application.models.application_access_token import ApplicationAccessToken
from common.constants.cache_version import Cache_Version
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.db.search import page_search
from system_manage.models.chat_user import (
    ChatUser,
    ResourceChatUserAuthorize,
    ResourceChatUserGroupAuthorize,
    ResourceType,
    UserGroupRelation,
)


def build_application_setting_dict(setting, show_source):
    return {
        "show_source": show_source,
        "show_history": setting.show_history,
        "draggable": setting.draggable,
        "show_guide": setting.show_guide,
        "avatar": setting.avatar,
        "show_avatar": setting.show_avatar,
        "float_icon": setting.float_icon,
        "disclaimer": setting.disclaimer,
        "disclaimer_value": setting.disclaimer_value,
        "custom_theme": setting.custom_theme or {"theme_color": "", "header_font_color": ""},
        "user_avatar": setting.user_avatar,
        "show_user_avatar": setting.show_user_avatar,
        "show_share": setting.show_share,
        "float_location": setting.float_location or {"x": {"type": "", "value": ""}, "y": {"type": "", "value": ""}},
        "chat_background": setting.chat_background,
    }


def get_application_settings_map(application_ids):
    """批量返回 application_id -> 门户设置信息；license 无效或模型缺失时返回空 dict"""
    application_setting_model = DatabaseModelManage.get_model("application_setting")
    if application_setting_model is None or not application_ids:
        return {}
    license_is_valid = cache.get(
        Cache_Version.SYSTEM.get_key(key="license_is_valid"), version=Cache_Version.SYSTEM.get_version()
    )
    if not license_is_valid:
        return {}
    settings = application_setting_model.objects.filter(application_id__in=application_ids)
    access_tokens = ApplicationAccessToken.objects.filter(application_id__in=application_ids).values_list(
        "application_id", "show_source"
    )
    token_map = {str(application_id): show_source for application_id, show_source in access_tokens}
    return {
        str(setting.application_id): build_application_setting_dict(
            setting, token_map.get(str(setting.application_id), False)
        )
        for setting in settings
    }


class PortalApplicationAuthMixin:
    """门户应用授权过滤公共逻辑"""

    @staticmethod
    def get_authorized_application_ids(user_id):
        public_apps = ApplicationAccessToken.objects.filter(application_id=OuterRef("id"), authentication=False)
        if not ChatUser.objects.filter(id=user_id).exists():
            return (
                Application.objects.filter(is_publish=True, is_portal=True)
                .filter(Exists(public_apps))
                .values_list("id", flat=True)
            )
        authed_token_exists = ApplicationAccessToken.objects.filter(application_id=OuterRef("id"), authentication=True)
        direct_auth = ResourceChatUserAuthorize.objects.filter(
            resource_id=OuterRef("id"), resource_type=ResourceType.APPLICATION.value, is_auth=True, user_id=user_id
        )
        user_groups = UserGroupRelation.objects.filter(user_id=user_id).values_list("group_id", flat=True)
        group_auth = ResourceChatUserGroupAuthorize.objects.filter(
            resource_id=OuterRef("id"),
            resource_type=ResourceType.APPLICATION.value,
            is_auth=True,
            user_group_id__in=user_groups,
        )
        return (
            Application.objects.filter(is_publish=True, is_portal=True)
            .filter(Exists(public_apps) | (Exists(authed_token_exists) & (Exists(direct_auth) | Exists(group_auth))))
            .values_list("id", flat=True)
        )


class ApplicationResponseSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    desc = serializers.CharField(required=True)
    icon = serializers.CharField(required=True)
    type = serializers.CharField(required=True)
    dialogue_number = serializers.IntegerField(required=True)
    prologue = serializers.CharField(required=True)
    is_publish = serializers.BooleanField(required=True)
    is_portal = serializers.BooleanField(required=True)


class PortalApplicationSerializer(serializers.Serializer):
    class Query(PortalApplicationAuthMixin, serializers.Serializer):
        name = serializers.CharField(
            required=False, allow_blank=True, label=_("Application Name"), help_text=_("Application name")
        )

        def get_query_set(self):
            queryset = Application.objects.filter(is_publish=True, is_portal=True)
            name = self.data.get("name")
            if name:
                queryset = queryset.filter(name__icontains=name)
            return queryset.order_by("-create_time")

        def page(self, current_page, page_size, user_id, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            queryset = self.get_query_set()
            queryset = queryset.filter(id__in=self.get_authorized_application_ids(user_id))
            return page_search(
                current_page,
                page_size,
                queryset,
                post_records_handler=lambda app: ApplicationResponseSerializer(app).data,
            )


def get_recent_chats_map(user_id, application_ids, limit=5):
    """批量返回 application_id -> 该应用最近的 limit 条历史会话；show_history=false 的应用不在此表里"""
    chats = Chat.objects.filter(chat_user_id=user_id, is_deleted=False, application_id__in=application_ids).order_by(
        "application_id", "-update_time", "id"
    )
    result = {}
    for chat in chats:
        key = str(chat.application_id)
        if len(result.get(key, [])) >= limit:
            continue
        result.setdefault(key, []).append(
            {
                "id": str(chat.id),
                "abstract": chat.abstract,
                "create_time": str(chat.create_time),
                "update_time": str(chat.update_time),
            }
        )
    return result


class PortalHistoricalConversationSerializer(serializers.Serializer):
    class Query(PortalApplicationAuthMixin, serializers.Serializer):
        name = serializers.CharField(
            required=False, allow_blank=True, label=_("Application Name"), help_text=_("Application name")
        )

        def get_query_set(self, user_id):
            # 主表是应用：返回用户有权限访问的已发布门户应用
            queryset = Application.objects.filter(
                is_publish=True,
                is_portal=True,
                id__in=self.get_authorized_application_ids(user_id),
            )
            name = self.data.get("name")
            if name:
                queryset = queryset.filter(name__icontains=name)
            return queryset.order_by("-create_time")

        def page(self, current_page, page_size, user_id, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            result = page_search(
                current_page,
                page_size,
                self.get_query_set(user_id),
                post_records_handler=lambda app: {
                    "id": str(app.id),
                    "name": app.name,
                    "icon": app.icon,
                },
            )
            app_ids = [record["id"] for record in result["records"]]
            settings_map = get_application_settings_map(app_ids)
            show_history_ids = [aid for aid in app_ids if settings_map.get(aid, {}).get("show_history")]
            chat_map = get_recent_chats_map(user_id, show_history_ids) if show_history_ids else {}
            for record in result["records"]:
                record.update(settings_map.get(record["id"], {}))
                record["conversations"] = chat_map.get(record["id"], [])
            return result
