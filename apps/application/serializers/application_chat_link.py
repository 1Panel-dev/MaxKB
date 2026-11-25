"""
@project: MaxKB
@Author: niu
@file: application_chat_link.py
@date: 2026/2/9 10:50
@desc:
"""

import re

from django.core.cache import cache
from django.db.models import F, Q, QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import Chat, ChatShareLink, ShareLinkType, ChatRecord
from common.constants.cache_version import Cache_Version
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.exception.app_exception import AppApiException
from common.utils.chat_link_code import UUIDEncoder
from knowledge.models import FileSourceType
import uuid_utils.compat as uuid


class ShareChatRecordModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRecord
        fields = ["id", "problem_text", "answer_text", "answer_text_list", "create_time", "question", "messages"]


def get_application_setting(application_id):
    application_setting_model = DatabaseModelManage.get_model("application_setting")
    license_is_valid = cache.get(
        Cache_Version.SYSTEM.get_key(key="license_is_valid"), version=Cache_Version.SYSTEM.get_version()
    )
    if application_setting_model is None or not license_is_valid:
        return None
    return QuerySet(application_setting_model).filter(application_id=application_id).first()


def validate_share_enabled(application_setting):
    if application_setting is not None and not application_setting.show_share:
        raise AppApiException(500, _("Application sharing is not enabled"))


class ChatRecordShareLinkRequestSerializer(serializers.Serializer):
    chat_record_ids = serializers.ListSerializer(
        child=serializers.UUIDField(), required=False, allow_empty=False, label=_("Chat record IDs")
    )
    is_current_all = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        if not attrs.get("is_current_all") and not attrs.get("chat_record_ids"):
            raise serializers.ValidationError(_("Chat record ids can not be empty"))
        return attrs


def extract_oss_file_urls(content):
    """从聊天记录内容中提取所有 ./oss/file/ 开头的链接"""
    file_urls = []
    if isinstance(content, str):
        file_urls.extend(re.findall(r"\./oss/file/[\w-]+", content))
    elif isinstance(content, dict):
        for value in content.values():
            file_urls.extend(extract_oss_file_urls(value))
    elif isinstance(content, (list, tuple)):
        for value in content:
            file_urls.extend(extract_oss_file_urls(value))
    return file_urls


def is_public_chat_attachment(file):
    """A public link grants access only to attachments in its selected records."""
    if file.source_type != FileSourceType.CHAT:
        return False
    links = ChatShareLink.objects.filter(
        chat_id=file.source_id,
        chat__is_deleted=False,
        application_id=F("chat__application_id"),
        share_type=ShareLinkType.PUBLIC,
    )
    application_id = links.values_list("application_id", flat=True).first()
    if application_id is None:
        return False
    setting = get_application_setting(application_id)
    if setting is not None and not setting.show_share:
        return False
    url = f"./oss/file/{file.id}"
    candidates = (
        ChatRecord.objects.filter(chat_id=file.source_id)
        .filter(Q(messages__icontains=url) | Q(question__icontains=url) | Q(answer_text_list__icontains=url))
        .values_list("id", "messages", "question", "answer_text_list")
    )
    record_ids = [record_id for record_id, *fields in candidates if url in extract_oss_file_urls(fields)]
    return bool(record_ids) and links.filter(chat_record_ids__overlap=record_ids).exists()


class ChatRecordShareLinkSerializer(serializers.Serializer):
    chat_id = serializers.UUIDField(required=True, label=_("Conversation ID"))
    application_id = serializers.UUIDField(required=True, label=_("Application ID"))
    user_id = serializers.UUIDField(required=False, label=_("User ID"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        chat_id = self.data.get("chat_id")
        application_id = self.data.get("application_id")
        user_id = self.data.get("user_id")

        chat_query_set = Chat.objects.filter(
            id=chat_id, application_id=application_id, chat_user_id=user_id, is_deleted=False
        )
        if not chat_query_set.exists():
            raise AppApiException(500, _("Chat id does not exist"))

    def generate_link(self, instance, with_valid=True):
        if with_valid:
            request_serializer = ChatRecordShareLinkRequestSerializer(data=instance)
            request_serializer.is_valid(raise_exception=True)
            self.is_valid(raise_exception=True)
            validate_share_enabled(get_application_setting(self.data.get("application_id")))
            if not instance.get("is_current_all", False):
                chat_record_ids: list[str] = instance.get("chat_record_ids")

                record_count = ChatRecord.objects.filter(
                    id__in=chat_record_ids, chat_id=self.data.get("chat_id")
                ).count()
                if record_count != len(chat_record_ids):
                    raise AppApiException(500, _("Invalid chat record ids"))
        chat_id = self.data.get("chat_id")
        application_id = self.data.get("application_id")
        user_id = self.data.get("user_id")

        is_current_all = instance.get("is_current_all", False)
        if is_current_all:
            sorted_ids = list(
                ChatRecord.objects.filter(chat_id=chat_id).order_by("create_time").values_list("id", flat=True)
            )
        else:
            chat_record_ids: list[str] = instance.get("chat_record_ids")
            sorted_ids = list(
                ChatRecord.objects.filter(id__in=chat_record_ids).order_by("create_time").values_list("id", flat=True)
            )

        existing = ChatShareLink.objects.filter(
            chat_id=chat_id,
            application_id=application_id,
            share_type=ShareLinkType.PUBLIC,
            user_id=user_id,
            chat_record_ids=sorted_ids,
        ).first()

        if existing:
            return {"link": UUIDEncoder.encode(existing.id)}
        chat_share_link_model = ChatShareLink(
            id=uuid.uuid7(),
            chat_id=chat_id,
            application_id=application_id,
            share_type=ShareLinkType.PUBLIC,
            user_id=user_id,
            chat_record_ids=sorted_ids,
        )
        chat_share_link_model.save()

        link = UUIDEncoder.encode(chat_share_link_model.id)

        return {"link": link}


class ChatShareLinkDetailSerializer(serializers.Serializer):
    link = serializers.CharField(required=True, label=_("Link"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)

        link = self.data.get("link")
        share_link_id = UUIDEncoder.decode_to_str(link)

        share_link_query_set = ChatShareLink.objects.filter(
            id=share_link_id, share_type=ShareLinkType.PUBLIC, application_id=F("chat__application_id")
        ).first()
        if not share_link_query_set:
            raise AppApiException(500, _("Share link does not exist"))
        if share_link_query_set.chat.is_deleted:
            raise AppApiException(500, _("Chat has been deleted"))

        return share_link_query_set

    def get_record_list(self):
        share_link_model = self.is_valid(raise_exception=True)

        chat_record_model_list = ChatRecord.objects.filter(
            id__in=share_link_model.chat_record_ids, chat_id=share_link_model.chat_id
        ).order_by("create_time")

        abstract = Chat.objects.filter(id=share_link_model.chat_id).values_list("abstract", flat=True).first()
        chat_record_list = ShareChatRecordModelSerializer(chat_record_model_list, many=True).data

        application_setting = get_application_setting(share_link_model.application_id)
        validate_share_enabled(application_setting)
        app_info = {}
        if application_setting is not None:
            app_info = {
                "avatar": application_setting.avatar,
                "show_avatar": application_setting.show_avatar,
                "user_avatar": application_setting.user_avatar,
                "show_user_avatar": application_setting.show_user_avatar,
                "custom_theme": application_setting.custom_theme or {"theme_color": "", "header_font_color": ""},
                "chat_background": application_setting.chat_background,
            }

        return {"abstract": abstract, "chat_record_list": chat_record_list, "app_info": app_info}
