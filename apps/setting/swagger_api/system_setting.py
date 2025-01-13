# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： system_setting.py
    @date：2024/3/19 16:05
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin
from django.utils.translation import gettext_lazy as _


class SystemSettingEmailApi(ApiMixin):
    @staticmethod
    def get_request_body_api():
        return openapi.Schema(type=openapi.TYPE_OBJECT,
                              title=_('Email related parameters'),
                              description=_('Email related parameters'),
                              required=['email_host', 'email_port', 'email_host_user', 'email_host_password',
                                        'email_use_tls', 'email_use_ssl', 'from_email'],
                              properties={
                                  'email_host': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title=_('SMTP host'),
                                                               description=_('SMTP host')),
                                  'email_port': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                               title=_('SMTP port'),
                                                               description=_('SMTP port')),
                                  'email_host_user': openapi.Schema(type=openapi.TYPE_STRING,
                                                                    title=_('Sender\'s email'),
                                                                    description=_('Sender\'s email')),
                                  'email_host_password': openapi.Schema(type=openapi.TYPE_STRING,
                                                                        title=_('Password'),
                                                                        description=_('Password')),
                                  'email_use_tls': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                  title=_('Whether to enable TLS'),
                                                                  description=_('Whether to enable TLS')),
                                  'email_use_ssl': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                  title=_('Whether to enable SSL'),
                                                                  description=_('Whether to enable SSL')),
                                  'from_email': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title=_('Sender\'s email'),
                                                               description=_('Sender\'s email'))
                              }
                              )

    @staticmethod
    def get_response_body_api():
        return openapi.Schema(type=openapi.TYPE_OBJECT,
                              title=_('Email related parameters'),
                              description=_('Email related parameters'),
                              required=['email_host', 'email_port', 'email_host_user', 'email_host_password',
                                        'email_use_tls', 'email_use_ssl', 'from_email'],
                              properties={
                                  'email_host': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title=_('SMTP host'),
                                                               description=_('SMTP host')),
                                  'email_port': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                               title=_('SMTP port'),
                                                               description=_('SMTP port')),
                                  'email_host_user': openapi.Schema(type=openapi.TYPE_STRING,
                                                                    title=_('Sender\'s email'),
                                                                    description=_('Sender\'s email')),
                                  'email_host_password': openapi.Schema(type=openapi.TYPE_STRING,
                                                                        title=_('Password'),
                                                                        description=_('Password')),
                                  'email_use_tls': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                  title=_('Whether to enable TLS'),
                                                                  description=_('Whether to enable TLS')),
                                  'email_use_ssl': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                  title=_('Whether to enable SSL'),
                                                                  description=_('Whether to enable SSL')),
                                  'from_email': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title=_('Sender\'s email'),
                                                               description=_('Sender\'s email'))
                              }
                              )
