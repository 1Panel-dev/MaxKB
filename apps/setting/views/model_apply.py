# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： model_apply.py
    @date：2024/8/20 20:38
    @desc:
"""
from urllib.request import Request

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.views import APIView

from common.response import result
from setting.serializers.model_apply_serializers import ModelApplySerializers
from django.utils.translation import gettext_lazy as _


class ModelApply(APIView):
    class EmbedDocuments(APIView):
        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_('Vectorization documentation'),
                             operation_id=_('Vectorization documentation'),
                             responses=result.get_default_response(),
                             tags=[_('model')])
        def post(self, request: Request, model_id):
            return result.success(
                ModelApplySerializers(data={'model_id': model_id}).embed_documents(request.data))

    class EmbedQuery(APIView):
        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_('Vectorization documentation'),
                             operation_id=_('Vectorization documentation'),
                             responses=result.get_default_response(),
                             tags=[_('model')])
        def post(self, request: Request, model_id):
            return result.success(
                ModelApplySerializers(data={'model_id': model_id}).embed_query(request.data))

    class CompressDocuments(APIView):
        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_('Reorder documents'),
                             operation_id=_('Reorder documents'),
                             responses=result.get_default_response(),
                             tags=[_('model')])
        def post(self, request: Request, model_id):
            return result.success(
                ModelApplySerializers(data={'model_id': model_id}).compress_documents(request.data))
