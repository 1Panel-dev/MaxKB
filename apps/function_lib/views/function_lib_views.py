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
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import RoleConstants, Permission, Group, Operate
from common.response import result
from function_lib.serializers.function_lib_serializer import FunctionLibSerializer
from function_lib.swagger_api.function_lib_api import FunctionLibApi
from django.utils.translation import gettext_lazy as _


class FunctionLibView(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=["GET"], detail=False)
    @swagger_auto_schema(operation_summary=_('Get function list'),
                         operation_id=_('Get function list'),
                         tags=[_('Function')],
                         manual_parameters=FunctionLibApi.Query.get_request_params_api())
    @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
    def get(self, request: Request):
        return result.success(
            FunctionLibSerializer.Query(
                data={'name': request.query_params.get('name'),
                      'desc': request.query_params.get('desc'),
                      'user_id': request.user.id}).list())

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_('Create function'),
                         operation_id=_('Create function'),
                         request_body=FunctionLibApi.Create.get_request_body_api(),
                         tags=[_('Function')])
    @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
    def post(self, request: Request):
        return result.success(FunctionLibSerializer.Create(data={'user_id': request.user.id}).insert(request.data))

    class Debug(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_('Debug function'),
                             operation_id=_('Debug function'),
                             request_body=FunctionLibApi.Debug.get_request_body_api(),
                             tags=[_('Function')])
        @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
        def post(self, request: Request):
            return result.success(
                FunctionLibSerializer.Debug(data={'user_id': request.user.id}).debug(
                    request.data))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_('Update function'),
                             operation_id=_('Update function'),
                             request_body=FunctionLibApi.Edit.get_request_body_api(),
                             tags=[_('Function')])
        @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
        def put(self, request: Request, function_lib_id: str):
            return result.success(
                FunctionLibSerializer.Operate(data={'user_id': request.user.id, 'id': function_lib_id}).edit(
                    request.data))

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary=_('Delete function'),
                             operation_id=_('Delete function'),
                             tags=[_('Function')])
        @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
        def delete(self, request: Request, function_lib_id: str):
            return result.success(
                FunctionLibSerializer.Operate(data={'user_id': request.user.id, 'id': function_lib_id}).delete())

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('Get function details'),
                             operation_id=_('Get function details'),
                             tags=[_('Function')])
        @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
        def get(self, request: Request, function_lib_id: str):
            return result.success(
                FunctionLibSerializer.Operate(data={'user_id': request.user.id, 'id': function_lib_id}).one())

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('Get function list by pagination'),
                             operation_id=_('Get function list by pagination'),
                             manual_parameters=result.get_page_request_params(
                                 FunctionLibApi.Query.get_request_params_api()),
                             responses=result.get_page_api_response(FunctionLibApi.get_response_body_api()),
                             tags=[_('Function')])
        @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
        def get(self, request: Request, current_page: int, page_size: int):
            return result.success(
                FunctionLibSerializer.Query(
                    data={'name': request.query_params.get('name'),
                          'desc': request.query_params.get('desc'),
                          'user_id': request.user.id,
                          'select_user_id': request.query_params.get('select_user_id')}).page(
                    current_page, page_size))

    class Import(APIView):
        authentication_classes = [TokenAuth]
        parser_classes = [MultiPartParser]

        @action(methods="POST", detail=False)
        @swagger_auto_schema(operation_summary=_("Import function"), operation_id=_("Import function"),
                             manual_parameters=FunctionLibApi.Import.get_request_params_api(),
                             tags=[_("function")]
                             )
        @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
        def post(self, request: Request):
            return result.success(FunctionLibSerializer.Import(
                data={'user_id': request.user.id, 'file': request.FILES.get('file')}).import_())

    class Export(APIView):
        authentication_classes = [TokenAuth]

        @action(methods="GET", detail=False)
        @swagger_auto_schema(operation_summary=_("Export function"), operation_id=_("Export function"),
                             manual_parameters=FunctionLibApi.Export.get_request_params_api(),
                             tags=[_("function")]
                             )
        @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
        def get(self, request: Request, id: str):
            return FunctionLibSerializer.Operate(
                data={'id': id, 'user_id': request.user.id}).export()