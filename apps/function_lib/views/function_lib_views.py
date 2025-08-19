# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： function_lib_views.py
    @date：2024/8/2 17:08
    @desc:
"""
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import RoleConstants
from common.log.log import log
from common.response import result
from function_lib.serializers.function_lib_serializer import FunctionLibSerializer
from function_lib.swagger_api.function_lib_api import FunctionLibApi
from function_lib.views.common import get_function_lib_operation_object


class FunctionLibView(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=["GET"], detail=False)
    @swagger_auto_schema(operation_summary=_('Get function list'),
                         operation_id=_('Get function list'),
                         tags=[_('Function')],
                         manual_parameters=FunctionLibApi.Query.get_request_params_api())
    @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
    @log(menu='Function', operate="Get function list")
    def get(self, request: Request):
        return result.success(
            FunctionLibSerializer.Query(
                data={'name': request.query_params.get('name'),
                      'desc': request.query_params.get('desc'),
                      'function_type': request.query_params.get('function_type'),
                      'user_id': request.user.id}).list())

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_('Create function'),
                         operation_id=_('Create function'),
                         request_body=FunctionLibApi.Create.get_request_body_api(),
                         responses=result.get_api_response(FunctionLibApi.Create.get_response_body_api()),
                         tags=[_('Function')])
    @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
    @log(menu='Function', operate="Create function",
         get_operation_object=lambda r, k: r.data.get('name'))
    def post(self, request: Request):
        return result.success(FunctionLibSerializer.Create(data={'user_id': request.user.id}).insert(request.data))

    class Debug(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_('Debug function'),
                             operation_id=_('Debug function'),
                             request_body=FunctionLibApi.Debug.get_request_body_api(),
                             responses=result.get_default_response(),
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
                             responses=result.get_api_response(FunctionLibApi.Edit.get_request_body_api()),
                             tags=[_('Function')])
        @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
        @log(menu='Function', operate="Update function",
             get_operation_object=lambda r, k: get_function_lib_operation_object(k.get('function_lib_id')))
        def put(self, request: Request, function_lib_id: str):
            return result.success(
                FunctionLibSerializer.Operate(data={'user_id': request.user.id, 'id': function_lib_id}).edit(
                    request.data))

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary=_('Delete function'),
                             operation_id=_('Delete function'),
                             responses=result.get_default_response(),
                             tags=[_('Function')])
        @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
        @log(menu='Function', operate="Delete function",
             get_operation_object=lambda r, k: get_function_lib_operation_object(k.get('function_lib_id')))
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
                          'function_type': request.query_params.get('function_type'),
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
        @log(menu='Function', operate="Import function")
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
        @log(menu='Function', operate="Export function",
             get_operation_object=lambda r, k: get_function_lib_operation_object(k.get('id')))
        def get(self, request: Request, id: str):
            return FunctionLibSerializer.Operate(
                data={'id': id, 'user_id': request.user.id}).export()

    class EditIcon(APIView):
        authentication_classes = [TokenAuth]
        parser_classes = [MultiPartParser]

        @action(methods=['PUT'], detail=False)
        @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
        @log(menu='Function', operate="Edit icon",
             get_operation_object=lambda r, k: get_function_lib_operation_object(k.get('id')))
        def put(self, request: Request, id: str):
            return result.success(
                FunctionLibSerializer.IconOperate(
                    data={'id': id, 'user_id': request.user.id,
                          'image': request.FILES.get('file')}).edit(request.data))

    class AddInternalFun(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
        @log(menu='Function', operate="Add internal function",
             get_operation_object=lambda r, k: get_function_lib_operation_object(k.get('id')))
        def post(self, request: Request, id: str):
            return result.success(
                FunctionLibSerializer.InternalFunction(
                    data={'id': id, 'user_id': request.user.id, 'name': request.data.get('name')})
                .add())
