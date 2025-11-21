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

from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants, ViewPermission, CompareConstants


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
    @has_permissions(PermissionConstants.APPLICATION_OVERVIEW_READ.get_workspace_application_permission(),
                     PermissionConstants.APPLICATION_OVERVIEW_READ.get_workspace_permission_workspace_manage_role(),
                     ViewPermission([RoleConstants.USER.get_workspace_role()],
                                    [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                    CompareConstants.AND),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def get(self, request: Request, workspace_id: str, application_id: str):
        return result.success(
            ApplicationStatisticsSerializer(data={'application_id': application_id, 'workspace_id': workspace_id,
                                                  'start_time': request.query_params.get(
                                                      'start_time'),
                                                  'end_time': request.query_params.get(
                                                      'end_time')
                                                  }).get_chat_record_aggregate_trend())

    class TokenUsageStatistics(APIView):
        authentication_classes = [TokenAuth]

        # 应用的token使用统计 根据人的使用数排序
        @extend_schema(
            methods=['GET'],
            description=_('Application token usage statistics'),
            summary=_('Application token usage statistics'),
            operation_id=_('Application token usage statistics'),  # type: ignore
            parameters=ApplicationStatsAPI.get_parameters(),
            responses=ApplicationStatsAPI.get_response(),
            tags=[_('Application')]  # type: ignore
        )
        @has_permissions(PermissionConstants.APPLICATION_OVERVIEW_READ.get_workspace_application_permission(),
                         PermissionConstants.APPLICATION_OVERVIEW_READ.get_workspace_permission_workspace_manage_role(),
                         ViewPermission([RoleConstants.USER.get_workspace_role()],
                                        [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                        CompareConstants.AND),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        def get(self, request: Request, workspace_id: str, application_id: str):
            return result.success(
                ApplicationStatisticsSerializer(data={'application_id': application_id, 'workspace_id': workspace_id,
                                                      'start_time': request.query_params.get(
                                                          'start_time'),
                                                      'end_time': request.query_params.get(
                                                          'end_time')
                                                      }).get_token_usage_statistics())

    class TopQuestionsStatistics(APIView):
        authentication_classes = [TokenAuth]
        # 应用的top问题统计
        @extend_schema(
            methods=['GET'],
            description=_('Application top question statistics'),
            summary=_('Application top question statistics'),
            operation_id=_('Application top question statistics'),  # type: ignore
            parameters=ApplicationStatsAPI.get_parameters(),
            responses=ApplicationStatsAPI.get_response(),
            tags=[_('Application')]  # type: ignore
        )
        @has_permissions(PermissionConstants.APPLICATION_OVERVIEW_READ.get_workspace_application_permission(),
                         PermissionConstants.APPLICATION_OVERVIEW_READ.get_workspace_permission_workspace_manage_role(),
                         ViewPermission([RoleConstants.USER.get_workspace_role()],
                                        [PermissionConstants.APPLICATION.get_workspace_application_permission()],
                                        CompareConstants.AND),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
        def get(self, request: Request, workspace_id: str, application_id: str):
            return result.success(
                ApplicationStatisticsSerializer(data={'application_id': application_id, 'workspace_id': workspace_id,
                                                      'start_time': request.query_params.get(
                                                          'start_time'),
                                                      'end_time': request.query_params.get(
                                                          'end_time')
                                                      }).get_top_questions_statistics())
