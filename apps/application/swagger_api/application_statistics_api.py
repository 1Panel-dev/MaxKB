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
from django.utils.translation import gettext_lazy as _

class ApplicationStatisticsApi(ApiMixin):
    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='application_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('Application ID')),
                openapi.Parameter(name='start_time',
                                  in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('Start time')),
                openapi.Parameter(name='end_time',
                                  in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('End time')),
                ]

    class ChatRecordAggregate(ApiMixin):
        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['star_num', 'trample_num', 'tokens_num', 'chat_record_count'],
                properties={
                    'star_num': openapi.Schema(type=openapi.TYPE_NUMBER, title=_("Number of Likes"),
                                               description=_("Number of Likes")),

                    'trample_num': openapi.Schema(type=openapi.TYPE_NUMBER, title=_("Number of thumbs-downs"), description=_("Number of thumbs-downs")),
                    'tokens_num': openapi.Schema(type=openapi.TYPE_NUMBER, title=_("Number of tokens used"),
                                                 description=_("Number of tokens used")),
                    'chat_record_count': openapi.Schema(type=openapi.TYPE_NUMBER, title=_("Number of conversations"),
                                                        description=_("Number of conversations")),
                    'customer_num': openapi.Schema(type=openapi.TYPE_NUMBER, title=_("Number of customers"),
                                                   description=_("Number of customers")),
                    'customer_added_count': openapi.Schema(type=openapi.TYPE_NUMBER, title=_("Number of new customers"),
                                                           description=_("Number of new customers")),
                    'day': openapi.Schema(type=openapi.TYPE_STRING,
                                          title=_("time"),
                                          description=_("Time, this field is only available when querying trends")),
                }
            )

    class CustomerCountTrend(ApiMixin):
        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['added_count'],
                properties={
                    'added_count': openapi.Schema(type=openapi.TYPE_NUMBER, title=_("New quantity"), description=_("New quantity")),

                    'day': openapi.Schema(type=openapi.TYPE_STRING,
                                          title=_("time"),
                                          description=_("time")),
                }
            )

    class CustomerCount(ApiMixin):
        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['added_count'],
                properties={
                    'today_added_count': openapi.Schema(type=openapi.TYPE_NUMBER, title=_("Today's new quantity"),
                                                        description=_("Today's new quantity")),
                    'added_count': openapi.Schema(type=openapi.TYPE_NUMBER, title=_("New quantity"), description=_("New quantity")),

                }
            )
