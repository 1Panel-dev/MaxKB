# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： workspace_user_resource_permission.py
    @date：2025/4/28 16:38
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
from common.constants.permission_constants import RoleConstants, Permission, Group, Operate, ViewPermission, \
    CompareConstants
from common.log.log import log
from system_manage.api.user_resource_permission import UserResourcePermissionAPI, EditUserResourcePermissionAPI, \
    ResourceUserPermissionAPI, ResourceUserPermissionPageAPI, ResourceUserPermissionEditAPI, \
    UserResourcePermissionPageAPI
from system_manage.serializers.user_resource_permission import UserResourcePermissionSerializer, \
    ResourceUserPermissionSerializer
from users.models import User


def get_user_operation_object(user_id):
    user_model = QuerySet(model=User).filter(id=user_id).first()
    if user_model is not None:
        return {
            "name": user_model.username
        }
    return {}


class WorkSpaceUserResourcePermissionView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_('Obtain resource authorization list'),
        operation_id=_('Obtain resource authorization list'),  # type: ignore
        parameters=UserResourcePermissionAPI.get_parameters(),
        responses=UserResourcePermissionAPI.get_response(),
        tags=[_('Resources authorization')]  # type: ignore
    )
    @has_permissions(
        lambda r, kwargs: Permission(group=Group(kwargs.get('resource') + '_WORKSPACE_USER_RESOURCE_PERMISSION'),
                                     operate=Operate.READ),
        RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def get(self, request: Request, workspace_id: str, user_id: str, resource: str):
        return result.success(UserResourcePermissionSerializer(
            data={'workspace_id': workspace_id, 'user_id': user_id, 'auth_target_type': resource}
        ).list({'name': request.query_params.get('name'),
                'permission': request.query_params.getlist('permission[]')}, request.user))

    @extend_schema(
        methods=['PUT'],
        description=_('Modify the resource authorization list'),
        operation_id=_('Modify the resource authorization list'),  # type: ignore
        parameters=EditUserResourcePermissionAPI.get_parameters(),
        request=EditUserResourcePermissionAPI.get_request(),
        responses=EditUserResourcePermissionAPI.get_response(),
        tags=[_('Resources authorization')]  # type: ignore
    )
    @log(menu='System', operate='Modify the resource authorization list',
         get_operation_object=lambda r, k: get_user_operation_object(k.get('user_id'))
         )
    @has_permissions(
        lambda r, kwargs: Permission(group=Group(kwargs.get('resource') + '_WORKSPACE_USER_RESOURCE_PERMISSION'),
                                     operate=Operate.EDIT),
        RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def put(self, request: Request, workspace_id: str, user_id: str, resource: str):
        return result.success(UserResourcePermissionSerializer(
            data={'workspace_id': workspace_id, 'user_id': user_id, 'auth_target_type': resource}
        ).edit(request.data, request.user))

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Obtain resource authorization list by page'),
            summary=_('Obtain resource authorization list by page'),
            operation_id=_('Obtain resource authorization list by page'),  # type: ignore
            request=None,
            parameters=UserResourcePermissionPageAPI.get_parameters(),
            responses=UserResourcePermissionPageAPI.get_response(),
            tags=[_('Resources authorization')]  # type: ignore
        )
        @has_permissions(
            lambda r, kwargs: Permission(group=Group(kwargs.get('resource') + '_WORKSPACE_USER_RESOURCE_PERMISSION'),
                                         operate=Operate.READ),
            RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        def get(self, request: Request, workspace_id: str, user_id: str, resource: str, current_page: str,
                page_size: str):
            return result.success(UserResourcePermissionSerializer(
                data={'workspace_id': workspace_id, 'user_id': user_id, 'auth_target_type': resource}
                ).page({'name': request.query_params.get('name'),
                        'permission': request.query_params.getlist('permission[]')}, current_page, page_size, request.user))


class WorkspaceResourceUserPermissionView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_('Get user authorization status of resource'),
        summary=_('Get user authorization status of resource'),
        operation_id=_('Get user authorization status of resource'),  # type: ignore
        parameters=ResourceUserPermissionAPI.get_parameters(),
        responses=ResourceUserPermissionAPI.get_response(),
        tags=[_('Resources authorization')]  # type: ignore
    )
    @has_permissions(
        lambda r, kwargs: Permission(group=Group(kwargs.get('resource')),
                                     operate=Operate.AUTH,
                                     resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}:ROLE/WORKSPACE_MANAGE"),
        lambda r, kwargs: Permission(group=Group(kwargs.get('resource')),
                                     operate=Operate.AUTH,
                                     resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}/{kwargs.get('resource')}/{kwargs.get('target')}"),
        ViewPermission([RoleConstants.USER.get_workspace_role()],
                       [lambda r, kwargs: Permission(group=Group(kwargs.get('resource')),
                                                     operate=Operate.SELF,
                                                     resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}/{kwargs.get('resource')}/{kwargs.get('target')}")],
                       CompareConstants.AND),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def get(self, request: Request, workspace_id: str, target: str, resource: str):
        return result.success(ResourceUserPermissionSerializer(
            data={'workspace_id': workspace_id, "target": target, 'auth_target_type': resource,
                  }).list(
            {'username': request.query_params.get("username"), 'nick_name': request.query_params.get("nick_name"),
             'permission': request.query_params.getlist("permission[]")
             }))

    @extend_schema(
        methods=['PUT'],
        description=_('Edit user authorization status of resource'),
        summary=_('Edit user authorization status of resource'),
        operation_id=_('Edit user authorization status of resource'),  # type: ignore
        parameters=ResourceUserPermissionEditAPI.get_parameters(),
        request=ResourceUserPermissionEditAPI.get_request(),
        responses=ResourceUserPermissionEditAPI.get_response(),
        tags=[_('Resources authorization')]  # type: ignore
    )
    @log(menu='System', operate='Edit user authorization status of resource',
         get_operation_object=lambda r, k: get_user_operation_object(k.get('user_id'))
         )
    @has_permissions(
        lambda r, kwargs: Permission(group=Group(kwargs.get('resource')),
                                     operate=Operate.AUTH,
                                     resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}:ROLE/WORKSPACE_MANAGE"),
        lambda r, kwargs: Permission(group=Group(kwargs.get('resource')),
                                     operate=Operate.AUTH,
                                     resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}/{kwargs.get('resource')}/{kwargs.get('target')}"),
        ViewPermission([RoleConstants.USER.get_workspace_role()],
                       [lambda r, kwargs: Permission(group=Group(kwargs.get('resource')),
                                                     operate=Operate.SELF,
                                                     resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}/{kwargs.get('resource')}/{kwargs.get('target')}")],
                       CompareConstants.AND),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def put(self, request: Request, workspace_id: str, target: str, resource: str):
        return result.success(ResourceUserPermissionSerializer(
            data={'workspace_id': workspace_id, "target": target, 'auth_target_type': resource, })
                              .edit(instance=request.data, current_user_id=request.user.id))

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Get user authorization status of resource by page'),
            summary=_('Get user authorization status of resource by page'),
            operation_id=_('Get user authorization status of resource by page'),  # type: ignore
            parameters=ResourceUserPermissionPageAPI.get_parameters(),
            responses=ResourceUserPermissionPageAPI.get_response(),
            tags=[_('Resources authorization')]  # type: ignore
        )
        @has_permissions(
            lambda r, kwargs: Permission(group=Group(kwargs.get('resource')),
                                         operate=Operate.AUTH,
                                         resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}:ROLE/WORKSPACE_MANAGE"),
        lambda r, kwargs: Permission(group=Group(kwargs.get('resource')),
                                     operate=Operate.AUTH,
                                     resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}/{kwargs.get('resource')}/{kwargs.get('target')}"),
             ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [lambda r, kwargs: Permission(group=Group(kwargs.get('resource')),
                                     operate=Operate.SELF,
                                     resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}/{kwargs.get('resource')}/{kwargs.get('target')}")],
                           CompareConstants.AND),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        def get(self, request: Request, workspace_id: str, target: str, resource: str, current_page: int,
                page_size: int):
            return result.success(ResourceUserPermissionSerializer(
                data={'workspace_id': workspace_id, "target": target, 'auth_target_type': resource, }
            ).page({'username': request.query_params.get("username"),
                    'nick_name': request.query_params.get("nick_name"),
                    'permission': request.query_params.getlist("permission[]")}, current_page, page_size,
                   ))
