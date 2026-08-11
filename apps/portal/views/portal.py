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
from common.constants.cache_version import Cache_Version
from common.log.log import log
from common.utils.common import query_params_to_single_dict
from django.core.cache import cache
from portal.api.portal import PortalAPI
from portal.serializers.portal import (
    PortalSerializer,
    PortalApplicationSerializer,
    PortalLoginSerializer,
    PortalHistoricalConversationSerializer,
)


class PortalView(APIView):
    authentication_classes = [TokenAuth]
    parser_classes = [JSONParser, MultiPartParser]

    @extend_schema(
        methods=["GET"],
        description=_("Get portal configuration"),
        summary=_("Get portal configuration"),
        operation_id=_("Get portal configuration"),
        responses=PortalAPI.Get.get_response(),
        tags=[_("Portal")],
    )
    @has_permissions(PermissionConstants.PORTAL_EDIT, RoleConstants.ADMIN)
    def get(self, request: Request):
        return result.success(PortalSerializer().one())

    @extend_schema(
        methods=["PUT"],
        description=_("Save portal configuration"),
        summary=_("Save portal configuration"),
        operation_id=_("Save portal configuration"),
        request=PortalAPI.Save.get_request(),
        responses=PortalAPI.Save.get_response(),
        tags=[_("Portal")],
    )
    @log(menu="Portal", operate="Save portal configuration")
    @has_permissions(PermissionConstants.PORTAL_EDIT, RoleConstants.ADMIN)
    def put(self, request: Request):
        return result.success(PortalSerializer().edit(request.data))


class PortalApplicationView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        description=_("Get published application list by page"),
        summary=_("Get published application list by page"),
        operation_id=_("Get published application list by page"),
        parameters=PortalAPI.Application.get_parameters(),
        responses=PortalAPI.Application.get_response(),
        tags=[_("Portal")],
    )
    @has_permissions(PermissionConstants.PORTAL_READ, RoleConstants.ADMIN)
    def get(self, request: Request, current_page: int, page_size: int):
        return result.success(
            PortalApplicationSerializer.Query(data={**query_params_to_single_dict(request.query_params)}).page(
                current_page, page_size, str(request.user.id)
            )
        )


class PortalHistoricalConversationView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        description=_("Get portal historical conversation by page"),
        summary=_("Get portal historical conversation by page"),
        operation_id=_("Get portal historical conversation by page"),
        parameters=PortalAPI.Conversation.get_parameters(),
        responses=PortalAPI.Conversation.get_response(),
        tags=[_("Portal")],
    )
    def get(self, request: Request, current_page: int, page_size: int):
        return result.success(
            PortalHistoricalConversationSerializer.Query(
                data={**query_params_to_single_dict(request.query_params)}
            ).page(current_page, page_size, str(request.user.id))
        )


class PortalLoginView(APIView):
    @extend_schema(
        methods=["POST"],
        description=_("Portal login"),
        summary=_("Portal login"),
        operation_id=_("Portal login"),
        tags=[_("Portal")],
        request=PortalAPI.Login.get_request(),
        responses=PortalAPI.Login.get_response(),
    )
    def post(self, request: Request):
        token_data, f_token = PortalLoginSerializer.login(request.data)
        response = result.success(token_data)
        secure = request.is_secure()
        response.set_cookie(
            "mk_file_auth",
            value=f_token,
            max_age=7 * 24 * 3600,
            path="/portal/",
            domain=None,
            secure=secure,
            httponly=True,
            samesite="Lax",
        )
        return response


class PortalInfoView(APIView):
    @extend_schema(
        methods=["GET"],
        description=_("Get portal login info"),
        summary=_("Get portal login info"),
        operation_id=_("Get portal login info"),
        tags=[_("Portal")],
    )
    def get(self, request: Request):
        return result.success(PortalLoginSerializer.get_login_profile())


class PortalLogoutView(APIView):
    @extend_schema(
        methods=["POST"],
        summary=_("Portal logout"),
        description=_("Portal logout"),
        operation_id=_("Portal logout"),
        tags=[_("Portal")],
        responses=PortalAPI.Logout.get_response(),
    )
    @log(menu="Portal", operate="Log out")
    def post(self, request: Request):
        version, get_key = Cache_Version.TOKEN.value
        cache.delete(get_key(token=request.META.get("HTTP_AUTHORIZATION")[7:]), version=version)
        return result.success(True)
