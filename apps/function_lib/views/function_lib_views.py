# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： function_lib_views.py
    @date：2024/8/2 17:08
    @desc:
"""
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import RoleConstants
from common.response import result
from function_lib.serializers.function_lib_serializer import FunctionLibSerializer
from function_lib.swagger_api.function_lib_api import FunctionLibApi


class FunctionLibView(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=["GET"], detail=False)
    @swagger_auto_schema(operation_summary="获取函数列表",
                         operation_id="获取函数列表",
                         tags=["函数库"],
                         manual_parameters=FunctionLibApi.Query.get_request_params_api())
    @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
    def get(self, request: Request):
        return result.success(
            FunctionLibSerializer.Query(
                data={'name': request.query_params.get('name'),
                      'desc': request.query_params.get('desc'),
                      'user_id': request.user.id}).list())

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary="创建函数",
                         operation_id="创建函数",
                         request_body=FunctionLibApi.Create.get_request_body_api(),
                         tags=['函数库'])
    @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
    def post(self, request: Request):
        return result.success(FunctionLibSerializer.Create(data={'user_id': request.user.id}).insert(request.data))

    class Debug(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary="调试函数",
                             operation_id="调试函数",
                             request_body=FunctionLibApi.Debug.get_request_body_api(),
                             tags=['函数库'])
        @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
        def post(self, request: Request):
            return result.success(
                FunctionLibSerializer.Debug(data={'user_id': request.user.id}).debug(
                    request.data))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary="修改函数",
                             operation_id="修改函数",
                             request_body=FunctionLibApi.Edit.get_request_body_api(),
                             tags=['函数库'])
        @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
        def put(self, request: Request, function_lib_id: str):
            return result.success(
                FunctionLibSerializer.Operate(data={'user_id': request.user.id, 'id': function_lib_id}).edit(
                    request.data))

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary="删除函数",
                             operation_id="删除函数",
                             tags=['函数库'])
        @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
        def delete(self, request: Request, function_lib_id: str):
            return result.success(
                FunctionLibSerializer.Operate(data={'user_id': request.user.id, 'id': function_lib_id}).delete())

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="分页获取函数列表",
                             operation_id="分页获取函数列表",
                             manual_parameters=result.get_page_request_params(
                                 FunctionLibApi.Query.get_request_params_api()),
                             responses=result.get_page_api_response(FunctionLibApi.get_response_body_api()),
                             tags=['函数库'])
        @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
        def get(self, request: Request, current_page: int, page_size: int):
            return result.success(
                FunctionLibSerializer.Query(
                    data={'name': request.query_params.get('name'),
                          'desc': request.query_params.get('desc'),
                          'user_id': request.user.id}).page(
                    current_page, page_size))
