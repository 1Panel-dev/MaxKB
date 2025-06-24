# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： valid.py
    @date：2024/7/8 17:50
    @desc:
"""
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from django.utils.translation import gettext_lazy as _

from common.result import result
from system_manage.serializers.valid_serializers import ValidSerializer


class Valid(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_('Get verification results'),
        summary=_('Get verification results'),
        operation_id=_('Get verification results'),  # type: ignore
        tags=[_('Validation')]  # type: ignore
    )
    def get(self, request: Request, valid_type: str, valid_count: int):
        return result.success(ValidSerializer(data={'valid_type': valid_type, 'valid_count': valid_count}).valid())
