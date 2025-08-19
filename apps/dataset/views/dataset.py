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

import dataset.models
from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import PermissionConstants, CompareConstants, Permission, Group, Operate, \
    ViewPermission, RoleConstants
from common.log.log import log
from common.response import result
from common.response.result import get_page_request_params, get_page_api_response, get_api_response
from common.swagger_api.common_api import CommonApi
from dataset.serializers.common_serializers import GenerateRelatedSerializer
from dataset.serializers.dataset_serializers import DataSetSerializers
from dataset.views.common import get_dataset_operation_object
from setting.serializers.provider_serializers import ModelSerializer
from django.utils.translation import gettext_lazy as _


class Dataset(APIView):
    authentication_classes = [TokenAuth]

    class SyncWeb(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_("Synchronize the knowledge base of the website"),
                             operation_id=_("Synchronize the knowledge base of the website"),
                             manual_parameters=DataSetSerializers.SyncWeb.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base')])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                            dynamic_tag=keywords.get('dataset_id'))],
            compare=CompareConstants.AND), PermissionConstants.DATASET_EDIT,
            compare=CompareConstants.AND)
        @log(menu='Knowledge Base', operate="Synchronize the knowledge base of the website",
             get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id')))
        def put(self, request: Request, dataset_id: str):
            return result.success(DataSetSerializers.SyncWeb(
                data={'sync_type': request.query_params.get('sync_type'), 'id': dataset_id,
                      'user_id': str(request.user.id)}).sync())

    class CreateQADataset(APIView):
        authentication_classes = [TokenAuth]
        parser_classes = [MultiPartParser]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_("Create QA knowledge base"),
                             operation_id=_("Create QA knowledge base"),
                             manual_parameters=DataSetSerializers.Create.CreateQASerializers.get_request_params_api(),
                             responses=get_api_response(
                                 DataSetSerializers.Create.CreateQASerializers.get_response_body_api()),
                             tags=[_('Knowledge Base')]
                             )
        @has_permissions(PermissionConstants.DATASET_CREATE, compare=CompareConstants.AND)
        @log(menu='Knowledge Base', operate="Create QA knowledge base",
             get_operation_object=lambda r, keywords: {'name': r.data.get('name'), 'desc': r.data.get('desc'),
                                                       'file_list': r.FILES.getlist('file')})
        def post(self, request: Request):
            return result.success(DataSetSerializers.Create(data={'user_id': request.user.id}).save_qa({
                'file_list': request.FILES.getlist('file'),
                'name': request.data.get('name'),
                'desc': request.data.get('desc')
            }))

    class CreateWebDataset(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_('Create a web site knowledge base'),
                             operation_id=_('Create a web site knowledge base'),
                             request_body=DataSetSerializers.Create.CreateWebSerializers.get_request_body_api(),
                             responses=get_api_response(
                                 DataSetSerializers.Create.CreateWebSerializers.get_response_body_api()),
                             tags=[_('Knowledge Base')]
                             )
        @has_permissions(PermissionConstants.DATASET_CREATE, compare=CompareConstants.AND)
        @log(menu='Knowledge Base', operate="Create a web site knowledge base",
             get_operation_object=lambda r, keywords: {'name': r.data.get('name'), 'desc': r.data.get('desc'),
                                                       'file_list': r.FILES.getlist('file'),
                                                       'meta': {'source_url': r.data.get('source_url'),
                                                                'selector': r.data.get('selector'),
                                                                'embedding_mode_id': r.data.get('embedding_mode_id')}}
             )
        def post(self, request: Request):
            return result.success(DataSetSerializers.Create(data={'user_id': request.user.id}).save_web(request.data))

    class Application(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('Get a list of applications available in the knowledge base'),
                             operation_id=_('Get a list of applications available in the knowledge base'),
                             manual_parameters=DataSetSerializers.Application.get_request_params_api(),
                             responses=result.get_api_array_response(
                                 DataSetSerializers.Application.get_response_body_api()),
                             tags=[_('Knowledge Base')])
        def get(self, request: Request, dataset_id: str):
            return result.success(DataSetSerializers.Operate(
                data={'id': dataset_id, 'user_id': str(request.user.id)}).list_application())

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary=_('Get a list of knowledge bases'),
                         operation_id=_('Get a list of knowledge bases'),
                         manual_parameters=DataSetSerializers.Query.get_request_params_api(),
                         responses=result.get_api_array_response(DataSetSerializers.Query.get_response_body_api()),
                         tags=[_('Knowledge Base')])
    @has_permissions(PermissionConstants.DATASET_READ, compare=CompareConstants.AND)
    def get(self, request: Request):
        data = {key: str(value) for key, value in request.query_params.items()}
        d = DataSetSerializers.Query(data={**data, 'user_id': str(request.user.id)})
        d.is_valid()
        return result.success(d.list())

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_('Create a knowledge base'),
                         operation_id=_('Create a knowledge base'),
                         request_body=DataSetSerializers.Create.get_request_body_api(),
                         responses=get_api_response(DataSetSerializers.Create.get_response_body_api()),
                         tags=[_('Knowledge Base')]
                         )
    @has_permissions(PermissionConstants.DATASET_CREATE, compare=CompareConstants.AND)
    @log(menu='Knowledge Base', operate="Create a knowledge base",
         get_operation_object=lambda r, keywords: {'name': r.data.get('name'), 'desc': r.data.get('desc')})
    def post(self, request: Request):
        return result.success(DataSetSerializers.Create(data={'user_id': request.user.id}).save(request.data))

    class HitTest(APIView):
        authentication_classes = [TokenAuth]

        @action(methods="GET", detail=False)
        @swagger_auto_schema(operation_summary=_('Hit test list'), operation_id=_('Hit test list'),
                             manual_parameters=CommonApi.HitTestApi.get_request_params_api(),
                             responses=result.get_api_array_response(CommonApi.HitTestApi.get_response_body_api()),
                             tags=[_('Knowledge Base')])
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
        @swagger_auto_schema(operation_summary=_('Re-vectorize'), operation_id=_('Re-vectorize'),
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base')]
                             )
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        @log(menu='Knowledge Base', operate="Re-vectorize",
             get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id')))
        def put(self, request: Request, dataset_id: str):
            return result.success(
                DataSetSerializers.Operate(data={'id': dataset_id, 'user_id': request.user.id}).re_embedding())

    class GenerateRelated(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_('Generate related'), operation_id=_('Generate related'),
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             request_body=GenerateRelatedSerializer.get_request_body_api(),
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base')]
                             )
        @log(menu='document', operate="Generate related documents",
             get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id'))
             )
        def put(self, request: Request, dataset_id: str):
            return result.success(
                DataSetSerializers.Operate(data={'id': dataset_id, 'user_id': request.user.id}).generate_related(
                    request.data))

    class Export(APIView):
        authentication_classes = [TokenAuth]

        @action(methods="GET", detail=False)
        @swagger_auto_schema(operation_summary=_('Export knowledge base'), operation_id=_('Export knowledge base'),
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             tags=[_('Knowledge Base')]
                             )
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        @log(menu='Knowledge Base', operate="Export knowledge base",
             get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id')))
        def get(self, request: Request, dataset_id: str):
            return DataSetSerializers.Operate(data={'id': dataset_id, 'user_id': request.user.id}).export_excel()

    class ExportZip(APIView):
        authentication_classes = [TokenAuth]

        @action(methods="GET", detail=False)
        @swagger_auto_schema(operation_summary=_('Export knowledge base containing images'),
                             operation_id=_('Export knowledge base containing images'),
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             tags=[_('Knowledge Base')]
                             )
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        @log(menu='Knowledge Base', operate="Export knowledge base containing images",
             get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id')))
        def get(self, request: Request, dataset_id: str):
            return DataSetSerializers.Operate(data={'id': dataset_id, 'user_id': request.user.id}).export_zip()

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods="DELETE", detail=False)
        @swagger_auto_schema(operation_summary=_('Delete knowledge base'), operation_id=_('Delete knowledge base'),
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base')])
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')),
                         lambda r, k: Permission(group=Group.DATASET, operate=Operate.DELETE,
                                                 dynamic_tag=k.get('dataset_id')), compare=CompareConstants.AND)
        @log(menu='Knowledge Base', operate="Delete knowledge base",
             get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id')))
        def delete(self, request: Request, dataset_id: str):
            operate = DataSetSerializers.Operate(data={'id': dataset_id})
            return result.success(operate.delete())

        @action(methods="GET", detail=False)
        @swagger_auto_schema(operation_summary=_('Query knowledge base details based on knowledge base id'),
                             operation_id=_('Query knowledge base details based on knowledge base id'),
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             responses=get_api_response(DataSetSerializers.Operate.get_response_body_api()),
                             tags=[_('Knowledge Base')])
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.USE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        def get(self, request: Request, dataset_id: str):
            return result.success(DataSetSerializers.Operate(data={'id': dataset_id, 'user_id': request.user.id}).one(
                user_id=request.user.id))

        @action(methods="PUT", detail=False)
        @swagger_auto_schema(operation_summary=_('Modify knowledge base information'),
                             operation_id=_('Modify knowledge base information'),
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             request_body=DataSetSerializers.Operate.get_request_body_api(),
                             responses=get_api_response(DataSetSerializers.Operate.get_response_body_api()),
                             tags=[_('Knowledge Base')]
                             )
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        @log(menu='Knowledge Base', operate="Modify knowledge base information",
             get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id')))
        def put(self, request: Request, dataset_id: str):
            return result.success(
                DataSetSerializers.Operate(data={'id': dataset_id, 'user_id': request.user.id}).edit(request.data,
                                                                                                     user_id=request.user.id))

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('Get the knowledge base paginated list'),
                             operation_id=_('Get the knowledge base paginated list'),
                             manual_parameters=get_page_request_params(
                                 DataSetSerializers.Query.get_request_params_api()),
                             responses=get_page_api_response(DataSetSerializers.Query.get_response_body_api()),
                             tags=[_('Knowledge Base')]
                             )
        @has_permissions(PermissionConstants.DATASET_READ, compare=CompareConstants.AND)
        def get(self, request: Request, current_page, page_size):
            d = DataSetSerializers.Query(
                data={'name': request.query_params.get('name', None), 'desc': request.query_params.get("desc", None),
                      'user_id': str(request.user.id),
                      'select_user_id': request.query_params.get('select_user_id', None)})
            d.is_valid()
            return result.success(d.page(current_page, page_size))

    class Model(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=["GET"], detail=False)
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                            dynamic_tag=keywords.get('dataset_id'))],
            compare=CompareConstants.AND))
        def get(self, request: Request, dataset_id: str):
            return result.success(
                ModelSerializer.Query(
                    data={'user_id': request.user.id, 'model_type': 'LLM'}).list(
                    with_valid=True)
            )
