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
    ToolExportAPI, ToolImportAPI, ToolPageAPI, PylintAPI
from tools.serializers.tool import ToolSerializer, ToolTreeSerializer


class ToolView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Create tool'),
        summary=_('Create tool'),
        operation_id=_('Create tool'),  # type: ignore
        parameters=ToolCreateAPI.get_parameters(),
        request=ToolCreateAPI.get_request(),
        responses=ToolCreateAPI.get_response(),
        tags=[_('Tool')]  # type: ignore
    )
    @has_permissions(PermissionConstants.TOOL_CREATE.get_workspace_permission())
    def post(self, request: Request, workspace_id: str):
        return result.success(ToolSerializer.Create(
            data={'user_id': request.user.id, 'workspace_id': workspace_id}
        ).insert(request.data))

    @extend_schema(
        methods=['GET'],
        description=_('Get tool by folder'),
        summary=_('Get tool by folder'),
        operation_id=_('Get tool by folder'),  # type: ignore
        parameters=ToolTreeReadAPI.get_parameters(),
        responses=ToolTreeReadAPI.get_response(),
        tags=[_('Tool')]  # type: ignore
    )
    @has_permissions(PermissionConstants.TOOL_READ.get_workspace_permission())
    def get(self, request: Request, workspace_id: str):
        return result.success(ToolTreeSerializer(
            data={'workspace_id': workspace_id}
        ).get_tools(request.query_params.get('folder_id')))

    class Debug(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['POST'],
            description=_('Debug Tool'),
            summary=_('Debug Tool'),
            operation_id=_('Debug Tool'),  # type: ignore
            request=ToolDebugApi.get_request(),
            responses=ToolDebugApi.get_response(),
            tags=[_('Tool')]  # type: ignore
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
            summary=_('Update tool'),
            operation_id=_('Update tool'),  # type: ignore
            parameters=ToolEditAPI.get_parameters(),
            request=ToolEditAPI.get_request(),
            responses=ToolEditAPI.get_response(),
            tags=[_('Tool')]  # type: ignore
        )
        @has_permissions(PermissionConstants.TOOL_EDIT.get_workspace_permission())
        def put(self, request: Request, workspace_id: str, tool_id: str):
            return result.success(ToolSerializer.Operate(
                data={'id': tool_id, 'workspace_id': workspace_id}
            ).edit(request.data))

        @extend_schema(
            methods=['GET'],
            description=_('Get tool'),
            summary=_('Get tool'),
            operation_id=_('Get tool'),  # type: ignore
            parameters=ToolReadAPI.get_parameters(),
            responses=ToolReadAPI.get_response(),
            tags=[_('Tool')]  # type: ignore
        )
        @has_permissions(PermissionConstants.TOOL_READ.get_workspace_permission())
        def get(self, request: Request, workspace_id: str, tool_id: str):
            return result.success(ToolSerializer.Operate(
                data={'id': tool_id, 'workspace_id': workspace_id}
            ).one())

        @extend_schema(
            methods=['DELETE'],
            description=_('Delete tool'),
            summary=_('Delete tool'),
            operation_id=_('Delete tool'),  # type: ignore
            parameters=ToolDeleteAPI.get_parameters(),
            responses=ToolDeleteAPI.get_response(),
            tags=[_('Tool')]  # type: ignore
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
            summary=_('Get tool list by pagination'),
            operation_id=_('Get tool list by pagination'),  # type: ignore
            parameters=ToolPageAPI.get_parameters(),
            responses=ToolPageAPI.get_response(),
            tags=[_('Tool')]  # type: ignore
        )
        @has_permissions(PermissionConstants.TOOL_READ.get_workspace_permission())
        def get(self, request: Request, workspace_id: str, current_page: int, page_size: int):
            return result.success(ToolTreeSerializer.Query(
                data={
                    'workspace_id': workspace_id,
                    'folder_id': request.query_params.get('folder_id'),
                    'name': request.query_params.get('name'),
                    'tool_type': request.query_params.get('tool_type'),
                }
            ).page_tool_with_folders(current_page, page_size))

    class Import(APIView):
        authentication_classes = [TokenAuth]
        parser_classes = [MultiPartParser]

        @extend_schema(
            methods=['POST'],
            description=_("Import tool"),
            summary=_("Import tool"),
            operation_id=_("Import tool"),  # type: ignore
            parameters=ToolImportAPI.get_parameters(),
            request=ToolImportAPI.get_request(),
            responses=ToolImportAPI.get_response(),
            tags=[_("Tool")]  # type: ignore
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
            summary=_("Export tool"),
            operation_id=_("Export tool"),  # type: ignore
            parameters=ToolExportAPI.get_parameters(),
            responses=ToolExportAPI.get_response(),
            tags=[_("Tool")]  # type: ignore
        )
        @has_permissions(PermissionConstants.TOOL_EXPORT.get_workspace_permission())
        def get(self, request: Request, tool_id: str, workspace_id: str):
            return ToolSerializer.Operate(
                data={'id': tool_id, 'workspace_id': workspace_id}
            ).export()

    class Pylint(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['POST'],
            summary=_('Check code'),
            operation_id=_('Check code'),  # type: ignore
            description=_('Check code'),
            request=PylintAPI.get_request(),
            responses=PylintAPI.get_response(),
            parameters=PylintAPI.get_parameters(),
            tags=[_('Tool')]  # type: ignore
        )
        @has_permissions(PermissionConstants.TOOL_EXPORT.get_workspace_permission())
        def post(self, request: Request, workspace_id: str):
            return result.success(ToolSerializer.Pylint(
                data={'workspace_id': workspace_id}
            ).run(request.data))
