import json

from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import ApplicationAccessToken
from common.constants.cache_version import Cache_Version
from common.exception.app_exception import AppApiException
from common.utils.common import password_encrypt
from common.utils.common import password_verify, needs_password_upgrade
from common.utils.rsa_util import decrypt
from system_manage.models import ChatUser
from users.serializers.login import LoginRequest

system_version, system_get_key = Cache_Version.SYSTEM.value


class ChatUserAccessTokenV3Serializer(serializers.Serializer):
    @staticmethod
    def get_auth_setting():
        application_access_token = ApplicationAccessToken.objects.filter(is_active=True).first()

        if not application_access_token:
            raise AppApiException(1005, _("Invalid access token"))

        return application_access_token.authentication_value

    @staticmethod
    def local_login(instance):
        username = instance.get("username", "")
        encryptedData = instance.get("encryptedData", "")
        if encryptedData:
            json_data = json.loads(decrypt(encryptedData))
            instance.update(json_data)
        try:
            LoginRequest(data=instance).is_valid(raise_exception=True)
        except Exception as e:
            raise e
        auth_setting = ChatUserAccessTokenV3Serializer.get_auth_setting()

        max_attempts = auth_setting.get("max_attempts", 1)
        password = instance.get("password")
        captcha = instance.get("captcha", "")

        # 判断是否需要验证码
        need_captcha = True
        if max_attempts == -1:
            need_captcha = False
        elif max_attempts > 0:
            fail_count = cache.get(system_get_key(f"chat_{username}"), version=system_version) or 0
            need_captcha = fail_count >= max_attempts

        if need_captcha:
            if not captcha:
                raise AppApiException(1005, _("Captcha is required"))

            captcha_cache = cache.get(
                Cache_Version.CAPTCHA.get_key(captcha=f"chat_{username}"), version=Cache_Version.CAPTCHA.get_version()
            )
            if captcha_cache is None or captcha.lower() != captcha_cache:
                raise AppApiException(1005, _("Captcha code error or expiration"))

        user = ChatUser.objects.filter(username=username).first()

        if not user or not password_verify(password, user.password):
            record_login_fail(username)
            raise AppApiException(500, _("The username or password is incorrect"))

        if needs_password_upgrade(user.password):
            user.password = password_encrypt(password)
            user.save(update_fields=["password"])
        if not user.is_active:
            raise AppApiException(1005, _("The user has been disabled, please contact the administrator!"))
        cache.delete(system_get_key(f"chat_{username}"), version=system_version)
        return user


def record_login_fail(username: str, expire: int = 600):
    """记录登录失败次数"""
    if not username:
        return
    fail_key = system_get_key(f"chat_{username}")
    fail_count = cache.get(fail_key, version=system_version)
    if fail_count is None:
        cache.set(fail_key, 1, timeout=expire, version=system_version)
    else:
        cache.incr(fail_key, 1, version=system_version)
