# coding=utf-8

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions, get_is_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants, ViewPermission, CompareConstants
from common.log.log import log
from common.result import result, DefaultResultSerializer
from knowledge.api.knowledge_workflow import KnowledgeWorkflowApi
from knowledge.serializers.knowledge_workflow import KnowledgeWorkflowSerializer
from tools.api.tool_workflow import ToolWorkflowApi, ToolWorkflowExportApi, ToolWorkflowImportApi
from tools.serializers.tool_workflow import ToolWorkflowSerializer
from tools.views import get_tool_operation_object


class ToolWorkflowView(APIView):
    authentication_classes = [TokenAuth]

    class Publish(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_("Publishing an tool"),
            summary=_("Publishing an tool"),
            operation_id=_("Publishing an tool"),  # type: ignore
            parameters=ToolWorkflowApi.get_parameters(),
            request=None,
            responses=DefaultResultSerializer,
            tags=[_('Tool')]  # type: ignore
        )
        @has_permissions(PermissionConstants.TOOL_EDIT.get_workspace_tool_permission(),
                         PermissionConstants.TOOL_EDIT.get_workspace_permission_workspace_manage_role(),
                         ViewPermission([RoleConstants.USER.get_workspace_role()],
                                        [PermissionConstants.TOOL.get_workspace_knowledge_permission()],
                                        CompareConstants.AND),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        @log(menu='Tool', operate='Publishing an tool',
             get_operation_object=lambda r, k: get_tool_operation_object(k.get('tool_id')))
        def put(self, request: Request, workspace_id: str, tool_id: str):
            return result.success(
                ToolWorkflowSerializer.Operate(
                    data={'tool_id': tool_id, 'user_id': request.user.id,
                          'workspace_id': workspace_id, }).publish())

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_('Edit tool workflow'),
            summary=_('Edit tool workflow'),
            operation_id=_('Edit tool workflow'),  # type: ignore
            parameters=ToolWorkflowApi.get_parameters(),
            request=ToolWorkflowApi.get_request(),
            responses=ToolWorkflowApi.get_response(),
            tags=[_('Tool')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.TOOL_EDIT.get_workspace_tool_permission(),
            PermissionConstants.TOOL_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission(
                [RoleConstants.USER.get_workspace_role()],
                [PermissionConstants.TOOL.get_workspace_tool_permission()],
                CompareConstants.AND
            )
        )
        @log(
            menu='Tool', operate="Modify tool workflow",
            get_operation_object=lambda r, k: get_tool_operation_object(k.get('tool_id')),
        )
        def put(self, request: Request, workspace_id: str, tool_id: str):
            return result.success(ToolWorkflowSerializer.Operate(
                data={'user_id': request.user.id, 'workspace_id': workspace_id, 'tool_id': tool_id}
            ).edit(request.data))

        @extend_schema(
            methods=['GET'],
            description=_('Get tool workflow'),
            summary=_('Get tool workflow'),
            operation_id=_('Get tool workflow'),  # type: ignore
            parameters=KnowledgeWorkflowApi.get_parameters(),
            responses=KnowledgeWorkflowApi.get_response(),
            tags=[_('Tool')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.TOOL_READ.get_workspace_tool_permission(),
            PermissionConstants.TOOL_READ.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission(
                [RoleConstants.USER.get_workspace_role()],
                [PermissionConstants.TOOL.get_workspace_tool_permission()],
                CompareConstants.AND
            ),
        )
        def get(self, request: Request, workspace_id: str, tool_id: str):
            return result.success(ToolWorkflowSerializer.Operate(
                data={'user_id': request.user.id, 'workspace_id': workspace_id, 'tool_id': tool_id}
            ).one())


class KnowledgeWorkflowVersionView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_('Get tool workflow version list'),
        summary=_('Get tool workflow version list'),
        operation_id=_('Get tool workflow version list'),  # type: ignore
        parameters=ToolWorkflowApi.get_parameters(),
        responses=ToolWorkflowApi.get_response(),
        tags=[_('Tool')]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.TOOL_READ.get_workspace_tool_permission(),
        PermissionConstants.TOOL_READ.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [PermissionConstants.TOOL.get_workspace_tool_permission()],
            CompareConstants.AND
        ),
    )
    def get(self, request: Request, workspace_id: str, tool_id: str):
        return result.success(KnowledgeWorkflowSerializer.Operate(
            data={'user_id': request.user.id, 'workspace_id': workspace_id, 'tool_id': tool_id}
        ).one())


class ToolWorkflowDebugView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('tool workflow debug'),
        summary=_('tool workflow debug'),
        operation_id=_('tool workflow debug'),  # type: ignore
        parameters=ToolWorkflowApi.get_parameters(),
        responses=ToolWorkflowApi.get_response(),
        tags=[_('Tool')]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.TOOL_EDIT.get_workspace_tool_permission(),
        PermissionConstants.TOOL_EDIT.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [PermissionConstants.TOOL.get_workspace_tool_permission()],
            CompareConstants.AND
        ),
    )
    def post(self, request: Request, workspace_id: str, tool_id: str):
        return ToolWorkflowSerializer.Operate(
            data={'workspace_id': workspace_id, 'tool_id': tool_id, 'user_id': request.user.id}).debug(
            request.data,
            request.user,
            True)
