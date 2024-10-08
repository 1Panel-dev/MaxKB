# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： py_lint.py
    @date：2024/9/30 15:35
    @desc:
"""
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import RoleConstants
from common.response import result
from function_lib.serializers.py_lint_serializer import PyLintSerializer
from function_lib.swagger_api.py_lint_api import PyLintApi


class PyLintView(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary="校验代码",
                         operation_id="校验代码",
                         request_body=PyLintApi.get_request_body_api(),
                         tags=['函数库'])
    @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
    def post(self, request: Request):
        return result.success(PyLintSerializer(data={'user_id': request.user.id}).pylint(request.data))
