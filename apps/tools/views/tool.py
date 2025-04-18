from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants
from common.result import result, DefaultResultSerializer
from tools.api.tool import ToolCreateAPI, ToolEditAPI, ToolReadAPI, ToolDeleteAPI, ToolTreeReadAPI
from tools.serializers.tool import ToolSerializer, ToolTreeSerializer


class ToolView(APIView):
    class Create(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['POST'],
                       description=_('Create tool'),
                       operation_id=_('Create tool'),
                       parameters=ToolCreateAPI.get_parameters(),
                       request=ToolCreateAPI.get_request(),
                       responses=ToolCreateAPI.get_response(),
                       tags=[_('Tool')])
        @has_permissions(PermissionConstants.TOOL_CREATE.get_workspace_permission())
        def post(self, request: Request, workspace_id: str):
            return result.success(ToolSerializer.Create(
                data={'user_id': request.user.id, 'workspace_id': workspace_id}
            ).insert(request.data))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['PUT'],
                       description=_('Update tool'),
                       operation_id=_('Update tool'),
                       parameters=ToolEditAPI.get_parameters(),
                       request=ToolEditAPI.get_request(),
                       responses=ToolEditAPI.get_response(),
                       tags=[_('Tool')])
        @has_permissions(PermissionConstants.TOOL_EDIT.get_workspace_permission())
        def put(self, request: Request, workspace_id: str, tool_id: str):
            return result.success(ToolSerializer.Operate(
                data={'id': tool_id, 'workspace_id': workspace_id}
            ).edit(request.data))

        @extend_schema(methods=['GET'],
                       description=_('Get tool'),
                       operation_id=_('Get tool'),
                       parameters=ToolReadAPI.get_parameters(),
                       responses=ToolReadAPI.get_response(),
                       tags=[_('Tool')])
        @has_permissions(PermissionConstants.TOOL_READ.get_workspace_permission())
        def get(self, request: Request, workspace_id: str, tool_id: str):
            return result.success(ToolSerializer.Operate(
                data={'id': tool_id, 'workspace_id': workspace_id}
            ).one())

        @extend_schema(methods=['DELETE'],
                       description=_('Delete tool'),
                       operation_id=_('Delete tool'),
                       parameters=ToolDeleteAPI.get_parameters(),
                       responses=DefaultResultSerializer,
                       tags=[_('Tool')])
        @has_permissions(PermissionConstants.TOOL_DELETE.get_workspace_permission())
        def delete(self, request: Request, workspace_id: str, tool_id: str):
            return result.success(ToolSerializer.Operate(
                data={'id': tool_id, 'workspace_id': workspace_id}
            ).delete())


class ToolTreeView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['GET'],
                   description=_('Get tool'),
                   operation_id=_('Get tool'),
                   parameters=ToolTreeReadAPI.get_parameters(),
                   responses=ToolTreeReadAPI.get_response(),
                   tags=[_('Tool')])
    @has_permissions(PermissionConstants.TOOL_READ.get_workspace_permission())
    def get(self, request: Request, workspace_id: str):
        return result.success(ToolTreeSerializer(
            data={'workspace_id': workspace_id}
        ).get_tools(request.query_params.get('module_id')))
