# coding=utf-8
"""
    @project: maxkb
    @file: display.py
    @desc: 外观/白标设置视图。

    端点说明：
      GET  /admin/api/display/info     — 公开免登录（登录页需要它加载 Logo / 背景 / 标题 / 主色）
      PUT  /admin/api/display/update   — 仅 ADMIN + APPEARANCE_SETTINGS_EDIT 可写
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants
from common.log.log import log
from common.result import result
from system_manage.api.display import DisplayAPI
from system_manage.serializers.display import DisplayInfoSerializer, IMAGE_FIELDS


def _get_display_update_details(request):
    """审计日志详情：剥掉文件字节，只记字段名 + 文本字段值。"""
    body = {}
    for key, value in (request.data or {}).items():
        if key in IMAGE_FIELDS:
            # 文件字段：只记名称/大小，不记二进制
            try:
                body[key] = f'<file:{getattr(value, "name", "")}:{getattr(value, "size", 0)}>'
            except Exception:
                body[key] = '<file>'
        else:
            body[key] = value
    return {
        'path': request.path,
        'body': body,
        'query': request.query_params,
    }


class DisplayInfo(APIView):
    """GET /display/info — 公开端点。

    登录页（未认证）也要能拿到 logo / 背景 / 主色，所以不挂任何 authentication_classes。
    返回的图片字段是 './oss/file/<uuid>' 形式相对路径，由 oss.FileRetrievalView 提供，
    该端点同样未要求认证，可被未登录前端直接 <img src=> 引用。
    """
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        methods=['GET'],
        summary=_('Get display (theme) settings'),
        description=_('Get display (theme) settings'),
        operation_id=_('Get display (theme) settings'),  # type: ignore
        responses=DisplayAPI.get_response(),
        tags=[_('Display Settings')],  # type: ignore
    )
    def get(self, request: Request):
        return result.success(DisplayInfoSerializer.one())


class DisplayUpdate(APIView):
    """PUT /display/update — 写入端点。

    前端使用 FormData，可能包含 File 对象（新上传的图片），因此必须支持 MultiPartParser；
    同时兼容 JSON 写入（纯文本字段更新时更轻量）。
    """
    authentication_classes = [TokenAuth]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(
        methods=['PUT'],
        summary=_('Update display (theme) settings'),
        description=_('Update display (theme) settings'),
        operation_id=_('Update display (theme) settings'),  # type: ignore
        request=DisplayAPI.get_request(),
        responses=DisplayAPI.get_response(),
        tags=[_('Display Settings')],  # type: ignore
    )
    @log(menu='Display settings', operate='Update display settings',
         get_details=_get_display_update_details)
    @has_permissions(PermissionConstants.APPEARANCE_SETTINGS_EDIT, RoleConstants.ADMIN)
    def put(self, request: Request):
        return result.success(
            DisplayInfoSerializer.Create(data=request.data).update_or_save()
        )
