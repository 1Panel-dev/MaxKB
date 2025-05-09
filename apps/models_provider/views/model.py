# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： user.py
    @date：2025/4/14 19:25
    @desc:
"""
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _
from rest_framework.request import Request

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants
from common.result import result
from common.utils.common import query_params_to_single_dict
from models_provider.api.model import ModelCreateAPI, GetModelApi, ModelEditApi, ModelListResponse, DefaultModelResponse
from models_provider.api.provide import ProvideApi
from models_provider.serializers.model_serializer import ModelSerializer


class Model(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['POST'],
                   summary=_("Create model"),
                   description=_("Create model"),
                   operation_id=_("Create model"),  # type: ignore
                   tags=[_("Model")],  # type: ignore
                   parameters=ModelCreateAPI.get_query_params_api(),
                   request=ModelCreateAPI.get_request(),
                   responses=ModelCreateAPI.get_response())
    @has_permissions(PermissionConstants.MODEL_CREATE.get_workspace_permission())
    def post(self, request: Request, workspace_id: str):
        return result.success(
            ModelSerializer.Create(data={**request.data, 'user_id': request.user.id}).insert(workspace_id,
                                                                                             with_valid=True))

    # @extend_schema(methods=['PUT'],
    #                summary=_('Update model'),
    #                operation_id=_('Update model'),  # type: ignore
    #                request=ModelEditApi.get_request(),
    #                responses=ModelCreateApi.get_response(),
    #                tags=[_('Model')])  # type: ignore
    # @has_permissions(PermissionConstants.MODEL_CREATE)
    # def put(self, request: Request):
    #     return result.success(
    #         ModelSerializer.Create(data={**request.data, 'user_id': str(request.user.id)}).insert(request.user.id,
    #                                                                                               with_valid=True))

    @extend_schema(methods=['GET'],
                   summary=_('Query model list'),
                   description=_('Query model list'),
                   operation_id=_('Query model list'),  # type: ignore
                   parameters=ModelCreateAPI.get_query_params_api(),
                   responses=ModelListResponse.get_response(),
                   tags=[_('Model')])  # type: ignore
    @has_permissions(PermissionConstants.MODEL_READ.get_workspace_permission())
    def get(self, request: Request, workspace_id: str):
        return result.success(
            ModelSerializer.Query(
                data={**query_params_to_single_dict(request.query_params)}).list(workspace_id=workspace_id,
                                                                                 with_valid=True))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['PUT'],
                       summary=_('Update model'),
                       description=_('Update model'),
                       operation_id=_('Update model'),  # type: ignore
                       request=ModelEditApi.get_request(),
                       parameters=GetModelApi.get_query_params_api(),
                       responses=ModelEditApi.get_response(),
                       tags=[_('Model')])  # type: ignore
        @has_permissions(PermissionConstants.MODEL_EDIT.get_workspace_permission())
        def put(self, request: Request, workspace_id, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id, 'user_id': request.user.id}).edit(request.data,
                                                                                                str(request.user.id)))

        @extend_schema(methods=['DELETE'],
                       summary=_('Delete model'),
                       description=_('Delete model'),
                       operation_id=_('Delete model'),  # type: ignore
                       parameters=GetModelApi.get_query_params_api(),
                       responses=DefaultModelResponse.get_response(),
                       tags=[_('Model')])  # type: ignore
        @has_permissions(PermissionConstants.MODEL_DELETE.get_workspace_permission())
        def delete(self, request: Request, workspace_id: str, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id, 'user_id': request.user.id}).delete())

        @extend_schema(methods=['GET'],
                       summary=_('Query model details'),
                       description=_('Query model details'),
                       operation_id=_('Query model details'),  # type: ignore
                       parameters=GetModelApi.get_query_params_api(),
                       responses=GetModelApi.get_response(),
                       tags=[_('Model')])  # type: ignore
        @has_permissions(PermissionConstants.MODEL_READ.get_workspace_permission())
        def get(self, request: Request, workspace_id: str, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id, 'user_id': request.user.id}).one(with_valid=True))

    class ModelParamsForm(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['GET'],
                       summary=_('Get model parameter form'),
                       description=_('Get model parameter form'),
                       operation_id=_('Get model parameter form'),  # type: ignore
                       parameters=GetModelApi.get_query_params_api(),
                       responses=ProvideApi.ModelParamsForm.get_response(),
                       tags=[_('Model')])  # type: ignore
        @has_permissions(PermissionConstants.MODEL_READ.get_workspace_permission())
        def get(self, request: Request, workspace_id: str, model_id: str):
            return result.success(
                ModelSerializer.ModelParams(data={'id': model_id}).get_model_params())

        @extend_schema(methods=['PUT'],
                       summary=_('Save model parameter form'),
                       description=_('Save model parameter form'),
                       operation_id=_('Save model parameter form'),  # type: ignore
                       parameters=GetModelApi.get_query_params_api(),
                       request=GetModelApi.get_request(),
                       responses=ProvideApi.ModelParamsForm.get_response(),
                       tags=[_('Model')])  # type: ignore
        @has_permissions(PermissionConstants.MODEL_READ.get_workspace_permission())
        def put(self, request: Request, workspace_id: str, model_id: str):
            return result.success(
                ModelSerializer.ModelParams(data={'id': model_id}).save_model_params_form(request.data))

    class ModelMeta(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['GET'],
                       summary=_(
                           'Query model meta information, this interface does not carry authentication information'),
                       description=_(
                           'Query model meta information, this interface does not carry authentication information'),
                       operation_id=_(
                           'Query model meta information, this interface does not carry authentication information'),
                       parameters=GetModelApi.get_query_params_api(),
                       responses=GetModelApi.get_response(),
                       tags=[_('Model')])  # type: ignore
        @has_permissions(PermissionConstants.MODEL_READ.get_workspace_permission())
        def get(self, request: Request, workspace_id: str, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id}).one_meta(with_valid=True))

    class PauseDownload(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['PUT'],
                       summary=_('Pause model download'),
                       description=_('Pause model download'),
                       operation_id=_('Pause model download'),  # type: ignore
                       parameters=GetModelApi.get_query_params_api(),
                       request=GetModelApi.get_request(),
                       responses=DefaultModelResponse.get_response(),
                       tags=[_('Model')])  # type: ignore
        @has_permissions(PermissionConstants.MODEL_CREATE.get_workspace_permission())
        def put(self, request: Request, workspace_id: str, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id}).pause_download())
