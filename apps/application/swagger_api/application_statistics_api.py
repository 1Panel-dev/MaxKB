# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： application_statistics_api.py
    @date：2024/3/27 15:09
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin


class ApplicationStatisticsApi(ApiMixin):
    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='application_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='应用id'),
                openapi.Parameter(name='start_time',
                                  in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='开始时间'),
                openapi.Parameter(name='end_time',
                                  in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='结束时间'),
                ]

    class ChatRecordAggregate(ApiMixin):
        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['star_num', 'trample_num', 'tokens_num', 'chat_record_count'],
                properties={
                    'star_num': openapi.Schema(type=openapi.TYPE_NUMBER, title="点赞数量",
                                               description="点赞数量"),

                    'trample_num': openapi.Schema(type=openapi.TYPE_NUMBER, title="点踩数量", description="点踩数量"),
                    'tokens_num': openapi.Schema(type=openapi.TYPE_NUMBER, title="token使用数量",
                                                 description="token使用数量"),
                    'chat_record_count': openapi.Schema(type=openapi.TYPE_NUMBER, title="对话次数",
                                                        description="对话次数"),
                    'customer_num': openapi.Schema(type=openapi.TYPE_NUMBER, title="客户数量",
                                                   description="客户数量"),
                    'customer_added_count': openapi.Schema(type=openapi.TYPE_NUMBER, title="客户新增数量",
                                                           description="客户新增数量"),
                    'day': openapi.Schema(type=openapi.TYPE_STRING,
                                          title="日期",
                                          description="日期,只有查询趋势的时候才有该字段"),
                }
            )

    class CustomerCountTrend(ApiMixin):
        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['added_count'],
                properties={
                    'added_count': openapi.Schema(type=openapi.TYPE_NUMBER, title="新增数量", description="新增数量"),

                    'day': openapi.Schema(type=openapi.TYPE_STRING,
                                          title="时间",
                                          description="时间"),
                }
            )

    class CustomerCount(ApiMixin):
        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['added_count'],
                properties={
                    'today_added_count': openapi.Schema(type=openapi.TYPE_NUMBER, title="今日新增数量",
                                                        description="今日新增数量"),
                    'added_count': openapi.Schema(type=openapi.TYPE_NUMBER, title="新增数量", description="新增数量"),

                }
            )
