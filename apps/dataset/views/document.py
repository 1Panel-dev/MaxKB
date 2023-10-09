# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： document.py
    @date：2023/9/22 11:32
    @desc:
"""

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import Permission, Group, Operate, PermissionConstants
from common.response import result
from dataset.serializers.dataset_serializers import CreateDocumentSerializers


class Document(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary="创建文档",
                         operation_id="创建文档",
                         request_body=CreateDocumentSerializers().get_request_body_api(),
                         manual_parameters=CreateDocumentSerializers().get_request_params_api())
    @has_permissions(PermissionConstants.DATASET_CREATE)
    def post(self, request: Request, dataset_id: str):
        d = CreateDocumentSerializers(data=request.data)
        if d.is_valid(dataset_id=dataset_id):
            d.save(dataset_id)
        return result.success("ok")


class DocumentDetails(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary="获取文档详情",
                         operation_id="获取文档详情",
                         request_body=CreateDocumentSerializers().get_request_body_api(),
                         manual_parameters=CreateDocumentSerializers().get_request_params_api())
    @has_permissions(
        lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE, dynamic_tag=k.get('dataset_id')))
    def get(self, request: Request, dataset_id: str):
        d = CreateDocumentSerializers(data=request.data)
        if d.is_valid(dataset_id=dataset_id):
            d.save(dataset_id)
        return result.success("ok")
