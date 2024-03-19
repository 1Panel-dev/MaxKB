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


class SystemSettingEmailApi(ApiMixin):
    @staticmethod
    def get_request_body_api():
        return openapi.Schema(type=openapi.TYPE_OBJECT,
                              title="邮箱相关参数",
                              description="邮箱相关参数",
                              required=['email_host', 'email_port', 'email_host_user', 'email_host_password',
                                        'email_use_tls', 'email_use_ssl', 'from_email'],
                              properties={
                                  'email_host': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title="SMTP 主机",
                                                               description="SMTP 主机"),
                                  'email_port': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                               title="SMTP 端口",
                                                               description="SMTP 端口"),
                                  'email_host_user': openapi.Schema(type=openapi.TYPE_STRING,
                                                                    title="发件人邮箱",
                                                                    description="发件人邮箱"),
                                  'email_host_password': openapi.Schema(type=openapi.TYPE_STRING,
                                                                        title="密码",
                                                                        description="密码"),
                                  'email_use_tls': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                  title="是否开启TLS",
                                                                  description="是否开启TLS"),
                                  'email_use_ssl': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                  title="是否开启SSL",
                                                                  description="是否开启SSL"),
                                  'from_email': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title="发送人邮箱",
                                                               description="发送人邮箱")
                              }
                              )

    @staticmethod
    def get_response_body_api():
        return openapi.Schema(type=openapi.TYPE_OBJECT,
                              title="邮箱相关参数",
                              description="邮箱相关参数",
                              required=['email_host', 'email_port', 'email_host_user', 'email_host_password',
                                        'email_use_tls', 'email_use_ssl', 'from_email'],
                              properties={
                                  'email_host': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title="SMTP 主机",
                                                               description="SMTP 主机"),
                                  'email_port': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                               title="SMTP 端口",
                                                               description="SMTP 端口"),
                                  'email_host_user': openapi.Schema(type=openapi.TYPE_STRING,
                                                                    title="发件人邮箱",
                                                                    description="发件人邮箱"),
                                  'email_host_password': openapi.Schema(type=openapi.TYPE_STRING,
                                                                        title="密码",
                                                                        description="密码"),
                                  'email_use_tls': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                  title="是否开启TLS",
                                                                  description="是否开启TLS"),
                                  'email_use_ssl': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                  title="是否开启SSL",
                                                                  description="是否开启SSL"),
                                  'from_email': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title="发送人邮箱",
                                                               description="发送人邮箱")
                              }
                              )
