from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.api.application_api_key import ApplicationKeyAPI
from application.models import Application
from application.serializers.application_api_key import ApplicationKeySerializer
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants, ViewPermission, CompareConstants
from common.log.log import log
from common.result import result, DefaultResultSerializer


def get_application_operation_object(application_id):
    application_model = QuerySet(model=Application).filter(id=application_id).first()
    if application_model is not None:
        return {
            "name": application_model.name
        }
    return {}


class ApplicationKey(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Create application ApiKey'),
        summary=_('Create application ApiKey'),
        operation_id=_('Create application ApiKey'),  # type: ignore
        parameters=ApplicationKeyAPI.get_parameters(),
        request=None,
        responses=ApplicationKeyAPI.get_response(),
        tags=[_('Application Api Key')]  # type: ignore
    )
    @log(menu='Application', operate="Add ApiKey",
         get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')),
         )
    @has_permissions(PermissionConstants.APPLICATION_OVERVIEW_API_KEY.get_workspace_application_permission(),
                     PermissionConstants.APPLICATION_READ.get_workspace_permission_workspace_manage_role(),
                     ViewPermission([RoleConstants.USER.get_workspace_role()],
                                    [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                    CompareConstants.AND),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role()
                     )
    def post(self, request: Request, workspace_id: str, application_id: str):
        return result.success(ApplicationKeySerializer(
            data={'application_id': application_id, 'user_id': request.user.id,
                  'workspace_id': workspace_id}).generate())

    @extend_schema(
        methods=['GET'],
        description=_('GET application ApiKey List'),
        summary=_('Create application ApiKey List'),
        operation_id=_('Create application ApiKey List'),  # type: ignore
        parameters=ApplicationKeyAPI.get_parameters(),
        responses=ApplicationKeyAPI.List.get_response(),
        tags=[_('Application Api Key')]  # type: ignore
    )
    @has_permissions(PermissionConstants.APPLICATION_OVERVIEW_API_KEY.get_workspace_application_permission(),
                     PermissionConstants.APPLICATION_OVERVIEW_API_KEY.get_workspace_permission_workspace_manage_role(),
                     ViewPermission([RoleConstants.USER.get_workspace_role()],
                                    [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                    CompareConstants.AND),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def get(self, request: Request, workspace_id: str, application_id: str):
        return result.success(ApplicationKeySerializer(
            data={'application_id': application_id,
                  'workspace_id': workspace_id}).list())

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_('Modify application API_KEY'),
            summary=_('Modify application API_KEY'),
            operation_id=_('Modify application API_KEY'),  # type: ignore
            parameters=ApplicationKeyAPI.Operate.get_parameters(),
            request=ApplicationKeyAPI.Operate.get_request(),
            responses=DefaultResultSerializer,
            tags=[_('Application Api Key')]  # type: ignore
        )
        @has_permissions(PermissionConstants.APPLICATION_OVERVIEW_API_KEY.get_workspace_application_permission(),
                         PermissionConstants.APPLICATION_OVERVIEW_API_KEY.get_workspace_permission_workspace_manage_role(),
                         ViewPermission([RoleConstants.USER.get_workspace_role()],
                                        [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                        CompareConstants.AND),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        @log(menu='Application', operate="Modify application API_KEY",
             get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')),
             )
        def put(self, request: Request, workspace_id: str, application_id: str, api_key_id: str):
            return result.success(
                ApplicationKeySerializer.Operate(
                    data={'workspace_id': workspace_id, 'application_id': application_id,
                          'api_key_id': api_key_id}).edit(
                    request.data))

        @extend_schema(
            methods=['DELETE'],
            description=_('Delete Application API_KEY'),
            summary=_('Delete Application API_KEY'),
            operation_id=_('Delete Application API_KEY'),  # type: ignore
            parameters=ApplicationKeyAPI.Operate.get_parameters(),
            request=ApplicationKeyAPI.Operate.get_request(),
            responses=DefaultResultSerializer,
            tags=[_('Application Api Key')]  # type: ignore
        )
        @has_permissions(PermissionConstants.APPLICATION_OVERVIEW_API_KEY.get_workspace_application_permission(),
                         PermissionConstants.APPLICATION_OVERVIEW_API_KEY.get_workspace_permission_workspace_manage_role(),
                         ViewPermission([RoleConstants.USER.get_workspace_role()],
                                        [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                        CompareConstants.AND),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        @log(menu='Application', operate="Delete application API_KEY",
             get_operation_object=lambda r, k: get_application_operation_object(k.get('application_id')),
             )
        def delete(self, request: Request, workspace_id: str, application_id: str, api_key_id: str):
            return result.success(
                ApplicationKeySerializer.Operate(
                    data={'workspace_id': workspace_id, 'application_id': application_id,
                          'api_key_id': api_key_id}).delete())
