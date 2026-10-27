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
from portal.models import Portal
from system_manage.models import ChatUser
from users.serializers.login import LoginRequest

system_version, system_get_key = Cache_Version.SYSTEM.value


class ChatUserAccessTokenV3Serializer(serializers.Serializer):
    @classmethod
    def get_auth_setting(cls, access_token):
        application_access_token = ApplicationAccessToken.objects.filter(
            access_token=access_token, is_active=True
        ).first()

        if not application_access_token:
            raise AppApiException(1005, _("Invalid access token"))

        return application_access_token.authentication_value

    @classmethod
    def _get_login_policy(cls, access_token):
        """返回 (scope, max_attempts, failed_attempts, lock_time)；scope 作为缓存 key 前缀。"""
        if access_token:
            auth_setting = cls.get_auth_setting(access_token)
            return (
                f"chat_{access_token}",
                auth_setting.get("max_attempts", 1),
                # 应用未配置锁定阈值时默认不锁定，保持原有行为
                auth_setting.get("failed_attempts", 5),
                auth_setting.get("lock_time", 10),
            )
        portal = Portal.objects.first()
        if portal is None or not portal.enable_auth:
            raise AppApiException(500, _("Portal authentication is not enabled"))
        auth_config = portal.auth_config or {}
        if "LOCAL" not in auth_config.get("login_value", ["LOCAL"]):
            raise AppApiException(500, _("Portal local login is not enabled"))
        return (
            "portal",
            auth_config.get("max_attempts", 1),
            auth_config.get("failed_attempts", 5),
            auth_config.get("lock_time", 10),
        )

    @classmethod
    def _is_account_locked(cls, scope, username, failed_attempts):
        if failed_attempts == -1:
            return False
        return bool(cache.get(system_get_key(f"{scope}_{username}_lock"), version=system_version))

    @classmethod
    def _need_captcha(cls, scope, username, max_attempts):
        if max_attempts == -1:
            return False
        if max_attempts > 0:
            fail_count = cache.get(system_get_key(f"{scope}_{username}"), version=system_version) or 0
            return fail_count >= max_attempts
        return True

    @classmethod
    def _validate_captcha(cls, scope, username, captcha, failed_attempts=5, lock_time=10):
        if not captcha:
            raise AppApiException(1005, _("Captcha is required"))
        captcha_key = Cache_Version.CAPTCHA.get_key(captcha=f"{scope}_{username}")
        captcha_cache = cache.get(captcha_key, version=Cache_Version.CAPTCHA.get_version())
        if captcha_cache is None or captcha.lower() != captcha_cache:
            # 校验失败与口令失败共用同一失败计数与锁定机制，防止"识别-试错"循环绕过验证码
            cls._record_login_failure(scope, username, failed_attempts, lock_time)
            raise AppApiException(1005, _("Captcha code error or expiration"))
        # 校验通过即销毁，保证验证码一次性使用
        cache.delete(captcha_key, version=Cache_Version.CAPTCHA.get_version())

    @classmethod
    def _record_login_failure(cls, scope, username, failed_attempts, lock_time):
        """记录一次认证失败（口令或验证码），累计计数并在达到阈值时创建锁键；不抛异常。"""
        try:
            _record_login_fail(scope, username)
        except Exception:
            pass
        lock_fail_count = 0
        try:
            lock_fail_count = _record_login_fail_lock(scope, username, lock_time)
        except Exception:
            pass
        if failed_attempts > 0 and lock_fail_count >= failed_attempts:
            try:
                cache.add(system_get_key(f"{scope}_{username}_lock"), 1, timeout=lock_time * 60, version=system_version)
            except Exception:
                pass
        return lock_fail_count

    @classmethod
    def _handle_failed_login(cls, scope, username, failed_attempts, lock_time):
        lock_fail_count = cls._record_login_failure(scope, username, failed_attempts, lock_time)
        # 仅由失败次数配置控制（CE/PE 同样生效）；计数在此之前已记录
        if failed_attempts <= 0:
            return
        if lock_fail_count < failed_attempts:
            remain_attempts = failed_attempts - lock_fail_count
            raise AppApiException(
                1005,
                _("Login failed %s times, account will be locked, you have %s more chances !")
                % (failed_attempts, remain_attempts),
            )
        raise AppApiException(
            1005, _("This account has been locked for %s minutes, please try again later") % lock_time
        )

    @classmethod
    def local_login(cls, instance, access_token=None):
        username = instance.get("username", "")
        encryptedData = instance.get("encryptedData", "")
        if encryptedData:
            json_data = json.loads(decrypt(encryptedData))
            instance.update(json_data)
        LoginRequest(data=instance).is_valid(raise_exception=True)

        scope, max_attempts, failed_attempts, lock_time = cls._get_login_policy(access_token)

        if cls._is_account_locked(scope, username, failed_attempts):
            raise AppApiException(
                1005, _("This account has been locked for %s minutes, please try again later") % lock_time
            )

        password = instance.get("password")
        captcha = instance.get("captcha", "")
        if cls._need_captcha(scope, username, max_attempts):
            cls._validate_captcha(scope, username, captcha, failed_attempts, lock_time)

        user = ChatUser.objects.filter(username=username).first()

        if not user or not password_verify(password, user.password):
            cls._handle_failed_login(scope, username, failed_attempts, lock_time)
            raise AppApiException(500, _("The username or password is incorrect"))

        if needs_password_upgrade(user.password):
            user.password = password_encrypt(password)
            user.save(update_fields=["password"])
        if not user.is_active:
            raise AppApiException(1005, _("The user has been disabled, please contact the administrator!"))
        cache.delete(system_get_key(f"{scope}_{username}"), version=system_version)
        cache.delete(system_get_key(f"{scope}_{username}_lock_count"), version=system_version)
        cache.delete(system_get_key(f"{scope}_{username}_lock"), version=system_version)
        return user


def _record_login_fail(scope, username, expire=600):
    if not username:
        return
    fail_key = system_get_key(f"{scope}_{username}")
    try:
        cache.incr(fail_key, 1, version=system_version)
    except ValueError:
        cache.set(fail_key, 1, timeout=expire, version=system_version)


def _record_login_fail_lock(scope, username, expire=10):
    if not username:
        return 0
    lock_key = system_get_key(f"{scope}_{username}_lock_count")
    try:
        fail_count = cache.incr(lock_key, 1, version=system_version)
    except ValueError:
        cache.set(lock_key, 1, timeout=expire * 60, version=system_version)
        fail_count = 1
    return fail_count
