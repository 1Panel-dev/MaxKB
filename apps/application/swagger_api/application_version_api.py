# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： application_version_api.py
    @date：2024/10/15 17:18
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin


class ApplicationVersionApi(ApiMixin):
    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'name', 'work_flow', 'create_time', 'update_time'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_NUMBER, title="主键id",
                                     description="主键id"),
                'name': openapi.Schema(type=openapi.TYPE_NUMBER, title="版本名称",
                                       description="版本名称"),
                'work_flow': openapi.Schema(type=openapi.TYPE_STRING, title="工作流数据", description='工作流数据'),
                'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="创建时间", description='创建时间'),
                'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="修改时间", description='修改时间')
            }
        )

    class Query(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='application_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='应用id'),
                    openapi.Parameter(name='name',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='版本名称')]

    class Operate(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='application_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='应用id'),
                    openapi.Parameter(name='work_flow_version_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='应用版本id'), ]

    class Edit(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=[],
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="版本名称",
                                           description="版本名称")
                }
            )
