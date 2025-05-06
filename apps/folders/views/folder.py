from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import Permission, Group, Operate
from common.result import result
from folders.api.folder import FolderCreateAPI, FolderEditAPI, FolderReadAPI, FolderTreeReadAPI, FolderDeleteAPI
from folders.serializers.folder import FolderSerializer, FolderTreeSerializer


class FolderView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Create folder'),
        summary=_('Create folder'),
        operation_id=_('Create folder'),
        parameters=FolderCreateAPI.get_parameters(),
        request=FolderCreateAPI.get_request(),
        responses=FolderCreateAPI.get_response(),
        tags=[_('Folder')]
    )
    @has_permissions(lambda r, kwargs: Permission(group=Group(kwargs.get('source')), operate=Operate.CREATE,
                                                  resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}"))
    def post(self, request: Request, workspace_id: str, source: str):
        return result.success(FolderSerializer.Create(
            data={'user_id': request.user.id,
                  'source': source,
                  'workspace_id': workspace_id}
        ).insert(request.data))

    @extend_schema(
        methods=['GET'],
        description=_('Get folder tree'),
        summary=_('Get folder tree'),
        operation_id=_('Get folder tree'),
        parameters=FolderTreeReadAPI.get_parameters(),
        responses=FolderTreeReadAPI.get_response(),
        tags=[_('Folder')]
    )
    @has_permissions(lambda r, kwargs: Permission(group=Group(kwargs.get('source')), operate=Operate.READ,
                                                  resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}"))
    def get(self, request: Request, workspace_id: str, source: str):
        return result.success(FolderTreeSerializer(
            data={'workspace_id': workspace_id, 'source': source}
        ).get_folder_tree(request.query_params.get('name')))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_('Update folder'),
            summary=_('Update folder'),
            operation_id=_('Update folder'),
            parameters=FolderEditAPI.get_parameters(),
            request=FolderEditAPI.get_request(),
            responses=FolderEditAPI.get_response(),
            tags=[_('Folder')]
        )
        @has_permissions(lambda r, kwargs: Permission(group=Group(kwargs.get('source')), operate=Operate.EDIT,
                                                      resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}"))
        def put(self, request: Request, workspace_id: str, source: str, folder_id: str):
            return result.success(FolderSerializer.Operate(
                data={'id': folder_id, 'workspace_id': workspace_id, 'source': source}
            ).edit(request.data))

        @extend_schema(
            methods=['GET'],
            description=_('Get folder'),
            summary=_('Get folder'),
            operation_id=_('Get folder'),
            parameters=FolderReadAPI.get_parameters(),
            responses=FolderReadAPI.get_response(),
            tags=[_('Folder')]
        )
        @has_permissions(lambda r, kwargs: Permission(group=Group(kwargs.get('source')), operate=Operate.READ,
                                                      resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}"))
        def get(self, request: Request, workspace_id: str, source: str, folder_id: str):
            return result.success(FolderSerializer.Operate(
                data={'id': folder_id, 'workspace_id': workspace_id, 'source': source}
            ).one())

        @extend_schema(
            methods=['DELETE'],
            description=_('Delete folder'),
            summary=_('Delete folder'),
            operation_id=_('Delete folder'),
            parameters=FolderDeleteAPI.get_parameters(),
            responses=FolderDeleteAPI.get_response(),
            tags=[_('Folder')]
        )
        @has_permissions(lambda r, kwargs: Permission(group=Group(kwargs.get('source')), operate=Operate.DELETE,
                                                      resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}"))
        def delete(self, request: Request, workspace_id: str, source: str, folder_id: str):
            return result.success(FolderSerializer.Operate(
                data={'id': folder_id, 'workspace_id': workspace_id, 'source': source}
            ).delete())
