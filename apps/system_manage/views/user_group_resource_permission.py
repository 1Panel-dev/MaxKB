# coding=utf-8
"""
@project: MaxKB
@Author：虎虎
@file： workspace_user_resource_permission.py
@date：2025/4/28 16:38
@desc:
"""

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.auth.constants.compare_constants import CompareConstants
from common.auth.constants.group_constants import Group
from common.auth.constants.operate_constants import Operate
from common.auth.constants.permission_constants import PermissionConstants
from common.auth.constants.role_constants import RoleConstants
from common.auth.struct.aggregate_permission import ViewPermission
from common.auth.struct.permission import Permission
from common.log.log import log
from system_manage.api.user_resource_permission import (
    UserResourcePermissionAPI,
    EditUserResourcePermissionAPI,
    ResourceUserPermissionAPI,
    ResourceUserPermissionPageAPI,
    ResourceUserPermissionEditAPI,
    UserResourcePermissionPageAPI,
)
from system_manage.serializers.user_group_resource_permission import (
    UserGroupResourcePermissionSerializer,
    ResourceUserGroupPermissionSerializer,
)
from users.models.user_group import SystemUserGroup


def get_user_operation_object(user_group_id):
    user_group = QuerySet(model=SystemUserGroup).filter(id=user_group_id).first()
    if user_group is not None:
        return {"name": user_group.name}
    return {}


class WorkSpaceUserGroupResourcePermissionView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        description=_("Obtain resource authorization list"),
        operation_id=_("Obtain resource authorization list"),  # type: ignore
        parameters=UserResourcePermissionAPI.get_parameters(),
        responses=UserResourcePermissionAPI.get_response(),
        tags=[_("Resources authorization")],  # type: ignore
    )
    @has_permissions(
        lambda r, kwargs: PermissionConstants[
            kwargs.get("resource") + "_RESOURCE_PERMISSION_READ"
        ]._build_workspace_permission(),
        RoleConstants.ADMIN,
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    def get(self, request: Request, workspace_id: str, user_group_id: str, resource: str):
        return result.success(
            UserGroupResourcePermissionSerializer(
                data={"workspace_id": workspace_id, "user_group_id": user_group_id, "auth_target_type": resource}
            ).list(
                {"name": request.query_params.get("name"), "permission": request.query_params.getlist("permission[]")},
                request.user,
            )
        )

    @extend_schema(
        methods=["PUT"],
        description=_("Modify the resource authorization list"),
        operation_id=_("Modify the resource authorization list"),  # type: ignore
        parameters=EditUserResourcePermissionAPI.get_parameters(),
        request=EditUserResourcePermissionAPI.get_request(),
        responses=EditUserResourcePermissionAPI.get_response(),
        tags=[_("Resources authorization")],  # type: ignore
    )
    @log(
        menu="System",
        operate="Modify the resource authorization list",
        get_operation_object=lambda r, k: get_user_operation_object(k.get("user_group_id")),
    )
    @has_permissions(
        lambda r, kwargs: PermissionConstants[
            kwargs.get("resource") + "_RESOURCE_PERMISSION_EDIT"
        ]._build_workspace_permission(),
        RoleConstants.ADMIN,
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    def put(self, request: Request, workspace_id: str, user_group_id: str, resource: str):
        return result.success(
            UserGroupResourcePermissionSerializer(
                data={"workspace_id": workspace_id, "user_group_id": user_group_id, "auth_target_type": resource}
            ).edit(request.data, request.user)
        )

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Obtain resource authorization list by page"),
            summary=_("Obtain resource authorization list by page"),
            operation_id=_("Obtain resource authorization list by page"),  # type: ignore
            request=None,
            parameters=UserResourcePermissionPageAPI.get_parameters(),
            responses=UserResourcePermissionPageAPI.get_response(),
            tags=[_("Resources authorization")],  # type: ignore
        )
        @has_permissions(
            lambda r, kwargs: PermissionConstants[
                kwargs.get("resource") + "_RESOURCE_PERMISSION_READ"
            ]._build_workspace_permission(),
            RoleConstants.ADMIN,
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        )
        def get(
            self,
            request: Request,
            workspace_id: str,
            user_group_id: str,
            resource: str,
            current_page: str,
            page_size: str,
        ):
            return result.success(
                UserGroupResourcePermissionSerializer(
                    data={"workspace_id": workspace_id, "user_group_id": user_group_id, "auth_target_type": resource}
                ).page(
                    {
                        "name": request.query_params.get("name"),
                        "permission": request.query_params.getlist("permission[]"),
                    },
                    current_page,
                    page_size,
                    request.user,
                )
            )


class WorkspaceResourceUserGroupPermissionView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        description=_("Get user group authorization status of resource"),
        summary=_("Get user group authorization status of resource"),
        operation_id=_("Get user group authorization status of resource"),  # type: ignore
        parameters=ResourceUserPermissionAPI.get_parameters(),
        responses=ResourceUserPermissionAPI.get_response(),
        tags=[_("Resources authorization")],  # type: ignore
    )
    @has_permissions(
        lambda r, kwargs: PermissionConstants[
            kwargs.get("resource").replace("_FOLDER", "") + "_RESOURCE_AUTHORIZATION"
        ].get_workspace_permission_workspace_manage_role(),
        lambda r, kwargs: PermissionConstants[
            kwargs.get("resource").replace("_FOLDER", "") + "_RESOURCE_AUTHORIZATION"
        ]._build_workspace_permission(resource_id_key="target"),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [
                lambda r, kwargs: PermissionConstants[
                    kwargs.get("resource").replace("_FOLDER", "")
                ]._build_workspace_permission(resource_id_key="target")(r, **kwargs)
            ],
            compare=CompareConstants.AND,
        ),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    def get(self, request: Request, workspace_id: str, target: str, resource: str):
        return result.success(
            UserGroupResourcePermissionSerializer(
                data={
                    "workspace_id": workspace_id,
                    "target": target,
                    "auth_target_type": resource.replace("_FOLDER", ""),
                }
            ).list(
                {"name": request.query_params.get("name"), "permission": request.query_params.getlist("permission[]")}
            )
        )

    @extend_schema(
        methods=["PUT"],
        description=_("Edit user group authorization status of resource"),
        summary=_("Edit user group authorization status of resource"),
        operation_id=_("Edit user group authorization status of resource"),  # type: ignore
        parameters=ResourceUserPermissionEditAPI.get_parameters(),
        request=ResourceUserPermissionEditAPI.get_request(),
        responses=ResourceUserPermissionEditAPI.get_response(),
        tags=[_("Resources authorization")],  # type: ignore
    )
    @log(
        menu="System",
        operate="Edit user group authorization status of resource",
        get_operation_object=lambda r, k: get_user_operation_object(k.get("user_id")),
    )
    @has_permissions(
        lambda r, kwargs: PermissionConstants[
            kwargs.get("resource").replace("_FOLDER", "") + "_RESOURCE_AUTHORIZATION"
        ].get_workspace_permission_workspace_manage_role(),
        lambda r, kwargs: PermissionConstants[
            kwargs.get("resource").replace("_FOLDER", "") + "_RESOURCE_AUTHORIZATION"
        ]._build_workspace_permission(resource_id_key="target"),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [
                lambda r, kwargs: PermissionConstants[
                    kwargs.get("resource").replace("_FOLDER", "")
                ]._build_workspace_permission(resource_id_key="target")(r, **kwargs)
            ],
            compare=CompareConstants.AND,
        ),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    def put(self, request: Request, workspace_id: str, target: str, resource: str):
        return result.success(
            ResourceUserGroupPermissionSerializer(
                data={
                    "workspace_id": workspace_id,
                    "target": target,
                    "auth_target_type": resource.replace("_FOLDER", ""),
                }
            ).edit(instance=request.data, current_user_id=request.user.id)
        )

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Get user group authorization status of resource by page"),
            summary=_("Get user group authorization status of resource by page"),
            operation_id=_("Get user group authorization status of resource by page"),  # type: ignore
            parameters=ResourceUserPermissionPageAPI.get_parameters(),
            responses=ResourceUserPermissionPageAPI.get_response(),
            tags=[_("Resources authorization")],  # type: ignore
        )
        @has_permissions(
            lambda r, kwargs: PermissionConstants[
                kwargs.get("resource").replace("_FOLDER", "") + "_RESOURCE_AUTHORIZATION"
            ].get_workspace_permission_workspace_manage_role(),
            lambda r, kwargs: PermissionConstants[
                kwargs.get("resource").replace("_FOLDER", "") + "_RESOURCE_AUTHORIZATION"
            ]._build_workspace_permission(resource_id_key="target"),
            ViewPermission(
                [RoleConstants.USER.get_workspace_role()],
                [
                    lambda r, kwargs: PermissionConstants[
                        kwargs.get("resource").replace("_FOLDER", "")
                    ]._build_workspace_permission(resource_id_key="target")(r, **kwargs)
                ],
                compare=CompareConstants.AND,
            ),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        )
        def get(
            self, request: Request, workspace_id: str, target: str, resource: str, current_page: int, page_size: int
        ):
            return result.success(
                ResourceUserGroupPermissionSerializer(
                    data={
                        "workspace_id": workspace_id,
                        "target": target,
                        "auth_target_type": resource.replace("_FOLDER", ""),
                    }
                ).page(
                    {
                        "name": request.query_params.get("name"),
                        "permission": request.query_params.getlist("permission[]"),
                    },
                    current_page,
                    page_size,
                )
            )
