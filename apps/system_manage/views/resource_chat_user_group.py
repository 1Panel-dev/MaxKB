from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.auth.constants.role_constants import RoleConstants
from common.result import result
from system_manage.api.resource_chat_user_group import ResourceChatUserGroupListAPI, ResourceChatUserGroupEditAPI
from system_manage.serializers.resource_chat_user_group import (
    ResourceChatUserGroupQuerySerializer,
    ResourceChatUserGroupSerializer,
)
from system_manage.views.resource_chat_user import get_chat_user_permission_constant, get_chat_user_role_permissions


class ResourceChatUserGroup(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        description=_("Get Resource chat user group List"),
        summary=_("Get Resource chat user group List"),
        operation_id=_("Get Resource chat user group List"),  # type: ignore
        parameters=ResourceChatUserGroupListAPI.get_parameters(),
        responses=None,
        tags=[_("Chat user")],  # type: ignore
    )
    @has_permissions(
        lambda r, kwargs: get_chat_user_permission_constant(
            kwargs.get("resource_type"), "READ"
        ).get_workspace_permission(),
        lambda r, kwargs: get_chat_user_permission_constant(
            kwargs.get("resource_type"), "READ"
        ).get_workspace_permission_workspace_manage_role(),
        *get_chat_user_role_permissions("READ"),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    def get(
        self,
        request: Request,
        workspace_id: str,
        resource_id: str,
        resource_type: str,
    ):
        return result.success(
            ResourceChatUserGroupQuerySerializer(
                data={
                    "workspace_id": workspace_id,
                    "resource_id": resource_id,
                    "resource_type": resource_type,
                    "user_group_name": request.query_params.get("user_group_name"),
                }
            ).list()
        )

    @extend_schema(
        methods=["PUT"],
        description=_("Edit Resource chat user group List"),
        summary=_("Edit Resource chat user group List"),
        operation_id=_("Edit Resource chat user group List"),  # type: ignore
        parameters=ResourceChatUserGroupEditAPI.get_parameters(),
        request=ResourceChatUserGroupEditAPI.get_request(),
        responses=ResourceChatUserGroupEditAPI.get_response(),
        tags=[_("Chat user")],  # type: ignore
    )
    @has_permissions(
        lambda r, kwargs: get_chat_user_permission_constant(
            kwargs.get("resource_type"), "EDIT"
        ).get_workspace_permission(),
        lambda r, kwargs: get_chat_user_permission_constant(
            kwargs.get("resource_type"), "EDIT"
        ).get_workspace_permission_workspace_manage_role(),
        *get_chat_user_role_permissions("EDIT"),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    def put(self, request: Request, workspace_id: str, resource_id: str, resource_type: str):
        return result.success(
            ResourceChatUserGroupSerializer(
                data={
                    "workspace_id": workspace_id,
                    "resource_id": resource_id,
                    "resource_type": resource_type,
                }
            ).edit(request.data)
        )

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Get Resource chat user group page List"),
            summary=_("Get Resource chat user page group List"),
            operation_id=_("Get Resource chat user group page List"),  # type: ignore
            parameters=ResourceChatUserGroupListAPI.get_parameters(),
            responses=None,
            tags=[_("Chat user")],  # type: ignore
        )
        @has_permissions(
            lambda r, kwargs: get_chat_user_permission_constant(
                kwargs.get("resource_type"), "READ"
            ).get_workspace_permission(),
            lambda r, kwargs: get_chat_user_permission_constant(
                kwargs.get("resource_type"), "READ"
            ).get_workspace_permission_workspace_manage_role(),
            *get_chat_user_role_permissions("READ"),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        )
        def get(
            self,
            request: Request,
            workspace_id: str,
            resource_id: str,
            resource_type: str,
            current_page: int,
            page_size: int,
        ):
            return result.success(
                ResourceChatUserGroupQuerySerializer(
                    data={
                        "workspace_id": workspace_id,
                        "resource_id": resource_id,
                        "resource_type": resource_type,
                        "user_group_name": request.query_params.get("user_group_name"),
                    }
                ).page(current_page, page_size)
            )
