# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： system_setting.py
    @date：2024/3/19 16:29
    @desc:
"""
import logging

from django.core.mail.backends.smtp import EmailBackend
from django.db.models import QuerySet
from rest_framework import serializers

from common.exception.app_exception import AppApiException
from django.utils.translation import gettext_lazy as _

from common.utils.logger import maxkb_logger
from system_manage.models import SystemSetting, SettingType


class EmailSettingSerializer(serializers.Serializer):
    @staticmethod
    def one():
        system_setting = QuerySet(SystemSetting).filter(type=SettingType.EMAIL.value).first()
        if system_setting is None:
            return {}
        return system_setting.meta

    class Create(serializers.Serializer):
        email_host = serializers.CharField(required=True, label=_('SMTP host'))
        email_port = serializers.IntegerField(required=True, label=_('SMTP port'))
        email_host_user = serializers.CharField(required=True, label=_('Sender\'s email'))
        email_host_password = serializers.CharField(required=True, label=_('Password'))
        email_use_tls = serializers.BooleanField(required=True, label=_('Whether to enable TLS'))
        email_use_ssl = serializers.BooleanField(required=True, label=_('Whether to enable SSL'))
        from_email = serializers.EmailField(required=True, label=_('Sender\'s email'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            try:
                EmailBackend(self.data.get("email_host"),
                             self.data.get("email_port"),
                             self.data.get("email_host_user"),
                             self.data.get("email_host_password"),
                             self.data.get("email_use_tls"),
                             False,
                             self.data.get("email_use_ssl")
                             ).open()
            except Exception as e:
                maxkb_logger.error(f'Exception: {e}')
                raise AppApiException(1004, _('Email verification failed'))

        def update_or_save(self):
            self.is_valid(raise_exception=True)
            system_setting = QuerySet(SystemSetting).filter(type=SettingType.EMAIL.value).first()
            if system_setting is None:
                system_setting = SystemSetting(type=SettingType.EMAIL.value)
            system_setting.meta = self.to_email_meta()
            system_setting.save()
            return system_setting.meta

        def to_email_meta(self):
            return {'email_host': self.data.get('email_host'),
                    'email_port': self.data.get('email_port'),
                    'email_host_user': self.data.get('email_host_user'),
                    'email_host_password': self.data.get('email_host_password'),
                    'email_use_tls': self.data.get('email_use_tls'),
                    'email_use_ssl': self.data.get('email_use_ssl'),
                    'from_email': self.data.get('from_email')
                    }
