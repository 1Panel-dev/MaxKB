# coding=utf-8
"""
@project: MaxKB
@Author：MaxKB
@file： portal.py
@date：2026/8/3
@desc: 门户配置序列化器
"""

import json
import uuid_utils.compat as uuid
from django.core import signing
from django.core.cache import cache
from django.db.models import Exists, OuterRef
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import Application, Chat
from application.models.application_access_token import ApplicationAccessToken
from common.auth.common import FileToken
from common.constants.cache_version import Cache_Version
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.db.search import page_search
from common.exception.app_exception import AppApiException
from common.log.log import record_log
from common.utils.common import password_verify, needs_password_upgrade, password_encrypt
from common.utils.rsa_util import decrypt, get_key_pair_by_sql
from knowledge.models import File, FileSourceType
from maxkb.const import CONFIG
from portal.models import Portal
from system_manage.models.chat_user import (
    ChatUser,
    ResourceChatUserAuthorize,
    ResourceChatUserGroupAuthorize,
    ResourceType,
    UserGroupRelation,
)
from users.serializers.login import LoginRequest

system_version, system_get_key = Cache_Version.SYSTEM.value


class PortalSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, label=_("portal name"), help_text=_("portal name"))
    description = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        label=_("portal description"),
        help_text=_("portal description"),
    )
    logo = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, label=_("portal logo"), help_text=_("portal logo")
    )
    tab_logo = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, label=_("tab logo"), help_text=_("tab logo")
    )
    enable_public_access = serializers.BooleanField(
        required=False, label=_("enable public access"), help_text=_("enable public access")
    )
    enable_api = serializers.BooleanField(required=False, label=_("enable api"), help_text=_("enable api"))
    enable_auth = serializers.BooleanField(required=False, label=_("enable auth"), help_text=_("enable auth"))
    auth_config = serializers.JSONField(required=False, label=_("auth config"), help_text=_("auth config"))
    enable_cors = serializers.BooleanField(required=False, label=_("enable cors"), help_text=_("enable cors"))
    cors_config = serializers.JSONField(required=False, label=_("cors config"), help_text=_("cors config"))

    class Model(serializers.ModelSerializer):
        class Meta:
            model = Portal
            fields = "__all__"

    def one(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        portal = Portal.objects.first()
        if portal is None:
            raise AppApiException(500, _("Portal configuration does not exist"))
        return PortalSerializer.Model(portal).data

    def _upload_file(self, file_obj):
        file_id = uuid.uuid7()
        file = File(
            id=file_id,
            file_name=file_obj.name,
            source_type=FileSourceType.SYSTEM,
            meta={"debug": False},
        )
        file.save(file_obj.read())
        return f"./oss/file/{file_id}"

    def _handle_file_field(self, portal, field_name, value):
        if hasattr(value, "read"):
            old_url = getattr(portal, field_name)
            if old_url:
                old_file_id = old_url.split("/")[-1]
                File.objects.filter(id=old_file_id).delete()
            new_url = self._upload_file(value)
            setattr(portal, field_name, new_url)
        else:
            setattr(portal, field_name, value)

    def edit(self, instance, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        portal = Portal.objects.first()
        if portal is None:
            raise AppApiException(500, _("Portal configuration does not exist"))
        file_fields = ["logo", "tab_logo", "id", "create_time", "update_time"]
        for field, value in instance.items():
            if hasattr(portal, field) and field not in file_fields:
                setattr(portal, field, value)
        for field_name in ["logo", "tab_logo"]:
            if field_name in instance:
                self._handle_file_field(portal, field_name, instance.get(field_name))
        portal.save()
        return PortalSerializer.Model(portal).data


class PortalApplicationAuthMixin:
    """门户应用授权过滤公共逻辑"""

    @staticmethod
    def get_authorized_application_queryset(user_id):
        public_apps = ApplicationAccessToken.objects.filter(application_id=OuterRef("id"), authentication=False)
        if not ChatUser.objects.filter(id=user_id).exists():
            return Application.objects.filter(Exists(public_apps))
        authed_token_exists = ApplicationAccessToken.objects.filter(application_id=OuterRef("id"), authentication=True)
        direct_auth = ResourceChatUserAuthorize.objects.filter(
            resource_id=OuterRef("id"), resource_type=ResourceType.APPLICATION.value, is_auth=True, user_id=user_id
        )
        user_groups = UserGroupRelation.objects.filter(user_id=user_id).values_list("group_id", flat=True)
        group_auth = ResourceChatUserGroupAuthorize.objects.filter(
            resource_id=OuterRef("id"),
            resource_type=ResourceType.APPLICATION.value,
            is_auth=True,
            user_group_id__in=user_groups,
        )
        return Application.objects.filter(
            Exists(public_apps) | (Exists(authed_token_exists) & (Exists(direct_auth) | Exists(group_auth)))
        )


class ApplicationResponseSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    desc = serializers.CharField(required=True)
    icon = serializers.CharField(required=True)
    type = serializers.CharField(required=True)
    dialogue_number = serializers.IntegerField(required=True)
    prologue = serializers.CharField(required=True)
    is_publish = serializers.BooleanField(required=True)


class PortalApplicationSerializer(serializers.Serializer):
    class Query(PortalApplicationAuthMixin, serializers.Serializer):
        name = serializers.CharField(
            required=False, allow_blank=True, label=_("Application Name"), help_text=_("Application name")
        )

        def get_query_set(self):
            queryset = Application.objects.filter(is_publish=True)
            name = self.data.get("name")
            if name:
                queryset = queryset.filter(name__icontains=name)
            return queryset.order_by("-create_time")

        def page(self, current_page, page_size, user_id, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            queryset = self.get_query_set()
            queryset = queryset.filter(id__in=self.get_authorized_application_queryset(user_id).values("id"))
            return page_search(
                current_page,
                page_size,
                queryset,
                post_records_handler=lambda app: ApplicationResponseSerializer(app).data,
            )


class PortalHistoricalConversationResponseSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    abstract = serializers.CharField(required=True)
    create_time = serializers.CharField(required=True)
    update_time = serializers.CharField(required=True)
    application = serializers.SerializerMethodField()

    def get_application(self, chat):
        return {
            "id": str(chat.application_id),
            "name": chat.application.name,
            "icon": chat.application.icon,
        }


class PortalHistoricalConversationSerializer(serializers.Serializer):
    class Query(PortalApplicationAuthMixin, serializers.Serializer):
        name = serializers.CharField(
            required=False, allow_blank=True, label=_("Application Name"), help_text=_("Application name")
        )

        def get_query_set(self, user_id):
            queryset = Chat.objects.filter(
                chat_user_id=user_id,
                is_deleted=False,
                application_id__in=self.get_authorized_application_queryset(user_id).values("id"),
            )
            name = self.data.get("name")
            if name:
                queryset = queryset.filter(application__name__icontains=name)
            return queryset.select_related("application").order_by("-update_time", "id")

        def page(self, current_page, page_size, user_id, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return page_search(
                current_page,
                page_size,
                self.get_query_set(user_id),
                post_records_handler=lambda chat: PortalHistoricalConversationResponseSerializer(chat).data,
            )


class PortalLoginSerializer(serializers.Serializer):
    @staticmethod
    def login(instance):
        username = instance.get("username", "")
        encrypted_data = instance.get("encryptedData", "")

        if encrypted_data:
            try:
                decrypted_raw = decrypt(encrypted_data)
                decrypted_data = json.loads(decrypted_raw) if decrypted_raw else {}
                if isinstance(decrypted_data, dict):
                    instance.update(decrypted_data)
            except Exception:
                raise AppApiException(500, _("Invalid encrypted data"))

        try:
            request_serializer = LoginRequest(data=instance)
            request_serializer.is_valid(raise_exception=True)
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise AppApiException(500, str(e))

        validated_data = request_serializer.validated_data
        username = validated_data.get("username", "")
        password = validated_data.get("password", "")
        captcha = validated_data.get("captcha", "")

        portal = Portal.objects.first()
        if portal is None or not portal.enable_auth:
            raise AppApiException(500, _("Portal authentication is not enabled"))
        auth_config = portal.auth_config or {}
        login_value = auth_config.get("login_value", [])
        if "LOCAL" not in login_value:
            raise AppApiException(500, _("Portal local login is not enabled"))

        max_attempts = auth_config.get("max_attempts", 1)
        failed_attempts = auth_config.get("failed_attempts", 5)
        lock_time = auth_config.get("lock_time", 10)

        license_validator = DatabaseModelManage.get_model("license_is_valid")
        is_license_valid = bool(license_validator()) if license_validator else False

        cache_key = system_get_key(f"portal_{username}")
        if is_license_valid:
            if PortalLoginSerializer._is_account_locked(username, failed_attempts):
                raise AppApiException(
                    1005, _("This account has been locked for %s minutes, please try again later") % lock_time
                )
        if PortalLoginSerializer._need_captcha(username, max_attempts):
            PortalLoginSerializer._validate_captcha(username, captcha)

        user = ChatUser.objects.filter(username=username).first()

        if not user or not password_verify(password, user.password):
            PortalLoginSerializer._handle_failed_login(username, is_license_valid, failed_attempts, lock_time)
            raise AppApiException(500, _("The username or password is incorrect"))

        if needs_password_upgrade(user.password):
            user.password = password_encrypt(password)
            user.save(update_fields=["password"])

        if not user.is_active:
            raise AppApiException(1005, _("The user has been disabled, please contact the administrator!"))

        cache.delete(cache_key, version=system_version)
        cache.delete(system_get_key(f"portal_{username}_lock"), version=system_version)

        token = signing.dumps(
            {
                "username": user.username,
                "id": str(user.id),
                "type": "PORTAL_USER",
            }
        )
        version, get_key = Cache_Version.TOKEN.value
        timeout = CONFIG.get_session_timeout()
        cache.set(get_key(token), user, timeout=timeout, version=version)
        f_token = FileToken(str(user.id), "PORTAL_USER").to_token()
        record_log(
            menu="Portal",
            operate="Log in",
            request=None,
            user={"username": user.username},
            status=200,
            operation_object={"name": user.username},
            workspace_id="default",
        )
        return {"token": token}, f_token

    @staticmethod
    def get_login_profile():
        portal = Portal.objects.first()
        if portal is None:
            raise AppApiException(500, _("Portal configuration does not exist"))
        auth_config = portal.auth_config or {}
        return {
            "name": portal.name,
            "description": portal.description or "",
            "logo": portal.logo or "",
            "enable_auth": portal.enable_auth,
            "authentication_type": auth_config.get("type", "password") if portal.enable_auth else "",
            "login_value": auth_config.get("login_value", []) if portal.enable_auth else [],
            "max_attempts": auth_config.get("max_attempts", 1) if portal.enable_auth else 1,
            "rsa_key": get_key_pair_by_sql().get("key", ""),
        }

    @staticmethod
    def _is_account_locked(username: str, failed_attempts: int) -> bool:
        if failed_attempts == -1:
            return False
        lock_cache = cache.get(system_get_key(f"portal_{username}_lock"), version=system_version)
        return bool(lock_cache)

    @staticmethod
    def _need_captcha(username: str, max_attempts: int) -> bool:
        cache_key = system_get_key(f"portal_{username}")
        if max_attempts == -1:
            return False
        if max_attempts > 0:
            fail_count = cache.get(cache_key, version=system_version) or 0
            return fail_count >= max_attempts
        return True

    @staticmethod
    def _validate_captcha(username: str, captcha: str) -> None:
        if not captcha:
            raise AppApiException(1005, _("Captcha is required"))
        captcha_cache = cache.get(
            Cache_Version.CAPTCHA.get_key(captcha=f"portal_{username}"), version=Cache_Version.CAPTCHA.get_version()
        )
        if captcha_cache is None or captcha.lower() != captcha_cache:
            raise AppApiException(1005, _("Captcha code error or expiration"))

    @staticmethod
    def _handle_failed_login(username: str, is_license_valid: bool, failed_attempts: int, lock_time: int) -> None:
        try:
            _record_login_fail(username)
        except Exception:
            pass
        lock_fail_count = 0
        try:
            lock_fail_count = _record_login_fail_lock(username, lock_time)
        except Exception:
            pass
        if not is_license_valid or failed_attempts <= 0:
            return
        if lock_fail_count < failed_attempts:
            remain_attempts = failed_attempts - lock_fail_count
            raise AppApiException(
                1005,
                _("Login failed %s times, account will be locked, you have %s more chances !")
                % (failed_attempts, remain_attempts),
            )
        try:
            cache.add(system_get_key(f"portal_{username}_lock"), 1, timeout=lock_time * 60, version=system_version)
        except Exception:
            pass
        raise AppApiException(
            1005, _("This account has been locked for %s minutes, please try again later") % lock_time
        )


def _record_login_fail(username: str, expire: int = 600):
    if not username:
        return
    fail_key = system_get_key(f"portal_{username}")
    try:
        cache.incr(fail_key, 1, version=system_version)
    except ValueError:
        cache.set(fail_key, 1, timeout=expire, version=system_version)


def _record_login_fail_lock(username: str, expire: int = 10):
    if not username:
        return 0
    lock_key = system_get_key(f"portal_{username}_lock_count")
    try:
        fail_count = cache.incr(lock_key, 1, version=system_version)
    except ValueError:
        cache.set(lock_key, 1, timeout=expire * 60, version=system_version)
        fail_count = 1
    return fail_count
