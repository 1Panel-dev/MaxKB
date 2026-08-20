# coding=utf-8
"""
@project: MaxKB
@Author：MaxKB
@file： portal.py
@date：2026/8/14
@desc: 门户配置序列化器
"""

from django.db.models import Exists, OuterRef
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import Application, Chat
from application.models.application_access_token import ApplicationAccessToken
from common.db.search import page_search
from system_manage.models.chat_user import (
    ChatUser,
    ResourceChatUserAuthorize,
    ResourceChatUserGroupAuthorize,
    ResourceType,
    UserGroupRelation,
)


class PortalApplicationAuthMixin:
    """门户应用授权过滤公共逻辑"""

    @staticmethod
    def get_authorized_application_queryset(user_id):
        public_apps = ApplicationAccessToken.objects.filter(application_id=OuterRef("id"), authentication=False)
        if not ChatUser.objects.filter(id=user_id).exists():
            return Application.objects.filter(is_publish=True, is_portal=True).filter(Exists(public_apps))
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
        return Application.objects.filter(is_publish=True, is_portal=True).filter(
            Exists(public_apps) | (Exists(authed_token_exists) & (Exists(direct_auth) | Exists(group_auth)))
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
            queryset = queryset.filter(id__in=self.get_authorized_application_queryset(user_id).values("id"))
            return page_search(
                current_page,
                page_size,
                queryset,
                post_records_handler=lambda app: ApplicationResponseSerializer(app).data,
            )


class PortalHistoricalConversationResponseSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    abstract = serializers.CharField(required=True)
    create_time = serializers.CharField(required=True)
    update_time = serializers.CharField(required=True)
    application = serializers.SerializerMethodField()

    def get_application(self, chat):
        return {
            "id": str(chat.application_id),
            "name": chat.application.name,
            "icon": chat.application.icon,
        }


class PortalHistoricalConversationSerializer(serializers.Serializer):
    class Query(PortalApplicationAuthMixin, serializers.Serializer):
        name = serializers.CharField(
            required=False, allow_blank=True, label=_("Application Name"), help_text=_("Application name")
        )

        def get_query_set(self, user_id):
            queryset = Chat.objects.filter(
                chat_user_id=user_id,
                is_deleted=False,
                application_id__in=self.get_authorized_application_queryset(user_id).values("id"),
            )
            name = self.data.get("name")
            if name:
                queryset = queryset.filter(application__name__icontains=name)
            return queryset.select_related("application").order_by("-update_time", "id")

        def page(self, current_page, page_size, user_id, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return page_search(
                current_page,
                page_size,
                self.get_query_set(user_id),
                post_records_handler=lambda chat: PortalHistoricalConversationResponseSerializer(chat).data,
            )
