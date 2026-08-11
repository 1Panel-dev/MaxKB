# coding=utf-8

import uuid_utils.compat as uuid
from collections import defaultdict
from django.db import transaction
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.auth.constants.role_constants import RoleConstants
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.db.search import page_search
from common.exception.app_exception import AppApiException
from system_manage.models import UserGroup, UserGroupRelation
from users.models.user_group import SystemUserGroup, SystemUserGroupRelation


@transaction.atomic
def add_or_edit_user_group_relation(user, user_group_ids):
    UserGroupRelation.objects.filter(user=user).delete()
    if not user_group_ids:
        return
    groups = UserGroup.objects.filter(id__in=user_group_ids)
    if groups.count() != len(user_group_ids):
        raise AppApiException(500, _("Some user groups do not exist"))

    UserGroupRelation.objects.bulk_create([UserGroupRelation(user=user, group=group) for group in groups])


class SystemUserGroupModelSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()

    def get_count(self, obj):
        return getattr(obj, "count", 0)

    class Meta:
        model = SystemUserGroup
        fields = ["id", "name", "workspace_id", "count"]


class SystemUserGroupCreateSerializer(serializers.Serializer):
    id = serializers.CharField(required=False, label="ID")
    name = serializers.CharField(required=True, label="User Group Name")
    workspace_id = serializers.CharField(required=True, label="Workspace ID")

    def validate(self, data):
        group_id = data.get("id")
        name = data.get("name")
        workspace_id = data.get("workspace_id")
        if group_id:
            if not SystemUserGroup.objects.filter(id=group_id, workspace_id=workspace_id).exists():
                raise AppApiException(500, _("User group does not exist"))
        if name:
            queryset = SystemUserGroup.objects.filter(name=name, workspace_id=workspace_id)
            if group_id:
                queryset = queryset.exclude(id=group_id)
            if queryset.exists():
                raise AppApiException(500, _("User group name already exists"))
        return data

    def create_or_update_group(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        data = self.validated_data
        group_id = data.get("id")
        name = data["name"]
        workspace_id = data["workspace_id"]

        if group_id:
            SystemUserGroup.objects.filter(id=group_id, workspace_id=workspace_id).update(name=name)
            group = SystemUserGroup.objects.get(id=group_id, workspace_id=workspace_id)
        else:
            group = SystemUserGroup.objects.create(
                id=uuid.uuid7(),
                name=name,
                workspace_id=workspace_id,
            )
        return SystemUserGroupModelSerializer(group).data

    class UserGroupDeleteSerializer(serializers.Serializer):
        id = serializers.CharField(required=True, label="ID")
        workspace_id = serializers.CharField(required=True, label="Workspace ID")

        group = None

        def validate(self, attrs):
            self.group = SystemUserGroup.objects.filter(
                id=attrs["id"],
                workspace_id=attrs["workspace_id"],
            ).first()

            if self.group is None:
                raise AppApiException(500, _("User group does not exist"))

            return attrs

        @transaction.atomic
        def delete(self, *, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)

            self.group.delete()
            return True

    class Query(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label="Workspace ID")

        def get_query_set(self):
            return (
                SystemUserGroup.objects.filter(workspace_id=self.data.get("workspace_id"))
                .annotate(count=Count("user_relations"))
                .order_by("name")
            )

        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return SystemUserGroupModelSerializer(self.get_query_set(), many=True).data


class UserGroupAddMemberSerializer(serializers.Serializer):
    id = serializers.CharField(required=True, label="ID")
    workspace_id = serializers.CharField(required=True, label="Workspace ID")
    user_ids = serializers.ListField(child=serializers.CharField(required=True), required=True, label=_("User IDs"))

    def validate_normal_users(self, workspace_id: str, user_ids: list[str]):
        if not user_ids:
            return

        license_is_valid = DatabaseModelManage.get_model("license_is_valid") or (lambda: False)
        license_is_valid = license_is_valid() if license_is_valid() is not None else False
        if not license_is_valid:
            return

        user_id_set = set(user_ids)

        mapping_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
        valid_user_ids = set(
            str(uid)
            for uid in mapping_model.objects.filter(
                workspace_id=workspace_id,
                user_id__in=user_id_set,
                role__type=RoleConstants.USER.name,
            ).values_list("user_id", flat=True)
        )

        invalid_user_ids = user_id_set - valid_user_ids
        if invalid_user_ids:
            raise AppApiException(500, _("Unauthorized users are present"))

    def validate(self, data):
        id = data.get("id")
        workspace_id = data.get("workspace_id")
        user_ids = data.get("user_ids")
        group = SystemUserGroup.objects.filter(id=id, workspace_id=workspace_id).first()
        if not group:
            raise AppApiException(500, _("User group does not exist"))
        if not user_ids:
            raise AppApiException(500, _("User IDs cannot be empty"))

        self.validate_normal_users(workspace_id, user_ids)
        return data

    def add_member(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        user_ids = self.data.get("user_ids")
        workspace_id = self.data.get("workspace_id")

        current_user_group_ids = set(
            str(user_id)
            for user_id in SystemUserGroupRelation.objects.filter(
                group__id=self.data.get("id"), group__workspace_id=workspace_id
            ).values_list("user_id", flat=True)
        )
        to_add = set(user_ids).difference(current_user_group_ids)
        if to_add:
            SystemUserGroupRelation.objects.bulk_create(
                [
                    SystemUserGroupRelation(id=uuid.uuid7(), user_id=user_id, group_id=self.data.get("id"))
                    for user_id in to_add
                ]
            )
        return True


class UserGroupRemoveMemberSerializer(serializers.Serializer):
    id = serializers.CharField(required=True, label="ID")
    workspace_id = serializers.CharField(required=True, label="Workspace ID")
    group_relation_ids = serializers.ListField(
        child=serializers.CharField(required=True), required=True, label=_("User group relation IDs")
    )

    def validate(self, data):
        group_id = data.get("id")
        workspace_id = data.get("workspace_id")
        relation_ids = data.get("group_relation_ids")
        if not SystemUserGroup.objects.filter(id=group_id, workspace_id=workspace_id).exists():
            raise AppApiException(500, _("User group does not exist"))
        if not relation_ids:
            raise AppApiException(500, _("User group relation IDs cannot be empty"))
        return data

    def remove_member(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        data = self.validated_data
        relation_ids = data["group_relation_ids"]
        SystemUserGroupRelation.objects.filter(
            id__in=relation_ids,
            group_id=data["id"],
            group__workspace_id=data["workspace_id"],
        ).delete()
        return True


class UserGroupListPageSerializer(serializers.Serializer):
    class Query(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label="Workspace ID")
        group_id = serializers.CharField(required=True, label=_("Group ID"))
        username = serializers.CharField(required=False, label=_("Username"), allow_null=True)
        nick_name = serializers.CharField(required=False, label=_("Nick Name"), allow_null=True)
        source = serializers.CharField(required=False, label=_("Source"), allow_null=True)

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=raise_exception)
            group_id = self.data.get("group_id")
            workspace_id = self.data.get("workspace_id")
            if not SystemUserGroup.objects.filter(id=group_id, workspace_id=workspace_id).exists():
                raise AppApiException(500, _("User group does not exist"))

        def page(self, current_page, page_size):
            self.is_valid()
            query_set = self.get_query_set()
            result = page_search(
                current_page,
                page_size,
                query_set,
                post_records_handler=lambda relation: {
                    "id": str(relation.user.id),
                    "username": relation.user.username,
                    "nick_name": relation.user.nick_name,
                    "email": relation.user.email,
                    "system_user_group_relation_id": str(relation.id),
                },
            )

            # 补充用户在指定工作空间的角色
            role_map = self._get_user_role_map(self.data.get("workspace_id"), result["records"])
            for user in result["records"]:
                user["roles"] = role_map.get(str(user["id"]), [])
            return result

        def _get_user_role_map(self, workspace_id, records):
            """查询 records 中用户在指定工作空间的角色列表"""
            role_model = DatabaseModelManage.get_model("role_model")
            user_role_relation_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
            if not role_model or not user_role_relation_model:
                return {}

            user_ids = [str(user["id"]) for user in records]
            user_role_relations = user_role_relation_model.objects.filter(
                workspace_id=workspace_id, user_id__in=user_ids, role__type="USER"
            ).select_related("role", "user")

            role_map = defaultdict(list)
            for relation in user_role_relations:
                role_map[str(relation.user_id)].append(relation.role.role_name)
            return role_map

        def get_query_set(self):
            group_id = self.data.get("group_id")
            username = self.data.get("username")
            nick_name = self.data.get("nick_name")
            source = self.data.get("source")
            query_set = SystemUserGroupRelation.objects.filter(group_id=group_id).select_related("user")

            if username is not None:
                query_set = query_set.filter(user__username__contains=username)
            if nick_name is not None:
                query_set = query_set.filter(user__nick_name__contains=nick_name)
            if source is not None:
                query_set = query_set.filter(user__source=source)
            return query_set.order_by("-user__create_time")
