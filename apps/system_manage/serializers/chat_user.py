# coding=utf-8
import json
import re
from collections import defaultdict

from dateutil.relativedelta import relativedelta

import uuid_utils.compat as uuid
from django.core import validators
from django.db import transaction
from django.db.models import Q, QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.constants.exception_code_constants import ExceptionCodeConstants
from common.db.search import page_search
from common.exception.app_exception import AppApiException
from common.utils.common import password_encrypt
from common.utils.rsa_util import decrypt
from system_manage.models import ChatUser, UserGroup, UserGroupRelation
from system_manage.models.chat_user_token_quota import ChatUserTokenQuota
from users.serializers.user import PASSWORD_REGEX


class ChatUserInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatUser
        fields = ["id", "username", "email", "phone", "is_active", "nick_name", "create_time", "update_time", "source"]


@transaction.atomic
def add_or_edit_user_group_relation(user, user_group_ids):
    UserGroupRelation.objects.filter(user=user).delete()
    if not user_group_ids:
        return
    groups = UserGroup.objects.filter(id__in=user_group_ids)
    if groups.count() != len(user_group_ids):
        raise AppApiException(500, _("Some user groups do not exist"))


class ChatUserSerializer(serializers.Serializer):
    class UserInstance(serializers.Serializer):
        email = serializers.EmailField(
            required=False,
            label=_("Email"),
            validators=[
                validators.EmailValidator(
                    message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                    code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code,
                )
            ],
            allow_null=True,
            allow_blank=True,
        )
        username = serializers.CharField(
            required=True,
            label=_("Username"),
            max_length=64,
            min_length=4,
            validators=[
                validators.RegexValidator(
                    regex=re.compile("^.{4,64}$"), message=_("Username must be 4-64 characters long")
                )
            ],
        )
        password = serializers.CharField(
            required=True,
            label=_("Password"),
            max_length=20,
            min_length=6,
            validators=[
                validators.RegexValidator(
                    regex=PASSWORD_REGEX,
                    message=_(
                        "The password must be 6-20 characters long and must be a combination of letters, numbers, and special characters."
                    ),
                )
            ],
        )
        nick_name = serializers.CharField(
            required=True,
            label=_("Nick name"),
            max_length=64,
        )
        phone = serializers.CharField(
            required=False, label=_("Phone"), max_length=20, allow_null=True, allow_blank=True
        )
        user_group_ids = serializers.ListField(
            child=serializers.CharField(required=True), required=False, label=_("User Group IDs")
        )
        source = serializers.CharField(required=False, label=_("Source"), max_length=20, default="LOCAL")

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            self._check_unique_username_and_email()

        def _check_unique_username_and_email(self):
            username = self.data.get("username")
            nick_name = self.data.get("nick_name")
            user = ChatUser.objects.filter(Q(username=username) | Q(nick_name=nick_name)).first()
            if user:
                if user.username == username:
                    raise ExceptionCodeConstants.USERNAME_IS_EXIST.value.to_app_api_exception()
                if user.nick_name == nick_name:
                    raise ExceptionCodeConstants.NICKNAME_IS_EXIST.value.to_app_api_exception()

    class Query(serializers.Serializer):
        username = serializers.CharField(required=False, label=_("Username"), allow_null=True, allow_blank=True)
        nick_name = serializers.CharField(required=False, label=_("Nickname"), allow_null=True, allow_blank=True)
        source = serializers.CharField(required=False, label=_("Source"), allow_null=True, allow_blank=True)
        is_active = serializers.BooleanField(required=False, label=_("Is active"), allow_null=True)

        def get_query_set(self):
            username = self.data.get("username")
            query_set = QuerySet(ChatUser)
            if username is not None:
                query_set = query_set.filter(Q(username__contains=username))
            nick_name = self.data.get("nick_name")
            if nick_name is not None:
                query_set = query_set.filter(Q(nick_name__contains=nick_name))
            source = self.data.get("source")
            if source is not None:
                query_set = query_set.filter(source=source)
            is_active = self.data.get("is_active", None)
            if is_active is not None:
                query_set = query_set.filter(is_active=is_active)
            query_set = query_set.order_by("-create_time")
            return query_set

        def page(self, current_page: int, page_size: int, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            result = page_search(
                current_page,
                page_size,
                self.get_query_set(),
                post_records_handler=lambda u: ChatUserInstanceSerializer(u).data,
            )
            user_ids = [user["id"] for user in result["records"]]
            user_groups = UserGroupRelation.objects.filter(user__id__in=user_ids).select_related("group")

            user_groups_map = defaultdict(lambda: {"user_group_ids": [], "user_group_names": []})

            for relation in user_groups:
                user_groups_map[str(relation.user_id)]["user_group_ids"].append(str(relation.group_id))
                user_groups_map[str(relation.user_id)]["user_group_names"].append(relation.group.name)

            for user in result["records"]:
                user.update(user_groups_map.get(str(user["id"]), {"user_group_ids": [], "user_group_names": []}))

            # 合并 Token 配额数据
            quotas = ChatUserTokenQuota.objects.filter(user_id__in=user_ids)
            now = timezone.now()
            quota_map = {}
            for q in quotas:
                effective_used = q.used_tokens
                effective_period_end = q.period_end
                if q.quota_type == "PERIODIC" and q.period_end and now >= q.period_end:
                    effective_used = 0
                    effective_period_end = q.period_end
                    delta_kwargs = {f"{q.period_type.lower()}s": q.period_value}
                    while effective_period_end <= now:
                        effective_period_end += relativedelta(**delta_kwargs)
                quota_map[str(q.user_id)] = {
                    "quota_type": q.quota_type,
                    "used_tokens": effective_used,
                    "token_limit": q.token_limit,
                    "total_tokens": q.total_tokens,
                    "period_end": effective_period_end.isoformat() if effective_period_end else None,
                }
            for user in result["records"]:
                quota = quota_map.get(str(user["id"]), None)
                user["token_quota"] = quota

            return result

    class BatchDeleteInstance(serializers.Serializer):
        ids = serializers.ListField(child=serializers.UUIDField(required=True), required=True, label=_("User IDs"))

        def batch_delete(self):
            user_ids = self.data.get("ids")
            if not user_ids:
                raise AppApiException(1004, _("User IDs cannot be empty"))
            ChatUser.objects.filter(id__in=user_ids).delete()
            return True

    class BatchAddGroup(serializers.Serializer):
        ids = serializers.ListField(child=serializers.UUIDField(required=True), required=True, label=_("User IDs"))
        user_group_ids = serializers.ListField(
            child=serializers.CharField(required=True), required=True, label=_("User Group IDs")
        )
        is_append = serializers.BooleanField(required=False, label=_("Is Append"), default=False)

        @transaction.atomic
        def batch_add_group(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            user_ids = self.data.get("ids")
            original_group_ids = self.data.get("user_group_ids")
            is_append = self.data.get("is_append", False)

            if not user_ids:
                raise AppApiException(1004, _("User IDs cannot be empty"))
            if not original_group_ids:
                raise AppApiException(1004, _("User Group IDs cannot be empty"))

            users = ChatUser.objects.filter(id__in=user_ids)
            if users.count() != len(user_ids):
                raise AppApiException(1004, _("Some users do not exist"))

            groups_count = UserGroup.objects.filter(id__in=original_group_ids).count()
            if groups_count != len(original_group_ids):
                raise AppApiException(1004, _("Some user groups do not exist"))

            if is_append:
                # 获取现有关系
                existing_relations = UserGroupRelation.objects.filter(user_id__in=user_ids).values_list(
                    "user_id", "group_id"
                )

                existing_groups_map = defaultdict(set)
                for user_id, group_id in existing_relations:
                    existing_groups_map[str(user_id)].add(group_id)

                # 准备要创建的新关系
                relations_to_create = []
                for user_id in user_ids:
                    # 只添加不在现有关系中的组
                    new_group_ids = set(original_group_ids) - existing_groups_map.get(user_id, set())

                    for group_id in new_group_ids:
                        relations_to_create.append(
                            UserGroupRelation(id=uuid.uuid7(), user_id=user_id, group_id=group_id)
                        )

                # 只创建不存在的关系，不删除现有关系
                if relations_to_create:
                    UserGroupRelation.objects.bulk_create(relations_to_create, batch_size=1000)

            else:
                # 非追加模式：直接批量删除旧关系，批量创建新关系
                UserGroupRelation.objects.filter(user_id__in=user_ids).delete()

                relations_to_create = [
                    UserGroupRelation(id=uuid.uuid7(), user_id=user_id, group_id=group_id)
                    for user_id in user_ids
                    for group_id in original_group_ids
                ]

                if relations_to_create:
                    UserGroupRelation.objects.bulk_create(relations_to_create, batch_size=1000)

    @transaction.atomic
    def save(self, instance, with_valid=True):
        if with_valid:
            if instance.get("encrypted"):
                instance["password"] = decrypt(instance.get("password"))
            self.UserInstance(data=instance).is_valid(raise_exception=True)

        user = ChatUser(
            id=uuid.uuid7(),
            email=instance.get("email"),
            phone=instance.get("phone", ""),
            nick_name=instance.get("nick_name", ""),
            username=instance.get("username"),
            password=password_encrypt(instance.get("password")),
            source=instance.get("source", "LOCAL"),
            is_active=True,
        )
        user.save()
        add_or_edit_user_group_relation(user, instance.get("user_group_ids", []))
        return ChatUserInstanceSerializer(user).data

    class UserEditInstance(serializers.Serializer):
        email = serializers.EmailField(
            required=False,
            label=_("Email"),
            validators=[
                validators.EmailValidator(
                    message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                    code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code,
                )
            ],
            allow_null=True,
            allow_blank=True,
        )
        nick_name = serializers.CharField(
            required=True,
            label=_("Name"),
            max_length=64,
        )
        phone = serializers.CharField(
            required=False, label=_("Phone"), max_length=20, allow_null=True, allow_blank=True
        )
        is_active = serializers.BooleanField(required=False, label=_("Is Active"))
        user_group_ids = serializers.ListField(
            child=serializers.CharField(required=True), required=False, label=_("User Group IDs")
        )

        def is_valid(self, *, user_id=None, raise_exception=False):
            super().is_valid(raise_exception=True)
            self._check_unique_nick_name(user_id)

        def _check_unique_nick_name(self, user_id):
            nick_name = self.data.get("nick_name")
            if nick_name and ChatUser.objects.filter(nick_name=nick_name).exclude(id=user_id).exists():
                raise AppApiException(1008, _("Nickname is already in use"))

    class RePasswordInstance(serializers.Serializer):
        password = serializers.CharField(
            required=True,
            label=_("Password"),
            max_length=20,
            min_length=6,
            validators=[
                validators.RegexValidator(
                    regex=PASSWORD_REGEX,
                    message=_(
                        "The password must be 6-20 characters long and must be a combination of letters, numbers, and special characters."
                    ),
                )
            ],
        )
        re_password = serializers.CharField(
            required=True,
            label=_("Re Password"),
            validators=[
                validators.RegexValidator(
                    regex=PASSWORD_REGEX,
                    message=_(
                        "The confirmation password must be 6-20 characters long and must be a combination of letters, numbers, and special characters."
                    ),
                )
            ],
        )

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            self._check_passwords_match()

        def _check_passwords_match(self):
            if self.data.get("password") != self.data.get("re_password"):
                raise ExceptionCodeConstants.PASSWORD_NOT_EQ_RE_PASSWORD.value.to_app_api_exception()

    class Operate(serializers.Serializer):
        id = serializers.UUIDField(required=True, label=_("User ID"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            self._check_user_exists()

        def _check_user_exists(self):
            if not ChatUser.objects.filter(id=self.data.get("id")).exists():
                raise AppApiException(1004, _("User does not exist"))

        @transaction.atomic
        def delete(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            user_id = self.data.get("id")
            ChatUser.objects.filter(id=user_id).delete()
            return True

        def edit(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                ChatUserSerializer.UserEditInstance(data=instance).is_valid(
                    user_id=self.data.get("id"), raise_exception=True
                )
            user = ChatUser.objects.filter(id=self.data.get("id")).first()
            self._update_user_fields(user, instance)
            user.save()
            add_or_edit_user_group_relation(user, instance.get("user_group_ids", []))
            return ChatUserInstanceSerializer(user).data

        @staticmethod
        def _update_user_fields(user, instance):
            update_keys = ["email", "nick_name", "phone", "is_active"]
            for key in update_keys:
                if key in instance and instance.get(key) is not None:
                    setattr(user, key, instance.get(key))

        def one(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            user = ChatUser.objects.filter(id=self.data.get("id")).first()
            user_data = ChatUserInstanceSerializer(user).data
            # 补充用户组信息
            user_data["user_group_ids"] = list(
                UserGroupRelation.objects.filter(user=user).values_list("group_id", flat=True)
            )
            return user_data

        def re_password(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                encrypted_data = instance.get("encryptedData", "")
                if encrypted_data:
                    try:
                        decrypted_raw = decrypt(encrypted_data)
                        # decrypt 可能返回非 JSON 字符串，防护解析异常
                        decrypted_data = json.loads(decrypted_raw) if decrypted_raw else {}
                        if isinstance(decrypted_data, dict):
                            instance.update(decrypted_data)
                    except Exception:
                        raise AppApiException(500, _("Invalid encrypted data"))
                ChatUserSerializer.RePasswordInstance(data=instance).is_valid(raise_exception=True)
            user = ChatUser.objects.filter(id=self.data.get("id")).first()
            user.password = password_encrypt(instance.get("password"))
            user.save()
            return True

    class GetUserListByGroup(serializers.Serializer):
        group_id = serializers.UUIDField(required=True, label=_("Group ID"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            group_id = self.data.get("group_id")
            if not UserGroup.objects.filter(id=group_id).exists():
                raise AppApiException(1004, _("User group does not exist"))

        def get_user_list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            group_id = self.data.get("group_id")
            user_ids = UserGroupRelation.objects.filter(group_id=group_id).values_list("user_id", flat=True)
            users = ChatUser.objects.exclude(id__in=user_ids)
            return ChatUserInstanceSerializer(users, many=True).data

    @classmethod
    def list(cls):
        users = ChatUser.objects.all().order_by("-create_time")
        return ChatUserInstanceSerializer(users, many=True).data


class UserGroupModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = ["id", "name"]


class UserGroupCreateSerializer(serializers.Serializer):
    id = serializers.CharField(required=False, label="ID")
    name = serializers.CharField(required=True, label="User Group Name")

    def validate(self, data):
        id = data.get("id")
        name = data.get("name")
        if id:
            group = UserGroup.objects.filter(id=id).first()
            if not group:
                raise AppApiException(500, _("User group does not exist"))
        if name:
            queryset = UserGroup.objects.filter(name=name)
            if id:
                # 排除当前用户组自身
                queryset = queryset.exclude(id=id)
            if queryset.exists():
                raise AppApiException(500, _("User group name already exists"))
        return data

    def create_or_update_group(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        id = self.data.get("id")
        name = self.data.get("name")

        if id:
            group = UserGroup.objects.get(id=id)
            group.name = name
            group.save()
        else:
            group = UserGroup.objects.create(id=uuid.uuid7(), name=name)
            group.save()
            return UserGroupModelSerializer(group).data

    def get_user_group_list(self):
        groups = UserGroup.objects.all().order_by("name")
        return UserGroupModelSerializer(groups, many=True).data

    class UserGroupDeleteSerializer(serializers.Serializer):
        id = serializers.CharField(required=True, label="ID")

        def validate(self, data):
            id = data.get("id")
            group = UserGroup.objects.filter(id=id).first()
            if not group:
                raise AppApiException(500, _("User group does not exist"))
            if group.id == "default":
                raise AppApiException(500, _("Default user group cannot be deleted"))
            return data

        def delete(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            id = self.data.get("id")
            UserGroupRelation.objects.filter(group_id=id).delete()
            UserGroup.objects.filter(id=id).delete()
            return True


class UserGroupAddMemberSerializer(serializers.Serializer):
    id = serializers.CharField(required=True, label="ID")
    user_ids = serializers.ListField(child=serializers.CharField(required=True), required=True, label=_("User IDs"))

    def validate(self, data):
        id = data.get("id")
        user_ids = data.get("user_ids")
        group = UserGroup.objects.filter(id=id).first()
        if not group:
            raise AppApiException(500, _("User group does not exist"))
        if not user_ids:
            raise AppApiException(500, _("User IDs cannot be empty"))
        return data

    def add_member(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        user_ids = self.data.get("user_ids")
        current_user_group_ids = set(
            str(user_id)
            for user_id in UserGroupRelation.objects.filter(group__id=self.data.get("id")).values_list(
                "user_id", flat=True
            )
        )
        to_add = set(user_ids).difference(current_user_group_ids)
        if to_add:
            UserGroupRelation.objects.bulk_create(
                [
                    UserGroupRelation(id=uuid.uuid7(), user_id=user_id, group_id=self.data.get("id"))
                    for user_id in to_add
                ]
            )
        return True


class UserGroupRemoveMemberSerializer(serializers.Serializer):
    id = serializers.CharField(required=True, label="ID")
    group_relation_ids = serializers.ListField(
        child=serializers.CharField(required=True), required=True, label=_("User group relation IDs")
    )

    def validate(self, data):
        id = data.get("id")
        user_ids = data.get("group_relation_ids")
        if UserGroup.objects.filter(id=id).count() == 0:
            raise AppApiException(500, _("User group does not exist"))
        if not user_ids:
            raise AppApiException(500, _("User group relation IDs cannot be empty"))
        return data

    def remove_member(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        group_relation_ids = self.data.get("group_relation_ids")
        UserGroupRelation.objects.filter(id__in=group_relation_ids).delete()
        return True


class UserGroupListPageSerializer(serializers.Serializer):
    class Query(serializers.Serializer):
        group_id = serializers.CharField(required=True, label=_("Group ID"))
        username = serializers.CharField(required=False, label=_("Username"), allow_null=True)
        nick_name = serializers.CharField(required=False, label=_("Nick Name"), allow_null=True)
        source = serializers.CharField(required=False, label=_("Source"), allow_null=True)

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=raise_exception)
            group_id = self.data.get("group_id")
            if not UserGroup.objects.filter(id=group_id).exists():
                raise AppApiException(500, _("User group does not exist"))

        def page(self, current_page, page_size):
            self.is_valid()
            query_set = self.get_query_set()
            result = page_search(
                current_page,
                page_size,
                query_set,
                post_records_handler=lambda relation: {
                    **ChatUserInstanceSerializer(relation.user).data,
                    "user_group_relation_id": relation.id,
                },
            )
            return result

        def get_query_set(self):
            group_id = self.data.get("group_id")

            username = self.data.get("username")
            nick_name = self.data.get("nick_name")
            source = self.data.get("source")
            query_set = UserGroupRelation.objects.filter(group_id=group_id).select_related("user")

            if username is not None:
                query_set = query_set.filter(user__username__contains=username)
            if nick_name is not None:
                query_set = query_set.filter(user__nick_name__contains=nick_name)
            if source is not None:
                query_set = query_set.filter(user__source=source)
            return query_set.order_by("-user__create_time")


class RePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        required=True,
        label=_("Password"),
        validators=[
            validators.RegexValidator(
                regex=re.compile(
                    "^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z_!@#$%^&*`~.()-+=]+$)(?![a-z0-9]+$)(?![a-z_!@#$%^&*`~()-+=]+$)"
                    "(?![0-9_!@#$%^&*`~()-+=]+$)[a-zA-Z0-9_!@#$%^&*`~.()-+=]{6,20}$"
                ),
                message=_(
                    "The confirmation password must be 6-20 characters long and must be a combination of letters, numbers, and special characters."
                ),
            )
        ],
    )

    re_password = serializers.CharField(
        required=True,
        label=_("Confirm Password"),
        validators=[
            validators.RegexValidator(
                regex=re.compile(
                    "^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z_!@#$%^&*`~.()-+=]+$)(?![a-z0-9]+$)(?![a-z_!@#$%^&*`~()-+=]+$)"
                    "(?![0-9_!@#$%^&*`~()-+=]+$)[a-zA-Z0-9_!@#$%^&*`~.()-+=]{6,20}$"
                ),
                message=_(
                    "The confirmation password must be 6-20 characters long and must be a combination of letters, numbers, and special characters."
                ),
            )
        ],
    )

    class Meta:
        model = ChatUser
        fields = "__all__"

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        if self.data.get("password") != self.data.get("re_password"):
            raise AppApiException(
                ExceptionCodeConstants.PASSWORD_NOT_EQ_RE_PASSWORD.value.code,
                ExceptionCodeConstants.PASSWORD_NOT_EQ_RE_PASSWORD.value.message,
            )
        return True

    def reset_password(self, user_id):
        """
        修改密码
        :return: 是否成功
        """
        if self.is_valid():
            QuerySet(ChatUser).filter(id=user_id).update(password=password_encrypt(self.data.get("password")))
            return True


class ChatUserProfileSerializer(serializers.Serializer):
    @staticmethod
    def profile(user: ChatUser):
        """
          获取对话用户详情
        @param user: 用户对象
        @return:
        """
        if not user:
            return {}
        return {
            "id": user.id,
            "username": user.username,
            "nick_name": user.nick_name,
            "email": user.email,
            "source": user.source,
        }
