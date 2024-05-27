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
from common.constants.permission_constants import Permission, Group, Operate, CompareConstants
from common.response import result
from common.util.common import query_params_to_single_dict
from dataset.serializers.common_serializers import BatchSerializer
from dataset.serializers.document_serializers import DocumentSerializers, DocumentWebInstanceSerializer
from dataset.swagger_api.document_api import DocumentApi


class Template(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary="获取QA模版",
                         operation_id="获取QA模版",
                         manual_parameters=DocumentSerializers.Export.get_request_params_api(),
                         tags=["知识库/文档"])
    def get(self, request: Request):
        return DocumentSerializers.Export(data={'type': request.query_params.get('type')}).export(with_valid=True)


class WebDocument(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary="创建Web站点文档",
                         operation_id="创建Web站点文档",
                         request_body=DocumentWebInstanceSerializer.get_request_body_api(),
                         manual_parameters=DocumentSerializers.Create.get_request_params_api(),
                         responses=result.get_api_response(DocumentSerializers.Operate.get_response_body_api()),
                         tags=["知识库/文档"])
    @has_permissions(
        lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                dynamic_tag=k.get('dataset_id')))
    def post(self, request: Request, dataset_id: str):
        return result.success(
            DocumentSerializers.Create(data={'dataset_id': dataset_id}).save_web(request.data, with_valid=True))


class QaDocument(APIView):
    authentication_classes = [TokenAuth]
    parser_classes = [MultiPartParser]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary="导入QA并创建文档",
                         operation_id="导入QA并创建文档",
                         manual_parameters=DocumentWebInstanceSerializer.get_request_params_api(),
                         responses=result.get_api_response(DocumentSerializers.Create.get_response_body_api()),
                         tags=["知识库/文档"])
    @has_permissions(
        lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                dynamic_tag=k.get('dataset_id')))
    def post(self, request: Request, dataset_id: str):
        return result.success(
            DocumentSerializers.Create(data={'dataset_id': dataset_id}).save_qa(
                {'file_list': request.FILES.getlist('file')},
                with_valid=True))


class Document(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary="创建文档",
                         operation_id="创建文档",
                         request_body=DocumentSerializers.Create.get_request_body_api(),
                         manual_parameters=DocumentSerializers.Create.get_request_params_api(),
                         responses=result.get_api_response(DocumentSerializers.Operate.get_response_body_api()),
                         tags=["知识库/文档"])
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
                         responses=result.get_api_response(DocumentSerializers.Query.get_response_body_api()),
                         tags=["知识库/文档"])
    @has_permissions(
        lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                dynamic_tag=k.get('dataset_id')))
    def get(self, request: Request, dataset_id: str):
        d = DocumentSerializers.Query(
            data={**query_params_to_single_dict(request.query_params), 'dataset_id': dataset_id})
        d.is_valid(raise_exception=True)
        return result.success(d.list())

    class BatchEditHitHandling(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary="批量修改文档命中处理方式",
                             operation_id="批量修改文档命中处理方式",
                             request_body=
                             DocumentApi.BatchEditHitHandlingApi.get_request_body_api(),
                             manual_parameters=DocumentSerializers.Create.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=["知识库/文档"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def put(self, request: Request, dataset_id: str):
            return result.success(
                DocumentSerializers.Batch(data={'dataset_id': dataset_id}).batch_edit_hit_handling(request.data))

    class Batch(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary="批量创建文档",
                             operation_id="批量创建文档",
                             request_body=
                             DocumentSerializers.Batch.get_request_body_api(),
                             manual_parameters=DocumentSerializers.Create.get_request_params_api(),
                             responses=result.get_api_array_response(
                                 DocumentSerializers.Operate.get_response_body_api()),
                             tags=["知识库/文档"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def post(self, request: Request, dataset_id: str):
            return result.success(DocumentSerializers.Batch(data={'dataset_id': dataset_id}).batch_save(request.data))

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary="批量同步文档",
                             operation_id="批量同步文档",
                             request_body=
                             BatchSerializer.get_request_body_api(),
                             manual_parameters=DocumentSerializers.Create.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=["知识库/文档"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def put(self, request: Request, dataset_id: str):
            return result.success(DocumentSerializers.Batch(data={'dataset_id': dataset_id}).batch_sync(request.data))

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary="批量删除文档",
                             operation_id="批量删除文档",
                             request_body=
                             BatchSerializer.get_request_body_api(),
                             manual_parameters=DocumentSerializers.Create.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=["知识库/文档"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def delete(self, request: Request, dataset_id: str):
            return result.success(DocumentSerializers.Batch(data={'dataset_id': dataset_id}).batch_delete(request.data))

    class SyncWeb(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary="同步web站点类型",
                             operation_id="同步web站点类型",
                             manual_parameters=DocumentSerializers.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=["知识库/文档"]
                             )
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def put(self, request: Request, dataset_id: str, document_id: str):
            return result.success(
                DocumentSerializers.Sync(data={'document_id': document_id, 'dataset_id': dataset_id}).sync(
                ))

    class Refresh(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary="刷新文档向量库",
                             operation_id="刷新文档向量库",
                             manual_parameters=DocumentSerializers.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=["知识库/文档"]
                             )
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def put(self, request: Request, dataset_id: str, document_id: str):
            return result.success(
                DocumentSerializers.Operate(data={'document_id': document_id, 'dataset_id': dataset_id}).refresh(
                ))

    class Migrate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary="批量迁移文档",
                             operation_id="批量迁移文档",
                             manual_parameters=DocumentSerializers.Migrate.get_request_params_api(),
                             request_body=DocumentSerializers.Migrate.get_request_body_api(),
                             responses=result.get_api_response(DocumentSerializers.Operate.get_response_body_api()),
                             tags=["知识库/文档"]
                             )
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')),
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('target_dataset_id')),
            compare=CompareConstants.AND
        )
        def put(self, request: Request, dataset_id: str, target_dataset_id: str):
            return result.success(
                DocumentSerializers.Migrate(
                    data={'dataset_id': dataset_id, 'target_dataset_id': target_dataset_id,
                          'document_id_list': request.data}).migrate(

                ))

    class Export(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="导出文档",
                             operation_id="导出文档",
                             manual_parameters=DocumentSerializers.Operate.get_request_params_api(),
                             tags=["知识库/文档"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                    dynamic_tag=k.get('dataset_id')))
        def get(self, request: Request, dataset_id: str, document_id: str):
            return DocumentSerializers.Operate(data={'document_id': document_id, 'dataset_id': dataset_id}).export()

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="获取文档详情",
                             operation_id="获取文档详情",
                             manual_parameters=DocumentSerializers.Operate.get_request_params_api(),
                             responses=result.get_api_response(DocumentSerializers.Operate.get_response_body_api()),
                             tags=["知识库/文档"])
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
                             responses=result.get_api_response(DocumentSerializers.Operate.get_response_body_api()),
                             tags=["知识库/文档"]
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
                             responses=result.get_default_response(),
                             tags=["知识库/文档"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def delete(self, request: Request, dataset_id: str, document_id: str):
            operate = DocumentSerializers.Operate(data={'document_id': document_id, 'dataset_id': dataset_id})
            operate.is_valid(raise_exception=True)
            return result.success(operate.delete())

    class SplitPattern(APIView):
        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="获取分段标识列表",
                             operation_id="获取分段标识列表",
                             tags=["知识库/文档"],
                             security=[])
        def get(self, request: Request):
            return result.success(DocumentSerializers.SplitPattern.list())

    class Split(APIView):
        parser_classes = [MultiPartParser]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary="分段文档",
                             operation_id="分段文档",
                             manual_parameters=DocumentSerializers.Split.get_request_params_api(),
                             tags=["知识库/文档"],
                             security=[])
        def post(self, request: Request):
            split_data = {'file': request.FILES.getlist('file')}
            request_data = request.data
            if 'patterns' in request.data and request.data.get('patterns') is not None and len(
                    request.data.get('patterns')) > 0:
                split_data.__setitem__('patterns', request_data.getlist('patterns'))
            if 'limit' in request.data:
                split_data.__setitem__('limit', request_data.get('limit'))
            if 'with_filter' in request.data:
                split_data.__setitem__('with_filter', request_data.get('with_filter'))
            ds = DocumentSerializers.Split(
                data=split_data)
            ds.is_valid(raise_exception=True)
            return result.success(ds.parse())

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="获取知识库分页列表",
                             operation_id="获取知识库分页列表",
                             manual_parameters=DocumentSerializers.Query.get_request_params_api(),
                             responses=result.get_page_api_response(DocumentSerializers.Query.get_response_body_api()),
                             tags=["知识库/文档"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                    dynamic_tag=k.get('dataset_id')))
        def get(self, request: Request, dataset_id: str, current_page, page_size):
            d = DocumentSerializers.Query(
                data={**query_params_to_single_dict(request.query_params), 'dataset_id': dataset_id})
            d.is_valid(raise_exception=True)
            return result.success(d.page(current_page, page_size))
