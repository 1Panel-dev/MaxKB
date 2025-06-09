from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _

from application.api.application_api_key import ApplicationKeyCreateAPI
from application.models import ApplicationApiKey
from application.serializers.application_api_key import ApplicationKeySerializer
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants
from common.log.log import log
from common.result import result, success


def get_application_operation_object(application_api_key_id):
    application_api_key_model = QuerySet(model=ApplicationApiKey).filter(id=application_api_key_id).first()
    if application_api_key_model is not None:
        return {
            "name": application_api_key_model.name
        }
    return {}


class ApplicationKey(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Create application ApiKey'),
        summary=_('Create application ApiKey'),
        operation_id=_('Create application ApiKey'),  # type: ignore
        parameters=ApplicationKeyCreateAPI.get_parameters(),
        tags=[_('Application Api Key')]  # type: ignore
    )
    @log(menu='Application', operate="Add ApiKey",
         get_operation_object=lambda r, k: get_application_operation_object(k.get('application_api_key_id')))
    @has_permissions(PermissionConstants.APPLICATION_OVERVIEW_API_KEY.get_workspace_application_permission())
    def post(self, request: Request, workspace_id: str, application_id: str):
        return result.success(ApplicationKeySerializer(
            data={'application_id': application_id, 'user_id': request.user.id,
                  'workspace_id': workspace_id}).generate())

    @extend_schema(
        methods=['GET'],
        description=_('GET application ApiKey List'),
        summary=_('Create application ApiKey List'),
        operation_id=_('Create application ApiKey List'),  # type: ignore
        parameters=ApplicationKeyCreateAPI.get_parameters(),
        tags=[_('Application Api Key')]  # type: ignore
    )
    @has_permissions(PermissionConstants.APPLICATION_OVERVIEW_API_KEY.get_workspace_application_permission())
    def get(self, request: Request, workspace_id: str, application_id: str):
        return result, success(ApplicationKeySerializer(
            data={'application_id': application_id, 'user_id': request.user.id,
                  'workspace_id': workspace_id}).list())

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('GET application ApiKey List'),
            summary=_('Create application ApiKey List'),
            operation_id=_('Create application ApiKey List'),  # type: ignore
            parameters=ApplicationKeyCreateAPI.get_parameters(),
            tags=[_('Application Api Key')]  # type: ignore
        )
        @has_permissions(PermissionConstants.APPLICATION_OVERVIEW_API_KEY.get_workspace_application_permission())
        def put(self, request: Request, application_id: str, workspace_id: str):
            return result.success(ApplicationKeySerializer.Operate())
