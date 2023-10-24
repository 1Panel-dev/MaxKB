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
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import Permission, Group, Operate
from common.response import result
from dataset.serializers.problem_serializers import ProblemSerializers


class Problem(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary="添加关联问题",
                         operation_id="添加段落关联问题",
                         manual_parameters=ProblemSerializers.Create.get_request_params_api(),
                         request_body=ProblemSerializers.Create.get_request_body_api(),
                         responses=result.get_api_response(ProblemSerializers.Operate.get_response_body_api()))
    @has_permissions(
        lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                dynamic_tag=k.get('dataset_id')))
    def post(self, request: Request, dataset_id: str, document_id: str, paragraph_id: str):
        return result.success(ProblemSerializers.Create(
            data={"dataset_id": dataset_id, 'document_id': document_id, 'paragraph_id': paragraph_id}).save(
            request.data, with_valid=True))

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary="获取段落问题列表",
                         operation_id="获取段落问题列表",
                         manual_parameters=ProblemSerializers.Query.get_request_params_api(),
                         responses=result.get_api_array_response(ProblemSerializers.Operate.get_response_body_api()))
    @has_permissions(
        lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                dynamic_tag=k.get('dataset_id')))
    def get(self, request: Request, dataset_id: str, document_id: str, paragraph_id: str):
        return result.success(ProblemSerializers.Query(
            data={"dataset_id": dataset_id, 'document_id': document_id, 'paragraph_id': paragraph_id}).list(
            with_valid=True))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary="删除段落问题",
                             operation_id="删除段落问题",
                             manual_parameters=ProblemSerializers.Query.get_request_params_api(),
                             responses=result.get_default_response())
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def delete(self, request: Request, dataset_id: str, document_id: str, paragraph_id: str, problem_id: str):
            o = ProblemSerializers.Operate(
                data={'dataset_id': dataset_id, 'document_id': document_id, 'paragraph_id': paragraph_id,
                      'problem_id': problem_id})
            return result.success(o.delete(with_valid=True))
