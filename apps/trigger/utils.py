# coding=utf-8
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from application.models import Application
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.exception.app_exception import AppApiException
from tools.models import Tool, ToolScope
from trigger.models import TriggerTask, TriggerTaskTypeChoices


def get_source_query_set(source_type, workspace_id):
    """Limit trigger targets to workspace resources and explicitly authorized shared tools."""
    if source_type == TriggerTaskTypeChoices.APPLICATION:
        return QuerySet(Application).filter(workspace_id=workspace_id)
    if source_type == TriggerTaskTypeChoices.TOOL:
        tools = QuerySet(Tool)
        query_set = tools.filter(workspace_id=workspace_id).exclude(scope=ToolScope.SHARED)
        get_authorized_tool = DatabaseModelManage.get_model('get_authorized_tool')
        if get_authorized_tool is not None:
            shared_tools = get_authorized_tool(tools.filter(scope=ToolScope.SHARED), workspace_id)
            query_set = query_set | shared_tools
        return query_set
    raise AppApiException(500, _('Error source type'))


def get_task_source(trigger_task):
    """Recheck persisted bindings and current workspace authorization before execution."""
    task = QuerySet(TriggerTask).filter(
        id=trigger_task.get('id'), trigger_id=trigger_task.get('trigger'),
        source_id=trigger_task.get('source_id'), source_type=trigger_task.get('source_type'),
        is_active=True, trigger__is_active=True,
    ).select_related('trigger').first()
    if task is None:
        return None
    return get_source_query_set(task.source_type, task.trigger.workspace_id).filter(id=task.source_id).first()
