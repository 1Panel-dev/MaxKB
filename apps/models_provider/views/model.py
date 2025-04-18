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
from models_provider.api.model import ModelCreateAPI, GetModelApi, ModelEditApi, ModelListResponse
from models_provider.api.provide import ProvideApi
from models_provider.serializers.model_serializer import ModelSerializer


class Model(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['POST'],
                   description=_("Create model"),
                   operation_id=_("Create model"),
                   tags=[_("Model")],
                   parameters=ModelCreateAPI.get_query_params_api(),
                   request=ModelCreateAPI.get_request(),
                   responses=ModelCreateAPI.get_response())
    @has_permissions(PermissionConstants.MODEL_CREATE.get_workspace_permission())
    def post(self, request: Request, workspace_id: str):
        return result.success(
            ModelSerializer.Create(data={**request.data, 'user_id': request.user.id}).insert(workspace_id,
                                                                                             with_valid=True))

    # @extend_schema(methods=['PUT'],
    #                description=_('Update model'),
    #                operation_id=_('Update model'),
    #                request=ModelEditApi.get_request(),
    #                responses=ModelCreateApi.get_response(),
    #                tags=[_('Model')])
    # @has_permissions(PermissionConstants.MODEL_CREATE)
    # def put(self, request: Request):
    #     return result.success(
    #         ModelSerializer.Create(data={**request.data, 'user_id': str(request.user.id)}).insert(request.user.id,
    #                                                                                               with_valid=True))

    @extend_schema(methods=['GET'],
                   description=_('Query model list'),
                   operation_id=_('Query model list'),
                   parameters=ModelCreateAPI.get_query_params_api(),
                   responses=ModelListResponse.get_response(),
                   tags=[_('Model')])
    @has_permissions(PermissionConstants.MODEL_READ.get_workspace_permission())
    def get(self, request: Request):
        return result.success(
            ModelSerializer.Query(
                data={**query_params_to_single_dict(request.query_params)}).list(
                with_valid=True))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['PUT'],
                       description=_('Update model'),
                       operation_id=_('Update model'),
                       request=ModelEditApi.get_request(),
                       parameters=GetModelApi.get_query_params_api(),
                       responses=ModelEditApi.get_response(),
                       tags=[_('Model')])
        @has_permissions(PermissionConstants.MODEL_EDIT.get_workspace_permission())
        def put(self, request: Request, workspace_id, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id, 'user_id': request.user.id}).edit(request.data,
                                                                                                str(request.user.id)))

        @extend_schema(methods=['DELETE'],
                       description=_('Delete model'),
                       operation_id=_('Delete model'),
                       parameters=GetModelApi.get_query_params_api(),
                       tags=[_('Model')])
        @has_permissions(PermissionConstants.MODEL_DELETE.get_workspace_permission())
        def delete(self, request: Request, workspace_id: str, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id, 'user_id': request.user.id}).delete())

        @extend_schema(methods=['GET'],
                       description=_('Query model details'),
                       operation_id=_('Query model details'),
                       parameters=GetModelApi.get_query_params_api(),
                       responses=GetModelApi.get_response(),
                       tags=[_('Model')])
        @has_permissions(PermissionConstants.MODEL_READ.get_workspace_permission())
        def get(self, request: Request, workspace_id: str, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id, 'user_id': request.user.id}).one(with_valid=True))

    class ModelParamsForm(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['GET'],
                       description=_('Get model parameter form'),
                       operation_id=_('Get model parameter form'),
                       parameters=GetModelApi.get_query_params_api(),
                       responses=ProvideApi.ModelParamsForm.get_response(),
                       tags=[_('Model')])
        @has_permissions(PermissionConstants.MODEL_READ.get_workspace_permission())
        def get(self, request: Request, workspace_id: str, model_id: str):
            return result.success(
                ModelSerializer.ModelParams(data={'id': model_id}).get_model_params())

        @extend_schema(methods=['PUT'],
                       description=_('Save model parameter form'),
                       operation_id=_('Save model parameter form'),
                       parameters=GetModelApi.get_query_params_api(),
                       responses=ProvideApi.ModelParamsForm.get_response(),
                       tags=[_('Model')])
        @has_permissions(PermissionConstants.MODEL_READ.get_workspace_permission())
        def put(self, request: Request, workspace_id: str, model_id: str):
            return result.success(
                ModelSerializer.ModelParams(data={'id': model_id}).save_model_params_form(request.data))

    class ModelMeta(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['GET'],
                       description=_(
                           'Query model meta information, this interface does not carry authentication information'),
                       operation_id=_(
                           'Query model meta information, this interface does not carry authentication information'),
                       parameters=GetModelApi.get_query_params_api(),
                       responses=GetModelApi.get_response(),
                       tags=[_('Model')])
        @has_permissions(PermissionConstants.MODEL_READ.get_workspace_permission())
        def get(self, request: Request, workspace_id: str, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id}).one_meta(with_valid=True))

    class PauseDownload(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['PUT'],
                       description=_('Pause model download'),
                       operation_id=_('Pause model download'),
                       parameters=GetModelApi.get_query_params_api(),
                       tags=[_('Model')])
        @has_permissions(PermissionConstants.MODEL_CREATE.get_workspace_permission())
        def put(self, request: Request, workspace_id: str, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id}).pause_download())
