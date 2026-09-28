# coding=utf-8
"""
@project: MaxKB-xpack
@Author：虎虎
@file： resource_chat_user.py
@date：2025/6/5 16:21
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
from common.auth.struct.permission import Permission

from system_manage.api.resource_chat_user import (
    WorkspaceResourceChatUserListAPI,
    EditResourceChatUserAPI,
    ResourceChatUserPageAPI,
)
from system_manage.serializers.resource_chat_user import ResourceChatUserQuerySerializer, ResourceChatUserSerializer


class ResourceChatUser(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        description=_("Get Resource chat user List"),
        summary=_("Get Resource chat user List"),
        operation_id=_("Get Resource chat user List"),  # type: ignore
        parameters=WorkspaceResourceChatUserListAPI.get_parameters(),
        responses=WorkspaceResourceChatUserListAPI.get_response(),
        tags=[_("Chat user")],  # type: ignore
    )
    @has_permissions(
        lambda r, kwargs: PermissionConstants[
            f"{kwargs.get('resource_type').upper()}_CHAT_USER_READ"
        ].get_workspace_permission(),
        lambda r, kwargs: PermissionConstants[
            f"{kwargs.get('resource_type').upper()}_CHAT_USER_READ"
        ].get_workspace_permission_workspace_manage_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [
                lambda r, kwargs: Permission(
                    group=PermissionConstants[kwargs.get("resource_type").upper()].value.group,
                    sub_group=PermissionConstants[kwargs.get("resource_type").upper()].value.sub_group,
                    operate=PermissionConstants[kwargs.get("resource_type").upper()].value.operate,
                    bit_index=PermissionConstants[kwargs.get("resource_type").upper()].value.bit_index,
                    workspace_id=kwargs.get("workspace_id"),
                    resource_id=kwargs.get("resource_id"),
                )
            ],
            compare=CompareConstants.AND,
        ),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    def get(self, request: Request, workspace_id: str, resource_type: str, resource_id: str, user_group_id: str):
        return result.success(
            ResourceChatUserQuerySerializer(
                data={
                    "workspace_id": workspace_id,
                    "resource_id": resource_id,
                    "resource_type": resource_type,
                    "username": request.query_params.get("username"),
                    "nick_name": request.query_params.get("nick_name"),
                    "source": request.query_params.get("source"),
                    "user_group_id": user_group_id,
                }
            ).list()
        )

    @extend_schema(
        methods=["PUT"],
        description=_("Edit Resource chat user List"),
        summary=_("Edit Resource chat user List"),
        operation_id=_("Edit Resource chat user List"),  # type: ignore
        parameters=EditResourceChatUserAPI.get_parameters(),
        request=EditResourceChatUserAPI.get_request(),
        responses=None,
        tags=[_("Chat user")],  # type: ignore
    )
    @has_permissions(
        lambda r, kwargs: PermissionConstants[
            f"{kwargs.get('resource_type').upper()}_CHAT_USER_EDIT"
        ].get_workspace_permission(),
        lambda r, kwargs: PermissionConstants[
            f"{kwargs.get('resource_type').upper()}_CHAT_USER_EDIT"
        ].get_workspace_permission_workspace_manage_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [
                lambda r, kwargs: Permission(
                    group=PermissionConstants[kwargs.get("resource_type").upper()].value.group,
                    sub_group=PermissionConstants[kwargs.get("resource_type").upper()].value.sub_group,
                    operate=PermissionConstants[kwargs.get("resource_type").upper()].value.operate,
                    bit_index=PermissionConstants[kwargs.get("resource_type").upper()].value.bit_index,
                    workspace_id=kwargs.get("workspace_id"),
                    resource_id=kwargs.get("resource_id"),
                )
            ],
            compare=CompareConstants.AND,
        ),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    def put(self, request: Request, workspace_id: str, resource_type, resource_id: str, user_group_id: str):
        return result.success(
            ResourceChatUserSerializer(
                data={
                    "workspace_id": workspace_id,
                    "resource_id": resource_id,
                    "resource_type": resource_type,
                    "user_group_id": user_group_id,
                }
            ).edit(request.data)
        )

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Get Resource chat user page List"),
            summary=_("Get Resource chat user page List"),
            operation_id=_("Get Resource chat user page List"),  # type: ignore
            parameters=ResourceChatUserPageAPI.get_parameters(),
            responses=ResourceChatUserPageAPI.get_response(),
            tags=[_("Chat user")],  # type: ignore
        )
        @has_permissions(
            lambda r, kwargs: PermissionConstants[
                f"{kwargs.get('resource_type').upper()}_CHAT_USER_READ"
            ].get_workspace_permission(),
            lambda r, kwargs: PermissionConstants[
                f"{kwargs.get('resource_type').upper()}_CHAT_USER_READ"
            ].get_workspace_permission_workspace_manage_role(),
            ViewPermission(
                [RoleConstants.USER.get_workspace_role()],
                [
                    lambda r, kwargs: Permission(
                        group=PermissionConstants[kwargs.get("resource_type").upper()].value.group,
                        sub_group=PermissionConstants[kwargs.get("resource_type").upper()].value.sub_group,
                        operate=PermissionConstants[kwargs.get("resource_type").upper()].value.operate,
                        bit_index=PermissionConstants[kwargs.get("resource_type").upper()].value.bit_index,
                        workspace_id=kwargs.get("workspace_id"),
                        resource_id=kwargs.get("resource_id"),
                    )
                ],
                compare=CompareConstants.AND,
            ),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        )
        def get(
            self,
            request: Request,
            workspace_id: str,
            resource_type: str,
            resource_id: str,
            user_group_id: str,
            current_page: int,
            page_size: int,
        ):
            return result.success(
                ResourceChatUserQuerySerializer(
                    data={
                        "workspace_id": workspace_id,
                        "resource_id": resource_id,
                        "resource_type": resource_type,
                        "username": request.query_params.get("username"),
                        "nick_name": request.query_params.get("nick_name"),
                        "source": request.query_params.get("source"),
                        "user_group_id": user_group_id,
                    }
                ).page(current_page, page_size)
            )
