# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： system_setting.py
    @date：2024/3/19 16:29
    @desc:
"""
from django.core.mail.backends.smtp import EmailBackend
from django.db.models import QuerySet
from rest_framework import serializers

from common.exception.app_exception import AppApiException
from common.util.field_message import ErrMessage
from setting.models.system_management import SystemSetting, SettingType


class SystemSettingSerializer(serializers.Serializer):
    class EmailSerializer(serializers.Serializer):
        @staticmethod
        def one():
            system_setting = QuerySet(SystemSetting).filter(type=SettingType.EMAIL.value).first()
            if system_setting is None:
                return {}
            return system_setting.meta

        class Create(serializers.Serializer):
            email_host = serializers.CharField(required=True, error_messages=ErrMessage.char("SMTP 主机"))
            email_port = serializers.IntegerField(required=True, error_messages=ErrMessage.char("SMTP 端口"))
            email_host_user = serializers.CharField(required=True, error_messages=ErrMessage.char("发件人邮箱"))
            email_host_password = serializers.CharField(required=True, error_messages=ErrMessage.char("密码"))
            email_use_tls = serializers.BooleanField(required=True, error_messages=ErrMessage.char("是否开启TLS"))
            email_use_ssl = serializers.BooleanField(required=True, error_messages=ErrMessage.char("是否开启SSL"))
            from_email = serializers.EmailField(required=True, error_messages=ErrMessage.char("发送人邮箱"))

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
                    raise AppApiException(1004, "邮箱校验失败")

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
