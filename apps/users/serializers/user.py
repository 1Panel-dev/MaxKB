# coding=utf-8
"""
@project: MaxKB
@Author：虎虎
@file： user.py
@date：2025/4/14 19:18
@desc:
"""

import json
import os
import random
import re
from collections import defaultdict

import uuid_utils.compat as uuid
from django.core import validators
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.mail.backends.smtp import EmailBackend
from django.db import transaction
from django.db.models import Q, QuerySet
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.auth.constants.role_constants import RoleConstants
from common.auth.struct.auth import Auth
from common.constants.cache_version import Cache_Version
from common.constants.exception_code_constants import ExceptionCodeConstants
from common.constants.resource_permission_constants import ResourcePermissionConstants
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.db.search import page_search
from common.exception.app_exception import AppApiException
from common.utils.common import password_encrypt, password_verify
from common.utils.rsa_util import decrypt
from maxkb.conf import PROJECT_DIR
from maxkb.const import CONFIG
from system_manage.models import AuthTargetType, SettingType, SystemSetting, WorkspaceUserResourcePermission
from users.models import User
from users.models.user_group import SystemUserGroup, SystemUserGroupRelation

PASSWORD_REGEX = re.compile(
    r"^"  # 开始
    r"(?=.*[a-z])"  # 至少一个小写字母
    r"(?=.*[-_!@#$%^&*`~.()+=])"  # 至少一个指定的特殊字符
    r"(?:(?=.*[A-Z])|(?=.*\d))"  # 至少一个大写字母 或 数字
    r"[a-zA-Z0-9-_!@#$%^&*`~.()+=]{6,20}"  # 总长度6~20个合法字符
    r"$"  # 结束
)

version, get_key = Cache_Version.SYSTEM.value
EMAIL_CODE_TYPE_REGEX = re.compile(r"^(register|reset_password)$")


class UserProfileResponse(serializers.ModelSerializer):
    is_edit_password = serializers.BooleanField(required=True, label=_("Is Edit Password"))
    permissions = serializers.ListField(required=True, label=_("permissions"))

    class Meta:
        model = User
        fields = ["id", "username", "nick_name", "email", "role", "permissions", "language", "is_edit_password"]


class CreateUserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, label=_("Username"))
    password = serializers.CharField(required=True, label=_("Password"))
    email = serializers.EmailField(required=True, label=_("Email"))
    nick_name = serializers.CharField(required=False, label=_("Nick name"))
    phone = serializers.CharField(required=False, label=_("Phone"))
    source = serializers.CharField(required=False, label=_("Source"), default="LOCAL")
    user_group_ids = serializers.ListField(
        child=serializers.CharField(required=False), required=False, label=_("User Group IDs")
    )


def _get_workspace_name_mapping():
    workspace_model = DatabaseModelManage.get_model("workspace_model")
    if not workspace_model:
        return {}
    return {str(workspace.id): workspace.name for workspace in workspace_model.objects.all()}


def _get_user_group_workspace_mapping(user_ids):
    user_group_relations = SystemUserGroupRelation.objects.filter(user_id__in=user_ids).select_related("group")
    workspace_mapping = _get_workspace_name_mapping()
    user_group_mapping = defaultdict(
        lambda: {
            "user_group_ids": [],
            "user_group_names": [],
            "user_group_workspace": defaultdict(list),
        }
    )

    for relation in user_group_relations:
        user_id = str(relation.user_id)
        group_name = relation.group.name
        workspace_name = workspace_mapping.get(relation.group.workspace_id, relation.group.workspace_id)
        user_group_mapping[user_id]["user_group_ids"].append(str(relation.group_id))
        user_group_mapping[user_id]["user_group_names"].append(group_name)
        user_group_mapping[user_id]["user_group_workspace"][workspace_name].append(group_name)

    return {
        user_id: {
            "user_group_ids": data["user_group_ids"],
            "user_group_names": data["user_group_names"],
            "user_group_workspace": [
                {"workspace": workspace_name, "user_group_names": group_names}
                for workspace_name, group_names in data["user_group_workspace"].items()
            ],
        }
        for user_id, data in user_group_mapping.items()
    }


def is_workspace_manage(user_id: str, workspace_id: str):
    workspace_user_role_mapping_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
    role_permission_mapping_model = DatabaseModelManage.get_model("role_permission_mapping_model")
    is_x_pack_ee = workspace_user_role_mapping_model is not None and role_permission_mapping_model is not None
    if is_x_pack_ee:
        return (
            QuerySet(workspace_user_role_mapping_model)
            .select_related("role", "user")
            .filter(
                workspace_id=workspace_id, user_id=user_id, role__type=RoleConstants.WORKSPACE_MANAGE.value.__str__()
            )
            .exists()
        )
    return QuerySet(User).filter(id=user_id, role=RoleConstants.ADMIN.value.__str__()).exists()


def is_workspace_manage_permission_read(user_id: str, workspace_id: str, permission_id):
    workspace_user_role_mapping_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
    role_permission_mapping_model = DatabaseModelManage.get_model("role_permission_mapping_model")
    is_x_pack_ee = workspace_user_role_mapping_model is not None and role_permission_mapping_model is not None
    if is_x_pack_ee:
        # 内置工作空间管理员（role_id 固定为 'WORKSPACE_MANAGE'）拥有全量权限，直接放行
        is_builtin_manage = (
            QuerySet(workspace_user_role_mapping_model)
            .filter(user_id=user_id, workspace_id=workspace_id, role_id=RoleConstants.WORKSPACE_MANAGE.value.__str__())
            .exists()
        )
        if is_builtin_manage:
            return True
        # 继承（自定义）工作空间管理员：需被显式授予对应权限
        has_permission = (
            QuerySet(role_permission_mapping_model)
            .filter(
                role__userrolerelation__user_id=user_id,
                role__userrolerelation__workspace_id=workspace_id,
                permission_id=permission_id,
                role__type=RoleConstants.WORKSPACE_MANAGE.value.__str__(),
            )
            .exists()
        )
        return has_permission
    return QuerySet(User).filter(id=user_id, role=RoleConstants.ADMIN.value.__str__()).exists()


def get_workspace_list_by_user(user_id):
    get_workspace_list = DatabaseModelManage.get_model("get_workspace_list_by_user")
    license_is_valid = DatabaseModelManage.get_model("license_is_valid") or (lambda: False)
    if get_workspace_list is not None and license_is_valid():
        return get_workspace_list(user_id)
    return [{"id": "default", "name": "default"}]


class UserProfileSerializer(serializers.Serializer):
    @staticmethod
    def profile(user: User, auth: Auth):
        """
          获取用户详情
        @param user: 用户对象
        @param auth: 认证对象
        @return:
        """
        workspace_list = get_workspace_list_by_user(user.id)
        user_role_relation_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
        role_name = [user.role]
        if user_role_relation_model:
            user_role_relations = (
                user_role_relation_model.objects.filter(user_id=user.id).select_related("role").distinct("role_id")
            )
            role_name = [relation.role.role_name for relation in user_role_relations]

        return {
            "id": user.id,
            "username": user.username,
            "nick_name": user.nick_name,
            "email": user.email,
            "source": user.source,
            "role": list(auth.roles),
            "permissions": auth.permissions,
            "is_edit_password": password_verify(CONFIG.get("DEFAULT_PASSWORD", "MaxKB@123.."), user.password)
            if user.source == "LOCAL"
            else False,
            "language": user.language,
            "workspace_list": workspace_list,
            "role_name": role_name,
        }


class UserInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "is_active",
            "role",
            "nick_name",
            "create_time",
            "update_time",
            "source",
        ]


class UserManageSerializer(serializers.Serializer):
    class UserInstance(serializers.Serializer):
        email = serializers.EmailField(
            required=True,
            label=_("Email"),
            validators=[
                validators.EmailValidator(
                    message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                    code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code,
                )
            ],
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
        source = serializers.CharField(required=False, label=_("Source"), max_length=20, default="LOCAL")

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            self._check_unique_username_and_email()

        def _check_unique_username_and_email(self):
            username = self.data.get("username")
            email = self.data.get("email")
            user = User.objects.filter(Q(username=username) | Q(email=email)).first()
            if user:
                if user.email == email:
                    raise ExceptionCodeConstants.EMAIL_IS_EXIST.value.to_app_api_exception()
                if user.username == username:
                    raise ExceptionCodeConstants.USERNAME_IS_EXIST.value.to_app_api_exception()

    class Query(serializers.Serializer):
        username = serializers.CharField(required=False, label=_("Username"), max_length=64, allow_blank=True)
        nick_name = serializers.CharField(required=False, label=_("Nick Name"), max_length=64, allow_blank=True)
        email = serializers.CharField(
            required=False,
            label=_("Email"),
            allow_blank=True,
        )
        is_active = serializers.BooleanField(
            required=False,
            label=_("Is active"),
        )
        source = serializers.CharField(
            required=False,
            label=_("Source"),
            allow_blank=True,
        )

        def get_query_set(self):
            username = self.data.get("username")
            nick_name = self.data.get("nick_name")
            email = self.data.get("email")
            is_active = self.data.get("is_active", None)
            source = self.data.get("source", None)
            query_set = QuerySet(User)
            if username is not None:
                query_set = query_set.filter(username__contains=username)
            if nick_name is not None:
                query_set = query_set.filter(nick_name__contains=nick_name)
            if email is not None:
                query_set = query_set.filter(email__contains=email)
            if is_active is not None:
                query_set = query_set.filter(is_active=is_active)
            if source is not None:
                query_set = query_set.filter(source=source)
            query_set = query_set.order_by("-create_time")
            return query_set

        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return [
                {"id": user_model.id, "username": user_model.username, "email": user_model.email}
                for user_model in self.get_query_set()
            ]

        def page(self, current_page: int, page_size: int, user_id: str, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            result = page_search(
                current_page,
                page_size,
                self.get_query_set(),
                post_records_handler=lambda u: UserInstanceSerializer(u).data,
            )
            user_group_mapping = _get_user_group_workspace_mapping([user["id"] for user in result["records"]])

            for user in result["records"]:
                user_group_data = user_group_mapping.get(
                    str(user["id"]),
                    {
                        "user_group_ids": [],
                        "user_group_names": [],
                        "user_group_workspace": [],
                    },
                )
                user["user_group_ids"] = user_group_data["user_group_ids"]
                user["user_group_names"] = user_group_data["user_group_names"]
                user["user_group_workspace"] = user_group_data["user_group_workspace"]
            role_model = DatabaseModelManage.get_model("role_model")
            user_role_relation_model = DatabaseModelManage.get_model("workspace_user_role_mapping")

            def _get_user_roles(user_ids, is_admin=True):
                workspace_model = DatabaseModelManage.get_model("workspace_model")
                if not (role_model and user_role_relation_model and workspace_model):
                    return {}

                workspace_mapping = {
                    str(workspace_model.id): workspace_model.name for workspace_model in workspace_model.objects.all()
                }

                # 获取所有相关角色关系，并预加载角色信息
                user_role_relations = (
                    user_role_relation_model.objects.filter(user_id__in=user_ids)
                    .select_related("role")
                    .distinct("user_id", "role_id", "workspace_id")  # 确保组合唯一性
                )

                # 构建用户ID到角色名称列表的映射
                user_role_mapping = defaultdict(set)  # 使用 set 去重
                # 构建用户ID到角色ID与工作空间ID映射
                user_role_setting_mapping = defaultdict(lambda: defaultdict(list))
                user_role_workspace_mapping = defaultdict(lambda: defaultdict(list))

                for relation in user_role_relations:
                    user_id = str(relation.user_id)
                    role_id = relation.role_id
                    workspace_id = relation.workspace_id
                    if not is_admin and relation.role.type == RoleConstants.ADMIN.name:
                        continue
                    user_role_mapping[user_id].add(relation.role.role_name)
                    user_role_setting_mapping[user_id][role_id].append(workspace_id)
                    user_role_workspace_mapping[user_id][relation.role.role_name].append(
                        workspace_mapping.get(workspace_id, workspace_id)
                    )

                    # 将 set 转换为 list 以符合返回格式
                user_role_mapping = {uid: list(roles) for uid, roles in user_role_mapping.items()}

                # 转换为所需的结构
                result_user_role_setting_mapping = {
                    user_id: [
                        {"role_id": role_id, "workspace_ids": workspace_ids} for role_id, workspace_ids in roles.items()
                    ]
                    for user_id, roles in user_role_setting_mapping.items()
                }
                result_user_role_workspace_mapping = {
                    user_id: {role_name: workspace_names for role_name, workspace_names in roles.items()}
                    for user_id, roles in user_role_workspace_mapping.items()
                }

                return user_role_mapping, result_user_role_setting_mapping, result_user_role_workspace_mapping

            if role_model and user_role_relation_model:
                # 获取当前用户的所有角色 判断是不是内置的系统管理员
                is_admin = user_role_relation_model.objects.filter(
                    user_id=user_id, role_id=RoleConstants.ADMIN.name
                ).exists()
                user_ids = [user["id"] for user in result["records"]]
                user_role_mapping, user_role_setting_mapping, user_role_workspace_mapping = _get_user_roles(
                    user_ids, is_admin
                )

                # 将角色信息添加回用户数据中
                for user in result["records"]:
                    user_id = str(user["id"])
                    user["role_name"] = user_role_mapping.get(user_id, [])
                    user["role_setting"] = user_role_setting_mapping.get(user_id, [])
                    user["role_workspace"] = user_role_workspace_mapping.get(user_id, [])

            # 用户设置用户组
            return result

    @transaction.atomic
    def save(self, instance, user_id, with_valid=True):
        if with_valid:
            if instance.get("encrypted"):
                instance["password"] = decrypt(instance.get("password"))
            self.UserInstance(data=instance).is_valid(raise_exception=True)

        user = User(
            id=uuid.uuid7(),
            email=instance.get("email"),
            phone=instance.get("phone", ""),
            nick_name=instance.get("nick_name", ""),
            username=instance.get("username"),
            password=password_encrypt(instance.get("password")),
            role=RoleConstants.USER.name,
            source=instance.get("source", "LOCAL"),
            is_active=True,
        )
        update_user_role(instance, user, user_id)
        set_user_groups(user.id, instance)
        user.save()
        return UserInstanceSerializer(user).data

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
        )
        nick_name = serializers.CharField(
            required=False,
            label=_("Name"),
            max_length=64,
        )
        phone = serializers.CharField(
            required=False, label=_("Phone"), max_length=20, allow_null=True, allow_blank=True
        )
        is_active = serializers.BooleanField(required=False, label=_("Is Active"))

        def is_valid(self, *, user_id=None, raise_exception=False):
            super().is_valid(raise_exception=True)
            self._check_unique_email(user_id)

        def _check_unique_email(self, user_id):
            email = self.data.get("email")
            if email and User.objects.filter(email=email).exclude(id=user_id).exists():
                raise AppApiException(1004, _("Email is already in use"))

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
            if not User.objects.filter(id=self.data.get("id")).exists():
                raise AppApiException(1004, _("User does not exist"))

        @transaction.atomic
        def delete(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                self._check_not_admin()
            user_id = self.data.get("id")
            # TODO  需要删除授权关系
            User.objects.filter(id=user_id).delete()
            return True

        def _check_not_admin(self):
            user = User.objects.filter(id=self.data.get("id")).first()
            if user.role == RoleConstants.ADMIN.name or str(user.id) == "f0dd8f71-e4ee-11ee-8c84-a8a1595801ab":
                raise AppApiException(1004, _("Unable to delete administrator"))

        def edit(self, instance, user_id, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                UserManageSerializer.UserEditInstance(data=instance).is_valid(
                    user_id=self.data.get("id"), raise_exception=True
                )
            user = User.objects.filter(id=self.data.get("id")).first()
            self._check_admin_modification(user, instance)
            self._update_user_fields(user, instance)
            update_user_role(instance, user, user_id)
            set_user_groups(user.id, instance)
            user.save()
            return UserInstanceSerializer(user).data

        @staticmethod
        def _check_admin_modification(user, instance):
            if (
                    user.role == RoleConstants.ADMIN.name
                    and "is_active" in instance
                    and instance.get("is_active") is not None
            ):
                raise AppApiException(1004, _("Cannot modify administrator status"))

        @staticmethod
        def _update_user_fields(user, instance):
            update_keys = ["email", "nick_name", "phone", "is_active"]
            for key in update_keys:
                if key in instance and instance.get(key) is not None:
                    setattr(user, key, instance.get(key))

        def one(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            user = User.objects.filter(id=self.data.get("id")).first()
            workspace_user_role_mapping_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
            if workspace_user_role_mapping_model:
                role_setting = {}
                workspace_user_role_mapping_list = QuerySet(workspace_user_role_mapping_model).filter(user_id=user.id)
                for workspace_user_role_mapping in workspace_user_role_mapping_list:
                    role_id = workspace_user_role_mapping.role_id
                    workspace_id = workspace_user_role_mapping.workspace_id
                    if role_id not in role_setting:
                        role_setting[role_id] = []
                    role_setting[role_id].append(workspace_id)
                return {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "phone": user.phone,
                    "nick_name": user.nick_name,
                    "is_active": user.is_active,
                    "role_setting": role_setting,
                }
            return UserInstanceSerializer(user).data

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
                UserManageSerializer.RePasswordInstance(data=instance).is_valid(raise_exception=True)
            user = User.objects.filter(id=self.data.get("id")).first()
            user.password = password_encrypt(instance.get("password"))
            user.save()
            return True

    def get_user_list(self, user_id, workspace_id, nick_name):
        """
        获取用户列表
        :param workspace_id: 工作空间ID
        :return: 用户列表
        """
        workspace_user_role_mapping_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
        if workspace_user_role_mapping_model:
            # 判断当前用户是否属于该空间，不属于直接返回空
            if not workspace_user_role_mapping_model.objects.filter(
                    workspace_id=workspace_id, user_id=user_id
            ).exists():
                query_set = User.objects.none()
            else:
                query_set = User.objects.filter(
                    id__in=workspace_user_role_mapping_model.objects.filter(workspace_id=workspace_id).values("user_id")
                )

        else:
            if user_id == "f0dd8f71-e4ee-11ee-8c84-a8a1595801ab":
                query_set = User.objects.all()
            else:
                query_set = User.objects.filter(role=RoleConstants.USER.name)

        if nick_name:
            query_set = query_set.filter(nick_name__contains=nick_name)

        users = query_set.values("id", "nick_name")[:200]

        return list(users)

    def get_user_members(self, workspace_id):
        """
        获取工作空间成员列表
        :param workspace_id: 工作空间ID
        :return: 成员列表
        """
        role_model = DatabaseModelManage.get_model("role_model")
        user_role_relation_model = DatabaseModelManage.get_model("workspace_user_role_mapping")

        if user_role_relation_model and role_model:
            user_role_relations = user_role_relation_model.objects.filter(
                workspace_id=workspace_id, role__type="USER"
            ).select_related("role", "user")
            user_dict = {}
            for relation in user_role_relations:
                user_id = relation.user.id
                if user_id not in user_dict:
                    user_dict[user_id] = {
                        "id": user_id,
                        "nick_name": relation.user.nick_name,
                        "roles": [relation.role.role_name],
                    }
                else:
                    user_dict[user_id]["roles"].append(relation.role.role_name)

            # 将字典值转换为列表形式
            return list(user_dict.values())
        user_list = User.objects.exclude(role=RoleConstants.ADMIN.name)
        return [{"id": user.id, "nick_name": user.nick_name, "roles": [RoleConstants.USER.name]} for user in user_list]

    class BatchDelete(serializers.Serializer):
        ids = serializers.ListField(required=True, label=_("User IDs"))

        def batch_delete(self, with_valid=True):
            user_ids = self.data.get("ids")
            if not user_ids:
                raise AppApiException(1004, _("User IDs cannot be empty"))
            User.objects.filter(id__in=user_ids).exclude(id="f0dd8f71-e4ee-11ee-8c84-a8a1595801ab").delete()
            return True

    def get_all_user_list(self, nick_name=None):
        query_set = User.objects.all()
        if nick_name:
            query_set = query_set.filter(nick_name__contains=nick_name)
        users = query_set.values("id", "nick_name", "username")[:200]
        return list(users)


def update_user_role(instance, user, user_id=None):
    workspace_user_role_mapping_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
    if workspace_user_role_mapping_model:
        role_setting = instance.get("role_setting")
        license_is_valid = DatabaseModelManage.get_model("license_is_valid") or (lambda: False)
        license_is_valid = license_is_valid() if license_is_valid() is not None else False
        if not role_setting or (
                len(role_setting) == 1
                and role_setting[0].get("role_id") == ""
                and len(role_setting[0].get("workspace_ids", [])) == 0
        ):
            if not license_is_valid:
                workspace_user_role_mapping_model.objects.create(
                    id=uuid.uuid7(), user_id=user.id, role_id=RoleConstants.USER.name, workspace_id="default"
                )
            return

        is_admin = workspace_user_role_mapping_model.objects.filter(
            user_id=user_id, role_id=RoleConstants.ADMIN.name
        ).exists()

        if str(user.id) == "f0dd8f71-e4ee-11ee-8c84-a8a1595801ab":
            # 需要判断当前角色的权限 不能删除系统管理员 空间管理员 普通管理员等角色
            # role_setting是一个数组 结构式 [{role_id:1,workspace_ids:[1,2]}]
            # 如果role_id不包含ADMIN 就直接报错   如果WORKSPACE_MANAGE 或者USER 必须判断workspace_ids是否包含默认工作空间 不包含就报错
            admin_role_id = RoleConstants.ADMIN.name
            workspace_manage_role_id = RoleConstants.WORKSPACE_MANAGE.name
            # 判断内置的三个角色是不是不在
            current_role_ids = {item["role_id"] for item in role_setting}
            initial_role = [admin_role_id, workspace_manage_role_id, RoleConstants.USER.name]
            if not set(initial_role).issubset(current_role_ids):
                raise AppApiException(1004, _("Cannot delete built-in role"))

            if not any(item["role_id"] == str(admin_role_id) for item in role_setting):
                raise AppApiException(1004, _("Cannot delete built-in role"))

            # 验证 WORKSPACE_MANAGE 或 USER 是否包含默认工作空间
            default_workspace_id = "default"

            for item in role_setting:
                role_id = item["role_id"]
                workspace_ids = item.get("workspace_ids", [])

                if role_id == str(workspace_manage_role_id) or role_id == str(RoleConstants.USER.value):
                    if default_workspace_id not in workspace_ids:
                        raise AppApiException(1004, _("Cannot delete built-in role"))
        if is_admin:
            workspace_user_role_mapping_model.objects.filter(user_id=user.id).delete()
        else:
            workspace_user_role_mapping_model.objects.filter(user_id=user.id).exclude(
                role__type=RoleConstants.ADMIN.name
            ).delete()

        relations = set()
        for item in role_setting:
            role_id = item["role_id"]
            workspace_ids = item["workspace_ids"] if item["workspace_ids"] else ["None"]
            for workspace_id in workspace_ids:
                relations.add((role_id, workspace_id))
        for role_id, workspace_id in relations:
            workspace_user_role_mapping_model.objects.create(
                id=uuid.uuid7(), role_id=role_id, workspace_id=workspace_id, user_id=user.id
            )
        permission_version, permission_get_key = Cache_Version.PERMISSION_LIST.value
        cache.delete(permission_get_key(str(user.id)), version=permission_version)
        role_version, role_get_key = Cache_Version.ROLE_LIST.value
        cache.delete(role_get_key(str(user.id)), version=role_version)


def set_user_groups(user_id, instance):
    user_group_ids = instance.get("user_group_ids") or []

    if SystemUserGroup.objects.filter(id__in=user_group_ids).count() != len(user_group_ids):
        raise AppApiException(
            1004,
            _("One or more user groups do not exist"),
        )
    SystemUserGroupRelation.objects.filter(user_id=user_id).delete()
    if user_group_ids:
        SystemUserGroupRelation.objects.bulk_create(
            SystemUserGroupRelation(
                id=uuid.uuid7(),
                user_id=user_id,
                group_id=group_id,
            )
            for group_id in user_group_ids
        )

    return None


class RePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        label=_("Email"),
        validators=[
            validators.EmailValidator(
                message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code,
            )
        ],
    )

    code = serializers.CharField(required=True, label=_("Code"))
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

    class Meta:
        model = User
        fields = "__all__"

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        email = self.data.get("email")
        cache_code = cache.get(get_key(email + ":reset_password"), version=version)
        if self.data.get("password") != self.data.get("re_password"):
            raise AppApiException(
                ExceptionCodeConstants.PASSWORD_NOT_EQ_RE_PASSWORD.value.code,
                ExceptionCodeConstants.PASSWORD_NOT_EQ_RE_PASSWORD.value.message,
            )
        if cache_code != self.data.get("code"):
            raise AppApiException(
                ExceptionCodeConstants.CODE_ERROR.value.code, ExceptionCodeConstants.CODE_ERROR.value.message
            )
        return True

    def reset_password(self):
        """
        修改密码
        :return: 是否成功
        """
        if self.is_valid():
            email = self.data.get("email")
            QuerySet(User).filter(email=email).update(password=password_encrypt(self.data.get("password")))
            code_cache_key = email + ":reset_password"
            cache.delete(get_key(code_cache_key), version=version)
            return True


class ResetCurrentUserPassword(serializers.Serializer):
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

    class Meta:
        model = User
        fields = "__all__"

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        if self.data.get("password") != self.data.get("re_password"):
            raise AppApiException(
                ExceptionCodeConstants.PASSWORD_NOT_EQ_RE_PASSWORD.value.code,
                ExceptionCodeConstants.PASSWORD_NOT_EQ_RE_PASSWORD.value.message,
            )
        return True

    def reset_password(self, user_id: str):
        """
        修改密码
        :return: 是否成功
        """
        if self.is_valid():
            QuerySet(User).filter(id=user_id).update(password=password_encrypt(self.data.get("password")))
            return True


class SendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        label=_("Email"),
        validators=[
            validators.EmailValidator(
                message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code,
            )
        ],
    )

    type = serializers.CharField(
        required=True,
        label=_("Type"),
        validators=[
            validators.RegexValidator(
                regex=EMAIL_CODE_TYPE_REGEX,
                message=_("The type only supports register|reset_password"),
                code=500,
            )
        ],
    )

    class Meta:
        model = User
        fields = "__all__"

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=raise_exception)
        code_cache_key = self.data.get("email") + ":" + self.data.get("type")
        code_cache_key_lock = code_cache_key + "_lock"
        ttl = cache.ttl(get_key(code_cache_key_lock), version=version)
        if ttl is not None and ttl > 0:
            raise AppApiException(
                500, _("Do not send emails again within {seconds} seconds").format(seconds=int(ttl.total_seconds()))
            )
        return True

    def send(self):
        """
        发送邮件
        :return:   是否发送成功
        :exception 发送失败异常
        """
        email = self.data.get("email")
        state = self.data.get("type")
        code = "".join(random.choices("0123456789", k=6))
        language = get_language()
        template_path = os.path.join(PROJECT_DIR, "apps", "common", "template", f"email_template_{language}.html")
        with open(template_path, "r", encoding="utf-8") as template_file:
            content = template_file.read()
        code_cache_key = email + ":" + state
        code_cache_key_lock = code_cache_key + "_lock"
        cache.set(get_key(code_cache_key_lock), code, timeout=60, version=version)
        system_setting = QuerySet(SystemSetting).filter(type=SettingType.EMAIL.value).first()
        if system_setting is None:
            cache.delete(get_key(code_cache_key_lock), version=version)
            raise AppApiException(
                1004,
                _(
                    "The email service has not been set up. Please contact the administrator to set up the email service in [Email Settings]."
                ),
            )
        try:
            connection = EmailBackend(
                system_setting.meta.get("email_host"),
                system_setting.meta.get("email_port"),
                system_setting.meta.get("email_host_user"),
                system_setting.meta.get("email_host_password"),
                system_setting.meta.get("email_use_tls"),
                False,
                system_setting.meta.get("email_use_ssl"),
            )
            # 发送邮件
            send_mail(
                _("【Intelligent knowledge base question and answer system-{action}】").format(
                    action=_("User registration") if state == "register" else _("Change password")
                ),
                "",
                html_message=f"{content.replace('${code}', code)}",
                from_email=system_setting.meta.get("from_email"),
                recipient_list=[email],
                fail_silently=False,
                connection=connection,
            )
        except Exception:
            cache.delete(get_key(code_cache_key_lock), version=version)
            raise AppApiException(500, _("Failed to send email. Please try again later."))
        cache.set(get_key(code_cache_key), code, timeout=60 * 30, version=version)
        return True


class CheckCodeSerializer(serializers.Serializer):
    """
    校验验证码
    """

    email = serializers.EmailField(
        required=True,
        label=_("Email"),
        validators=[
            validators.EmailValidator(
                message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code,
            )
        ],
    )
    code = serializers.CharField(required=True, label=_("Verification code"))

    type = serializers.CharField(
        required=True,
        label=_("Type"),
        validators=[
            validators.RegexValidator(
                regex=EMAIL_CODE_TYPE_REGEX,
                message=_("The type only supports register|reset_password"),
                code=500,
            )
        ],
    )

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=raise_exception)
        value = cache.get(get_key(self.data.get("email") + ":" + self.data.get("type")), version=version)
        if value is None or value != self.data.get("code"):
            raise ExceptionCodeConstants.CODE_ERROR.value.to_app_api_exception()
        return True


class SwitchLanguageSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(required=True, label=_("user id"))
    language = serializers.CharField(required=True, label=_("language"))

    def switch(self):
        self.is_valid(raise_exception=True)
        language = self.data.get("language")
        support_language_list = CONFIG.get_languages()
        # 这个是一个list 完事是对象 key是语言的key value是语言的value  我只需要提取语言的key就行
        support_keys = [lang[0] for lang in support_language_list]
        # support_language_list = ['zh-CN', 'zh-Hant', 'en-US'] en_US,ja,zh_CN,zh_Hant
        if language not in support_keys:
            raise AppApiException(500, _("language only support:") + ",".join(support_keys))
        QuerySet(User).filter(id=self.data.get("user_id")).update(language=language)
