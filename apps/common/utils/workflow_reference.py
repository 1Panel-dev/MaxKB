from django.db.models import QuerySet

from common.exception.app_exception import AppUnauthorizedFailed
from common.utils.shared_resource_auth import filter_authorized_ids
from tools.models import Tool, ToolScope


def validate_resource_references(instance, workspace_id, user_id, created_tool_ids=()):
    # Import lazily: application and tool serializers both use this boundary.
    from application.serializers.application import (
        get_bound_application_ids, get_bound_tool_ids, validate_bound_tool_permissions,
    )

    if not user_id:
        raise AppUnauthorizedFailed(403, 'No permission to access')
    created_tool_ids = {str(value) for value in created_tool_ids}
    tool_ids = [value for value in get_bound_tool_ids(instance) if value not in created_tool_ids]
    visible_ids = set(filter_authorized_ids('tool', tool_ids, workspace_id))
    if any(value not in visible_ids for value in tool_ids):
        raise AppUnauthorizedFailed(403, 'No permission to access')
    validate_bound_tool_permissions(user_id, workspace_id, {
        'tool_ids': tool_ids,
        'application_ids': get_bound_application_ids(instance),
    })


def get_exportable_tools(tool_ids, workspace_id, user_id):
    tools = list(QuerySet(Tool).filter(id__in=tool_ids).exclude(scope=ToolScope.SHARED))
    # Sharing grants use of a tool, not redistribution of its code/package.
    if any(tool.workspace_id != workspace_id for tool in tools):
        raise AppUnauthorizedFailed(403, 'No permission to access')
    validate_resource_references({'tool_ids': [str(tool.id) for tool in tools]}, workspace_id, user_id)
    return tools
