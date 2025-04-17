# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： user.py
    @date：2025/4/14 19:25
    @desc:
"""
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _
from rest_framework.request import Request

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants
from common.result import result
from models_provider.api.model import ModelCreateAPI
from models_provider.serializers.model import ModelSerializer


class Model(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['POST'],
                   description=_("Create model"),
                   operation_id=_("Create model"),
                   tags=[_("Model")],
                   request=ModelCreateAPI.get_request(),
                   responses=ModelCreateAPI.get_response())
    @has_permissions(PermissionConstants.MODEL_CREATE)
    def post(self, request: Request, workspace_id: str):
        return result.success(
            ModelSerializer.Create(data={**request.data, 'user_id': request.user.id}).insert(workspace_id,
                                                                                             with_valid=True))
