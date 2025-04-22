from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants
from common.result import result
from tools.api.tool import ToolCreateAPI, ToolEditAPI, ToolReadAPI, ToolDeleteAPI, ToolTreeReadAPI, ToolDebugApi, \
    ToolExportAPI, ToolImportAPI, ToolPageAPI
from tools.serializers.tool import ToolSerializer, ToolTreeSerializer


class ToolView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Create tool'),
        operation_id=_('Create tool'),
        parameters=ToolCreateAPI.get_parameters(),
        request=ToolCreateAPI.get_request(),
        responses=ToolCreateAPI.get_response(),
        tags=[_('Tool')]
    )
    @has_permissions(PermissionConstants.TOOL_CREATE.get_workspace_permission())
    def post(self, request: Request, workspace_id: str):
        return result.success(ToolSerializer.Create(
            data={'user_id': request.user.id, 'workspace_id': workspace_id}
        ).insert(request.data))

    @extend_schema(
        methods=['GET'],
        description=_('Get tool by module'),
        operation_id=_('Get tool by module'),
        parameters=ToolTreeReadAPI.get_parameters(),
        responses=ToolTreeReadAPI.get_response(),
        tags=[_('Tool')]
    )
    @has_permissions(PermissionConstants.TOOL_READ.get_workspace_permission())
    def get(self, request: Request, workspace_id: str):
        return result.success(ToolTreeSerializer(
            data={'workspace_id': workspace_id}
        ).get_tools(request.query_params.get('module_id')))

    class Debug(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['POST'],
            description=_('Debug Tool'),
            operation_id=_('Debug Tool'),
            request=ToolDebugApi.get_request(),
            responses=ToolDebugApi.get_response(),
            tags=[_('Tool')]
        )
        @has_permissions(PermissionConstants.TOOL_DEBUG.get_workspace_permission())
        def post(self, request: Request, workspace_id: str, tool_id: str):
            return result.success(ToolSerializer.Debug(
                data={'tool_id': tool_id, 'workspace_id': workspace_id}
            ).debug(request.data))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_('Update tool'),
            operation_id=_('Update tool'),
            parameters=ToolEditAPI.get_parameters(),
            request=ToolEditAPI.get_request(),
            responses=ToolEditAPI.get_response(),
            tags=[_('Tool')]
        )
        @has_permissions(PermissionConstants.TOOL_EDIT.get_workspace_permission())
        def put(self, request: Request, workspace_id: str, tool_id: str):
            return result.success(ToolSerializer.Operate(
                data={'id': tool_id, 'workspace_id': workspace_id}
            ).edit(request.data))

        @extend_schema(
            methods=['GET'],
            description=_('Get tool'),
            operation_id=_('Get tool'),
            parameters=ToolReadAPI.get_parameters(),
            responses=ToolReadAPI.get_response(),
            tags=[_('Tool')]
        )
        @has_permissions(PermissionConstants.TOOL_READ.get_workspace_permission())
        def get(self, request: Request, workspace_id: str, tool_id: str):
            return result.success(ToolSerializer.Operate(
                data={'id': tool_id, 'workspace_id': workspace_id}
            ).one())

        @extend_schema(
            methods=['DELETE'],
            description=_('Delete tool'),
            operation_id=_('Delete tool'),
            parameters=ToolDeleteAPI.get_parameters(),
            responses=ToolDeleteAPI.get_response(),
            tags=[_('Tool')]
        )
        @has_permissions(PermissionConstants.TOOL_DELETE.get_workspace_permission())
        def delete(self, request: Request, workspace_id: str, tool_id: str):
            return result.success(ToolSerializer.Operate(
                data={'id': tool_id, 'workspace_id': workspace_id}
            ).delete())

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Get tool list by pagination'),
            operation_id=_('Get tool list by pagination'),
            parameters=ToolPageAPI.get_parameters(),
            responses=ToolPageAPI.get_response(),
            tags=[_('Tool')]
        )
        @has_permissions(PermissionConstants.TOOL_READ.get_workspace_permission())
        def get(self, request: Request, current_page: int, page_size: int):
            return result.success(
                ToolSerializer.Query(
                    data={
                        'name': request.query_params.get('name'),
                        'desc': request.query_params.get('desc'),
                        'function_type': request.query_params.get('function_type'),
                        'user_id': request.user.id,
                        'select_user_id': request.query_params.get('select_user_id')
                    }
                ).page(current_page, page_size))

    class Import(APIView):
        authentication_classes = [TokenAuth]
        parser_classes = [MultiPartParser]

        @extend_schema(
            methods=['POST'],
            description=_("Import tool"),
            operation_id=_("Import tool"),
            parameters=ToolImportAPI.get_parameters(),
            request=ToolImportAPI.get_request(),
            responses=ToolImportAPI.get_response(),
            tags=[_("Tool")]
        )
        @has_permissions(PermissionConstants.TOOL_IMPORT.get_workspace_permission())
        def post(self, request: Request, workspace_id: str):
            return result.success(ToolSerializer.Import(
                data={'workspace_id': workspace_id, 'file': request.FILES.get('file'), 'user_id': request.user.id}
            ).import_())

    class Export(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_("Export tool"),
            operation_id=_("Export tool"),
            parameters=ToolExportAPI.get_parameters(),
            responses=ToolExportAPI.get_response(),
            tags=[_("Tool")]
        )
        @has_permissions(PermissionConstants.TOOL_EXPORT.get_workspace_permission())
        def get(self, request: Request, tool_id: str, workspace_id: str):
            return ToolSerializer.Operate(
                data={'id': tool_id, 'workspace_id': workspace_id}
            ).export()
