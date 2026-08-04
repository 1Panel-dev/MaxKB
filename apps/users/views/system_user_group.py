# coding=utf-8

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants
from common.log.log import log
from models_provider.api.model import DefaultModelResponse
from users.api.user_group import (
    AddMemberApi, CreateUserGroupApi, DeleteUserGroupApi,
    RemoveMemberApi, UserGroupListApi, UserGroupListPageApi
)
from users.models.user_group import SystemUserGroup
from users.serializers.user_group import (
    SystemUserGroupCreateSerializer,
    UserGroupAddMemberSerializer,
    UserGroupRemoveMemberSerializer,
    UserGroupListPageSerializer
)


def _get_operation_object(request, kwargs):
    try:
        return {"name": request.data.get("name", None)}
    except Exception:
        return {}


def _get_group_operation_object(group_id):
    try:
        group = SystemUserGroup.objects.filter(id=group_id).values("name").first()
        return group or {}
    except Exception:
        return {}


class SystemUserGroupView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["POST"],
        summary=_("Create or update System User Group"),
        description=_("Create or update System User Group"),
        operation_id=_("Create or update System User Group"),
        request=CreateUserGroupApi.get_request(),
        responses=CreateUserGroupApi.get_response(),
        tags=["IAM/System User Group"],
    )
    @has_permissions(PermissionConstants.SYSTEM_USER_GROUP_CREATE,
                     PermissionConstants.SYSTEM_USER_GROUP_EDIT,
                     RoleConstants.ADMIN)
    @log(
        menu="IAM/System User Group",
        operate="Create or update System User Group",
        get_operation_object=_get_operation_object,
    )
    def post(self, request: Request, workspace_id: str):
        serializer = SystemUserGroupCreateSerializer(
            data={
                **request.data,
                "workspace_id": workspace_id,
            }
        )
        data = serializer.create_or_update_group(with_valid=True)
        return result.success(data)

    @extend_schema(
        methods=["GET"],
        summary=_("Get System User Group list by workspace id"),
        description=_("Get System User Group list by workspace id"),
        operation_id=_("Get System User Group list by workspace id"),
        request=UserGroupListApi.get_parameters(),
        responses=UserGroupListApi.get_response(),
        tags=["IAM/System User Group"],
    )
    @has_permissions(PermissionConstants.SYSTEM_USER_GROUP_READ, RoleConstants.ADMIN)
    def get(self, request: Request, workspace_id: str):
        return result.success(SystemUserGroupCreateSerializer.Query(
            data={'workspace_id': workspace_id}
        ).list())

    class Delete(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["DELETE"],
            summary=_("Delete System User Group"),
            description=_("Delete System User Group"),
            operation_id=_("Delete System User Group"),
            parameters=DeleteUserGroupApi.get_parameters(),
            responses=DefaultModelResponse.get_response(),
            tags=["IAM/System User Group"],
        )
        @has_permissions(PermissionConstants.SYSTEM_USER_GROUP_DELETE, RoleConstants.ADMIN)
        @log(
            menu="IAM/System User Group",
            operate="Delete System User Group",
            get_operation_object=lambda r, k: _get_group_operation_object(k.get("user_group_id")),
        )
        def delete(self, request: Request, workspace_id, user_group_id: str):
            return result.success(
                SystemUserGroupCreateSerializer.UserGroupDeleteSerializer(
                    data={"id": user_group_id, "workspace_id": workspace_id}).delete()
            )

    class AddMember(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["POST"],
            summary=_("Add members to System User Group"),
            description=_("Add members to System User Group"),
            operation_id=_("Add members to System User Group"),
            parameters=AddMemberApi.get_parameters(),
            request=AddMemberApi.get_request(),
            responses=DefaultModelResponse.get_response(),
            tags=["IAM/System User Group"],
        )
        @has_permissions(PermissionConstants.SYSTEM_USER_GROUP_ADD_MEMBER, RoleConstants.ADMIN)
        @log(
            menu="IAM/System User Group",
            operate="Add members to System User Group",
        )
        def post(self, request: Request, workspace_id: str, user_group_id: str):
            return result.success(
                UserGroupAddMemberSerializer(
                    data={"id": user_group_id, "workspace_id": workspace_id,
                          "user_ids": request.data.get("user_ids", [])}
                ).add_member()
            )

    class RemoveMember(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["DELETE"],
            summary=_("Remove members from System User Group"),
            description=_("Remove members from System User Group"),
            operation_id=_("Remove members from System User Group"),
            parameters=RemoveMemberApi.get_parameters(),
            request=RemoveMemberApi.get_request(),
            responses=DefaultModelResponse.get_response(),
            tags=["IAM/System User Group"],
        )
        @has_permissions(PermissionConstants.SYSTEM_USER_GROUP_REMOVE_MEMBER, RoleConstants.ADMIN)
        @log(
            menu="IAM/System User Group",
            operate="Remove members from System User Group",
        )
        def delete(self, request: Request, workspace_id: str, user_group_id: str):
            return result.success(
                UserGroupRemoveMemberSerializer(
                    data={"id": user_group_id, "workspace_id": workspace_id,
                          "group_relation_ids": request.data.get("group_relation_ids", [])}
                ).remove_member()
            )

    class UserList(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            summary=_("Get user list by group"),
            description=_("Get user list by group"),
            operation_id=_("Get user list by group"),  # type: ignore
            tags=[_("IAM/System User Group")],  # type: ignore
            parameters=UserGroupListPageApi.get_parameters(),
            responses=UserGroupListPageApi.get_response(),
        )
        @has_permissions(PermissionConstants.SYSTEM_USER_GROUP_READ, RoleConstants.ADMIN)
        def get(self, request: Request, workspace_id: str, user_group_id: str, current_page: int, page_size: int):
            d = UserGroupListPageSerializer.Query(
                data={
                    "username": request.query_params.get("username", None),
                    "nick_name": request.query_params.get("nick_name", None),
                    "source": request.query_params.get("source", None),
                    "group_id": user_group_id,
                    "workspace_id": workspace_id,
                }
            )
            return result.success(d.page(current_page, page_size))
