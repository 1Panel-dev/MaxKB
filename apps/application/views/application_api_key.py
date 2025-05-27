from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _

from application.api.application_api_key import ApplicationKeyCreateAPI
from application.serializers.application_api_key import ApplicationKeySerializer
from common.auth import TokenAuth
from common.result import result, success


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
    def post(self,request: Request, application_id: str, workspace_id: str):
        return result.success(ApplicationKeySerializer(
                data={'application_id': application_id, 'user_id': request.user.id,
                      'workspace_id':workspace_id}).generate())

    @extend_schema(
        methods=['GET'],
        description=_('GET application ApiKey List'),
        summary=_('Create application ApiKey List'),
        operation_id=_('Create application ApiKey List'),  # type: ignore
        parameters=ApplicationKeyCreateAPI.get_parameters(),
        tags=[_('Application Api Key')]  # type: ignore
    )
    def get(self,request: Request, application_id: str, workspace_id: str):
        return result,success(ApplicationKeySerializer(
            data={'application_id':application_id, 'user_id':request.user.id,
                  'workspace_id':workspace_id}).list())


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
        def put(self, request: Request, application_id: str, workspace_id: str):
            return result.success(ApplicationKeySerializer.Operate(

            )
                                  )

