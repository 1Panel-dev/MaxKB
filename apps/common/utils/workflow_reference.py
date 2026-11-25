from types import SimpleNamespace

from common.auth.authentication import get_is_permissions
from common.auth.constants.permission_constants import PermissionConstants
from common.database_model_manage.database_model_manage import DatabaseModelManage
from tools.models import Tool, ToolScope
from common.auth.constants.role_constants import RoleConstants
from common.auth.handle.impl.user_token import get_auth
from common.exception.app_exception import AppApiException
from django.utils.translation import gettext_lazy as _
from users.models import User


def authorized_resource_ids(resources, user_id, workspace_id, kind, permission):
    if not user_id or not workspace_id:
        return []
    user = User.objects.filter(id=user_id, is_active=True).first()
    if user is None:
        return []
    request = SimpleNamespace(user=user, auth=get_auth(user))
    permissions = (
        RoleConstants.ADMIN,
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        permission.get_workspace_permission_workspace_manage_role(),
        getattr(permission, f"get_workspace_{kind}_permission")(),
    )
    ids = resources.filter(workspace_id=workspace_id).values_list("id", flat=True)
    return [
        str(pk)
        for pk in ids
        if get_is_permissions(request, workspace_id=workspace_id, **{f"{kind}_id": str(pk)})(*permissions)
    ]


def require_authorized_ids(requested, authorized):
    if set(map(str, requested)) - set(map(str, authorized)):
        raise AppApiException(403, _("No permission to access"))


def get_authorized_tool_ids(user_id, workspace_id, tool_ids):
    if not tool_ids or not user_id or not workspace_id:
        return []
    tools = Tool.objects.filter(id__in=tool_ids)
    local = authorized_resource_ids(
        tools.filter(scope=ToolScope.WORKSPACE), user_id, workspace_id, "tool", PermissionConstants.TOOL_READ
    )
    authorize_shared = DatabaseModelManage.get_model("get_authorized_tool")
    if authorize_shared is None:
        return local
    user = User.objects.filter(id=user_id, is_active=True).first()
    if user is None:
        return []
    request = SimpleNamespace(user=user, auth=get_auth(user))
    shared = authorize_shared(tools.filter(scope=ToolScope.SHARED), workspace_id).values_list("id", flat=True)
    if workspace_id == "None":
        if get_is_permissions(request)(RoleConstants.ADMIN, PermissionConstants.SHARED_TOOL_READ):
            local.extend(map(str, shared))
        return local
    for pk in shared:
        if get_is_permissions(request, workspace_id=workspace_id, tool_id=str(pk))(
            RoleConstants.ADMIN,
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            RoleConstants.USER.get_workspace_role(),
            PermissionConstants.TOOL_READ.get_workspace_permission(),
            PermissionConstants.TOOL_READ.get_workspace_tool_permission(),
            PermissionConstants.TOOL_READ.get_workspace_permission_workspace_manage_role(),
        ):
            local.append(str(pk))
    return local


def require_workflow_tools(tool_ids, user_id, workspace_id):
    if tool_ids:
        require_authorized_ids(tool_ids, get_authorized_tool_ids(user_id, workspace_id, tool_ids))


def validate_workflow_references(work_flow, user_id, workspace_id, created_ids=()):
    from application.serializers.application import get_bound_tool_ids, validate_application_bindings

    bindings = {"work_flow": work_flow}
    require_workflow_tools(set(get_bound_tool_ids(bindings)) - set(map(str, created_ids)), user_id, workspace_id)
    validate_application_bindings(user_id, workspace_id, bindings)
