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
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import PermissionConstants, CompareConstants, Permission, Group, Operate, \
    ViewPermission, RoleConstants
from common.response import result
from common.response.result import get_page_request_params, get_page_api_response, get_api_response
from common.swagger_api.common_api import CommonApi
from dataset.serializers.dataset_serializers import DataSetSerializers


class Dataset(APIView):
    authentication_classes = [TokenAuth]

    class SyncWeb(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary="同步Web站点知识库",
                             operation_id="同步Web站点知识库",
                             manual_parameters=DataSetSerializers.SyncWeb.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=["知识库"])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                            dynamic_tag=keywords.get('dataset_id'))],
            compare=CompareConstants.AND), PermissionConstants.DATASET_EDIT,
            compare=CompareConstants.AND)
        def put(self, request: Request, dataset_id: str):
            return result.success(DataSetSerializers.SyncWeb(
                data={'sync_type': request.query_params.get('sync_type'), 'id': dataset_id,
                      'user_id': str(request.user.id)}).sync())

    class CreateQADataset(APIView):
        authentication_classes = [TokenAuth]
        parser_classes = [MultiPartParser]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary="创建QA知识库",
                             operation_id="创建QA知识库",
                             manual_parameters=DataSetSerializers.Create.CreateQASerializers.get_request_params_api(),
                             responses=get_api_response(
                                 DataSetSerializers.Create.CreateQASerializers.get_response_body_api()),
                             tags=["知识库"]
                             )
        @has_permissions(PermissionConstants.DATASET_CREATE, compare=CompareConstants.AND)
        def post(self, request: Request):
            return result.success(DataSetSerializers.Create(data={'user_id': request.user.id}).save_qa({
                'file_list': request.FILES.getlist('file'),
                'name': request.data.get('name'),
                'desc': request.data.get('desc')
            }))

    class CreateWebDataset(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary="创建web站点知识库",
                             operation_id="创建web站点知识库",
                             request_body=DataSetSerializers.Create.CreateWebSerializers.get_request_body_api(),
                             responses=get_api_response(
                                 DataSetSerializers.Create.CreateWebSerializers.get_response_body_api()),
                             tags=["知识库"]
                             )
        @has_permissions(PermissionConstants.DATASET_CREATE, compare=CompareConstants.AND)
        def post(self, request: Request):
            return result.success(DataSetSerializers.Create(data={'user_id': request.user.id}).save_web(request.data))

    class Application(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="获取知识库可用应用列表",
                             operation_id="获取知识库可用应用列表",
                             manual_parameters=DataSetSerializers.Application.get_request_params_api(),
                             responses=result.get_api_array_response(
                                 DataSetSerializers.Application.get_response_body_api()),
                             tags=["知识库"])
        def get(self, request: Request, dataset_id: str):
            return result.success(DataSetSerializers.Operate(
                data={'id': dataset_id, 'user_id': str(request.user.id)}).list_application())

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary="获取知识库列表",
                         operation_id="获取知识库列表",
                         manual_parameters=DataSetSerializers.Query.get_request_params_api(),
                         responses=result.get_api_array_response(DataSetSerializers.Query.get_response_body_api()),
                         tags=["知识库"])
    @has_permissions(PermissionConstants.DATASET_READ, compare=CompareConstants.AND)
    def get(self, request: Request):
        d = DataSetSerializers.Query(data={**request.query_params, 'user_id': str(request.user.id)})
        d.is_valid()
        return result.success(d.list())

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary="创建知识库",
                         operation_id="创建知识库",
                         request_body=DataSetSerializers.Create.get_request_body_api(),
                         responses=get_api_response(DataSetSerializers.Create.get_response_body_api()),
                         tags=["知识库"]
                         )
    @has_permissions(PermissionConstants.DATASET_CREATE, compare=CompareConstants.AND)
    def post(self, request: Request):
        return result.success(DataSetSerializers.Create(data={'user_id': request.user.id}).save(request.data))

    class HitTest(APIView):
        authentication_classes = [TokenAuth]

        @action(methods="GET", detail=False)
        @swagger_auto_schema(operation_summary="命中测试列表", operation_id="命中测试列表",
                             manual_parameters=CommonApi.HitTestApi.get_request_params_api(),
                             responses=result.get_api_array_response(CommonApi.HitTestApi.get_response_body_api()),
                             tags=["知识库"])
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.USE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        def get(self, request: Request, dataset_id: str):
            return result.success(
                DataSetSerializers.HitTest(data={'id': dataset_id, 'user_id': request.user.id,
                                                 "query_text": request.query_params.get("query_text"),
                                                 "top_number": request.query_params.get("top_number"),
                                                 'similarity': request.query_params.get('similarity'),
                                                 'search_mode': request.query_params.get('search_mode')}).hit_test(
                ))

    class Embedding(APIView):
        authentication_classes = [TokenAuth]

        @action(methods="PUT", detail=False)
        @swagger_auto_schema(operation_summary="重新向量化", operation_id="重新向量化",
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=["知识库"]
                             )
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        def put(self, request: Request, dataset_id: str):
            return result.success(
                DataSetSerializers.Operate(data={'id': dataset_id, 'user_id': request.user.id}).re_embedding())

    class Export(APIView):
        authentication_classes = [TokenAuth]

        @action(methods="GET", detail=False)
        @swagger_auto_schema(operation_summary="导出知识库", operation_id="导出知识库",
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             tags=["知识库"]
                             )
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        def get(self, request: Request, dataset_id: str):
            return DataSetSerializers.Operate(data={'id': dataset_id, 'user_id': request.user.id}).export_excel()

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods="DELETE", detail=False)
        @swagger_auto_schema(operation_summary="删除知识库", operation_id="删除知识库",
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=["知识库"])
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')),
                         lambda r, k: Permission(group=Group.DATASET, operate=Operate.DELETE,
                                                 dynamic_tag=k.get('dataset_id')), compare=CompareConstants.AND)
        def delete(self, request: Request, dataset_id: str):
            operate = DataSetSerializers.Operate(data={'id': dataset_id})
            return result.success(operate.delete())

        @action(methods="GET", detail=False)
        @swagger_auto_schema(operation_summary="查询知识库详情根据知识库id", operation_id="查询知识库详情根据知识库id",
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             responses=get_api_response(DataSetSerializers.Operate.get_response_body_api()),
                             tags=["知识库"])
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.USE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        def get(self, request: Request, dataset_id: str):
            return result.success(DataSetSerializers.Operate(data={'id': dataset_id, 'user_id': request.user.id}).one(
                user_id=request.user.id))

        @action(methods="PUT", detail=False)
        @swagger_auto_schema(operation_summary="修改知识库信息", operation_id="修改知识库信息",
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             request_body=DataSetSerializers.Operate.get_request_body_api(),
                             responses=get_api_response(DataSetSerializers.Operate.get_response_body_api()),
                             tags=["知识库"]
                             )
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        def put(self, request: Request, dataset_id: str):
            return result.success(
                DataSetSerializers.Operate(data={'id': dataset_id, 'user_id': request.user.id}).edit(request.data,
                                                                                                     user_id=request.user.id))

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="获取知识库分页列表",
                             operation_id="获取知识库分页列表",
                             manual_parameters=get_page_request_params(
                                 DataSetSerializers.Query.get_request_params_api()),
                             responses=get_page_api_response(DataSetSerializers.Query.get_response_body_api()),
                             tags=["知识库"]
                             )
        @has_permissions(PermissionConstants.DATASET_READ, compare=CompareConstants.AND)
        def get(self, request: Request, current_page, page_size):
            d = DataSetSerializers.Query(
                data={'name': request.query_params.get('name', None), 'desc': request.query_params.get("desc", None),
                      'user_id': str(request.user.id)})
            d.is_valid()
            return result.success(d.page(current_page, page_size))
