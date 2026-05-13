# coding=utf-8
"""
    @project: maxkb
    @file: ocr_setting.py
    @desc: OCR 设置视图。复用 EmailSetting 的三动作模式（GET/PUT/POST 测试）。
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants
from common.log.log import log
from common.result import result
from system_manage.api.ocr_setting import OcrSettingAPI
from system_manage.serializers.ocr_setting import OcrSettingSerializer


class OcrSetting(APIView):
    """对外端点：

    - GET    /admin/api/ocr_setting       — 读 OCR 配置（管理员可见）
    - PUT    /admin/api/ocr_setting       — 写 OCR 配置
    - POST   /admin/api/ocr_setting       — 测试当前提交的配置是否可用
    """
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        summary=_('Get OCR settings'),
        description=_('Get OCR settings'),
        operation_id=_('Get OCR settings'),  # type: ignore
        responses=OcrSettingAPI.get_response(),
        tags=[_('OCR Settings')],  # type: ignore
    )
    # 复用外观设置的读权限（CE 也已可见）。后续若需独立权限再拆分。
    @has_permissions(PermissionConstants.APPEARANCE_SETTINGS_READ, RoleConstants.ADMIN)
    def get(self, request: Request):
        return result.success(OcrSettingSerializer.one())

    @extend_schema(
        methods=['PUT'],
        summary=_('Update OCR settings'),
        description=_('Update OCR settings'),
        operation_id=_('Update OCR settings'),  # type: ignore
        request=OcrSettingAPI.get_request(),
        responses=OcrSettingAPI.get_response(),
        tags=[_('OCR Settings')],  # type: ignore
    )
    @log(menu='OCR settings', operate='Update OCR settings')
    @has_permissions(PermissionConstants.APPEARANCE_SETTINGS_EDIT, RoleConstants.ADMIN)
    def put(self, request: Request):
        return result.success(
            OcrSettingSerializer.Create(data=request.data).update_or_save()
        )

    @extend_schema(
        methods=['POST'],
        summary=_('Test OCR settings'),
        description=_('Test OCR settings without saving'),
        operation_id=_('Test OCR settings'),  # type: ignore
        request=OcrSettingAPI.get_request(),
        responses=OcrSettingAPI.get_response(),
        tags=[_('OCR Settings')],  # type: ignore
    )
    @has_permissions(PermissionConstants.APPEARANCE_SETTINGS_EDIT, RoleConstants.ADMIN)
    def post(self, request: Request):
        return result.success(
            OcrSettingSerializer.Create(data=request.data).is_valid_config()
        )
