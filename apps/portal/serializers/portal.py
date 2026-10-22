# coding=utf-8
"""
@project: MaxKB
@Author：MaxKB
@file： portal.py
@date：2026/8/3
@desc: 门户配置序列化器
"""

import uuid_utils.compat as uuid
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.exception.app_exception import AppApiException
from common.utils.rsa_util import get_key_pair_by_sql
from knowledge.models import File, FileSourceType
from portal.models import Portal


class LogoField(serializers.CharField):
    """门户Logo字段，兼容字符串URL（JSON）与 multipart 上传文件"""

    def to_internal_value(self, data):
        if data is not None and hasattr(data, "read"):
            # multipart 上传的文件对象（InMemoryUploadedFile / TemporaryUploadedFile）
            return data
        return super().to_internal_value(data)


class PortalSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, label=_("portal name"), help_text=_("portal name"))
    description = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        label=_("portal description"),
        help_text=_("portal description"),
    )
    logo = LogoField(
        required=False, allow_null=True, allow_blank=True, label=_("portal logo"), help_text=_("portal logo")
    )
    enable_public_access = serializers.BooleanField(
        required=False, label=_("enable public access"), help_text=_("enable public access")
    )
    enable_api = serializers.BooleanField(required=False, label=_("enable api"), help_text=_("enable api"))
    enable_knowledge_base_api = serializers.BooleanField(
        required=False, label=_("enable knowledge base api"), help_text=_("enable knowledge base api")
    )
    enable_auth = serializers.BooleanField(required=False, label=_("enable auth"), help_text=_("enable auth"))
    auth_config = serializers.JSONField(required=False, label=_("auth config"), help_text=_("auth config"))
    enable_cors = serializers.BooleanField(required=False, label=_("enable cors"), help_text=_("enable cors"))
    cross_domain_list = serializers.ListSerializer(
        required=False,
        child=serializers.CharField(required=True, label=_("Cross-domain address")),
        label=_("Cross-domain list"),
    )

    class Model(serializers.ModelSerializer):
        class Meta:
            model = Portal
            fields = "__all__"

    @staticmethod
    def _is_license_valid():
        license_validator = DatabaseModelManage.get_model("license_is_valid") or (lambda: False)
        license_status = license_validator()
        return license_status if license_status is not None else False

    def _get_enabled_auth_types(self):
        # 无有效授权（license）或 ChatUserPlatformSource 模型不存在时，仅提供 LOCAL 登录
        if not self._is_license_valid():
            return []
        chat_platform_source_model = DatabaseModelManage.get_model("chat_platform")
        if chat_platform_source_model is None:
            return []
        return list(
            chat_platform_source_model.objects.filter(is_active=True, is_valid=True)
            .order_by("type")
            .values_list("auth_type", flat=True)
        )

    def _enrich_auth_config(self, auth_config):
        auth_config = dict(auth_config or {})
        auth_config.setdefault("type", "LOCAL")
        auth_config.setdefault("max_attempts", 1)
        auth_config.setdefault("failed_attempts", 5)
        auth_config.setdefault("lock_time", 10)

        enabled_auth_types = self._get_enabled_auth_types()
        all_available_auths = ["LOCAL"] + enabled_auth_types

        if "login_value" not in auth_config:
            auth_config["login_value"] = all_available_auths
        else:
            auth_config["login_value"] = [
                method for method in auth_config.get("login_value", []) if method in all_available_auths
            ]

        options = [{"label": _(_type), "value": _type} for _type in all_available_auths]
        options.sort(key=lambda x: (0 if x["value"] == "LOCAL" else 1, x["label"]))

        auth_config["system_options"] = options
        return auth_config

    def one(self):
        portal = Portal.objects.first()
        if portal is None:
            raise AppApiException(500, _("Portal configuration does not exist"))
        data = PortalSerializer.Model(portal).data
        # 授权无效时不展示 auth_config，避免暴露认证配置
        if self._is_license_valid():
            data["auth_config"] = self._enrich_auth_config(data["auth_config"])
        else:
            data["auth_config"] = {}
        return data

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
        file_fields = ["logo", "id", "create_time", "update_time"]
        for field, value in instance.items():
            if hasattr(portal, field) and field not in file_fields:
                setattr(portal, field, value)
        for field_name in ["logo"]:
            if field_name in instance:
                self._handle_file_field(portal, field_name, instance.get(field_name))
        portal.save()
        return PortalSerializer.Model(portal).data


class PortalLoginSerializer(serializers.Serializer):
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
            "authentication_type": auth_config.get("type", "LOCAL") if portal.enable_auth else "",
            "login_value": auth_config.get("login_value", []) if portal.enable_auth else [],
            "max_attempts": auth_config.get("max_attempts", 1) if portal.enable_auth else 1,
            "rsa_key": get_key_pair_by_sql().get("key", ""),
        }
