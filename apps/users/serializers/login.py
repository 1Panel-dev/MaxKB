# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： login.py
    @date：2025/4/14 11:08
    @desc:
"""
import base64
import datetime
import json

from captcha.image import ImageCaptcha
from django.core import signing
from django.core.cache import cache
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import ApplicationAccessToken
from common.constants.authentication_type import AuthenticationType
from common.constants.cache_version import Cache_Version
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.exception.app_exception import AppApiException
from common.utils.common import password_encrypt, get_random_chars
from common.utils.rsa_util import encrypt, decrypt
from maxkb.const import CONFIG
from users.models import User


class LoginRequest(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=64, help_text=_("Username"), label=_("Username"))
    password = serializers.CharField(required=True, max_length=128, label=_("Password"))
    captcha = serializers.CharField(required=False, max_length=64, label=_('captcha'), allow_null=True,
                                    allow_blank=True)
    encryptedData = serializers.CharField(required=False, label=_('encryptedData'), allow_null=True,
                                          allow_blank=True)


system_version, system_get_key = Cache_Version.SYSTEM.value


class LoginResponse(serializers.Serializer):
    """
    登录响应对象
    """
    token = serializers.CharField(required=True, label=_("token"))


def record_login_fail(username: str, expire: int = 600):
    """记录登录失败次数"""
    if not username:
        return
    fail_key = system_get_key(f'system_{username}')
    fail_count = cache.get(fail_key, version=system_version)
    if fail_count is None:
        cache.set(fail_key, 1, timeout=expire, version=system_version)
    else:
        cache.incr(fail_key, 1, version=system_version)


class LoginSerializer(serializers.Serializer):

    @staticmethod
    def get_auth_setting():
        """获取认证设置"""
        auth_setting_model = DatabaseModelManage.get_model('auth_setting')
        auth_setting = {}
        if auth_setting_model:
            setting_obj = auth_setting_model.objects.filter(param_key='auth_setting').first()
            if setting_obj:
                try:
                    auth_setting = json.loads(setting_obj.param_value) or {}
                except Exception:
                    auth_setting = {}
        return auth_setting

    @staticmethod
    def login(instance):
        username = instance.get("username", "")
        encryptedData = instance.get("encryptedData", "")
        if encryptedData:
            json_data = json.loads(decrypt(encryptedData))
            instance.update(json_data)
        try:
            LoginRequest(data=instance).is_valid(raise_exception=True)
        except Exception as e:
            record_login_fail(username)
            raise e
        auth_setting = LoginSerializer.get_auth_setting()

        max_attempts = auth_setting.get("max_attempts", 1)
        password = instance.get("password")
        captcha = instance.get("captcha", "")

        # 判断是否需要验证码
        need_captcha = False
        if max_attempts == -1:
            need_captcha = False
        elif max_attempts > 0:
            fail_count = cache.get(system_get_key(f'system_{username}'), version=system_version) or 0
            need_captcha = fail_count >= max_attempts

        if need_captcha:
            if not captcha:
                raise AppApiException(1005, _("Captcha is required"))

            captcha_cache = cache.get(
                Cache_Version.CAPTCHA.get_key(captcha=f"system_{username}"),
                version=Cache_Version.CAPTCHA.get_version()
            )
            if captcha_cache is None or captcha.lower() != captcha_cache:
                raise AppApiException(1005, _("Captcha code error or expiration"))

        user = QuerySet(User).filter(username=username, password=password_encrypt(password)).first()
        if user is None:
            record_login_fail(username)
            raise AppApiException(500, _('The username or password is incorrect'))
        if not user.is_active:
            record_login_fail(username)
            raise AppApiException(1005, _("The user has been disabled, please contact the administrator!"))
        cache.delete(system_get_key(f'system_{username}'), version=system_version)
        token = signing.dumps({'username': user.username,
                               'id': str(user.id),
                               'email': user.email,
                               'type': AuthenticationType.SYSTEM_USER.value})
        version, get_key = Cache_Version.TOKEN.value
        timeout = CONFIG.get_session_timeout()
        cache.set(get_key(token), user, timeout=timeout, version=version)
        return {'token': token}


class CaptchaResponse(serializers.Serializer):
    """
       登录响应对象
       """
    captcha = serializers.CharField(required=True, label=_("captcha"))


class CaptchaSerializer(serializers.Serializer):
    @staticmethod
    def generate(username: str, type: str = 'system'):
        auth_setting = LoginSerializer.get_auth_setting()
        max_attempts = auth_setting.get("max_attempts", 1)

        need_captcha = True
        if max_attempts == -1:
            need_captcha = False
        elif max_attempts > 0:
            fail_count = cache.get(system_get_key(f'system_{username}'), version=system_version) or 0
            need_captcha = fail_count >= max_attempts

        return CaptchaSerializer._generate_captcha_if_needed(username, type, need_captcha)

    @staticmethod
    def chat_generate(username: str, type: str = 'chat', access_token: str = ''):
        application_access_token = ApplicationAccessToken.objects.filter(
            access_token=access_token
        ).first()

        if not application_access_token:
            raise AppApiException(1005, _('Invalid access token'))

        auth_setting = application_access_token.authentication_value
        max_attempts = auth_setting.get("max_attempts", 1)

        need_captcha = True
        if max_attempts == -1:
            need_captcha = False
        elif max_attempts > 0:
            fail_count = cache.get(system_get_key(f'{type}_{username}'), version=system_version) or 0
            need_captcha = fail_count >= max_attempts


        return CaptchaSerializer._generate_captcha_if_needed(username, type, need_captcha)

    @staticmethod
    def _generate_captcha_if_needed(username: str, type: str, need_captcha: bool):
        """
        提取的公共验证码生成方法
        """
        if need_captcha:
            chars = get_random_chars()
            image = ImageCaptcha()
            data = image.generate(chars)
            captcha = base64.b64encode(data.getbuffer())
            cache.set(Cache_Version.CAPTCHA.get_key(captcha=f'{type}_{username}'), chars.lower(),
                      timeout=300, version=Cache_Version.CAPTCHA.get_version())
            return {'captcha': 'data:image/png;base64,' + captcha.decode()}
        return {'captcha': ''}
