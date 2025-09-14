from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants, ViewPermission, CompareConstants
from common.log.log import log
from common.result import result
from tools.api.tool import ToolCreateAPI, ToolEditAPI, ToolReadAPI, ToolDeleteAPI, ToolTreeReadAPI, ToolDebugApi, \
    ToolExportAPI, ToolImportAPI, ToolPageAPI, PylintAPI, EditIconAPI, GetInternalToolAPI, AddInternalToolAPI
from tools.models import ToolScope, Tool
from tools.serializers.tool import ToolSerializer, ToolTreeSerializer


def get_tool_operation_object(tool_id):
    tool_model = QuerySet(model=Tool).filter(id=tool_id).first()
    if tool_model is not None:
        return {
            "name": tool_model.name
        }
    return {}


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
    @has_permissions(
        PermissionConstants.TOOL_CREATE.get_workspace_permission(),
        PermissionConstants.TOOL_CREATE.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(), RoleConstants.USER.get_workspace_role()
    )
    @log(
        menu="Tool", operate="Create tool",
        get_operation_object=lambda r, k: r.data.get('name'),
    )
    def post(self, request: Request, workspace_id: str):
        return result.success(ToolSerializer.Create(
            data={'user_id': request.user.id, 'workspace_id': workspace_id}
        ).insert({**request.data, 'scope': ToolScope.WORKSPACE}))

    @extend_schema(
        methods=['GET'],
        description=_('Get tool by folder'),
        summary=_('Get tool by folder'),
        operation_id=_('Get tool by folder'),  # type: ignore
        parameters=ToolTreeReadAPI.get_parameters(),
        responses=ToolTreeReadAPI.get_response(),
        tags=[_('Tool')]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.TOOL_READ.get_workspace_permission(),
        PermissionConstants.TOOL_READ.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(), RoleConstants.USER.get_workspace_role()
    )
    def get(self, request: Request, workspace_id: str):
        return result.success(ToolTreeSerializer.Query(
            data={
                'workspace_id': workspace_id,
                'folder_id': request.query_params.get('folder_id'),
                'name': request.query_params.get('name'),
                'scope': request.query_params.get('scope', ToolScope.WORKSPACE),
                'tool_type': request.query_params.get('tool_type'),
                'user_id': request.user.id,
                'create_user': request.query_params.get('create_user'),
            }
        ).get_tools())

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
        @has_permissions(
            PermissionConstants.TOOL_DEBUG.get_workspace_permission(),
            PermissionConstants.TOOL_DEBUG.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(), RoleConstants.USER.get_workspace_role()
        )
        def post(self, request: Request, workspace_id: str):
            return result.success(ToolSerializer.Debug(
                data={'workspace_id': workspace_id, 'user_id': request.user.id}
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
        @has_permissions(
            PermissionConstants.TOOL_EDIT.get_workspace_tool_permission(),
            PermissionConstants.TOOL_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.TOOL.get_workspace_tool_permission()],
                           CompareConstants.AND),
        )
        @log(
            menu='Tool', operate='Update tool',
            get_operation_object=lambda r, k: get_tool_operation_object(k.get('tool_id')),

        )
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
        @has_permissions(
            PermissionConstants.TOOL_READ.get_workspace_tool_permission(),
            PermissionConstants.TOOL_READ.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            PermissionConstants.APPLICATION_READ.get_workspace_permission(),
            PermissionConstants.APPLICATION_READ.get_workspace_permission_workspace_manage_role(),
            RoleConstants.USER.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.TOOL.get_workspace_tool_permission()],
                           CompareConstants.AND),
        )
        @log(menu='Tool', operate='Get tool')
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
        @has_permissions(
            PermissionConstants.TOOL_DELETE.get_workspace_tool_permission(),
            PermissionConstants.TOOL_DELETE.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.TOOL.get_workspace_tool_permission()],
                           CompareConstants.AND),
        )
        @log(
            menu='Tool', operate="Delete tool",
            get_operation_object=lambda r, k: get_tool_operation_object(k.get('tool_id')),

        )
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
        @has_permissions(
            PermissionConstants.TOOL_READ.get_workspace_permission(),
            PermissionConstants.TOOL_READ.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(), RoleConstants.USER.get_workspace_role()
        )
        @log(menu='Tool', operate='Get tool list')
        def get(self, request: Request, workspace_id: str, current_page: int, page_size: int):
            return result.success(ToolTreeSerializer.Query(
                data={
                    'workspace_id': workspace_id,
                    'folder_id': request.query_params.get('folder_id'),
                    'name': request.query_params.get('name'),
                    'scope': request.query_params.get('scope'),
                    'tool_type': request.query_params.get('tool_type'),
                    'user_id': request.user.id,
                    'create_user': request.query_params.get('create_user'),
                }
            ).page_tool_with_folders(current_page, page_size))

    class Query(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Get tool list '),
            summary=_('Get tool list'),
            operation_id=_('Get tool list'),  # type: ignore
            parameters=ToolReadAPI.get_parameters(),
            responses=ToolReadAPI.get_response(),
            tags=[_('Tool')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.TOOL_READ.get_workspace_permission(),
            PermissionConstants.TOOL_READ.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(), RoleConstants.USER.get_workspace_role()
        )
        @log(menu='Tool', operate='Get tool list')
        def get(self, request: Request, workspace_id: str):
            return result.success(ToolSerializer.Query(
                data={
                    'workspace_id': workspace_id,
                    'folder_id': request.query_params.get('folder_id'),
                    'name': request.query_params.get('name'),
                    'scope': request.query_params.get('scope'),
                    'tool_type': request.query_params.get('tool_type'),
                    'user_id': request.user.id,
                    'create_user': request.query_params.get('create_user'),
                }
            ).get_tools())

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
        @has_permissions(
            PermissionConstants.TOOL_IMPORT.get_workspace_permission(),
            PermissionConstants.TOOL_IMPORT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(), RoleConstants.USER.get_workspace_role()
        )
        @log(menu='Tool', operate='Import tool', )
        def post(self, request: Request, workspace_id: str):
            return result.success(ToolSerializer.Import(
                data={
                    'workspace_id': workspace_id,
                    'file': request.FILES.get('file'),
                    'user_id': request.user.id,
                    'folder_id': request.data.get('folder_id')
                }
            ).import_(ToolScope.WORKSPACE))

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
        @has_permissions(
            PermissionConstants.TOOL_EXPORT.get_workspace_tool_permission(),
            PermissionConstants.TOOL_EXPORT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.TOOL.get_workspace_tool_permission()],
                           CompareConstants.AND),
        )
        @log(
            menu='Tool', operate="Export tool",
            get_operation_object=lambda r, k: get_tool_operation_object(k.get('tool_id')),
        )
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
        @has_permissions(
            PermissionConstants.TOOL_READ.get_workspace_permission(),
            PermissionConstants.TOOL_READ.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            RoleConstants.USER.get_workspace_role()
        )
        def post(self, request: Request, workspace_id: str):
            return result.success(ToolSerializer.Pylint(
                data={'workspace_id': workspace_id}
            ).run(request.data))

    class EditIcon(APIView):
        authentication_classes = [TokenAuth]
        parser_classes = [MultiPartParser]

        @extend_schema(
            methods=['PUT'],
            summary=_('Edit tool icon'),
            operation_id=_('Edit tool icon'),  # type: ignore
            description=_('Edit tool icon'),
            request=EditIconAPI.get_request(),
            responses=EditIconAPI.get_response(),
            parameters=EditIconAPI.get_parameters(),
            tags=[_('Tool')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.TOOL_EDIT.get_workspace_tool_permission(),
            PermissionConstants.TOOL_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.TOOL.get_workspace_tool_permission()],
                           CompareConstants.AND),
        )
        def put(self, request: Request, tool_id: str, workspace_id: str):
            return result.success(ToolSerializer.IconOperate(data={
                'id': tool_id,
                'workspace_id': workspace_id,
                'user_id': request.user.id,
                'image': request.FILES.get('file')
            }).edit(request.data))

    class InternalTool(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_("Get internal tool"),
            summary=_("Get internal tool"),
            operation_id=_("Get internal tool"),  # type: ignore
            parameters=GetInternalToolAPI.get_parameters(),
            responses=GetInternalToolAPI.get_response(),
            tags=[_("Tool")]  # type: ignore
        )
        def get(self, request: Request):
            return result.success(ToolSerializer.InternalTool(data={
                'user_id': request.user.id,
                'name': request.query_params.get('name', ''),
            }).get_internal_tools())

    class AddInternalTool(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['POST'],
            description=_("Add internal tool"),
            summary=_("Add internal tool"),
            operation_id=_("Add internal tool"),  # type: ignore
            parameters=AddInternalToolAPI.get_parameters(),
            request=AddInternalToolAPI.get_request(),
            responses=AddInternalToolAPI.get_response(),
            tags=[_("Tool")]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.TOOL_CREATE.get_workspace_permission(),
            PermissionConstants.TOOL_CREATE.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            RoleConstants.USER.get_workspace_role(),
        )
        @log(
            menu='Tool', operate="Add internal tool",
            get_operation_object=lambda r, k: get_tool_operation_object(k.get('tool_id')),
        )
        def post(self, request: Request, tool_id: str, workspace_id: str):
            return result.success(ToolSerializer.AddInternalTool(data={
                'tool_id': tool_id,
                'user_id': request.user.id,
                'workspace_id': workspace_id
            }).add(request.data))

    class StoreTool(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_("Get Appstore tools"),
            summary=_("Get Appstore tools"),
            operation_id=_("Get Appstore tools"),  # type: ignore
            responses=GetInternalToolAPI.get_response(),
            tags=[_("Tool")]  # type: ignore
        )
        def get(self, request: Request):
            return result.success(ToolSerializer.StoreTool(data={
                'user_id': request.user.id,
                'name': request.query_params.get('name', ''),
            }).get_appstore_tools())

    class AddStoreTool(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['POST'],
            description=_("Add Appstore tool"),
            summary=_("Add Appstore tool"),
            operation_id=_("Add Appstore tool"),  # type: ignore
            parameters=AddInternalToolAPI.get_parameters(),
            request=AddInternalToolAPI.get_request(),
            responses=AddInternalToolAPI.get_response(),
            tags=[_("Tool")]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.TOOL_CREATE.get_workspace_permission(),
            PermissionConstants.TOOL_CREATE.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            RoleConstants.USER.get_workspace_role(),
        )
        @log(
            menu='Tool', operate="Add Appstore tool",
            get_operation_object=lambda r, k: get_tool_operation_object(k.get('tool_id')),
        )
        def post(self, request: Request, tool_id: str, workspace_id: str):
            return result.success(ToolSerializer.AddStoreTool(data={
                'tool_id': tool_id,
                'user_id': request.user.id,
                'workspace_id': workspace_id,
            }).add(request.data))

    class UpdateStoreTool(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['POST'],
            description=_("Update Appstore tool"),
            summary=_("Update Appstore tool"),
            operation_id=_("Update Appstore tool"),  # type: ignore
            parameters=AddInternalToolAPI.get_parameters(),
            request=AddInternalToolAPI.get_request(),
            responses=AddInternalToolAPI.get_response(),
            tags=[_("Tool")]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.TOOL_CREATE.get_workspace_permission(),
            PermissionConstants.TOOL_CREATE.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            RoleConstants.USER.get_workspace_role(),
        )
        @log(
            menu='Tool', operate="Update Appstore tool",
            get_operation_object=lambda r, k: get_tool_operation_object(k.get('tool_id')),
        )
        def post(self, request: Request, tool_id: str, workspace_id: str):
            return result.success(ToolSerializer.UpdateStoreTool(data={
                'tool_id': tool_id,
                'user_id': request.user.id,
                'workspace_id': workspace_id,
                'download_url': request.data.get('download_url'),
                'download_callback_url': request.data.get('download_callback_url'),
                'icon': request.data.get('icon'),
                'versions': request.data.get('versions'),
            }).update_tool(request.data))