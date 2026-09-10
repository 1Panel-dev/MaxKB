# coding=utf-8
"""
@project: MaxKB
@Author：虎虎
@file： resource_mapping.py
@date：2025/12/25 15:28
@desc:
"""

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.auth.constants.compare_constants import CompareConstants
from common.auth.constants.permission_constants import PermissionConstants
from common.auth.constants.role_constants import RoleConstants
from common.auth.struct.aggregate_permission import ViewPermission
from system_manage.api.resource_mapping import ResourceMappingAPI
from system_manage.serializers.resource_mapping_serializers import ResourceMappingSerializer, MappingResourceSerializer


class ResourceMappingView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        description=_("Retrieve the pagination list of resource relationships"),
        operation_id=_("Retrieve the pagination list of resource relationships"),  # type: ignore
        responses=ResourceMappingAPI.get_response(),
        parameters=ResourceMappingAPI.get_parameters(),
        tags=[_("Resources mapping")],  # type: ignore
    )
    @has_permissions(
        lambda r, kwargs: PermissionConstants[
            f"{kwargs.get('resource')}_RELATE_RESOURCE_VIEW"
        ].get_workspace_permission_workspace_manage_role()(r, kwargs),
        lambda r, kwargs: PermissionConstants[
            f"{kwargs.get('resource')}_RELATE_RESOURCE_VIEW"
        ]._build_workspace_permission(resource_id_key="resource_id")(r, kwargs),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [
                lambda r, kwargs: PermissionConstants[kwargs.get("resource")]._build_workspace_permission(
                    resource_id_key="resource_id"
                )(r, kwargs)
            ],
            compare=CompareConstants.AND,
        ),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    def get(self, request: Request, workspace_id: str, resource: str, resource_id: str, current_page, page_size):
        return result.success(
            ResourceMappingSerializer(
                {
                    "resource": resource,
                    "resource_id": resource_id,
                    "resource_name": request.query_params.get("resource_name"),
                    "user_name": request.query_params.get("user_name"),
                    "source_type": request.query_params.getlist("source_type[]"),
                }
            ).page(current_page, page_size)
        )


class MappingResourceView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        description=_("Retrieve the pagination list of resource relationships"),
        operation_id=_("Retrieve the pagination list of resource relationships"),  # type: ignore
        responses=ResourceMappingAPI.get_response(),
        parameters=ResourceMappingAPI.get_parameters(),
        tags=[_("Mapping Resource")],  # type: ignore
    )
    @has_permissions(
        lambda r, kwargs: PermissionConstants[
            f"{kwargs.get('resource')}_RELATE_RESOURCE_VIEW"
        ].get_workspace_permission_workspace_manage_role()(r, kwargs),
        lambda r, kwargs: PermissionConstants[
            f"{kwargs.get('resource')}_RELATE_RESOURCE_VIEW"
        ]._build_workspace_permission(resource_id_key="resource_id")(r, kwargs),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [
                lambda r, kwargs: PermissionConstants[kwargs.get("resource")]._build_workspace_permission(
                    resource_id_key="resource_id"
                )(r, kwargs)
            ],
            compare=CompareConstants.AND,
        ),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    def get(self, request: Request, workspace_id: str, resource: str, resource_id: str, current_page, page_size):
        return result.success(
            MappingResourceSerializer(
                {
                    "resource": resource,
                    "resource_id": resource_id,
                    "resource_name": request.query_params.get("resource_name"),
                    "user_name": request.query_params.get("user_name"),
                    "target_type": request.query_params.getlist("target_type[]"),
                }
            ).page(current_page, page_size)
        )
