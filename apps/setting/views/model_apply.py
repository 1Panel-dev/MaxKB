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


class ModelApply(APIView):
    class EmbedDocuments(APIView):
        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary="向量化文档",
                             operation_id="向量化文档",
                             responses=result.get_default_response(),
                             tags=["模型"])
        def post(self, request: Request, model_id):
            return result.success(
                ModelApplySerializers(data={'model_id': model_id}).embed_documents(request.data))

    class EmbedQuery(APIView):
        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary="向量化文档",
                             operation_id="向量化文档",
                             responses=result.get_default_response(),
                             tags=["模型"])
        def post(self, request: Request, model_id):
            return result.success(
                ModelApplySerializers(data={'model_id': model_id}).embed_query(request.data))

    class CompressDocuments(APIView):
        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary="重排序文档",
                             operation_id="重排序文档",
                             responses=result.get_default_response(),
                             tags=["模型"])
        def post(self, request: Request, model_id):
            return result.success(
                ModelApplySerializers(data={'model_id': model_id}).compress_documents(request.data))
