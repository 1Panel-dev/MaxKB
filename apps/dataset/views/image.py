# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： image.py
    @date：2024/4/22 16:23
    @desc:
"""
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth
from common.response import result
from dataset.serializers.image_serializers import ImageSerializer


class Image(APIView):
    authentication_classes = [TokenAuth]
    parser_classes = [MultiPartParser]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary="上传图片",
                         operation_id="上传图片",
                         manual_parameters=[openapi.Parameter(name='file',
                                                              in_=openapi.IN_FORM,
                                                              type=openapi.TYPE_FILE,
                                                              required=True,
                                                              description='上传文件')],
                         tags=["图片"])
    def post(self, request: Request):
        return result.success(ImageSerializer(data={'image': request.FILES.get('file')}).upload())

    class Operate(APIView):
        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="获取图片",
                             operation_id="获取图片",
                             tags=["图片"])
        def get(self, request: Request, image_id: str):
            return ImageSerializer.Operate(data={'id': image_id}).get()
