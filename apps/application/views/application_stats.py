# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_stats.py
    @date：2025/6/9 20:30
    @desc:
"""
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.api.application_stats import ApplicationStatsAPI
from application.serializers.application_stats import ApplicationStatisticsSerializer
from common import result
from common.auth import TokenAuth
from django.utils.translation import gettext_lazy as _


class ApplicationStats(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_('Dialogue-related statistical trends'),
        summary=_('Dialogue-related statistical trends'),
        operation_id=_('Dialogue-related statistical trends'),  # type: ignore
        parameters=ApplicationStatsAPI.get_parameters(),
        responses=ApplicationStatsAPI.get_response(),
        tags=[_('Application')]  # type: ignore
    )
    def get(self, request: Request, workspace_id: str, application_id: str):
        return result.success(
            ApplicationStatisticsSerializer(data={'application_id': application_id,
                                                  'start_time': request.query_params.get(
                                                      'start_time'),
                                                  'end_time': request.query_params.get(
                                                      'end_time')
                                                  }).get_chat_record_aggregate_trend())
