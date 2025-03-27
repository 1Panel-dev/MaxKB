# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： problem.py
    @date：2023/10/23 13:54
    @desc:
"""
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import Permission, Group, Operate
from common.log.log import log
from common.response import result
from common.util.common import query_params_to_single_dict
from dataset.serializers.problem_serializers import ProblemSerializers
from dataset.swagger_api.problem_api import ProblemApi
from django.utils.translation import gettext_lazy as _

from dataset.views import get_dataset_operation_object


class Problem(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary=_('Question list'),
                         operation_id=_('Question list'),
                         manual_parameters=ProblemApi.Query.get_request_params_api(),
                         responses=result.get_api_array_response(ProblemApi.get_response_body_api()),
                         tags=[_('Knowledge Base/Documentation/Paragraph/Question')]
                         )
    @has_permissions(
        lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                dynamic_tag=k.get('dataset_id')))
    def get(self, request: Request, dataset_id: str):
        q = ProblemSerializers.Query(
            data={**query_params_to_single_dict(request.query_params), 'dataset_id': dataset_id})
        q.is_valid(raise_exception=True)
        return result.success(q.list())

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_('Create question'),
                         operation_id=_('Create question'),
                         manual_parameters=ProblemApi.BatchCreate.get_request_params_api(),
                         request_body=ProblemApi.BatchCreate.get_request_body_api(),
                         responses=result.get_api_response(ProblemApi.Query.get_response_body_api()),
                         tags=[_('Knowledge Base/Documentation/Paragraph/Question')])
    @has_permissions(
        lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                dynamic_tag=k.get('dataset_id')))
    @log(menu='problem', operate='Create question',
         get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id'))
         )
    def post(self, request: Request, dataset_id: str):
        return result.success(
            ProblemSerializers.Create(
                data={'dataset_id': dataset_id, 'problem_list': request.data}).batch())

    class Paragraph(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('Get a list of associated paragraphs'),
                             operation_id=_('Get a list of associated paragraphs'),
                             manual_parameters=ProblemApi.Paragraph.get_request_params_api(),
                             responses=result.get_api_array_response(ProblemApi.Paragraph.get_response_body_api()),
                             tags=[_('Knowledge Base/Documentation/Paragraph/Question')])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                    dynamic_tag=k.get('dataset_id')))
        def get(self, request: Request, dataset_id: str, problem_id: str):
            return result.success(ProblemSerializers.Operate(
                data={**query_params_to_single_dict(request.query_params), 'dataset_id': dataset_id,
                      'problem_id': problem_id}).list_paragraph())

    class OperateBatch(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary=_('Batch deletion issues'),
                             operation_id=_('Batch deletion issues'),
                             request_body=
                             ProblemApi.BatchOperate.get_request_body_api(),
                             manual_parameters=ProblemApi.BatchOperate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base/Documentation/Paragraph/Question')])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        @log(menu='problem', operate='Batch deletion issues',
             get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id')))
        def delete(self, request: Request, dataset_id: str):
            return result.success(
                ProblemSerializers.BatchOperate(data={'dataset_id': dataset_id}).delete(request.data))

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_('Batch associated paragraphs'),
                             operation_id=_('Batch associated paragraphs'),
                             request_body=ProblemApi.BatchAssociation.get_request_body_api(),
                             manual_parameters=ProblemApi.BatchOperate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base/Documentation/Paragraph/Question')])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        @log(menu='problem', operate='Batch associated paragraphs',
             get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id')))
        def post(self, request: Request, dataset_id: str):
            return result.success(
                ProblemSerializers.BatchOperate(data={'dataset_id': dataset_id}).association(request.data))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary=_('Delete question'),
                             operation_id=_('Delete question'),
                             manual_parameters=ProblemApi.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=[_('Knowledge Base/Documentation/Paragraph/Question')])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        @log(menu='problem', operate='Delete question',
             get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id')))
        def delete(self, request: Request, dataset_id: str, problem_id: str):
            return result.success(ProblemSerializers.Operate(
                data={**query_params_to_single_dict(request.query_params), 'dataset_id': dataset_id,
                      'problem_id': problem_id}).delete())

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_('Modify question'),
                             operation_id=_('Modify question'),
                             manual_parameters=ProblemApi.Operate.get_request_params_api(),
                             request_body=ProblemApi.Operate.get_request_body_api(),
                             responses=result.get_api_response(ProblemApi.get_response_body_api()),
                             tags=[_('Knowledge Base/Documentation/Paragraph/Question')])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        @log(menu='problem', operate='Modify question',
             get_operation_object=lambda r, keywords: get_dataset_operation_object(keywords.get('dataset_id')))
        def put(self, request: Request, dataset_id: str, problem_id: str):
            return result.success(ProblemSerializers.Operate(
                data={**query_params_to_single_dict(request.query_params), 'dataset_id': dataset_id,
                      'problem_id': problem_id}).edit(request.data))

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('Get the list of questions by page'),
                             operation_id=_('Get the list of questions by page'),
                             manual_parameters=result.get_page_request_params(
                                 ProblemApi.Query.get_request_params_api()),
                             responses=result.get_page_api_response(ProblemApi.get_response_body_api()),
                             tags=[_('Knowledge Base/Documentation/Paragraph/Question')])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                    dynamic_tag=k.get('dataset_id')))
        def get(self, request: Request, dataset_id: str, current_page, page_size):
            d = ProblemSerializers.Query(
                data={**query_params_to_single_dict(request.query_params), 'dataset_id': dataset_id})
            d.is_valid(raise_exception=True)
            return result.success(d.page(current_page, page_size))
