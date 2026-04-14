# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_version.py.py
    @date：2025/6/3 15:46
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
from common.constants.permission_constants import PermissionConstants, RoleConstants, ViewPermission, CompareConstants
from common.log.log import log
from knowledge.api.knowledge_version import KnowledgeVersionListAPI, KnowledgeVersionPageAPI, \
    KnowledgeVersionOperateAPI
from knowledge.models import Knowledge
from tools.serializers.tool_version import ToolWorkflowVersionSerializer
from tools.views import get_tool_operation_object


def get_knowledge_operation_object(knowledge_id):
    knowledge_model = QuerySet(model=Knowledge).filter(id=knowledge_id).first()
    if knowledge_model is not None:
        return {
            'name': knowledge_model.name
        }
    return {}


class ToolWorkflowVersionView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_("Get the tool version list"),
        summary=_("Get the tool version list"),
        operation_id=_("Get the tool version list"),  # type: ignore
        parameters=KnowledgeVersionListAPI.get_parameters(),
        responses=KnowledgeVersionListAPI.get_response(),
        tags=[_('Tool/Version')]  # type: ignore
    )
    @has_permissions(PermissionConstants.TOOL_READ.get_workspace_tool_permission(),
                     PermissionConstants.TOOL_READ.get_workspace_permission_workspace_manage_role(),
                     ViewPermission([RoleConstants.USER.get_workspace_role()],
                                    [PermissionConstants.TOOL.get_workspace_tool_permission()],
                                    CompareConstants.AND),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def get(self, request: Request, workspace_id, tool_id: str):
        return result.success(
            ToolWorkflowVersionSerializer.Query(
                data={'workspace_id': workspace_id}).list(
                {'name': request.query_params.get("name"), 'tool_id': tool_id}))

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_("Get the list of tool versions by page"),
            summary=_("Get the list of tool versions by page"),
            operation_id=_("Get the list of tool versions by page"),  # type: ignore
            parameters=KnowledgeVersionPageAPI.get_parameters(),
            responses=KnowledgeVersionPageAPI.get_response(),
            tags=[_('Tool/Version')]  # type: ignore
        )
        @has_permissions(PermissionConstants.TOOL_READ.get_workspace_tool_permission(),
                         PermissionConstants.TOOL_READ.get_workspace_permission_workspace_manage_role(),
                         ViewPermission([RoleConstants.USER.get_workspace_role()],
                                        [PermissionConstants.TOOL.get_workspace_tool_permission()],
                                        CompareConstants.AND),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        def get(self, request: Request, workspace_id: str, tool_id: str, current_page: int, page_size: int):
            return result.success(
                ToolWorkflowVersionSerializer.Query(
                    data={'workspace_id': workspace_id}).page(
                    {'name': request.query_params.get("name"), 'tool_id': tool_id},
                    current_page, page_size))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_("Get tool version details"),
            summary=_("Get tool version details"),
            operation_id=_("Get tool version details"),  # type: ignore
            parameters=KnowledgeVersionOperateAPI.get_parameters(),
            responses=KnowledgeVersionOperateAPI.get_response(),
            tags=[_('Tool/Version')]  # type: ignore
        )
        @has_permissions(PermissionConstants.TOOL_READ.get_workspace_tool_permission(),
                         PermissionConstants.TOOL_READ.get_workspace_permission_workspace_manage_role(),
                         ViewPermission([RoleConstants.USER.get_workspace_role()],
                                        [PermissionConstants.TOOL.get_workspace_tool_permission()],
                                        CompareConstants.AND),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        def get(self, request: Request, workspace_id: str, tool_id: str, tool_version_id: str):
            return result.success(
                ToolWorkflowVersionSerializer.Operate(
                    data={'user_id': request.user, 'workspace_id': workspace_id,
                          'tool_id': tool_id, 'tool_version_id': tool_version_id}).one())

        @extend_schema(
            methods=['PUT'],
            description=_("Modify tool version information"),
            summary=_("Modify tool version information"),
            operation_id=_("Modify tool version information"),  # type: ignore
            parameters=KnowledgeVersionOperateAPI.get_parameters(),
            request=None,
            responses=KnowledgeVersionOperateAPI.get_response(),
            tags=[_('Tool/Version')]  # type: ignore
        )
        @has_permissions(PermissionConstants.TOOL_EDIT.get_workspace_tool_permission(),
                         PermissionConstants.TOOL_EDIT.get_workspace_permission_workspace_manage_role(),
                         ViewPermission([RoleConstants.USER.get_workspace_role()],
                                        [PermissionConstants.TOOL.get_workspace_tool_permission()],
                                        CompareConstants.AND),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        @log(menu='Tool', operate="Modify tool version information",
             get_operation_object=lambda r, k: get_tool_operation_object(k.get('tool_id')),
             )
        def put(self, request: Request, workspace_id: str, tool_id: str, tool_version_id: str):
            return result.success(
                ToolWorkflowVersionSerializer.Operate(
                    data={'tool_id': tool_id, 'workspace_id': workspace_id,
                          'tool_version_id': tool_version_id,
                          'user_id': request.user.id}).edit(
                    request.data))
