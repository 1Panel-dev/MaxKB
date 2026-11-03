# coding=utf-8


from common import result
from common.auth import TokenAuth
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from models_provider.api.provide import ProvideApi
from models_provider.constants.model_provider_constants import ModelProvideConstants
from models_provider.serializers.model_serializer import get_default_model_params_setting
from rest_framework.request import Request
from rest_framework.views import APIView


class Provide(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get a list of model suppliers"),
        description=_("Get a list of model suppliers"),
        operation_id=_("Get a list of model suppliers"),  # type: ignore
        responses=ProvideApi.get_response(),
        tags=[_("Model")],  # type: ignore
    )
    def get(self, request: Request):
        model_type = request.query_params.get("model_type")
        if model_type:
            providers = []
            for key in ModelProvideConstants.__members__:
                if (
                    len(
                        [
                            item
                            for item in ModelProvideConstants[key].get_model_type_list()
                            if item["value"] == model_type
                        ]
                    )
                    > 0
                ):
                    providers.append(ModelProvideConstants[key].get_model_provide_info().to_dict())
            return result.success(providers)
        return result.success(
            [ModelProvideConstants[key].get_model_provide_info().to_dict() for key in ModelProvideConstants.__members__]
        )

    class ModelTypeList(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            summary=_("Get a list of model types"),
            description=_("Get a list of model types"),
            operation_id=_("Get a list of model types"),  # type: ignore
            parameters=ProvideApi.ModelTypeList.get_query_params_api(),
            responses=ProvideApi.ModelTypeList.get_response(),
            tags=[_("Model")],  # type: ignore
        )
        def get(self, request: Request):
            provider = request.query_params.get("provider")
            return result.success(ModelProvideConstants[provider].get_model_type_list())

    class ModelList(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            summary=_("Example of obtaining model list"),
            description=_("Example of obtaining model list"),
            operation_id=_("Example of obtaining model list"),  # type: ignore
            parameters=ProvideApi.ModelList.get_query_params_api(),
            responses=ProvideApi.ModelList.get_response(),
            tags=[_("Model")],  # type: ignore
        )
        @staticmethod
        def _get_model_list(provider, model_type, api_key, api_base, credential, search):
            model_list = ModelProvideConstants[provider].get_model_list(
                model_type,
                api_key=api_key,
                api_base=api_base,
                credential=credential,
            )
            if search:
                search = str(search).strip().lower()
                model_list = [
                    model
                    for model in model_list
                    if search in str(model.get("name", "")).lower() or search in str(model.get("desc", "")).lower()
                ]
            return model_list

        def get(self, request: Request):
            """内置列表查询；带凭证的查询必须走 POST，避免 api_key 出现在 URL/访问日志中。"""
            return result.success(
                self._get_model_list(
                    request.query_params.get("provider"),
                    request.query_params.get("model_type"),
                    None,
                    None,
                    None,
                    request.query_params.get("search"),
                )
            )

        def post(self, request: Request):
            """携带凭证的查询走 POST，避免 api_key 出现在 URL/访问日志中。"""
            data = request.data or {}
            return result.success(
                self._get_model_list(
                    data.get("provider"),
                    data.get("model_type"),
                    data.get("api_key"),
                    data.get("api_base"),
                    data.get("credential"),
                    data.get("search"),
                )
            )

    class ModelParamsForm(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            summary=_("Get model default parameters"),
            description=_("Get model default parameters"),
            operation_id=_("Get model default parameters"),  # type: ignore
            parameters=ProvideApi.ModelParamsForm.get_query_params_api(),
            responses=ProvideApi.ModelParamsForm.get_response(),
            tags=[_("Model")],  # type: ignore
        )
        def get(self, request: Request):
            provider = request.query_params.get("provider")
            model_type = request.query_params.get("model_type")
            model_name = request.query_params.get("model_name")

            return result.success(get_default_model_params_setting(provider, model_type, model_name))

    class ModelForm(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            summary=_("Get the model creation form"),
            description=_("Get the model creation form"),
            operation_id=_("Get the model creation form"),  # type: ignore
            parameters=ProvideApi.ModelParamsForm.get_query_params_api(),
            responses=ProvideApi.ModelParamsForm.get_response(),
            tags=[_("Model")],  # type: ignore
        )
        def get(self, request: Request):
            provider = request.query_params.get("provider")
            model_type = request.query_params.get("model_type")
            model_name = request.query_params.get("model_name")
            return result.success(
                ModelProvideConstants[provider].get_model_credential(model_type, model_name).to_form_list()
            )
