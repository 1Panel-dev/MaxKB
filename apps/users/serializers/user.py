# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： user.py
    @date：2025/4/14 19:18
    @desc:
"""
import datetime
import os
import random
import re
from collections import defaultdict
from itertools import product

from django.core.cache import cache
from django.core.mail.backends.smtp import EmailBackend
from django.db import transaction
from django.db.models import Q, QuerySet
from rest_framework import serializers
import uuid_utils.compat as uuid

from common.constants.cache_version import Cache_Version
from common.constants.exception_code_constants import ExceptionCodeConstants
from common.constants.permission_constants import RoleConstants, Auth
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.db.search import page_search
from common.exception.app_exception import AppApiException
from common.utils.common import valid_license, password_encrypt
from maxkb.conf import PROJECT_DIR
from system_manage.models import SystemSetting, SettingType
from users.models import User
from django.utils.translation import gettext_lazy as _, to_locale
from django.core import validators
from django.core.mail import send_mail
from django.utils.translation import get_language

PASSWORD_REGEX = re.compile(
    r"^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z_!@#$%^&*`~.()-+=]+$)(?![a-z0-9]+$)(?![a-z_!@#$%^&*`~()-+=]+$)"
    r"(?![0-9_!@#$%^&*`~()-+=]+$)[a-zA-Z0-9_!@#$%^&*`~.()-+=]{6,20}$"
)

version, get_key = Cache_Version.SYSTEM.value


class UserProfileResponse(serializers.ModelSerializer):
    is_edit_password = serializers.BooleanField(required=True, label=_('Is Edit Password'))
    permissions = serializers.ListField(required=True, label=_('permissions'))

    class Meta:
        model = User
        fields = ['id', 'username', 'nick_name', 'email', 'role', 'permissions', 'language', 'is_edit_password']


class CreateUserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, label=_('Username'))
    password = serializers.CharField(required=True, label=_('Password'))
    email = serializers.EmailField(required=True, label=_('Email'))
    nick_name = serializers.CharField(required=False, label=_('Nick name'))
    phone = serializers.CharField(required=False, label=_('Phone'))


def is_workspace_manage(user_id: str, workspace_id: str):
    workspace_user_role_mapping_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
    role_permission_mapping_model = DatabaseModelManage.get_model("role_permission_mapping_model")
    is_x_pack_ee = workspace_user_role_mapping_model is not None and role_permission_mapping_model is not None
    if is_x_pack_ee:
        return QuerySet(workspace_user_role_mapping_model).select_related('role', 'user').filter(
            workspace_id=workspace_id, user_id=user_id,
            role_type=RoleConstants.WORKSPACE_MANAGE.value.__str__()).exists()
    return QuerySet(User).filter(id=user_id, role=RoleConstants.ADMIN.value.__str__()).exists()


class UserProfileSerializer(serializers.Serializer):
    @staticmethod
    def profile(user: User, auth: Auth):
        """
          获取用户详情
        @param user: 用户对象
        @param auth: 认证对象
        @return:
        """
        return {
            'id': user.id,
            'username': user.username,
            'nick_name': user.nick_name,
            'email': user.email,
            'role': auth.role_list,
            'permissions': auth.permission_list,
            'is_edit_password': user.role == RoleConstants.ADMIN.name and user.password == 'd880e722c47a34d8e9fce789fc62389d',
            'language': user.language,
        }


class UserInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'is_active', 'role', 'nick_name', 'create_time', 'update_time',
                  'source']


class UserManageSerializer(serializers.Serializer):
    class UserInstance(serializers.Serializer):
        email = serializers.EmailField(
            required=True,
            label=_("Email"),
            validators=[validators.EmailValidator(
                message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code
            )]
        )
        username = serializers.CharField(
            required=True,
            label=_("Username"),
            max_length=20,
            min_length=4,
            validators=[
                validators.RegexValidator(
                    regex=re.compile("^.{4,20}$"),
                    message=_('Username must be 4-20 characters long')
                )
            ]
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
                    )
                )
            ]
        )
        nick_name = serializers.CharField(
            required=True,
            label=_("Nick name"),
            max_length=20,
        )
        phone = serializers.CharField(
            required=False,
            label=_("Phone"),
            max_length=20,
            allow_null=True,
            allow_blank=True
        )

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            self._check_unique_username_and_email()

        def _check_unique_username_and_email(self):
            username = self.data.get('username')
            email = self.data.get('email')
            nick_name = self.data.get('nick_name')
            user = User.objects.filter(Q(username=username) | Q(email=email) | Q(nick_name=nick_name)).first()
            if user:
                if user.email == email:
                    raise ExceptionCodeConstants.EMAIL_IS_EXIST.value.to_app_api_exception()
                if user.username == username:
                    raise ExceptionCodeConstants.USERNAME_IS_EXIST.value.to_app_api_exception()
                if user.nick_name == nick_name:
                    raise ExceptionCodeConstants.NICKNAME_IS_EXIST.value.to_app_api_exception()

    class Query(serializers.Serializer):
        email_or_username = serializers.CharField(required=False, allow_null=True,
                                                  label=_('Email or username'))

        def get_query_set(self):
            email_or_username = self.data.get('email_or_username')
            query_set = QuerySet(User)
            if email_or_username is not None:
                query_set = query_set.filter(
                    Q(username__contains=email_or_username) | Q(email__contains=email_or_username) | Q(
                        nick_name__contains=email_or_username))
            query_set = query_set.order_by("-create_time")
            return query_set

        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return [{'id': user_model.id, 'username': user_model.username, 'email': user_model.email} for user_model in
                    self.get_query_set()]

        def page(self, current_page: int, page_size: int, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            result = page_search(current_page, page_size,
                                 self.get_query_set(),
                                 post_records_handler=lambda u: UserInstanceSerializer(u).data)
            role_model = DatabaseModelManage.get_model("role_model")
            user_role_relation_model = DatabaseModelManage.get_model("workspace_user_role_mapping")

            def _get_user_roles(user_ids):
                if not (role_model and user_role_relation_model):
                    return {}

                # 获取所有相关角色关系，并预加载角色信息
                user_role_relations = (
                    user_role_relation_model.objects
                    .filter(user_id__in=user_ids)
                    .select_related('role_id')  # 预加载外键数据
                )

                # 构建用户ID到角色名称列表的映射
                user_role_mapping = defaultdict(list)
                for relation in user_role_relations:
                    user_role_mapping[relation.user_id].append(relation.role_id.name)

                return user_role_mapping

            if role_model and user_role_relation_model:
                user_ids = [user['id'] for user in result['records']]
                user_role_mapping = _get_user_roles(user_ids)

                # 将角色信息添加回用户数据中
                for user in result['records']:
                    user['role'] = user_role_mapping.get(user['id'], [])
            return result

    @valid_license(model=User, count=2,
                   message=_(
                       'The community version supports up to 2 users. If you need more users, please contact us (https://fit2cloud.com/).'))
    @transaction.atomic
    def save(self, instance, with_valid=True):
        if with_valid:
            self.UserInstance(data=instance).is_valid(raise_exception=True)

        user = User(
            id=uuid.uuid7(),
            email=instance.get('email'),
            phone=instance.get('phone', ''),
            nick_name=instance.get('nick_name', ''),
            username=instance.get('username'),
            password=password_encrypt(instance.get('password')),
            role=RoleConstants.USER.name,
            source="LOCAL",
            is_active=True
        )
        update_user_role(instance, user)
        user.save()
        return UserInstanceSerializer(user).data

    class UserEditInstance(serializers.Serializer):
        email = serializers.EmailField(
            required=False,
            label=_("Email"),
            validators=[validators.EmailValidator(
                message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code
            )]
        )
        nick_name = serializers.CharField(
            required=True,
            label=_("Name"),
            max_length=20,
        )
        phone = serializers.CharField(
            required=False,
            label=_("Phone"),
            max_length=20,
            allow_null=True,
            allow_blank=True
        )
        is_active = serializers.BooleanField(
            required=False,
            label=_("Is Active")
        )

        def is_valid(self, *, user_id=None, raise_exception=False):
            super().is_valid(raise_exception=True)
            self._check_unique_email(user_id)
            self._check_unique_nick_name(user_id)

        def _check_unique_nick_name(self, user_id):
            nick_name = self.data.get('nick_name')
            if nick_name and User.objects.filter(nick_name=nick_name).exclude(id=user_id).exists():
                raise AppApiException(1008, _('Nickname is already in use'))

        def _check_unique_email(self, user_id):
            email = self.data.get('email')
            if email and User.objects.filter(email=email).exclude(id=user_id).exists():
                raise AppApiException(1004, _('Email is already in use'))

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
                    )
                )
            ]
        )
        re_password = serializers.CharField(
            required=True,
            label=_("Re Password"),
            validators=[
                validators.RegexValidator(
                    regex=PASSWORD_REGEX,
                    message=_(
                        "The confirmation password must be 6-20 characters long and must be a combination of letters, numbers, and special characters."
                    )
                )
            ]
        )

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            self._check_passwords_match()

        def _check_passwords_match(self):
            if self.data.get('password') != self.data.get('re_password'):
                raise ExceptionCodeConstants.PASSWORD_NOT_EQ_RE_PASSWORD.value.to_app_api_exception()

    class Operate(serializers.Serializer):
        id = serializers.UUIDField(required=True, label=_('User ID'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            self._check_user_exists()

        def _check_user_exists(self):
            if not User.objects.filter(id=self.data.get('id')).exists():
                raise AppApiException(1004, _('User does not exist'))

        @transaction.atomic
        def delete(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                self._check_not_admin()
            user_id = self.data.get('id')
            # TODO  需要删除授权关系
            User.objects.filter(id=user_id).delete()
            return True

        def _check_not_admin(self):
            user = User.objects.filter(id=self.data.get('id')).first()
            if user.role == RoleConstants.ADMIN.name:
                raise AppApiException(1004, _('Unable to delete administrator'))

        def edit(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                UserManageSerializer.UserEditInstance(data=instance).is_valid(user_id=self.data.get('id'),
                                                                              raise_exception=True)
            user = User.objects.filter(id=self.data.get('id')).first()
            self._check_admin_modification(user, instance)
            self._update_user_fields(user, instance)
            update_user_role(instance, user)
            user.save()
            return UserInstanceSerializer(user).data

        @staticmethod
        def _check_admin_modification(user, instance):
            if user.role == RoleConstants.ADMIN.name and 'is_active' in instance and instance.get(
                    'is_active') is not None:
                raise AppApiException(1004, _('Cannot modify administrator status'))

        @staticmethod
        def _update_user_fields(user, instance):
            update_keys = ['email', 'nick_name', 'phone', 'is_active']
            for key in update_keys:
                if key in instance and instance.get(key) is not None:
                    setattr(user, key, instance.get(key))

        def one(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            user = User.objects.filter(id=self.data.get('id')).first()
            workspace_user_role_mapping_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
            if workspace_user_role_mapping_model:
                role_setting = {}
                workspace_user_role_mapping_list = QuerySet(workspace_user_role_mapping_model).filter(
                    user_id=user.id)
                for workspace_user_role_mapping in workspace_user_role_mapping_list:
                    role_id = workspace_user_role_mapping.role_id
                    workspace_id = workspace_user_role_mapping.workspace_id
                    if role_id not in role_setting:
                        role_setting[role_id] = []
                    role_setting[role_id].append(workspace_id)
                return {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'phone': user.phone,
                    'nick_name': user.nick_name,
                    'is_active': user.is_active,
                    'role_setting': role_setting
                }
            return UserInstanceSerializer(user).data

        def re_password(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                UserManageSerializer.RePasswordInstance(data=instance).is_valid(raise_exception=True)
            user = User.objects.filter(id=self.data.get('id')).first()
            user.password = password_encrypt(instance.get('password'))
            user.save()
            return True

    def get_user_list(self, workspace_id):
        """
        获取用户列表
        :param workspace_id: 工作空间ID
        :return: 用户列表
        """
        workspace_user_role_mapping_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
        if workspace_user_role_mapping_model:
            user_ids = (
                workspace_user_role_mapping_model.objects
                .filter(workspace_id=workspace_id)
                .values_list('user_id', flat=True)
                .distinct()
            )
        else:
            user_ids = User.objects.values_list('id', flat=True)

        users = User.objects.filter(id__in=user_ids).values('id', 'nick_name')
        return list(users)

    class BatchDelete(serializers.Serializer):
        ids = serializers.ListField(required=True, label=_('User IDs'))

        def batch_delete(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            ids = self.data.get('ids')
            if not ids:
                raise AppApiException(1004, _('User IDs cannot be empty'))
            User.objects.filter(id__in=ids).delete()
            return True


def update_user_role(instance, user):
    workspace_user_role_mapping_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
    role_setting_model = DatabaseModelManage.get_model("role_model")
    if workspace_user_role_mapping_model:
        role_setting = instance.get('role_setting')
        workspace_user_role_mapping_model.objects.filter(user_id=user.id).delete()
        relations = set()
        for item in role_setting:
            for role_id, workspace_ids in item.items():
                relations.update(set(product([role_id], workspace_ids)))

        role_ids = {role_id for item in role_setting for role_id in item}
        role_ids_is_system = role_setting_model.objects.filter(id__in=role_ids,
                                                               type=RoleConstants.ADMIN.name).values_list(
            'id', flat=True)
        if role_ids_is_system:
            relations = {(role_id, 'SYSTEM') if role_id in role_ids_is_system else (role_id, workspace_id)
                         for role_id, workspace_id in relations}
        for role_id, workspace_id in relations:
            workspace_user_role_mapping_model.objects.create(
                id=uuid.uuid7(),
                role_id=role_id,
                workspace_id=workspace_id,
                user_id=user.id
            )


class RePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        label=_("Email"),
        validators=[validators.EmailValidator(message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                                              code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code)])

    code = serializers.CharField(required=True, label=_("Verification code"))

    password = serializers.CharField(required=True, label=_("Password"),
                                     validators=[validators.RegexValidator(regex=re.compile(
                                         "^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z_!@#$%^&*`~.()-+=]+$)(?![a-z0-9]+$)(?![a-z_!@#$%^&*`~()-+=]+$)"
                                         "(?![0-9_!@#$%^&*`~()-+=]+$)[a-zA-Z0-9_!@#$%^&*`~.()-+=]{6,20}$")
                                         , message=_(
                                             "The confirmation password must be 6-20 characters long and must be a combination of letters, numbers, and special characters."))])

    re_password = serializers.CharField(required=True, label=_("Confirm Password"),
                                        validators=[validators.RegexValidator(regex=re.compile(
                                            "^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z_!@#$%^&*`~.()-+=]+$)(?![a-z0-9]+$)(?![a-z_!@#$%^&*`~()-+=]+$)"
                                            "(?![0-9_!@#$%^&*`~()-+=]+$)[a-zA-Z0-9_!@#$%^&*`~.()-+=]{6,20}$")
                                            , message=_(
                                                "The confirmation password must be 6-20 characters long and must be a combination of letters, numbers, and special characters."))]
                                        )

    class Meta:
        model = User
        fields = '__all__'

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        email = self.data.get("email")
        cache_code = cache.get(get_key(email + ':reset_password'), version=version)
        if self.data.get('password') != self.data.get('re_password'):
            raise AppApiException(ExceptionCodeConstants.PASSWORD_NOT_EQ_RE_PASSWORD.value.code,
                                  ExceptionCodeConstants.PASSWORD_NOT_EQ_RE_PASSWORD.value.message)
        if cache_code != self.data.get('code'):
            raise AppApiException(ExceptionCodeConstants.CODE_ERROR.value.code,
                                  ExceptionCodeConstants.CODE_ERROR.value.message)
        return True

    def reset_password(self):
        """
        修改密码
        :return: 是否成功
        """
        if self.is_valid():
            email = self.data.get("email")
            QuerySet(User).filter(email=email).update(
                password=password_encrypt(self.data.get('password')))
            code_cache_key = email + ":reset_password"
            # 删除验证码缓存
            cache.delete(code_cache_key, version=version)
            return True


class SendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True
        , label=_("Email"),
        validators=[validators.EmailValidator(message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                                              code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code)])

    type = serializers.CharField(required=True, label=_("Type"), validators=[
        validators.RegexValidator(regex=re.compile("^register|reset_password$"),
                                  message=_("The type only supports register|reset_password"), code=500)
    ])

    class Meta:
        model = User
        fields = '__all__'

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=raise_exception)
        user_exists = QuerySet(User).filter(email=self.data.get('email')).exists()
        if not user_exists and self.data.get('type') == 'reset_password':
            raise ExceptionCodeConstants.EMAIL_IS_NOT_EXIST.value.to_app_api_exception()
        elif user_exists and self.data.get('type') == 'register':
            raise ExceptionCodeConstants.EMAIL_IS_EXIST.value.to_app_api_exception()
        code_cache_key = self.data.get('email') + ":" + self.data.get("type")
        code_cache_key_lock = code_cache_key + "_lock"
        ttl = cache.ttl(code_cache_key_lock)
        if ttl is not None:
            raise AppApiException(500, _("Do not send emails again within {seconds} seconds").format(
                seconds=int(ttl.total_seconds())))
        return True

    def send(self):
        """
        发送邮件
        :return:   是否发送成功
        :exception 发送失败异常
        """
        email = self.data.get("email")
        state = self.data.get("type")
        # 生成随机验证码
        code = "".join(list(map(lambda i: random.choice(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'
                                                         ]), range(6))))
        # 获取邮件模板
        language = get_language()
        file = open(
            os.path.join(PROJECT_DIR, "apps", "common", 'template', f'email_template_{to_locale(language)}.html'), "r",
            encoding='utf-8')
        content = file.read()
        file.close()
        code_cache_key = email + ":" + state
        code_cache_key_lock = code_cache_key + "_lock"
        # 设置缓存
        cache.set(get_key(code_cache_key_lock), code, timeout=datetime.timedelta(minutes=1), version=version)
        system_setting = QuerySet(SystemSetting).filter(type=SettingType.EMAIL.value).first()
        if system_setting is None:
            cache.delete(get_key(code_cache_key_lock), version=version)
            raise AppApiException(1004,
                                  _("The email service has not been set up. Please contact the administrator to set up the email service in [Email Settings]."))
        try:
            connection = EmailBackend(system_setting.meta.get("email_host"),
                                      system_setting.meta.get('email_port'),
                                      system_setting.meta.get('email_host_user'),
                                      system_setting.meta.get('email_host_password'),
                                      system_setting.meta.get('email_use_tls'),
                                      False,
                                      system_setting.meta.get('email_use_ssl')
                                      )
            # 发送邮件
            send_mail(_('【Intelligent knowledge base question and answer system-{action}】').format(
                action=_('User registration') if state == 'register' else _('Change password')),
                '',
                html_message=f'{content.replace("${code}", code)}',
                from_email=system_setting.meta.get('from_email'),
                recipient_list=[email], fail_silently=False, connection=connection)
        except Exception as e:
            cache.delete(get_key(code_cache_key_lock))
            raise AppApiException(500, f"{str(e)}" + _("Email sending failed"))
        cache.set(get_key(code_cache_key), code, timeout=datetime.timedelta(minutes=30), version=version)
        return True


class CheckCodeSerializer(serializers.Serializer):
    """
     校验验证码
    """
    email = serializers.EmailField(
        required=True,
        label=_("Email"),
        validators=[validators.EmailValidator(message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                                              code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code)])
    code = serializers.CharField(required=True, label=_("Verification code"))

    type = serializers.CharField(required=True,
                                 label=_("Type"),
                                 validators=[
                                     validators.RegexValidator(regex=re.compile("^register|reset_password$"),
                                                               message=_(
                                                                   "The type only supports register|reset_password"),
                                                               code=500)
                                 ])

    def is_valid(self, *, raise_exception=False):
        super().is_valid()
        value = cache.get(get_key(self.data.get("email") + ":" + self.data.get("type")), version=version)
        if value is None or value != self.data.get("code"):
            raise ExceptionCodeConstants.CODE_ERROR.value.to_app_api_exception()
        return True
