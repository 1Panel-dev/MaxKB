from common.auth.constants.permission_constants import PermissionConstants
from common.auth.constants.role_constants import RoleConstants
from common.auth.struct.aggregate_permission import ViewPermission
from common.database_model_manage.database_model_manage import DatabaseModelManage
from tools.models import Tool, ToolScope


def get_tool_read_permission(request, kwargs):
    """Shared tool details follow workspace authorization and list permissions."""
    get_authorized_tool = DatabaseModelManage.get_model("get_authorized_tool")
    if get_authorized_tool is not None:
        shared_tools = Tool.objects.filter(id=kwargs["tool_id"], scope=ToolScope.SHARED)
        if get_authorized_tool(shared_tools, kwargs["workspace_id"]).exists():
            return ViewPermission(
                roles=[RoleConstants.USER.get_workspace_role()],
                permissions=[
                    PermissionConstants.TOOL_READ.get_workspace_permission(),
                    PermissionConstants.TOOL_READ.get_workspace_tool_permission(),
                ],
            )
    return PermissionConstants.TOOL_READ.get_workspace_tool_permission()(request, kwargs)
