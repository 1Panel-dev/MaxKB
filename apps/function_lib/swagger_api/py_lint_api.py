# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： py_lint_api.py
    @date：2024/9/30 15:48
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin
from django.utils.translation import gettext_lazy as _


class PyLintApi(ApiMixin):
    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['code'],
            properties={
                'code': openapi.Schema(type=openapi.TYPE_STRING, title=_('function content'),
                                       description=_('function content'))
            }
        )
