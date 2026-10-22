# coding=utf-8
"""
@project: MaxKB
@Author：MaxKB
@file： portal.py
@date：2026/8/3
@desc: 门户配置视图
"""

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.request import Request
from rest_framework.views import APIView

from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.auth.constants.permission_constants import PermissionConstants
from common.auth.constants.role_constants import RoleConstants
from common.log.log import log
from portal.api.portal import PortalAPI
from portal.serializers.portal import (
    PortalSerializer,
    PortalLoginSerializer,
)


class PortalView(APIView):
    authentication_classes = [TokenAuth]
    parser_classes = [JSONParser, MultiPartParser]

    @extend_schema(
        methods=["GET"],
        description=_("Get portal configuration"),
        summary=_("Get portal configuration"),
        operation_id=_("Get portal configuration"),  # type: ignore
        responses=PortalAPI.Get.get_response(),
        tags=[_("Portal")],  # type: ignore
    )
    @has_permissions(PermissionConstants.PORTAL_EDIT, RoleConstants.ADMIN)
    def get(self, request: Request):
        return result.success(PortalSerializer().one())

    @extend_schema(
        methods=["PUT"],
        description=_("Save portal configuration"),
        summary=_("Save portal configuration"),
        operation_id=_("Save portal configuration"),  # type: ignore
        request=PortalAPI.Save.get_request(),
        responses=PortalAPI.Save.get_response(),
        tags=[_("Portal")],  # type: ignore
    )
    @log(menu="Portal", operate="Save portal configuration")
    @has_permissions(PermissionConstants.PORTAL_EDIT, RoleConstants.ADMIN)
    def put(self, request: Request):
        return result.success(PortalSerializer(data=request.data).edit(request.data))


class PortalInfoView(APIView):
    @extend_schema(
        methods=["GET"],
        description=_("Get portal login info"),
        summary=_("Get portal login info"),
        operation_id=_("Get portal login info"),  # type: ignore
        tags=[_("Portal")],  # type: ignore
    )
    def get(self, request: Request):
        return result.success(PortalLoginSerializer.get_login_profile())
