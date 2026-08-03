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
from common.constants.permission_constants import PermissionConstants, RoleConstants
from common.log.log import log
from portal.api.portal import PortalAPI
from portal.serializers.portal import PortalSerializer


class PortalView(APIView):
    authentication_classes = [TokenAuth]
    parser_classes = [JSONParser, MultiPartParser]

    @extend_schema(
        methods=['GET'],
        description=_('Get portal configuration'),
        summary=_('Get portal configuration'),
        operation_id=_('Get portal configuration'),
        responses=PortalAPI.Get.get_response(),
        tags=[_('Portal')]
    )
    @has_permissions(
        PermissionConstants.PORTAL_EDIT, RoleConstants.ADMIN)
    def get(self, request: Request):
        return result.success(PortalSerializer().one())

    @extend_schema(
        methods=['PUT'],
        description=_('Save portal configuration'),
        summary=_('Save portal configuration'),
        operation_id=_('Save portal configuration'),
        request=PortalAPI.Save.get_request(),
        responses=PortalAPI.Save.get_response(),
        tags=[_('Portal')]
    )
    @log(menu='Portal', operate='Save portal configuration')
    @has_permissions(
        PermissionConstants.PORTAL_EDIT, RoleConstants.ADMIN)
    def put(self, request: Request):
        return result.success(PortalSerializer().edit(request.data))
