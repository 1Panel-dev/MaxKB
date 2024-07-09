# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： valid.py
    @date：2024/7/8 17:50
    @desc:
"""
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import RoleConstants
from common.response import result
from setting.serializers.valid_serializers import ValidSerializer
from setting.swagger_api.valid_api import ValidApi


class Valid(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary="获取校验结果",
                         operation_id="获取校验结果",
                         manual_parameters=ValidApi.get_request_params_api(),
                         responses=result.get_default_response()
        , tags=["校验"])
    @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
    def get(self, request: Request, valid_type: str, valid_count: int):
        return result.success(ValidSerializer(data={'valid_type': valid_type, 'valid_count': valid_count}).valid())
