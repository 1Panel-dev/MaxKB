# coding=utf-8

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants
from models_provider.api.provide import ProvideApi
from models_provider.constants.model_provider_constants import ModelProvideConstants
from models_provider.serializers.model_serializer import get_default_model_params_setting


class Provide(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['GET'],
                   summary=_('Get a list of model suppliers'),
                   description=_('Get a list of model suppliers'),
                   operation_id=_('Get a list of model suppliers'),  # type: ignore
                   responses=ProvideApi.get_response(),
                   tags=[_('Model')])  # type: ignore
    def get(self, request: Request):
        model_type = request.query_params.get('model_type')
        if model_type:
            providers = []
            for key in ModelProvideConstants.__members__:
                if len([item for item in ModelProvideConstants[key].value.get_model_type_list() if
                        item['value'] == model_type]) > 0:
                    providers.append(ModelProvideConstants[key].value.get_model_provide_info().to_dict())
            return result.success(providers)
        return result.success(
            [ModelProvideConstants[key].value.get_model_provide_info().to_dict() for key in
             ModelProvideConstants.__members__])

    class ModelTypeList(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['GET'],
                       summary=_('Get a list of model types'),
                       description=_('Get a list of model types'),
                       operation_id=_('Get a list of model types'),  # type: ignore
                       parameters=ProvideApi.ModelTypeList.get_query_params_api(),
                       responses=ProvideApi.ModelTypeList.get_response(),
                       tags=[_('Model')])  # type: ignore
        def get(self, request: Request):
            provider = request.query_params.get('provider')
            return result.success(ModelProvideConstants[provider].value.get_model_type_list())

    class ModelList(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['GET'],
                       summary=_('Example of obtaining model list'),
                       description=_('Example of obtaining model list'),
                       operation_id=_('Example of obtaining model list'),  # type: ignore
                       parameters=ProvideApi.ModelList.get_query_params_api(),
                       responses=ProvideApi.ModelList.get_response(),
                       tags=[_('Model')])  # type: ignore
        def get(self, request: Request):
            provider = request.query_params.get('provider')
            model_type = request.query_params.get('model_type')

            return result.success(
                ModelProvideConstants[provider].value.get_model_list(
                    model_type))

    class ModelParamsForm(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['GET'],
                       summary=_('Get model default parameters'),
                       description=_('Get model default parameters'),
                       operation_id=_('Get model default parameters'),  # type: ignore
                       parameters=ProvideApi.ModelParamsForm.get_query_params_api(),
                       responses=ProvideApi.ModelParamsForm.get_response(),
                       tags=[_('Model')])  # type: ignore
        def get(self, request: Request):
            provider = request.query_params.get('provider')
            model_type = request.query_params.get('model_type')
            model_name = request.query_params.get('model_name')

            return result.success(get_default_model_params_setting(provider, model_type, model_name))

    class ModelForm(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['GET'],
                       summary=_('Get the model creation form'),
                       description=_('Get the model creation form'),
                       operation_id=_('Get the model creation form'),  # type: ignore
                       parameters=ProvideApi.ModelParamsForm.get_query_params_api(),
                       responses=ProvideApi.ModelParamsForm.get_response(),
                       tags=[_('Model')])  # type: ignore
        def get(self, request: Request):
            provider = request.query_params.get('provider')
            model_type = request.query_params.get('model_type')
            model_name = request.query_params.get('model_name')
            return result.success(
                ModelProvideConstants[provider].value.get_model_credential(model_type, model_name).to_form_list())
