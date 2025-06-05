# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： model_apply.py
    @date：2024/8/20 20:38
    @desc:
"""
from urllib.request import Request

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView

from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants
from common.result import result
from models_provider.api.model import DefaultModelResponse
from models_provider.serializers.model_apply_serializers import ModelApplySerializers


class ModelApply(APIView):
    class EmbedDocuments(APIView):
        @extend_schema(methods=['POST'],
                       summary=_('Vectorization documentation'),
                       description=_('Vectorization documentation'),
                       operation_id=_('Vectorization documentation'),  # type: ignore
                       responses=DefaultModelResponse.get_response(),
                       tags=[_('Model')]  # type: ignore
                       )
        def post(self, request: Request, model_id):
            return result.success(
                ModelApplySerializers(data={'model_id': model_id}).embed_documents(request.data))

    class EmbedQuery(APIView):
        @extend_schema(methods=['POST'],
                       summary=_('Vectorization documentation'),
                       description=_('Vectorization documentation'),
                       operation_id=_('Vectorization documentation'),  # type: ignore
                       responses=DefaultModelResponse.get_response(),
                       tags=[_('Model')]  # type: ignore
                       )
        def post(self, request: Request, model_id):
            return result.success(
                ModelApplySerializers(data={'model_id': model_id}).embed_query(request.data))

    class CompressDocuments(APIView):
        @extend_schema(methods=['POST'],
                       summary=_('Reorder documents'),
                       description=_('Reorder documents'),
                       operation_id=_('Reorder documents'),  # type: ignore
                       responses=DefaultModelResponse.get_response(),
                       tags=[_('Model')]  # type: ignore
                       )
        def post(self, request: Request, model_id):
            return result.success(
                ModelApplySerializers(data={'model_id': model_id}).compress_documents(request.data))
