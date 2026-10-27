# coding=utf-8

import hashlib

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.db.search import page_search
from system_manage.models import ChatUserApiKey


class ChatUserApiKeyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatUserApiKey
        fields = ["id", "secret_key", "is_active", "create_time", "user_id"]


class ChatUserApiKeySerializer(serializers.Serializer):
    user_id = serializers.UUIDField(required=True, label=_("user id"))
    order_by = serializers.CharField(required=False, label=_("order by"), allow_null=True, allow_blank=True)

    def generate(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        user_id = self.data.get("user_id")
        # 一个用户只保留一个 key；每次生成都作废旧 key 并重新生成一个新的
        QuerySet(ChatUserApiKey).filter(user_id=user_id).delete()
        api_key = ChatUserApiKey(
            id=uuid.uuid7(),
            secret_key=f"chat-{hashlib.md5(uuid.uuid7().bytes).hexdigest()}",
            user_id=user_id,
        )
        api_key.save()
        return ChatUserApiKeyModelSerializer(api_key).data
