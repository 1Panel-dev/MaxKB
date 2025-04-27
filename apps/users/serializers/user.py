# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： user.py
    @date：2025/4/14 19:18
    @desc:
"""
import re

from django.db import transaction
from django.db.models import QuerySet, Q
from rest_framework import serializers
import uuid_utils.compat as uuid
from common.constants.exception_code_constants import ExceptionCodeConstants
from common.constants.permission_constants import RoleConstants
from common.utils.common import valid_license, password_encrypt
from users.models import User
from django.utils.translation import gettext_lazy as _
from django.core import validators


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


class UserProfileSerializer(serializers.Serializer):
    @staticmethod
    def profile(user: User):
        """
        获取用户详情
        :param user: 用户对象
        :return:
        """
        return {'id': user.id,
                'username': user.username,
                'nick_name': user.nick_name,
                'email': user.email,
                'role': user.role,
                'permissions': [str(p) for p in []],
                'is_edit_password': user.password == 'd880e722c47a34d8e9fce789fc62389d' if user.role == 'ADMIN' else False,
                'language': user.language}


class UserManageSerializer(serializers.Serializer):
    class UserInstance(serializers.Serializer):
        email = serializers.EmailField(
            required=True,
            label=_("Email"),
            validators=[validators.EmailValidator(message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                                                  code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code)])

        username = serializers.CharField(required=True,
                                         label=_("Username"),
                                         max_length=20,
                                         min_length=6,
                                         validators=[
                                             validators.RegexValidator(regex=re.compile("^.{6,20}$"),
                                                                       message=_(
                                                                           'Username must be 6-20 characters long'))
                                         ])
        password = serializers.CharField(required=True, label=_("Password"), max_length=20, min_length=6,
                                         validators=[validators.RegexValidator(regex=re.compile(
                                             "^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z_!@#$%^&*`~.()-+=]+$)(?![a-z0-9]+$)(?![a-z_!@#$%^&*`~()-+=]+$)"
                                             "(?![0-9_!@#$%^&*`~()-+=]+$)[a-zA-Z0-9_!@#$%^&*`~.()-+=]{6,20}$")
                                             , message=_(
                                                 "The password must be 6-20 characters long and must be a combination of letters, numbers, and special characters."))])

        nick_name = serializers.CharField(required=False, label=_("Nick name"), max_length=64,
                                          allow_null=True, allow_blank=True)
        phone = serializers.CharField(required=False, label=_("Phone"), max_length=20,
                                      allow_null=True, allow_blank=True)

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            username = self.data.get('username')
            email = self.data.get('email')
            u = QuerySet(User).filter(Q(username=username) | Q(email=email)).first()
            if u is not None:
                if u.email == email:
                    raise ExceptionCodeConstants.EMAIL_IS_EXIST.value.to_app_api_exception()
                if u.username == username:
                    raise ExceptionCodeConstants.USERNAME_IS_EXIST.value.to_app_api_exception()

    @valid_license(model=User, count=2,
                   message=_(
                       'The community version supports up to 2 users. If you need more users, please contact us (https://fit2cloud.com/).'))
    @transaction.atomic
    def save(self, instance, with_valid=True):
        if with_valid:
            UserManageSerializer.UserInstance(data=instance).is_valid(raise_exception=True)

        user = User(id=uuid.uuid7(), email=instance.get('email'),
                    phone="" if instance.get('phone') is None else instance.get('phone'),
                    nick_name="" if instance.get('nick_name') is None else instance.get('nick_name')
                    , username=instance.get('username'), password=password_encrypt(instance.get('password')),
                    role=RoleConstants.USER.name, source="LOCAL",
                    is_active=True)
        user.save()
        return UserProfileSerializer(user).data
