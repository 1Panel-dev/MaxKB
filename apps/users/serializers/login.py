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

from application.models import ApplicationAccessToken
from captcha.image import ImageCaptcha
from common.auth.common import FileToken
from common.constants.authentication_type import AuthenticationType
from common.constants.cache_version import Cache_Version
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.exception.app_exception import AppApiException
from common.utils.common import get_random_chars, needs_password_upgrade, password_encrypt, password_verify
from common.utils.logger import maxkb_logger
from common.utils.rsa_util import decrypt
from django.core import signing
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from maxkb.const import CONFIG
from rest_framework import serializers
from users.models import User

system_version, system_get_key = Cache_Version.SYSTEM.value


class LoginRequest(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=64, label=_("Username"))
    password = serializers.CharField(required=True, max_length=128, label=_("Password"))
    captcha = serializers.CharField(required=False, max_length=64, allow_null=True, allow_blank=True)
    encryptedData = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class LoginResponse(serializers.Serializer):
    token = serializers.CharField(required=True, label=_("token"))


def _incr_fail_count(cache_key: str, expire: int) -> int:
    """原子递增失败计数，key 不存在时初始化并返回当前值"""
    try:
        return cache.incr(cache_key, 1, version=system_version)
    except ValueError:
        cache.set(cache_key, 1, timeout=expire, version=system_version)
        return 1


def record_login_fail(username: str, expire: int = 600) -> int:
    """记录登录失败次数（原子）返回当前失败计数"""
    if not username:
        return 0
    return _incr_fail_count(system_get_key(f"system_{username}"), expire)


def record_login_fail_lock(username: str, expire: int = 10) -> int:
    """
    使用 cache.incr 保证原子递增，并在不存在时初始化计数器并返回当前值。
    这里的计数器用于判断是否应当进入"锁定"分支，避免依赖非原子 get -> set 的组合。
    """
    if not username:
        return 0
    return _incr_fail_count(system_get_key(f"system_{username}_lock_count"), expire * 60)


class LoginSerializer(serializers.Serializer):
    @staticmethod
    def get_auth_setting():
        """获取认证设置"""
        auth_setting_model = DatabaseModelManage.get_model("auth_setting")
        if not auth_setting_model:
            return {}
        setting_obj = auth_setting_model.objects.filter(param_key="auth_setting").first()
        if not setting_obj:
            return {}
        try:
            return json.loads(setting_obj.param_value) or {}
        except Exception:
            return {}

    @staticmethod
    def _decrypt_request_data(instance: dict) -> dict:
        """解密并合并 encryptedData，返回更新后的请求数据"""
        username = instance.get("username", "")
        encrypted_data = instance.get("encryptedData", "")
        if not encrypted_data:
            return instance

        try:
            decrypted_raw = decrypt(encrypted_data)
            # decrypt 可能返回非 JSON 字符串，防护解析异常
            decrypted_data = json.loads(decrypted_raw) if decrypted_raw else {}
            if isinstance(decrypted_data, dict):
                instance.update(decrypted_data)
        except Exception as e:
            maxkb_logger.exception("Failed to decrypt/parse encryptedData for user %s: %s", username, e)
            raise AppApiException(500, _("Invalid encrypted data"))
        return instance

    @staticmethod
    def _authenticate(username: str, password: str) -> User | None:
        """校验用户名密码，失败记录计数并抛异常"""
        user = User.objects.filter(username=username).first()
        if not user or not password_verify(password, user.password):
            return None

        # Transparently upgrade legacy MD5 hash to PBKDF2
        if needs_password_upgrade(user.password):
            user.password = password_encrypt(password)
            user.save(update_fields=["password"])
        return user

    @staticmethod
    def _issue_token(user: User) -> str:
        """签发登录 token 并写入缓存"""
        token = signing.dumps(
            {
                "username": user.username,
                "id": str(user.id),
                "email": user.email,
                "type": AuthenticationType.SYSTEM_USER.value,
            }
        )
        version, get_key = Cache_Version.TOKEN.value
        cache.set(get_key(token), user, timeout=CONFIG.get_session_timeout(), version=version)
        return token

    @staticmethod
    def login(instance):
        # 解密数据
        instance = LoginSerializer._decrypt_request_data(instance)

        request_serializer = LoginRequest(data=instance)
        request_serializer.is_valid(raise_exception=True)
        validated_data = request_serializer.validated_data
        username = validated_data["username"]
        password = validated_data["password"]
        captcha = validated_data.get("captcha", "")

        # 获取认证配置
        auth_setting = LoginSerializer.get_auth_setting()
        max_attempts = auth_setting.get("max_attempts", 1)
        failed_attempts = auth_setting.get("failed_attempts", 5)
        lock_time = auth_setting.get("lock_time", 10)

        # 检查许可证有效性
        license_validator = DatabaseModelManage.get_model("license_is_valid")
        is_license_valid = bool(license_validator()) if license_validator else False

        if is_license_valid and LoginSerializer._is_account_locked(username, failed_attempts):
            # 检查账户是否被锁定
            raise AppApiException(
                1005, _("This account has been locked for %s minutes, please try again later") % lock_time
            )
        if LoginSerializer._need_captcha(username, max_attempts):
            # 验证验证码
            LoginSerializer._validate_captcha(username, captcha)

        # 验证用户凭据：先按用户名查找，再用 password_verify 验证密码
        user = LoginSerializer._authenticate(username, password)
        if user is None:
            LoginSerializer._handle_failed_login(username, is_license_valid, failed_attempts, lock_time)
            raise AppApiException(500, _("The username or password is incorrect"))

        if not user.is_active:
            raise AppApiException(1005, _("The user has been disabled, please contact the administrator!"))

        # 清除失败计数并生成令牌
        cache.delete(system_get_key(f"system_{username}"), version=system_version)
        cache.delete(system_get_key(f"system_{username}_lock"), version=system_version)
        token = LoginSerializer._issue_token(user)

        return {"token": token}, FileToken(str(user.id), AuthenticationType.SYSTEM_USER.value).to_token()

    @staticmethod
    def _is_account_locked(username: str, failed_attempts: int) -> bool:
        """检查账户是否被锁定"""
        if failed_attempts == -1:
            return False
        lock_cache = cache.get(system_get_key(f"system_{username}_lock"), version=system_version)
        return bool(lock_cache)

    @staticmethod
    def _need_captcha(username: str, max_attempts: int) -> bool:
        return LoginSerializer._need_captcha_by_key(system_get_key(f"system_{username}"), max_attempts)

    @staticmethod
    def _need_captcha_by_key(cache_key: str, max_attempts: int) -> bool:
        """判断是否需要验证码"""
        if max_attempts == -1:
            return False
        if max_attempts > 0:
            fail_count = cache.get(cache_key, version=system_version) or 0
            return fail_count >= max_attempts
        return True

    @staticmethod
    def _validate_captcha(username: str, captcha: str) -> None:
        """验证验证码"""
        if not captcha:
            raise AppApiException(1005, _("Captcha is required"))

        captcha_cache = cache.get(
            Cache_Version.CAPTCHA.get_key(captcha=f"system_{username}"), version=Cache_Version.CAPTCHA.get_version()
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
          其他并发到达的请求若发现计数已到达阈值也应当返回"已锁定"响应，避免出现绕过。
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
                _("Login failed %s times, account will be locked, you have %s more chances !")
                % (failed_attempts, remain_attempts),
            )

        # 当计数达到或超过阈值时，尝试原子创建锁键；无论 cache.add 返回 True/False，都返回已锁定响应，
        # 因为若为 False 说明其他并发请求已将账户标记为锁定，行为应一致。
        try:
            locked = cache.add(
                system_get_key(f"system_{username}_lock"), 1, timeout=lock_time * 60, version=system_version
            )
            if locked:
                maxkb_logger.info("Account %s locked by setting cache key", username)
            else:
                maxkb_logger.info("Account %s lock key already present (another request set it)", username)
        except Exception:
            maxkb_logger.exception("Failed to set lock key for user %s", username)

        raise AppApiException(
            1005, _("This account has been locked for %s minutes, please try again later") % lock_time
        )


class CaptchaResponse(serializers.Serializer):
    captcha = serializers.CharField(required=True, label=_("captcha"))


class CaptchaSerializer(serializers.Serializer):
    @staticmethod
    def generate(username: str, type: str = "system"):
        auth_setting = LoginSerializer.get_auth_setting()
        max_attempts = auth_setting.get("max_attempts", 1)
        need_captcha = LoginSerializer._need_captcha_by_key(system_get_key(f"system_{username}"), max_attempts)

        return CaptchaSerializer._generate_captcha_if_needed(username, type, need_captcha)

    @staticmethod
    def chat_generate(username: str, type: str = "chat", access_token: str = ""):
        application_access_token = ApplicationAccessToken.objects.filter(access_token=access_token).first()

        if not application_access_token:
            raise AppApiException(1005, _("Invalid access token"))

        auth_setting = application_access_token.authentication_value
        max_attempts = auth_setting.get("max_attempts", 1)
        need_captcha = LoginSerializer._need_captcha_by_key(system_get_key(f"{type}_{username}"), max_attempts)

        return CaptchaSerializer._generate_captcha_if_needed(username, type, need_captcha)

    @staticmethod
    def _generate_captcha_if_needed(username: str, type: str, need_captcha: bool):
        """提取的公共验证码生成方法"""
        if need_captcha:
            chars = get_random_chars()
            data = ImageCaptcha().generate(chars)
            captcha = base64.b64encode(data.getbuffer())
            cache.set(
                Cache_Version.CAPTCHA.get_key(captcha=f"{type}_{username}"),
                chars.lower(),
                timeout=300,
                version=Cache_Version.CAPTCHA.get_version(),
            )
            return {"captcha": "data:image/png;base64," + captcha.decode()}
        return {"captcha": ""}
