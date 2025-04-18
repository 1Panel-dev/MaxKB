from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import Permission, Group, Operate
from common.result import result
from modules.api.module import ModuleCreateAPI, ModuleEditAPI, ModuleReadAPI, ModuleTreeReadAPI, ModuleDeleteAPI
from modules.serializers.module import ModuleSerializer, ModuleTreeSerializer


class ModuleView(APIView):
    class Create(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['POST'],
                       description=_('Create module'),
                       operation_id=_('Create module'),
                       parameters=ModuleCreateAPI.get_parameters(),
                       request=ModuleCreateAPI.get_request(),
                       responses=ModuleCreateAPI.get_response(),
                       tags=[_('Module')])
        @has_permissions(lambda r, kwargs: Permission(group=Group(kwargs.get('source')), operate=Operate.CREATE,
                                                      resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}"))
        def post(self, request: Request, workspace_id: str, source: str):
            return result.success(ModuleSerializer.Create(
                data={'user_id': request.user.id,
                      'source': source,
                      'workspace_id': workspace_id}
            ).insert(request.data))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['PUT'],
                       description=_('Update module'),
                       operation_id=_('Update module'),
                       parameters=ModuleEditAPI.get_parameters(),
                       request=ModuleEditAPI.get_request(),
                       responses=ModuleEditAPI.get_response(),
                       tags=[_('Module')])
        @has_permissions(lambda r, kwargs: Permission(group=Group(kwargs.get('source')), operate=Operate.EDIT,
                                                      resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}"))
        def put(self, request: Request, workspace_id: str, source: str, module_id: str):
            return result.success(ModuleSerializer.Operate(
                data={'id': module_id, 'workspace_id': workspace_id, 'source': source}
            ).edit(request.data))

        @extend_schema(methods=['GET'],
                       description=_('Get module'),
                       operation_id=_('Get module'),
                       parameters=ModuleReadAPI.get_parameters(),
                       responses=ModuleReadAPI.get_response(),
                       tags=[_('Module')])
        @has_permissions(lambda r, kwargs: Permission(group=Group(kwargs.get('source')), operate=Operate.READ,
                                                      resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}"))
        def get(self, request: Request, workspace_id: str, source: str, module_id: str):
            return result.success(ModuleSerializer.Operate(
                data={'id': module_id, 'workspace_id': workspace_id, 'source': source}
            ).one())

        @extend_schema(methods=['DELETE'],
                       description=_('Delete module'),
                       operation_id=_('Delete module'),
                       parameters=ModuleDeleteAPI.get_parameters(),
                       tags=[_('Module')])
        @has_permissions(lambda r, kwargs: Permission(group=Group(kwargs.get('source')), operate=Operate.DELETE,
                                                      resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}"))
        def delete(self, request: Request, workspace_id: str, source: str, module_id: str):
            return result.success(ModuleSerializer.Operate(
                data={'id': module_id, 'workspace_id': workspace_id, 'source': source}
            ).delete())


class ModuleTreeView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['GET'],
                   description=_('Get module tree'),
                   operation_id=_('Get module tree'),
                   parameters=ModuleTreeReadAPI.get_parameters(),
                   responses=ModuleTreeReadAPI.get_response(),
                   tags=[_('Module')])
    @has_permissions(lambda r, kwargs: Permission(group=Group(kwargs.get('source')), operate=Operate.READ,
                                                  resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}"))
    def get(self, request: Request, workspace_id: str, source: str):
        return result.success(ModuleTreeSerializer(
            data={'workspace_id': workspace_id, 'source': source}
        ).get_module_tree())
