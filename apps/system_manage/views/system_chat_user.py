from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.auth.constants.permission_constants import PermissionConstants
from common.auth.constants.role_constants import RoleConstants
from common.log.log import log
from common.result import result
from models_provider.api.model import DefaultModelResponse
from system_manage.api.chat_user import BatchAddGroupApi, ChatUserAPI, ChatUserPageApi, EditUserApi
from system_manage.api.user_group import AddMemberApi, CreateUserGroupApi, DeleteUserGroupApi, RemoveMemberApi, \
    UserGroupListApi
from system_manage.models import ChatUser, UserGroup
from system_manage.serializers.chat_user import (
    ChatUserSerializer,
    UserGroupAddMemberSerializer,
    UserGroupCreateSerializer,
    UserGroupListPageSerializer,
    UserGroupRemoveMemberSerializer,
)
from users.api.user import ChangeUserPasswordApi, DeleteUserApi, UserPageApi, UserProfileAPI


def get_user_operation_object(user_id):
    user_model = QuerySet(model=ChatUser).filter(id=user_id).first()
    if user_model is not None:
        return {"name": user_model.username}
    return {}


def get_batch_delete_user_operation_object(user_ids):
    user_models = QuerySet(model=ChatUser).filter(id__in=user_ids)
    if user_models.exists():
        return {"name": ", ".join([user.username for user in user_models])}
    return {}


def get_user_group_operation_object(user_group_id):
    user_group_model = QuerySet(model=UserGroup).filter(id=user_group_id).first()
    if user_group_model is not None:
        return {"name": user_group_model.name}
    return {}


class SystemChatUserView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["POST"],
        summary=_("Create chat user"),
        description=_("Create chat user"),
        operation_id=_("Create chat user"),  # type: ignore
        tags=[_("System/Chat user")],  # type: ignore
        request=ChatUserAPI.get_request(),
        responses=ChatUserAPI.get_response(),
    )
    @has_permissions(PermissionConstants.CHAT_USER_CREATE, RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE)
    @log(
        menu="User management",
        operate="Add user",
        get_operation_object=lambda r, k: {"name": r.data.get("username", None)},
    )
    def post(self, request: Request):
        return result.success(ChatUserSerializer().save(request.data))

    class List(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            summary=_("Get chat user list"),
            description=_("Get chat user list"),
            operation_id=_("Get chat user list"),  # type: ignore
            tags=[_("System/Chat user")],  # type: ignore
            responses=ChatUserPageApi.get_response(),
        )
        @has_permissions(PermissionConstants.CHAT_USER_READ, PermissionConstants.USER_GROUP_READ, RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE)
        def get(self, request: Request):
            return result.success(ChatUserSerializer.list())

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["DELETE"],
            description=_("Delete chat user"),
            summary=_("Delete chat user"),
            operation_id=_("Delete chat user"),  # type: ignore
            tags=[_("System/Chat user")],  # type: ignore
            parameters=DeleteUserApi.get_parameters(),
            responses=DefaultModelResponse.get_response(),
        )
        @has_permissions(PermissionConstants.CHAT_USER_DELETE, RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE)
        @log(
            menu="User management",
            operate="Delete user",
            get_operation_object=lambda r, k: get_user_operation_object(k.get("user_id")),
        )
        def delete(self, request: Request, user_id):
            return result.success(ChatUserSerializer.Operate(data={"id": user_id}).delete(with_valid=True))

        @extend_schema(
            methods=["GET"],
            summary=_("Get chat user information"),
            description=_("Get chat user information"),
            operation_id=_("Get chat user information"),  # type: ignore
            tags=[_("System/Chat user")],  # type: ignore
            request=DeleteUserApi.get_parameters(),
            responses=UserProfileAPI.get_response(),
        )
        @has_permissions(PermissionConstants.CHAT_USER_READ, RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE)
        def get(self, request: Request, user_id):
            return result.success(ChatUserSerializer.Operate(data={"id": user_id}).one(with_valid=True))

        @extend_schema(
            methods=["PUT"],
            summary=_("Update chat user information"),
            description=_("Update chat user information"),
            operation_id=_("Update chat user information"),  # type: ignore
            tags=[_("System/Chat user")],  # type: ignore
            parameters=DeleteUserApi.get_parameters(),
            request=EditUserApi.get_request(),
            responses=UserProfileAPI.get_response(),
        )
        @has_permissions(PermissionConstants.CHAT_USER_EDIT, RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE)
        @log(
            menu="Chat user",
            operate="Update user information",
            get_operation_object=lambda r, k: get_user_operation_object(k.get("user_id")),
        )
        def put(self, request: Request, user_id):
            return result.success(ChatUserSerializer.Operate(data={"id": user_id}).edit(request.data, with_valid=True))

    class GetUserListByGroup(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            summary=_("Get user list by group"),
            description=_("Get user list by group"),
            operation_id=_("Get user list by group"),  # type: ignore
            tags=[_("System/Chat user")],  # type: ignore
            request=AddMemberApi.get_parameters(),
            responses=UserProfileAPI.get_response(),
        )
        @has_permissions(PermissionConstants.CHAT_USER_READ, RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE)
        def get(self, request: Request, user_group_id):
            return result.success(
                ChatUserSerializer.GetUserListByGroup(data={"group_id": user_group_id}).get_user_list()
            )

    class BatchDelete(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["POST"],
            summary=_("Batch delete chat user"),
            description=_("Batch delete chat user"),
            operation_id=_("Batch delete chat user"),  # type: ignore
            tags=[_("System/Chat user")],  # type: ignore
            request=DeleteUserApi.get_request(),
            responses=DefaultModelResponse.get_response(),
        )
        @has_permissions(PermissionConstants.CHAT_USER_DELETE, RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE)
        @log(
            menu="Chat user",
            operate="Batch delete user",
            get_operation_object=lambda r, k: get_batch_delete_user_operation_object(r.data.get("ids", [])),
        )
        def post(self, request: Request):
            return result.success(ChatUserSerializer.BatchDeleteInstance({"ids": request.data}).batch_delete())

    class BatchAddGroup(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["POST"],
            summary=_("Batch add chat user to group"),
            description=_("Batch add chat user to group"),
            operation_id=_("Batch add chat user to group"),  # type: ignore
            tags=[_("System/Chat user")],  # type: ignore
            request=BatchAddGroupApi.get_request(),
            responses=DefaultModelResponse.get_response(),
        )
        @has_permissions(PermissionConstants.CHAT_USER_GROUP, RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE)
        @log(
            menu="Chat user",
            operate="Batch add user to group",
            get_operation_object=lambda r, k: get_batch_delete_user_operation_object(r.data.get("user_group_ids", [])),
        )
        def post(self, request: Request):
            return result.success(ChatUserSerializer.BatchAddGroup(data=request.data).batch_add_group(with_valid=True))

    class RePassword(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["PUT"],
            summary=_("Change chat user password"),
            description=_("Change chat user password"),
            operation_id=_("Change chat user password"),  # type: ignore
            tags=[_("System/Chat user")],  # type: ignore
            parameters=DeleteUserApi.get_parameters(),
            request=ChangeUserPasswordApi.get_request(),
            responses=DefaultModelResponse.get_response(),
        )
        @has_permissions(PermissionConstants.CHAT_USER_EDIT, RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE)
        @log(
            menu="Chat user",
            operate="Change password",
            get_operation_object=lambda r, k: get_user_operation_object(k.get("user_id")),
        )
        def put(self, request: Request, user_id):
            return result.success(
                ChatUserSerializer.Operate(data={"id": user_id}).re_password(request.data, with_valid=True)
            )

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            summary=_("Get user paginated list"),
            description=_("Get user paginated list"),
            operation_id=_("Get user paginated list"),  # type: ignore
            tags=[_("System/Chat user")],  # type: ignore
            parameters=ChatUserPageApi.get_parameters(),
            responses=UserPageApi.get_response(),
        )
        @has_permissions(PermissionConstants.CHAT_USER_READ, RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE)
        def get(self, request: Request, current_page, page_size):
            d = ChatUserSerializer.Query(
                data={
                    "username": request.query_params.get("username", None),
                    "nick_name": request.query_params.get("nick_name", None),
                    "source": request.query_params.get("source", None),
                    "is_active": request.query_params.get("is_active", None),
                    "user_id": str(request.user.id),
                }
            )
            return result.success(d.page(current_page, page_size))


class SystemChatUserGroupView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["POST"],
        summary=_("Create or update Chat User Group"),
        description=_("Create or update Chat User Group"),
        operation_id=_("Create or update Chat User Group"),  # type: ignore
        request=CreateUserGroupApi.get_request(),
        responses=CreateUserGroupApi.get_response(),
        tags=[_("System/User Group")],  # type: ignore
    )  # type: ignore
    @has_permissions(PermissionConstants.USER_GROUP_CREATE, PermissionConstants.USER_GROUP_EDIT, RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE)
    @log(
        menu="User group",
        operate="Create or update user group",
        get_operation_object=lambda r, k: {"name": r.data.get("name", None)},
    )
    def post(self, request: Request):
        return result.success(UserGroupCreateSerializer(data=request.data).create_or_update_group(with_valid=True))

    @extend_schema(
        methods=["GET"],
        summary=_("Get user group list"),
        description=_("Get user group list"),
        operation_id=_("Get user group list"),  # type: ignore
        responses=UserGroupListApi.get_response(),
        tags=[_("System/User Group")],  # type: ignore
    )
    @has_permissions(PermissionConstants.USER_GROUP_READ, RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE)
    def get(self, request: Request):
        return result.success(UserGroupCreateSerializer().get_user_group_list())

    class Delete(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["DELETE"],
            summary=_("Delete chat user group"),
            description=_("Delete chat user group"),
            operation_id=_("Delete chat user group"),  # type: ignore
            parameters=DeleteUserGroupApi.get_parameters(),
            responses=DefaultModelResponse,
            tags=[_("System/User Group")],  # type: ignore
        )
        @has_permissions(PermissionConstants.USER_GROUP_DELETE, RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE)
        @log(
            menu="User group",
            operate="Delete user group",
            get_operation_object=lambda r, k: get_user_group_operation_object(k.get("user_group_id")),
        )
        def delete(self, request: Request, user_group_id: str):
            return result.success(
                UserGroupCreateSerializer.UserGroupDeleteSerializer(data={"id": user_group_id}).delete()
            )

    class AddMember(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["POST"],
            summary=_("Add member to chat user group"),
            description=_("Add member to chat user group"),
            operation_id=_("Add member to chat user group"),  # type: ignore
            parameters=AddMemberApi.get_parameters(),
            request=AddMemberApi.get_request(),
            responses=DefaultModelResponse,
            tags=[_("System/User Group")],  # type: ignore
        )
        @has_permissions(PermissionConstants.USER_GROUP_ADD_MEMBER, RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE)
        @log(
            menu="User group",
            operate="Add member to user group",
            get_operation_object=lambda r, k: get_user_group_operation_object(k.get("user_group_id")),
            get_user=lambda r: {"user_name": None, "email": None},
            get_details=lambda r: {"user_ids": r.data.get("user_ids", [])},
        )
        def post(self, request: Request, user_group_id: str):
            return result.success(
                UserGroupAddMemberSerializer(
                    data={"id": user_group_id, "user_ids": request.data.get("user_ids", [])}
                ).add_member()
            )

    class RemoveMember(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["POST"],
            summary=_("Remove member from chat user group"),
            description=_("Remove member from chat user group"),
            operation_id=_("Remove member from chat user group"),  # type: ignore
            parameters=AddMemberApi.get_parameters(),
            request=RemoveMemberApi.get_request(),
            responses=DefaultModelResponse,
            tags=[_("System/User Group")],  # type: ignore
        )
        @has_permissions(PermissionConstants.USER_GROUP_REMOVE_MEMBER, RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE)
        @log(
            menu="User group",
            operate="Remove member from user group",
            get_operation_object=lambda r, k: get_user_group_operation_object(k.get("user_group_id")),
            get_user=lambda r: {"user_name": None, "email": None},
            get_details=lambda r: {"group_relation_ids": r.data.get("group_relation_ids", [])},
        )
        def post(self, request: Request, user_group_id: str):
            return result.success(
                UserGroupRemoveMemberSerializer(
                    data={"id": user_group_id, "group_relation_ids": request.data.get("group_relation_ids", [])}
                ).remove_member()
            )

    class UserList(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            summary=_("Get user list by group"),
            description=_("Get user list by group"),
            operation_id=_("Get user list by group"),  # type: ignore
            tags=[_("System/User Group")],  # type: ignore
            parameters=UserGroupListApi.get_parameters(),
            responses=UserGroupListApi.get_response(),
        )
        @has_permissions(PermissionConstants.USER_GROUP_READ, RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE)
        def get(self, request: Request, user_group_id: str, current_page: int, page_size: int):
            d = UserGroupListPageSerializer.Query(
                data={
                    "username": request.query_params.get("username", None),
                    "nick_name": request.query_params.get("nick_name", None),
                    "source": request.query_params.get("source", None),
                    "group_id": user_group_id,
                }
            )
            return result.success(d.page(current_page, page_size))
