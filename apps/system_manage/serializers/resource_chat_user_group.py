import os
from typing import List

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.db.search import native_search, native_page_search
from common.exception.app_exception import AppApiException
from common.utils.common import get_file_content
from maxkb.conf import PROJECT_DIR
from system_manage.models import ResourceChatUserGroupAuthorize, UserGroup


class ResourceChatUserGroupQuerySerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=False, label=_('workspace id'))
    resource_type = serializers.CharField(required=True, label=_('Resource type'))
    resource_id = serializers.UUIDField(required=True, label=_('Resource id'))
    user_group_name = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                            label=_('User group name'))

    def get_query_set(self):
        workspace_id = self.data.get('workspace_id')
        resource_type = self.data.get('resource_type')
        resource_id = self.data.get('resource_id')
        user_group_name = self.data.get('user_group_name')

        resource_chat_user_group_authorize_query_set = QuerySet(
            ResourceChatUserGroupAuthorize).filter(resource_id=resource_id,
                                                   resource_type=resource_type)
        query_set = QuerySet(UserGroup)
        if user_group_name is not None:
            query_set = query_set.filter(name__contains=user_group_name)
        if workspace_id is not None:
            resource_chat_user_group_authorize_query_set = resource_chat_user_group_authorize_query_set.filter(
                workspace_id=workspace_id
            )
        else:
            resource_chat_user_group_authorize_query_set = resource_chat_user_group_authorize_query_set.filter(
                workspace_id__isnull=True
            )
        return {'default_query_set': query_set,
                'resource_chat_user_group_authorize_query_set': resource_chat_user_group_authorize_query_set
                }

    def list(self):
        self.is_valid(raise_exception=True)
        return native_search(
            self.get_query_set(),
            select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "system_manage", "sql", "list_resource_chat_user_group.sql")
            ))

    def page(self, current_page: int, page_size: int):
        self.is_valid(raise_exception=True)
        return native_page_search(
            current_page,
            page_size,
            self.get_query_set(),
            select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "system_manage", "sql", "list_resource_chat_user_group.sql")
            ),
            post_records_handler=lambda r: r
        )


class ResourceChatUserGroupEditItemSerializer(serializers.Serializer):
    user_group_id = serializers.CharField(required=True, label=_('user_group_id'))
    is_auth = serializers.BooleanField(required=True, label=_('is auth'))


class ResourceChatUserGroupEditSerializer(serializers.ListSerializer):
    child = ResourceChatUserGroupEditItemSerializer(required=True)

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        user_group_list = QuerySet(UserGroup).values('id').filter(
            id__in=[instance.get('user_group_id') for instance in self.data])
        if len(user_group_list) != len(self.data):
            raise AppApiException(500, "存在未知的user_group_id")


class ResourceChatUserGroupSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=False, label=_('workspace id'))
    resource_type = serializers.CharField(required=True, label=_('Resource type'))
    resource_id = serializers.UUIDField(required=True, label=_('Resource id'))

    def edit(self, instance_list: List[dict]):
        self.is_valid(raise_exception=True)
        ResourceChatUserGroupEditSerializer(data=instance_list).is_valid(raise_exception=True)

        workspace_id = self.data.get('workspace_id')
        resource_id = self.data.get('resource_id')
        resource_type = self.data.get('resource_type')
        resource_chat_user_group_authorize_list = [
            ResourceChatUserGroupAuthorize(workspace_id=workspace_id,
                                           is_auth=instance.get('is_auth'),
                                           user_group_id=instance.get('user_group_id'),
                                           resource_id=resource_id, resource_type=resource_type
                                           ) for instance in instance_list]
        old_resource_chat_user_group_authorize_list = QuerySet(ResourceChatUserGroupAuthorize).filter(
            user_group_id__in=[instance.get('user_group_id') for instance in instance_list], resource_id=resource_id,
            resource_type=resource_type)
        create_list = []
        update_list = []
        for resource_chat_user_group_authorize in resource_chat_user_group_authorize_list:
            is_exist = False
            for old_resource_chat_user_group_authorize in old_resource_chat_user_group_authorize_list:
                if (resource_chat_user_group_authorize.resource_id == str(
                        old_resource_chat_user_group_authorize.resource_id) and
                        str(resource_chat_user_group_authorize.user_group_id) == str(
                            old_resource_chat_user_group_authorize.user_group_id)):
                    old_resource_chat_user_group_authorize.is_auth = resource_chat_user_group_authorize.is_auth
                    update_list.append(old_resource_chat_user_group_authorize)
                    is_exist = True
                    break
            if not is_exist:
                create_list.append(resource_chat_user_group_authorize)
        QuerySet(ResourceChatUserGroupAuthorize).bulk_create(create_list) if len(
            create_list) > 0 else None
        QuerySet(ResourceChatUserGroupAuthorize).bulk_update(update_list, ['is_auth']) if len(
            update_list) > 0 else None
        return True
