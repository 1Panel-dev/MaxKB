# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： login.py
    @date：2025/4/14 11:08
    @desc:
"""
import base64
import json
import logging

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
from common.utils.rsa_util import decrypt
from maxkb.const import CONFIG
from users.models import User
from common.utils.logger import maxkb_logger


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
    """记录登录失败次数（原子）返回当前失败计数"""
    if not username:
        return 0
    fail_key = system_get_key(f'system_{username}')
    try:
        fail_count = cache.incr(fail_key, 1, version=system_version)
    except ValueError:
        # key 不存在，初始化并设置过期
        cache.set(fail_key, 1, timeout=expire, version=system_version)
        fail_count = 1
    return fail_count


def record_login_fail_lock(username: str, expire: int = 10):
    """
    使用 cache.incr 保证原子递增，并在不存在时初始化计数器并返回当前值。
    这里的计数器用于判断是否应当进入“锁定”分支，避免依赖非原子 get -> set 的组合。
    """
    if not username:
        return 0
    fail_key = system_get_key(f'system_{username}_lock_count')
    try:
        fail_count = cache.incr(fail_key, 1, version=system_version)
    except ValueError:
        # key 不存在，初始化并设置过期（分钟转秒）
        cache.set(fail_key, 1, timeout=expire * 60, version=system_version)
        fail_count = 1
    return fail_count


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
        # 解密数据
        username = instance.get("username", "")
        encrypted_data = instance.get("encryptedData", "")

        if encrypted_data:
            try:
                decrypted_raw = decrypt(encrypted_data)
                # decrypt 可能返回非 JSON 字符串，防护解析异常
                decrypted_data = json.loads(decrypted_raw) if decrypted_raw else {}
                if isinstance(decrypted_data, dict):
                    instance.update(decrypted_data)
            except Exception as e:
                maxkb_logger.exception("Failed to decrypt/parse encryptedData for user %s: %s", username, e)
                raise AppApiException(500, _("Invalid encrypted data"))

        try:
            LoginRequest(data=instance).is_valid(raise_exception=True)
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise AppApiException(500, str(e))

        password = instance.get("password")
        captcha = instance.get("captcha", "")

        # 获取认证配置
        auth_setting = LoginSerializer.get_auth_setting()
        max_attempts = auth_setting.get("max_attempts", 1)
        failed_attempts = auth_setting.get("failed_attempts", 5)
        lock_time = auth_setting.get("lock_time", 10)

        # 检查许可证有效性
        license_validator = DatabaseModelManage.get_model('license_is_valid') or (lambda: False)
        is_license_valid = license_validator() if license_validator() is not None else False

        if is_license_valid:
            # 检查账户是否被锁定
            if LoginSerializer._is_account_locked(username, failed_attempts):
                raise AppApiException(
                    1005,
                    _("This account has been locked for %s minutes, please try again later") % lock_time
                )

            # 验证验证码
            if LoginSerializer._need_captcha(username, max_attempts):
                LoginSerializer._validate_captcha(username, captcha)

        # 验证用户凭据
        user = User.objects.filter(
            username=username,
            password=password_encrypt(password)
        ).first()

        if not user:
            LoginSerializer._handle_failed_login(username, is_license_valid, failed_attempts, lock_time)
            raise AppApiException(500, _('The username or password is incorrect'))

        if not user.is_active:
            raise AppApiException(1005, _("The user has been disabled, please contact the administrator!"))

        # 清除失败计数并生成令牌
        cache.delete(system_get_key(f'system_{username}'), version=system_version)
        cache.delete(system_get_key(f'system_{username}_lock'), version=system_version)
        token = signing.dumps({
            'username': user.username,
            'id': str(user.id),
            'email': user.email,
            'type': AuthenticationType.SYSTEM_USER.value
        })

        version, get_key = Cache_Version.TOKEN.value
        timeout = CONFIG.get_session_timeout()
        cache.set(get_key(token), user, timeout=timeout, version=version)

        return {'token': token}

    @staticmethod
    def _is_account_locked(username: str, failed_attempts: int) -> bool:
        """检查账户是否被锁定"""
        if failed_attempts == -1:
            return False
        lock_cache = cache.get(system_get_key(f'system_{username}_lock'), version=system_version)
        return bool(lock_cache)

    @staticmethod
    def _need_captcha(username: str, max_attempts: int) -> bool:
        """判断是否需要验证码"""
        if max_attempts == -1:
            return False
        elif max_attempts > 0:
            fail_count = cache.get(system_get_key(f'system_{username}'), version=system_version) or 0
            return fail_count >= max_attempts
        return True

    @staticmethod
    def _validate_captcha(username: str, captcha: str) -> None:
        """验证验证码"""
        if not captcha:
            raise AppApiException(1005, _("Captcha is required"))

        captcha_cache = cache.get(
            Cache_Version.CAPTCHA.get_key(captcha=f"system_{username}"),
            version=Cache_Version.CAPTCHA.get_version()
        )

        if captcha_cache is None or captcha.lower() != captcha_cache:
            raise AppApiException(1005, _("Captcha code error or expiration"))

    @staticmethod
    def _handle_failed_login(username: str, is_license_valid: bool, failed_attempts: int, lock_time: int) -> None:
        """处理登录失败

        修复要点：
        - 使用 record_login_fail / record_login_fail_lock 两个原子 incr 来记录失败；
        - 不再依赖精确等于 0 的比较来触发锁，而是基于原子计数 >= 阈值来决定进入锁定分支；
        - 使用 cache.add 原子创建锁键，cache.add 保证只有第一个成功创建者可写入该键；
          其他并发到达的请求若发现计数已到达阈值也应当返回“已锁定”响应，避免出现绕过。
        """
        # 记录普通失败计数（供验证码触发使用）
        try:
            record_login_fail(username)
        except Exception:
            maxkb_logger.exception("Failed to record login fail for user %s", username)

        # 记录用于锁定判断的失败计数（按 lock_time 作为初始化过期分钟）
        lock_fail_count = 0
        try:
            lock_fail_count = record_login_fail_lock(username, lock_time)
        except Exception:
            maxkb_logger.exception("Failed to record lock fail count for user %s", username)

        # 如果不是企业版或禁用锁定功能，直接返回（但计数已经记录）
        if not is_license_valid or failed_attempts <= 0:
            return

        # 当计数小于阈值，告知剩余尝试次数
        if lock_fail_count < failed_attempts:
            remain_attempts = failed_attempts - lock_fail_count
            raise AppApiException(
                1005,
                _("Login failed %s times, account will be locked, you have %s more chances !") % (
                    failed_attempts, remain_attempts
                )
            )

        # 当计数达到或超过阈值时，尝试原子创建锁键；无论 cache.add 返回 True/False，都返回已锁定响应，
        # 因为若为 False 说明其他并发请求已将账户标记为锁定，行为应一致。
        try:
            locked = cache.add(
                system_get_key(f'system_{username}_lock'),
                1,
                timeout=lock_time * 60,
                version=system_version
            )
            if locked:
                maxkb_logger.info("Account %s locked by setting cache key", username)
            else:
                maxkb_logger.info("Account %s lock key already present (another request set it)", username)
        except Exception:
            maxkb_logger.exception("Failed to set lock key for user %s", username)

        raise AppApiException(
            1005,
            _("This account has been locked for %s minutes, please try again later") % lock_time
        )


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
