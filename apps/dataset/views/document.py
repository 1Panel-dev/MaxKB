# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： document.py
    @date：2023/9/22 11:32
    @desc:
"""

from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import Permission, Group, Operate, CompareConstants
from common.log.log import log
from common.response import result
from common.util.common import query_params_to_single_dict
from dataset.serializers.common_serializers import BatchSerializer
from dataset.serializers.document_serializers import DocumentSerializers, DocumentWebInstanceSerializer
from dataset.swagger_api.document_api import DocumentApi
from dataset.views.common import get_dataset_document_operation_object, get_dataset_operation_object, \
    get_document_operation_object_batch, get_document_operation_object


class Template(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary=_('Get QA template'),
                         operation_id=_('Get QA template'),
                         manual_parameters=DocumentSerializers.Export.get_request_params_api(),
                         tags=[_('Knowledge Base/Documentation')])
    def get(self, request: Request):
        return DocumentSerializers.Export(data={'type': request.query_params.get('type')}).export(with_valid=True)


class TableTemplate(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary=_('Get form template'),
                         operation_id=_('Get form template'),
                         manual_parameters=DocumentSerializers.Export.get_request_params_api(),
                         tags=[_('Knowledge Base/Documentation')])
    def get(self, request: Request):
        return DocumentSerializers.Export(data={'type': request.query_params.get('type')}).table_export(with_valid=True)


class WebDocument(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_('Create Web site documents'),
                         operation_id=_('Create Web site documents'),
                         request_body=DocumentWebInstanceSerializer.get_request_body_api(),
                         manual_parameters=DocumentSerializers.Create.get_request_params_api(),
                         responses=result.get_api_response(DocumentSerializers.Operate.get_response_body_api()),
                         tags=[_('Knowledge Base/Documentation')])
    @has_permissions(
        lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                dynamic_tag=k.get('dataset_id')))
    @log(menu='document', operate="Create Web site documents",
         get_operation_object=lambda r, keywords: get_dataset_document_operation_object(
             get_dataset_operation_object(keywords.get('dataset_id')),
             {'name': f'[{",".join([url for url in r.data.get("source_url_list", [])])}]',
              'document_list': [{'name': url} for url in r.data.get("source_url_list", [])]}))
    def post(self, request: Request, dataset_id: str):
        return result.success(
            DocumentSerializers.Create(data={'dataset_id': dataset_id}).save_web(request.data, with_valid=True))


class QaDocument(APIView):
    authentication_classes = [TokenAuth]
    parser_classes = [MultiPartParser]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_('Import QA and create documentation'),
                         operation_id=_('Import QA and create documentation'),
                         manual_parameters=DocumentWebInstanceSerializer.get_request_params_api(),
                         responses=result.get_api_response(DocumentSerializers.Create.get_response_body_api()),
                         tags=[_('Knowledge Base/Documentation')])
    @has_permissions(
        lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                dynamic_tag=k.get('dataset_id')))
    @log(menu='document', operate="Import QA and create documentation",
         get_operation_object=lambda r, keywords: get_dataset_document_operation_object(
             get_dataset_operation_object(keywords.get('dataset_id')),
             {'name': f'[{",".join([file.name for file in r.FILES.getlist("file")])}]',
              'document_list': [{'name': file.name} for file in r.FILES.getlist("file")]}))
    def post(self, request: Request, dataset_id: str):
        return result.success(
            DocumentSerializers.Create(data={'dataset_id': dataset_id}).save_qa(
                {'file_list': request.FILES.getlist('file')},
                with_valid=True))


class TableDocument(APIView):
    authentication_classes = [TokenAuth]
    parser_classes = [MultiPartParser]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_('Import tables and create documents'),
                         operation_id=_('Import tables and create documents'),
                         manual_parameters=DocumentWebInstanceSerializer.get_request_params_api(),
                         responses=result.get_api_response(DocumentSerializers.Create.get_response_body_api()),
                         tags=[_('Knowledge Base/Documentation')])
    @has_permissions(
        lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                dynamic_tag=k.get('dataset_id')))
    @log(menu='document', operate="Import tables and create documents",
         get_operation_object=lambda r, keywords: get_dataset_document_operation_object(
             get_dataset_operation_object(keywords.get('dataset_id')),
             {'name': f'[{",".join([file.name for file in r.FILES.getlist("file")])}]',
              'document_list': [{'name': file.name} for file in r.FILES.getlist("file")]}))
    def post(self, request: Request, dataset_id: str):
        return result.success(
            DocumentSerializers.Create(data={'dataset_id': dataset_id}).save_table(
                {'file_list': request.FILES.getlist('file')},
                with_valid=True))


class Document(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_('Create document'),
                         operation_id=_('Create document'),
                         request_body=DocumentSerializers.Create.get_request_body_api(),
                         manual_parameters=DocumentSerializers.Create.get_request_params_api(),
                         responses=result.get_api_response(DocumentSerializers.Operate.get_response_body_api()),
                         tags=[_('Knowledge Base/Documentation')])
    @has_permissions(
        lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                dynamic_tag=k.get('dataset_id')))
    @log(menu='document', operate="Create document",
         get_operation_object=lambda r, keywords: get_dataset_document_operation_object(
             get_dataset_operation_object(keywords.get('dataset_id')),
             {'name': r.data.get('name')}))
    def post(self, request: Request, dataset_id: str):
        return result.success(
            DocumentSerializers.Create(data={'dataset_id': dataset_id}).save(request.data, with_valid=True))

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary=_('Document list'),
                         operation_id=_('Document list'),
                         manual_parameters=DocumentSerializers.Query.get_request_params_api(),
                         responses=result.get_api_response(DocumentSerializers.Query.get_response_body_api()),
                         tags=[_('Knowledge Base/Documentation')])
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
        @swagger_auto_schema(operation_summary=_('Modify document hit processing methods in batches'),
                             operation_id=_('Modify document hit processing methods in batches'),
                             request_body=
                             DocumentApi.BatchEditHitHandlingApi.get_request_body_api(),
                             manual_parameters=DocumentSerializers.Create.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base/Documentation')])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        @log(menu='document', operate="Modify document hit processing methods in batches",
             get_operation_object=lambda r, keywords: get_dataset_document_operation_object(
                 get_dataset_operation_object(keywords.get('dataset_id')),
                 get_document_operation_object_batch(r.data.get('id_list'))))
        def put(self, request: Request, dataset_id: str):
            return result.success(
                DocumentSerializers.Batch(data={'dataset_id': dataset_id}).batch_edit_hit_handling(request.data))

    class Batch(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_('Create documents in batches'),
                             operation_id=_('Create documents in batches'),
                             request_body=
                             DocumentSerializers.Batch.get_request_body_api(),
                             manual_parameters=DocumentSerializers.Create.get_request_params_api(),
                             responses=result.get_api_array_response(
                                 DocumentSerializers.Operate.get_response_body_api()),
                             tags=[_('Knowledge Base/Documentation')])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        @log(menu='document', operate="Create documents in batches",
             get_operation_object=lambda r, keywords: get_dataset_document_operation_object(
                 get_dataset_operation_object(keywords.get('dataset_id')),
                 {'name': f'[{",".join([document.get("name") for document in r.data])}]',
                  'document_list': r.data})
             )
        def post(self, request: Request, dataset_id: str):
            return result.success(DocumentSerializers.Batch(data={'dataset_id': dataset_id}).batch_save(request.data))

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_('Batch sync documents'),
                             operation_id=_('Batch sync documents'),
                             request_body=
                             BatchSerializer.get_request_body_api(),
                             manual_parameters=DocumentSerializers.Create.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base/Documentation')])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        @log(menu='document', operate="Batch sync documents",
             get_operation_object=lambda r, keywords: get_dataset_document_operation_object(
                 get_dataset_operation_object(keywords.get('dataset_id')),
                 get_document_operation_object_batch(r.data.get('id_list')))
             )
        def put(self, request: Request, dataset_id: str):
            return result.success(DocumentSerializers.Batch(data={'dataset_id': dataset_id}).batch_sync(request.data))

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary=_('Delete documents in batches'),
                             operation_id=_('Delete documents in batches'),
                             request_body=
                             BatchSerializer.get_request_body_api(),
                             manual_parameters=DocumentSerializers.Create.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base/Documentation')])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        @log(menu='document', operate="Delete documents in batches",
             get_operation_object=lambda r, keywords: get_dataset_document_operation_object(
                 get_dataset_operation_object(keywords.get('dataset_id')),
                 get_document_operation_object_batch(r.data.get('id_list'))))
        def delete(self, request: Request, dataset_id: str):
            return result.success(DocumentSerializers.Batch(data={'dataset_id': dataset_id}).batch_delete(request.data))

    class SyncWeb(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_('Synchronize web site types'),
                             operation_id=_('Synchronize web site types'),
                             manual_parameters=DocumentSerializers.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base/Documentation')]
                             )
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        @log(menu='document', operate="Synchronize web site types",
             get_operation_object=lambda r, keywords: get_dataset_document_operation_object(
                 get_dataset_operation_object(keywords.get('dataset_id')),
                 get_document_operation_object(keywords.get('document_id'))
             ))
        def put(self, request: Request, dataset_id: str, document_id: str):
            return result.success(
                DocumentSerializers.Sync(data={'document_id': document_id, 'dataset_id': dataset_id}).sync(
                ))

    class CancelTask(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_('Cancel task'),
                             operation_id=_('Cancel task'),
                             manual_parameters=DocumentSerializers.Operate.get_request_params_api(),
                             request_body=DocumentApi.Cancel.get_request_body_api(),
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base/Documentation')]
                             )
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        @log(menu='document', operate="Cancel task",
             get_operation_object=lambda r, keywords: get_dataset_document_operation_object(
                 get_dataset_operation_object(keywords.get('dataset_id')),
                 get_document_operation_object(keywords.get('document_id'))
             ))
        def put(self, request: Request, dataset_id: str, document_id: str):
            return result.success(
                DocumentSerializers.Operate(data={'document_id': document_id, 'dataset_id': dataset_id}).cancel(
                    request.data
                ))

        class Batch(APIView):
            authentication_classes = [TokenAuth]

            @action(methods=['PUT'], detail=False)
            @swagger_auto_schema(operation_summary=_('Cancel tasks in batches'),
                                 operation_id=_('Cancel tasks in batches'),
                                 request_body=DocumentApi.BatchCancel.get_request_body_api(),
                                 manual_parameters=DocumentSerializers.Create.get_request_params_api(),
                                 responses=result.get_default_response(),
                                 tags=[_('Knowledge Base/Documentation')]
                                 )
            @has_permissions(
                lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                        dynamic_tag=k.get('dataset_id')))
            @log(menu='document', operate="Cancel tasks in batches",
                 get_operation_object=lambda r, keywords: get_dataset_document_operation_object(
                     get_dataset_operation_object(keywords.get('dataset_id')),
                     get_document_operation_object_batch(r.data.get('id_list'))
                 )
                 )
            def put(self, request: Request, dataset_id: str):
                return result.success(
                    DocumentSerializers.Batch(data={'dataset_id': dataset_id}).batch_cancel(request.data))

    class Refresh(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_('Refresh document vector library'),
                             operation_id=_('Refresh document vector library'),
                             request_body=DocumentApi.EmbeddingState.get_request_body_api(),
                             manual_parameters=DocumentSerializers.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base/Documentation')]
                             )
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        @log(menu='document', operate="Refresh document vector library",
             get_operation_object=lambda r, keywords: get_dataset_document_operation_object(
                 get_dataset_operation_object(keywords.get('dataset_id')),
                 get_document_operation_object(keywords.get('document_id'))
             )
             )
        def put(self, request: Request, dataset_id: str, document_id: str):
            return result.success(
                DocumentSerializers.Operate(data={'document_id': document_id, 'dataset_id': dataset_id}).refresh(
                    request.data.get('state_list')
                ))

    class BatchRefresh(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_('Batch refresh document vector library'),
                             operation_id=_('Batch refresh document vector library'),
                             request_body=
                             DocumentApi.BatchEditHitHandlingApi.get_request_body_api(),
                             manual_parameters=DocumentSerializers.Create.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base/Documentation')])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        @log(menu='document', operate="Batch refresh document vector library",
             get_operation_object=lambda r, keywords: get_dataset_document_operation_object(
                 get_dataset_operation_object(keywords.get('dataset_id')),
                 get_document_operation_object_batch(r.data.get('id_list'))
             )
             )
        def put(self, request: Request, dataset_id: str):
            return result.success(
                DocumentSerializers.Batch(data={'dataset_id': dataset_id}).batch_refresh(request.data))

    class Migrate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_('Migrate documents in batches'),
                             operation_id=_('Migrate documents in batches'),
                             manual_parameters=DocumentSerializers.Migrate.get_request_params_api(),
                             request_body=DocumentSerializers.Migrate.get_request_body_api(),
                             responses=result.get_api_response(DocumentSerializers.Operate.get_response_body_api()),
                             tags=[_('Knowledge Base/Documentation')]
                             )
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')),
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('target_dataset_id')),
            compare=CompareConstants.AND
        )
        @log(menu='document', operate="Migrate documents in batches",
             get_operation_object=lambda r, keywords: get_dataset_document_operation_object(
                 get_dataset_operation_object(keywords.get('dataset_id')),
                 get_document_operation_object_batch(r.data)
             )
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
        @swagger_auto_schema(operation_summary=_('Export document'),
                             operation_id=_('Export document'),
                             manual_parameters=DocumentSerializers.Operate.get_request_params_api(),
                             tags=[_('Knowledge Base/Documentation')])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        @log(menu='document', operate="Export document",
             get_operation_object=lambda r, keywords: get_dataset_document_operation_object(
                 get_dataset_operation_object(keywords.get('dataset_id')),
                 get_document_operation_object(keywords.get('document_id'))
             )
             )
        def get(self, request: Request, dataset_id: str, document_id: str):
            return DocumentSerializers.Operate(data={'document_id': document_id, 'dataset_id': dataset_id}).export()

    class ExportZip(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('Export Zip document'),
                             operation_id=_('Export Zip document'),
                             manual_parameters=DocumentSerializers.Operate.get_request_params_api(),
                             tags=[_('Knowledge Base/Documentation')])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        @log(menu='document', operate="Export Zip document",
             get_operation_object=lambda r, keywords: get_dataset_document_operation_object(
                 get_dataset_operation_object(keywords.get('dataset_id')),
                 get_document_operation_object(keywords.get('document_id'))
             )
             )
        def get(self, request: Request, dataset_id: str, document_id: str):
            return DocumentSerializers.Operate(data={'document_id': document_id, 'dataset_id': dataset_id}).export_zip()

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('Get document details'),
                             operation_id=_('Get document details'),
                             manual_parameters=DocumentSerializers.Operate.get_request_params_api(),
                             responses=result.get_api_response(DocumentSerializers.Operate.get_response_body_api()),
                             tags=[_('Knowledge Base/Documentation')])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                    dynamic_tag=k.get('dataset_id')))
        def get(self, request: Request, dataset_id: str, document_id: str):
            operate = DocumentSerializers.Operate(data={'document_id': document_id, 'dataset_id': dataset_id})
            operate.is_valid(raise_exception=True)
            return result.success(operate.one())

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_('Modify document'),
                             operation_id=_('Modify document'),
                             manual_parameters=DocumentSerializers.Operate.get_request_params_api(),
                             request_body=DocumentSerializers.Operate.get_request_body_api(),
                             responses=result.get_api_response(DocumentSerializers.Operate.get_response_body_api()),
                             tags=[_('Knowledge Base/Documentation')]
                             )
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        @log(menu='document', operate="Modify document",
             get_operation_object=lambda r, keywords: get_dataset_document_operation_object(
                 get_dataset_operation_object(keywords.get('dataset_id')),
                 get_document_operation_object(keywords.get('document_id'))
             )
             )
        def put(self, request: Request, dataset_id: str, document_id: str):
            return result.success(
                DocumentSerializers.Operate(data={'document_id': document_id, 'dataset_id': dataset_id}).edit(
                    request.data,
                    with_valid=True))

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary=_('Delete document'),
                             operation_id=_('Delete document'),
                             manual_parameters=DocumentSerializers.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base/Documentation')])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        @log(menu='document', operate="Delete document",
             get_operation_object=lambda r, keywords: get_dataset_document_operation_object(
                 get_dataset_operation_object(keywords.get('dataset_id')),
                 get_document_operation_object(keywords.get('document_id'))
             )
             )
        def delete(self, request: Request, dataset_id: str, document_id: str):
            operate = DocumentSerializers.Operate(data={'document_id': document_id, 'dataset_id': dataset_id})
            operate.is_valid(raise_exception=True)
            return result.success(operate.delete())

    class SplitPattern(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('Get a list of segment IDs'),
                             operation_id=_('Get a list of segment IDs'),
                             tags=[_('Knowledge Base/Documentation')])
        def get(self, request: Request):
            return result.success(DocumentSerializers.SplitPattern.list())

    class Split(APIView):
        authentication_classes = [TokenAuth]
        parser_classes = [MultiPartParser]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_('Segmented document'),
                             operation_id=_('Segmented document'),
                             manual_parameters=DocumentSerializers.Split.get_request_params_api(),
                             tags=[_('Knowledge Base/Documentation')])
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
        @swagger_auto_schema(operation_summary=_('Get the knowledge base paginated list'),
                             operation_id=_('Get the knowledge base paginated list'),
                             manual_parameters=DocumentSerializers.Query.get_request_params_api(),
                             responses=result.get_page_api_response(DocumentSerializers.Query.get_response_body_api()),
                             tags=[_('Knowledge Base/Documentation')])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                    dynamic_tag=k.get('dataset_id')))
        def get(self, request: Request, dataset_id: str, current_page, page_size):
            d = DocumentSerializers.Query(
                data={**query_params_to_single_dict(request.query_params), 'dataset_id': dataset_id})
            d.is_valid(raise_exception=True)
            return result.success(d.page(current_page, page_size))

    class BatchGenerateRelated(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        @log(menu='document', operate="Batch generate related documents",
             get_operation_object=lambda r, keywords: get_dataset_document_operation_object(
                 get_dataset_operation_object(keywords.get('dataset_id')),
                 get_document_operation_object_batch(r.data.get('document_id_list'))
             )
             )
        def put(self, request: Request, dataset_id: str):
            return result.success(DocumentSerializers.BatchGenerateRelated(data={'dataset_id': dataset_id})
                                  .batch_generate_related(request.data))
