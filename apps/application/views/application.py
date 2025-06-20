# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application.py
    @date：2025/5/26 16:51
    @desc:
"""
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.views import APIView

from application.api.application_api import ApplicationCreateAPI, ApplicationQueryAPI, ApplicationImportAPI, \
    ApplicationExportAPI, ApplicationOperateAPI, ApplicationEditAPI
from application.models import Application
from application.serializers.application import ApplicationSerializer, Query, ApplicationOperateSerializer
from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants
from common.log.log import log


def get_application_operation_object(application_id):
    application_model = QuerySet(model=Application).filter(id=application_id).first()
    if application_model is not None:
        return {
            'name': application_model.name
        }
    return {}


class ApplicationAPI(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Create an application'),
        summary=_('Create an application'),
        operation_id=_('Create an application'),  # type: ignore
        parameters=ApplicationCreateAPI.get_parameters(),
        request=ApplicationCreateAPI.get_request(),
        responses=ApplicationCreateAPI.get_response(),
        tags=[_('Application')]  # type: ignore
    )
    @has_permissions(PermissionConstants.APPLICATION_CREATE.get_workspace_permission(),
                     RoleConstants.USER.get_workspace_role(),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    @log(menu='Application', operate='Create an application',
         get_operation_object=lambda r, k: {'name': r.data.get('name')},
         )
    def post(self, request: Request, workspace_id: str):
        return result.success(
            ApplicationSerializer(data={'workspace_id': workspace_id, 'user_id': request.user.id}).insert(request.data))

    @extend_schema(
        methods=['GET'],
        description=_('Get the application list'),
        summary=_('Get the application list'),
        operation_id=_('Get the application list'),  # type: ignore
        parameters=ApplicationQueryAPI.get_parameters(),
        responses=ApplicationQueryAPI.get_response(),
        tags=[_('Application')]  # type: ignore
    )
    @has_permissions(PermissionConstants.APPLICATION_READ.get_workspace_permission(),
                     RoleConstants.USER.get_workspace_role(),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def get(self, request: Request, workspace_id: str):
        return result.success(Query(data={'workspace_id': workspace_id, 'user_id': request.user.id}).list(request.data))

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Get the application list by page'),
            summary=_('Get the application list by page'),
            operation_id=_('Get the application list by page'),  # type: ignore
            parameters=ApplicationQueryAPI.get_parameters(),
            responses=ApplicationQueryAPI.get_page_response(),
            tags=[_('Application')]  # type: ignore
        )
        @has_permissions(PermissionConstants.APPLICATION_READ.get_workspace_permission(),
                         RoleConstants.USER.get_workspace_role(),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        def get(self, request: Request, workspace_id: str, current_page: int, page_size: int):
            return result.success(
                Query(data={'workspace_id': workspace_id, 'user_id': request.user.id}).page(current_page, page_size,
                                                                                            request.query_params))

    class Import(APIView):
        authentication_classes = [TokenAuth]
        parser_classes = [MultiPartParser]

        @extend_schema(
            methods=['POST'],
            description=_('Import Application'),
            summary=_('Import Application'),
            operation_id=_('Import Application'),  # type: ignore
            parameters=ApplicationImportAPI.get_parameters(),
            request=ApplicationImportAPI.get_request(),
            responses=result.DefaultResultSerializer,
            tags=[_('Application')]  # type: ignore
        )
        @has_permissions(PermissionConstants.APPLICATION_IMPORT.get_workspace_permission(),
                         RoleConstants.USER.get_workspace_role(),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        @log(menu='Application', operate="Import Application", )
        def post(self, request: Request, workspace_id: str):
            return result.success(ApplicationSerializer(
                data={'user_id': request.user.id, 'workspace_id': workspace_id,
                      }).import_({'file': request.FILES.get('file')}))

    class Export(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['POST'],
            description=_('Export application'),
            summary=_('Export application'),
            operation_id=_('Export application'),  # type: ignore
            parameters=ApplicationExportAPI.get_parameters(),
            request=None,
            responses=ApplicationExportAPI.get_response(),
            tags=[_('Application')]  # type: ignore
        )
        @has_permissions(PermissionConstants.APPLICATION_EXPORT.get_workspace_application_permission(),
                         PermissionConstants.APPLICATION_EXPORT.get_workspace_permission_workspace_manage_role(),
                         RoleConstants.USER.get_workspace_role(),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        @log(menu='Application', operate="Export Application",
             get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')),
             )
        def post(self, request: Request, workspace_id: str, application_id: str):
            return ApplicationOperateSerializer(
                data={'application_id': application_id,
                      'workspace_id': workspace_id,
                      'user_id': request.user.id}).export(request.data)

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['DELETE'],
            description=_('Deleting application'),
            summary=_('Deleting application'),
            operation_id=_('Deleting application'),  # type: ignore
            parameters=ApplicationOperateAPI.get_parameters(),
            responses=result.DefaultResultSerializer,
            tags=[_('Application')]  # type: ignore
        )
        @has_permissions(PermissionConstants.APPLICATION_DELETE.get_workspace_application_permission(),
                         PermissionConstants.APPLICATION_DELETE.get_workspace_permission_workspace_manage_role(),
                         RoleConstants.USER.get_workspace_role(),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        @log(menu='Application', operate='Deleting application',
             get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')),

             )
        def delete(self, request: Request, workspace_id: str, application_id: str):
            return result.success(ApplicationOperateSerializer(
                data={'application_id': application_id, 'user_id': request.user.id,
                      'workspace_id': workspace_id, }).delete(
                with_valid=True))

        @extend_schema(
            methods=['PUT'],
            description=_('Modify the application'),
            summary=_('Modify the application'),
            operation_id=_('Modify the application'),  # type: ignore
            parameters=ApplicationOperateAPI.get_parameters(),
            request=ApplicationEditAPI.get_request(),
            responses=ApplicationCreateAPI.get_response(),
            tags=[_('Application')]  # type: ignore
        )
        @has_permissions(PermissionConstants.APPLICATION_EDIT.get_workspace_application_permission(),
                         PermissionConstants.APPLICATION_EDIT.get_workspace_permission_workspace_manage_role(),
                         RoleConstants.USER.get_workspace_role(),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        @log(menu='Application', operate="Modify the application",
             get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')),
             )
        def put(self, request: Request, workspace_id: str, application_id: str):
            return result.success(
                ApplicationOperateSerializer(
                    data={'application_id': application_id, 'user_id': request.user.id,
                          'workspace_id': workspace_id, }).edit(
                    request.data))

        @extend_schema(
            methods=['GET'],
            description=_('Get application details'),
            summary=_('Get application details'),
            operation_id=_('Get application details'),  # type: ignore
            parameters=ApplicationOperateAPI.get_parameters(),
            request=ApplicationEditAPI.get_request(),
            responses=result.DefaultResultSerializer,
            tags=[_('Application')]  # type: ignore
        )
        @has_permissions(PermissionConstants.APPLICATION_READ.get_workspace_application_permission(),
                         PermissionConstants.APPLICATION_READ.get_workspace_permission_workspace_manage_role(),
                         RoleConstants.USER.get_workspace_role(),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        def get(self, request: Request, workspace_id: str, application_id: str):
            return result.success(ApplicationOperateSerializer(
                data={'application_id': application_id, 'user_id': request.user.id,
                      'workspace_id': workspace_id, }).one())

    class Publish(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_("Publishing an application"),
            summary=_("Publishing an application"),
            operation_id=_("Publishing an application"),  # type: ignore
            parameters=ApplicationOperateAPI.get_parameters(),
            request=ApplicationEditAPI.get_request(),
            responses=result.DefaultResultSerializer,
            tags=[_('Application')]  # type: ignore
        )
        @has_permissions(PermissionConstants.APPLICATION_EDIT.get_workspace_application_permission(),
                         PermissionConstants.APPLICATION_EDIT.get_workspace_permission_workspace_manage_role(),
                         RoleConstants.USER.get_workspace_role(),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        @log(menu='Application', operate='Publishing an application',
             get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')))
        def put(self, request: Request, workspace_id: str, application_id: str):
            return result.success(
                ApplicationOperateSerializer(
                    data={'application_id': application_id, 'user_id': request.user.id,
                          'workspace_id': workspace_id, }).publish(request.data))
