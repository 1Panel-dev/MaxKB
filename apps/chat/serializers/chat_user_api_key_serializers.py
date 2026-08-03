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
        fields = ['id', 'secret_key', 'is_active', 'create_time', 'user_id']


class ChatUserApiKeySerializer(serializers.Serializer):
    user_id = serializers.UUIDField(required=True, label=_('user id'))
    order_by = serializers.CharField(required=False, label=_('order by'), allow_null=True, allow_blank=True)

    def generate(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        api_key = ChatUserApiKey(
            id=uuid.uuid7(),
            secret_key=hashlib.md5(uuid.uuid7().bytes).hexdigest(),
            user_id=self.data.get('user_id')
        )
        api_key.save()
        return ChatUserApiKeyModelSerializer(api_key).data

    def page(self, current_page: int, page_size: int, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        user_id = self.data.get('user_id')
        query_set = QuerySet(ChatUserApiKey).filter(user_id=user_id)
        order_by = '-create_time' if self.data.get('order_by') is None or self.data.get('order_by') == '' else self.data.get('order_by')
        query_set = query_set.order_by(order_by)
        return page_search(current_page, page_size,
                           query_set,
                           post_records_handler=lambda u: ChatUserApiKeyModelSerializer(u).data)

    class Operate(serializers.Serializer):
        id = serializers.UUIDField(required=True, label=_('api key id'))
        user_id = serializers.UUIDField(required=True, label=_('user id'))

        def destroy(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            QuerySet(ChatUserApiKey).filter(
                id=self.data.get('id'), user_id=self.data.get('user_id')
            ).delete()
            return True