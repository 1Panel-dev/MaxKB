# coding=utf-8
"""
    @project: qabot
    @Author：虎
    @file： team_serializers.py
    @date：2023/9/5 16:32
    @desc:
"""
import datetime
import os
import random
import re
import uuid

from django.core import validators, signing, cache
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q, QuerySet
from drf_yasg import openapi
from rest_framework import serializers

from common.constants.authentication_type import AuthenticationType
from common.constants.exception_code_constants import ExceptionCodeConstants
from common.constants.permission_constants import RoleConstants, get_permission_list_by_role
from common.exception.app_exception import AppApiException
from common.mixins.api_mixin import ApiMixin
from common.response.result import get_api_response
from common.util.lock import lock
from setting.models import Team
from smartdoc.conf import PROJECT_DIR
from smartdoc.settings import EMAIL_ADDRESS
from users.models.user import User, password_encrypt, get_user_dynamics_permission

user_cache = cache.caches['user_cache']


class LoginSerializer(ApiMixin, serializers.Serializer):
    username = serializers.CharField(required=True,
                                     validators=[
                                         validators.MaxLengthValidator(limit_value=20,
                                                                       message=ExceptionCodeConstants.USERNAME_ERROR.value.message),
                                         validators.MinLengthValidator(limit_value=6,
                                                                       message=ExceptionCodeConstants.USERNAME_ERROR.value.message)
                                     ])

    password = serializers.CharField(required=True)

    def is_valid(self, *, raise_exception=False):
        """
        校验参数
        :param raise_exception: 是否抛出异常 只能是True
        :return: 用户信息
        """
        super().is_valid(raise_exception=True)
        username = self.data.get("username")
        password = password_encrypt(self.data.get("password"))
        user = self.Meta.model.objects.filter(Q(username=username,
                                                password=password) | Q(email=username,
                                                                       password=password)).first()
        if user is None:
            raise ExceptionCodeConstants.INCORRECT_USERNAME_AND_PASSWORD.value.to_app_api_exception()
        return user

    def get_user_token(self):
        """
        获取用户Token
        :return: 用户Token(认证信息)
        """
        user = self.is_valid()
        token = signing.dumps({'username': user.username, 'id': str(user.id), 'email': user.email,
                               'type': AuthenticationType.USER.value})
        return token

    class Meta:
        model = User
        fields = '__all__'

    def get_request_body_api(self):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, title="用户名", description="用户名"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, title="密码", description="密码")
            }
        )

    def get_response_body_api(self):
        return get_api_response(openapi.Schema(
            type=openapi.TYPE_STRING,
            title="token",
            default="xxxx",
            description="认证token"
        ))


class RegisterSerializer(ApiMixin, serializers.Serializer):
    """
    注册请求对象
    """
    email = serializers.EmailField(
        validators=[validators.EmailValidator(message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                                              code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code)])

    username = serializers.CharField(required=True,
                                     validators=[
                                         validators.MaxLengthValidator(limit_value=20,
                                                                       message=ExceptionCodeConstants.USERNAME_ERROR.value.message),
                                         validators.MinLengthValidator(limit_value=6,
                                                                       message=ExceptionCodeConstants.USERNAME_ERROR.value.message)
                                     ])
    password = serializers.CharField(required=True)

    re_password = serializers.CharField(required=True)

    code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = '__all__'

    @lock(lock_key=lambda this, raise_exception: (
            this.initial_data.get("email") + ":register"

    ))
    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        if self.data.get('password') != self.data.get('re_password'):
            raise ExceptionCodeConstants.PASSWORD_NOT_EQ_RE_PASSWORD.value.to_app_api_exception()
        username = self.data.get("username")
        email = self.data.get("email")
        code = self.data.get("code")
        code_cache_key = email + ":register"
        cache_code = user_cache.get(code_cache_key)
        if code != cache_code:
            raise ExceptionCodeConstants.CODE_ERROR.value.to_app_api_exception()
        u = User.objects.filter(Q(username=username) | Q(email=email)).first()
        if u is not None:
            if u.email == email:
                raise ExceptionCodeConstants.EMAIL_IS_EXIST.value.to_app_api_exception()
            if u.username == username:
                raise ExceptionCodeConstants.USERNAME_IS_EXIST.value.to_app_api_exception()

        return True

    @transaction.atomic
    def save(self, **kwargs):
        m = User(
            **{'id': uuid.uuid1(), 'email': self.data.get("email"), 'username': self.data.get("username"),
               'role': RoleConstants.USER.name})
        m.set_password(self.data.get("password"))
        # 插入用户
        m.save()
        # 初始化用户团队
        Team(**{'user': m, 'name': m.username + '的团队'}).save()
        email = self.data.get("email")
        code_cache_key = email + ":register"
        # 删除验证码缓存
        user_cache.delete(code_cache_key)

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'email', 'password', 're_password', 'code'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, title="用户名", description="用户名"),
                'email': openapi.Schema(type=openapi.TYPE_STRING, title="邮箱", description="邮箱地址"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, title="密码", description="密码"),
                're_password': openapi.Schema(type=openapi.TYPE_STRING, title="确认密码", description="确认密码"),
                'code': openapi.Schema(type=openapi.TYPE_STRING, title="验证码", description="验证码")
            }
        )


class CheckCodeSerializer(ApiMixin, serializers.Serializer):
    """
     校验验证码
    """
    email = serializers.EmailField(
        validators=[validators.EmailValidator(message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                                              code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code)])
    code = serializers.CharField(required=True)

    type = serializers.CharField(required=True, validators=[
        validators.RegexValidator(regex=re.compile("^register|reset_password$"),
                                  message="只支持register|reset_password", code=500)
    ])

    def is_valid(self, *, raise_exception=False):
        super().is_valid()
        value = user_cache.get(self.data.get("email") + ":" + self.data.get("type"))
        if value is None or value != self.data.get("code"):
            raise ExceptionCodeConstants.CODE_ERROR.value.to_app_api_exception()
        return True

    class Meta:
        model = User
        fields = '__all__'

    def get_request_body_api(self):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'code', 'type'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, title="邮箱", description="邮箱地址"),
                'code': openapi.Schema(type=openapi.TYPE_STRING, title="验证码", description="验证码"),
                'type': openapi.Schema(type=openapi.TYPE_STRING, title="类型", description="register|reset_password")
            }
        )

    def get_response_body_api(self):
        return get_api_response(openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            title="是否成功",
            default=True,
            description="错误提示"))


class RePasswordSerializer(ApiMixin, serializers.Serializer):
    email = serializers.EmailField(
        validators=[validators.EmailValidator(message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                                              code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code)])

    code = serializers.CharField(required=True)

    password = serializers.CharField(required=True)

    re_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = '__all__'

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        email = self.data.get("email")
        cache_code = user_cache.get(email + ':reset_password')
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
            self.Meta.model.objects.filter(email=email).update(
                password=password_encrypt(self.data.get('password')))
            code_cache_key = email + ":reset_password"
            # 删除验证码缓存
            user_cache.delete(code_cache_key)
            return True

    def get_request_body_api(self):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'code', "password", 're_password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, title="邮箱", description="邮箱地址"),
                'code': openapi.Schema(type=openapi.TYPE_STRING, title="验证码", description="验证码"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, title="密码", description="密码"),
                're_password': openapi.Schema(type=openapi.TYPE_STRING, title="确认密码", description="确认密码")
            }
        )


class SendEmailSerializer(ApiMixin, serializers.Serializer):
    email = serializers.EmailField(
        validators=[validators.EmailValidator(message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                                              code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code)])

    type = serializers.CharField(required=True, validators=[
        validators.RegexValidator(regex=re.compile("^register|reset_password$"),
                                  message="只支持register|reset_password", code=500)
    ])

    class Meta:
        model = User
        fields = '__all__'

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=raise_exception)
        user_exists = self.Meta.model.objects.filter(email=self.data.get('email')).exists()
        if not user_exists and self.data.get('type') == 'reset_password':
            raise ExceptionCodeConstants.EMAIL_IS_NOT_EXIST.value.to_app_api_exception()
        elif user_exists and self.data.get('type') == 'register':
            raise ExceptionCodeConstants.EMAIL_IS_EXIST.value.to_app_api_exception()
        code_cache_key = self.data.get('email') + ":" + self.data.get("type")
        code_cache_key_lock = code_cache_key + "_lock"
        ttl = user_cache.ttl(code_cache_key_lock)
        if ttl is not None:
            raise AppApiException(500, f"{ttl.total_seconds()}秒内请勿重复发送邮件")
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
        file = open(os.path.join(PROJECT_DIR, "apps", "common", 'template', 'email_template.html'), "r",
                    encoding='utf-8')
        content = file.read()
        file.close()
        code_cache_key = email + ":" + state
        code_cache_key_lock = code_cache_key + "_lock"
        # 设置缓存
        user_cache.set(code_cache_key_lock, code, timeout=datetime.timedelta(minutes=1))
        try:
            # 发送邮件
            send_mail(f'【智能客服{"用户注册" if state == "register" else "修改密码"}】',
                      '',
                      html_message=f'{content.replace("${code}", code)}',
                      from_email=EMAIL_ADDRESS,
                      recipient_list=[email], fail_silently=False)
        except Exception as e:
            user_cache.delete(code_cache_key_lock)
            raise AppApiException(500, f"{str(e)}邮件发送失败")
        user_cache.set(code_cache_key, code, timeout=datetime.timedelta(minutes=30))
        return True

    def get_request_body_api(self):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'type'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, title="邮箱", description="邮箱地址"),
                'type': openapi.Schema(type=openapi.TYPE_STRING, title="类型", description="register|reset_password")
            }
        )

    def get_response_body_api(self):
        return get_api_response(openapi.Schema(type=openapi.TYPE_STRING, default=True))


class UserProfile(ApiMixin):

    @staticmethod
    def get_user_profile(user: User):
        """
        获取用户详情
        :param user: 用户对象
        :return:
        """
        permission_list = get_user_dynamics_permission(str(user.id))
        permission_list += [p.value for p in get_permission_list_by_role(RoleConstants[user.role])]
        return {'id': user.id, 'username': user.username, 'email': user.email, 'role': user.role,
                'permissions': [str(p) for p in permission_list]}

    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'username', 'email', 'role', 'is_active'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, title="用户id", description="用户id"),
                'username': openapi.Schema(type=openapi.TYPE_STRING, title="用户名", description="用户名"),
                'email': openapi.Schema(type=openapi.TYPE_STRING, title="邮箱", description="邮箱地址"),
                'role': openapi.Schema(type=openapi.TYPE_STRING, title="角色", description="角色"),
                'is_active': openapi.Schema(type=openapi.TYPE_STRING, title="是否可用", description="是否可用"),
                "permissions": openapi.Schema(type=openapi.TYPE_ARRAY, title="权限列表", description="权限列表",
                                              items=openapi.Schema(type=openapi.TYPE_STRING))
            }
        )


class UserSerializer(ApiMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "id",
                  "username", ]

    def get_response_body_api(self):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'username', 'email', 'role', 'is_active'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, title="用户id", description="用户id"),
                'username': openapi.Schema(type=openapi.TYPE_STRING, title="用户名", description="用户名"),
                'email': openapi.Schema(type=openapi.TYPE_STRING, title="邮箱", description="邮箱地址"),
                'role': openapi.Schema(type=openapi.TYPE_STRING, title="角色", description="角色"),
                'is_active': openapi.Schema(type=openapi.TYPE_STRING, title="是否可用", description="是否可用")
            }
        )

    class Query(ApiMixin, serializers.Serializer):
        email_or_username = serializers.CharField(required=True)

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='email_or_username',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='邮箱或者用户名')]

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['username', 'email', 'id'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title='用户主键id', description="用户主键id"),
                    'username': openapi.Schema(type=openapi.TYPE_STRING, title="用户名", description="用户名"),
                    'email': openapi.Schema(type=openapi.TYPE_STRING, title="邮箱", description="邮箱地址")
                }
            )

        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            email_or_username = self.data.get('email_or_username')
            return [{'id': user_model.id, 'username': user_model.username, 'email': user_model.email} for user_model in
                    QuerySet(User).filter(Q(username=email_or_username) | Q(email=email_or_username))]
