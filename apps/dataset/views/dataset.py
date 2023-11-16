# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： dataset.py
    @date：2023/9/21 15:52
    @desc:
"""

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import PermissionConstants, CompareConstants, Permission, Group, Operate
from common.response import result
from common.response.result import get_page_request_params, get_page_api_response, get_api_response
from dataset.serializers.dataset_serializers import DataSetSerializers


class Dataset(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary="获取数据集列表",
                         operation_id="获取数据集列表",
                         manual_parameters=DataSetSerializers.Query.get_request_params_api(),
                         responses=result.get_api_array_response(DataSetSerializers.Query.get_response_body_api()),
                         tags=["数据集"])
    @has_permissions(PermissionConstants.DATASET_READ, compare=CompareConstants.AND)
    def get(self, request: Request):
        d = DataSetSerializers.Query(data={**request.query_params, 'user_id': str(request.user.id)})
        d.is_valid()
        return result.success(d.list())

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary="创建数据集",
                         operation_id="创建数据集",
                         request_body=DataSetSerializers.Create.get_request_body_api(),
                         responses=get_api_response(DataSetSerializers.Create.get_response_body_api()),
                         tags=["数据集"]
                         )
    @has_permissions(PermissionConstants.DATASET_CREATE, compare=CompareConstants.AND)
    def post(self, request: Request):
        s = DataSetSerializers.Create(data=request.data)
        s.is_valid(raise_exception=True)
        return result.success(s.save(request.user))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods="DELETE", detail=False)
        @swagger_auto_schema(operation_summary="删除数据集", operation_id="删除数据集",
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=["数据集"])
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')),
                         lambda r, k: Permission(group=Group.DATASET, operate=Operate.DELETE,
                                                 dynamic_tag=k.get('dataset_id')), compare=CompareConstants.AND)
        def delete(self, request: Request, dataset_id: str):
            operate = DataSetSerializers.Operate(data={'id': dataset_id})
            return result.success(operate.delete())

        @action(methods="GET", detail=False)
        @swagger_auto_schema(operation_summary="查询数据集详情根据数据集id", operation_id="查询数据集详情根据数据集id",
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             responses=get_api_response(DataSetSerializers.Operate.get_response_body_api()),
                             tags=["数据集"])
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.USE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        def get(self, request: Request, dataset_id: str):
            return result.success(DataSetSerializers.Operate(data={'id': dataset_id}).one(user_id=request.user.id))

        @action(methods="PUT", detail=False)
        @swagger_auto_schema(operation_summary="修改数据集信息", operation_id="修改数据集信息",
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             request_body=DataSetSerializers.Operate.get_request_body_api(),
                             responses=get_api_response(DataSetSerializers.Operate.get_response_body_api()),
                             tags=["数据集"]
                             )
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        def put(self, request: Request, dataset_id: str):
            return result.success(
                DataSetSerializers.Operate(data={'id': dataset_id}).edit(request.data, user_id=request.user.id))

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="获取数据集分页列表",
                             operation_id="获取数据集分页列表",
                             manual_parameters=get_page_request_params(
                                 DataSetSerializers.Query.get_request_params_api()),
                             responses=get_page_api_response(DataSetSerializers.Query.get_response_body_api()),
                             tags=["数据集"]
                             )
        @has_permissions(PermissionConstants.DATASET_READ, compare=CompareConstants.AND)
        def get(self, request: Request, current_page, page_size):
            d = DataSetSerializers.Query(
                data={'name': request.query_params.get('name', None), 'desc': request.query_params.get("desc", None),
                      'user_id': str(request.user.id)})
            d.is_valid()
            return result.success(d.page(current_page, page_size))
