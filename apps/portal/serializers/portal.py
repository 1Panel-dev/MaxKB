# coding=utf-8
"""
    @project: MaxKB
    @Author：MaxKB
    @file： portal.py
    @date：2026/8/3
    @desc: 门户配置序列化器
"""
import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.exception.app_exception import AppApiException
from knowledge.models import File, FileSourceType
from portal.models import Portal


class PortalSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, label=_('portal name'), help_text=_('portal name'))
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                        label=_('portal description'), help_text=_('portal description'))
    logo = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                 label=_('portal logo'), help_text=_('portal logo'))
    tab_logo = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                     label=_('tab logo'), help_text=_('tab logo'))
    enable_public_access = serializers.BooleanField(required=False, label=_('enable public access'),
                                                    help_text=_('enable public access'))
    enable_api = serializers.BooleanField(required=False, label=_('enable api'), help_text=_('enable api'))
    enable_auth = serializers.BooleanField(required=False, label=_('enable auth'), help_text=_('enable auth'))
    auth_config = serializers.JSONField(required=False, label=_('auth config'), help_text=_('auth config'))
    enable_cors = serializers.BooleanField(required=False, label=_('enable cors'), help_text=_('enable cors'))
    cors_config = serializers.JSONField(required=False, label=_('cors config'), help_text=_('cors config'))

    class Model(serializers.ModelSerializer):
        class Meta:
            model = Portal
            fields = '__all__'

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
        if hasattr(value, 'read'):
            old_url = getattr(portal, field_name)
            if old_url:
                old_file_id = old_url.split("/")[-1]
                QuerySet(File).filter(id=old_file_id).delete()
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
        file_fields = ['logo', 'tab_logo', 'id', 'create_time', 'update_time']
        for field, value in instance.items():
            if hasattr(portal, field) and field not in file_fields:
                setattr(portal, field, value)
        for field_name in ['logo', 'tab_logo']:
            if field_name in instance:
                self._handle_file_field(portal, field_name, instance.get(field_name))
        portal.save()
        return PortalSerializer.Model(portal).data
