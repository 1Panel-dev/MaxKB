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
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import Permission, Group, Operate, PermissionConstants
from common.response import result
from common.util.common import query_params_to_single_dict
from dataset.serializers.document_serializers import DocumentSerializers


class Document(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary="创建文档",
                         operation_id="创建文档",
                         request_body=DocumentSerializers.Create.get_request_body_api(),
                         manual_parameters=DocumentSerializers.Create.get_request_params_api(),
                         responses=result.get_api_response(DocumentSerializers.Operate.get_response_body_api()))
    @has_permissions(
        lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                dynamic_tag=k.get('dataset_id')))
    def post(self, request: Request, dataset_id: str):
        return result.success(
            DocumentSerializers.Create(data={'dataset_id': dataset_id}).save(request.data, with_valid=True))

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary="文档列表",
                         operation_id="文档列表",
                         manual_parameters=DocumentSerializers.Query.get_request_params_api(),
                         responses=result.get_api_response(DocumentSerializers.Query.get_response_body_api()))
    @has_permissions(
        lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                dynamic_tag=k.get('dataset_id')))
    def get(self, request: Request, dataset_id: str):
        d = DocumentSerializers.Query(
            data={**query_params_to_single_dict(request.query_params), 'dataset_id': dataset_id})
        d.is_valid(raise_exception=True)
        return result.success(d.list())

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="获取文档详情",
                             operation_id="获取文档详情",
                             manual_parameters=DocumentSerializers.Operate.get_request_params_api(),
                             responses=result.get_api_response(DocumentSerializers.Operate.get_response_body_api()))
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                    dynamic_tag=k.get('dataset_id')))
        def get(self, request: Request, dataset_id: str, document_id: str):
            operate = DocumentSerializers.Operate(data={'document_id': document_id, 'dataset_id': dataset_id})
            operate.is_valid(raise_exception=True)
            return result.success(operate.one())

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary="修改文档",
                             operation_id="修改文档",
                             manual_parameters=DocumentSerializers.Operate.get_request_params_api(),
                             request_body=DocumentSerializers.Operate.get_request_body_api(),
                             responses=result.get_api_response(DocumentSerializers.Operate.get_response_body_api())
                             )
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def put(self, request: Request, dataset_id: str, document_id: str):
            return result.success(
                DocumentSerializers.Operate(data={'document_id': document_id, 'dataset_id': dataset_id}).edit(
                    request.data,
                    with_valid=True))

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary="删除文档",
                             operation_id="删除文档",
                             manual_parameters=DocumentSerializers.Operate.get_request_params_api(),
                             responses=result.get_default_response())
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def delete(self, request: Request, dataset_id: str, document_id: str):
            operate = DocumentSerializers.Operate(data={'document_id': document_id, 'dataset_id': dataset_id})
            operate.is_valid(raise_exception=True)
            return result.success(operate.delete())

    class Split(APIView):
        parser_classes = [MultiPartParser]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary="分段文档",
                             operation_id="分段文档",
                             manual_parameters=DocumentSerializers.Split.get_request_params_api())
        def post(self, request: Request):
            ds = DocumentSerializers.Split(
                data={'file': request.FILES.getlist('file'),
                      'patterns': request.data.getlist('patterns[]')})
            ds.is_valid(raise_exception=True)
            return result.success(ds.parse())

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="获取数据集分页列表",
                             operation_id="获取数据集分页列表",
                             manual_parameters=DocumentSerializers.Query.get_request_params_api(),
                             responses=result.get_page_api_response(DocumentSerializers.Query.get_response_body_api()))
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                    dynamic_tag=k.get('dataset_id')))
        def get(self, request: Request, dataset_id: str, current_page, page_size):
            d = DocumentSerializers.Query(
                data={**query_params_to_single_dict(request.query_params), 'dataset_id': dataset_id})
            d.is_valid(raise_exception=True)
            return result.success(d.page(current_page, page_size))
