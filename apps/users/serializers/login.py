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

from captcha.image import ImageCaptcha
from django.core import signing
from django.core.cache import cache
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.constants.authentication_type import AuthenticationType
from common.constants.cache_version import Cache_Version
from common.exception.app_exception import AppApiException
from common.utils.common import password_encrypt, get_random_chars
from maxkb.const import CONFIG
from users.models import User


class LoginRequest(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=64, help_text=_("Username"), label=_("Username"))
    password = serializers.CharField(required=True, max_length=128, label=_("Password"))
    captcha = serializers.CharField(required=True, max_length=64, label=_('captcha'))


class LoginResponse(serializers.Serializer):
    """
    登录响应对象
    """
    token = serializers.CharField(required=True, label=_("token"))


class LoginSerializer(serializers.Serializer):

    @staticmethod
    def login(instance):
        LoginRequest(data=instance).is_valid(raise_exception=True)
        username = instance.get('username')
        password = instance.get('password')
        captcha = instance.get('captcha')
        captcha_cache = cache.get(Cache_Version.CAPTCHA.get_key(captcha=captcha.lower()),
                                  version=Cache_Version.CAPTCHA.get_version())
        if captcha_cache is None:
            raise AppApiException(1005, _("Captcha code error or expiration"))
        user = QuerySet(User).filter(username=username, password=password_encrypt(password)).first()
        if user is None:
            raise AppApiException(500, _('The username or password is incorrect'))
        if not user.is_active:
            raise AppApiException(1005, _("The user has been disabled, please contact the administrator!"))
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
    def generate():
        chars = get_random_chars()
        image = ImageCaptcha()
        data = image.generate(chars)
        captcha = base64.b64encode(data.getbuffer())
        cache.set(Cache_Version.CAPTCHA.get_key(captcha=chars.lower()), chars,
                  timeout=60, version=Cache_Version.CAPTCHA.get_version())
        return {'captcha': 'data:image/png;base64,' + captcha.decode()}
