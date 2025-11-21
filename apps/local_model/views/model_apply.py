# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： model_apply.py
    @date：2024/8/20 20:38
    @desc:
"""
from urllib.request import Request

from rest_framework.views import APIView

from common.result import result
from local_model.serializers.model_apply_serializers import ModelApplySerializers, ValidateModelSerializers


class LocalModelApply(APIView):
    class EmbedDocuments(APIView):

        def post(self, request: Request, model_id):
            return result.success(
                ModelApplySerializers(data={'model_id': model_id}).embed_documents(request.data))

    class EmbedQuery(APIView):

        def post(self, request: Request, model_id):
            return result.success(
                ModelApplySerializers(data={'model_id': model_id}).embed_query(request.data))

    class CompressDocuments(APIView):

        def post(self, request: Request, model_id):
            return result.success(
                ModelApplySerializers(data={'model_id': model_id}).compress_documents(request.data))

    class Unload(APIView):
        def post(self, request: Request, model_id):
            return result.success(
                ModelApplySerializers(data={'model_id': model_id}).compress_documents(request.data))

    class Validate(APIView):
        def post(self, request: Request):
            return result.success(ValidateModelSerializers(data=request.data).validate_model())
