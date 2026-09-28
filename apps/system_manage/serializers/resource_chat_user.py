# coding=utf-8
"""
    @project: MaxKB-xpack
    @Author：虎虎
    @file： resource_chat_user.py
    @date：2025/6/5 16:25
    @desc:
"""
import os
from typing import List, Dict

from django.db import models
from django.db.models import QuerySet, Q
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.db.search import get_dynamics_model, native_page_search, native_search
from common.exception.app_exception import AppApiException
from common.utils.common import get_file_content
from maxkb.conf import PROJECT_DIR
from system_manage.models import ChatUser, ResourceChatUserAuthorize


class ResourceChatUserResultSerializer(serializers.ModelSerializer):
    is_auth = serializers.BooleanField(required=True, label=_('is auth'))

    class Meta:
        model = ChatUser
        fields = '__all__'


class ResourceChatUserQuerySerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=False, label=_('workspace id'))
    resource_type = serializers.CharField(required=True, label=_('Resource type'))
    resource_id = serializers.UUIDField(required=True, label=_('Resource id'))
    username = serializers.CharField(required=False, allow_null=True,
                                     label=_('Username'))
    nick_name = serializers.CharField(required=False, allow_null=True,
                                      label=_('Nickname'))
    source = serializers.CharField(required=False, allow_null=True,
                                   label=_('Source'))

    user_group_id = serializers.CharField(required=True, label=_('User group id'))

    def get_query_set(self):
        username = self.data.get('username')
        nick_name = self.data.get('nick_name')
        source = self.data.get('source')
        workspace_id = self.data.get("workspace_id")
        user_group_id = self.data.get('user_group_id')
        resource_id = self.data.get('resource_id')
        resource_type = self.data.get('resource_type')
        resource_chat_user_authorize_query_set = QuerySet(ResourceChatUserAuthorize).filter(resource_id=resource_id,
                                                                                            resource_type=resource_type)
        query_set = QuerySet(model=get_dynamics_model({
            'username': models.CharField(),
            'nick_name': models.CharField(),
            'source': models.CharField(),
            "user_group_relation.group_id": models.CharField(),
            'create_time': models.DateTimeField()
        }))
        if username is not None:
            query_set = query_set.filter(
                Q(username__contains=username))
        if nick_name is not None:
            query_set = query_set.filter(
                Q(nick_name__contains=nick_name))
        if source is not None:
            query_set = query_set.filter(
                Q(source=source))
        if workspace_id is not None:
            resource_chat_user_authorize_query_set = resource_chat_user_authorize_query_set.filter(
                workspace_id=workspace_id)
        else:
            resource_chat_user_authorize_query_set = resource_chat_user_authorize_query_set.filter(
                workspace_id__isnull=True)
        if user_group_id is not None:
            query_set = query_set.filter(**{'user_group_relation.group_id': user_group_id})
        query_set = query_set.order_by("-create_time")
        return {'default_query_set': query_set,
                'resource_chat_user_authorize_query_set': resource_chat_user_authorize_query_set}

    def list(self):
        self.is_valid(raise_exception=True)
        return native_search(
            self.get_query_set(),
            select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "system_manage", 'sql', 'list_resource_chat_user.sql')
            )
        )

    def page(self, current_page: int, page_size: int):
        self.is_valid(raise_exception=True)
        return native_page_search(
            current_page,
            page_size,
            self.get_query_set(),
            select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "system_manage", 'sql', 'list_resource_chat_user.sql')
            ),
            post_records_handler=lambda r: r
        )


class ResourceChatUserEditItemSerializer(serializers.Serializer):
    chat_user_id = serializers.UUIDField(required=True, label=_("Chat user id"))
    is_auth = serializers.BooleanField(required=True, label=_("Is auth"))


class ResourceChatUserEditSerializer(serializers.ListSerializer):
    child = ResourceChatUserEditItemSerializer(required=True)

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        chat_user_list = QuerySet(ChatUser).values('id').filter(
            id__in=[instance.get('chat_user_id') for instance in self.data])
        if len(chat_user_list) != len(self.data):
            raise AppApiException(500, "存在未知的chat_user_id")


class ResourceChatUserSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=False, label=_('workspace id'))
    resource_type = serializers.CharField(required=True, label=_('Resource type'))
    resource_id = serializers.UUIDField(required=True, label=_('Resource id'))
    user_group_id = serializers.CharField(required=True, label=_('User group id'))

    def edit(self, instance_list: List[Dict]):
        self.is_valid(raise_exception=True)
        ResourceChatUserEditSerializer(data=instance_list).is_valid(raise_exception=True)

        workspace_id = self.data.get('workspace_id')
        resource_id = self.data.get('resource_id')
        resource_type = self.data.get('resource_type')
        user_group_id = self.data.get('user_group_id')
        resource_chat_user_authorize_list = [
            ResourceChatUserAuthorize(workspace_id=workspace_id, user_id=instance.get('chat_user_id'),
                                      is_auth=instance.get('is_auth'),
                                      user_group_id=user_group_id,
                                      resource_id=resource_id, resource_type=resource_type) for instance in
            instance_list]
        QuerySet(ResourceChatUserAuthorize).filter(
            user_id__in=[instance.get('chat_user_id') for instance in instance_list], resource_id=resource_id,
            resource_type=resource_type).filter(
            **({'user_group_id__isnull': True} if user_group_id is None else {'user_group_id': user_group_id})).delete()
        old_resource_chat_user_authorize_list = []
        create_list = []
        update_list = []
        for resource_chat_user_authorize in resource_chat_user_authorize_list:
            is_exist = False
            for old_resource_chat_user_authorize in old_resource_chat_user_authorize_list:
                if (resource_chat_user_authorize.resource_id == str(old_resource_chat_user_authorize.resource_id) and
                        resource_chat_user_authorize.user_id == str(old_resource_chat_user_authorize.user_id)
                        and str(resource_chat_user_authorize.user_group_id) == str(
                            old_resource_chat_user_authorize.user_group_id)):
                    old_resource_chat_user_authorize.is_auth = resource_chat_user_authorize.is_auth
                    update_list.append(old_resource_chat_user_authorize)
                    is_exist = True
                    break
            if not is_exist:
                create_list.append(resource_chat_user_authorize)
        QuerySet(ResourceChatUserAuthorize).bulk_create(create_list) if len(
            create_list) > 0 else None
        QuerySet(ResourceChatUserAuthorize).bulk_update(update_list, ['is_auth']) if len(
            update_list) > 0 else None
        return True
