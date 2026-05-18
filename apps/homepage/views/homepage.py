# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： homepage.py
    @date：2026/5/13 16:40
    @desc:
"""
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.api.application_stats import ApplicationStatsAPI
from common import result
from common.auth import TokenAuth
from homepage.api.home_page_api import ApplicationTokensRankingAPI, ApplicationQuestionRankingAPI, UserTokensRankingAPI, \
    ApplicationAggregationAPI, KnowledgeAggregationAPI, ToolAggregationAPI, ModelAggregationAPI
from homepage.serializers.homepage import HomePageSerializer
from django.utils.translation import gettext_lazy as _


class HomePageAPI(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        description=_("Top applications by token consumption"),
        summary=_("Top applications by token consumption"),
        operation_id="homepage_application_tokens_ranking",
        parameters=ApplicationTokensRankingAPI.get_parameters(),
        responses=ApplicationTokensRankingAPI.get_response(),
        tags=[_("Home page")],
    )
    class ApplicationTokensRanking(APIView):
        authentication_classes = [TokenAuth]

        def get(self, request: Request, workspace_id: str, current_page: int, page_size: int):
            return result.success(HomePageSerializer.ApplicationTokensRanking(
                data={'user_id': request.user.id, 'workspace_id': workspace_id})
                                  .ranking(request.auth, current_page, page_size))

    @extend_schema(
        methods=["GET"],
        description=_("Top applications by question count"),
        summary=_("Top applications by question count"),
        operation_id="homepage_application_question_ranking",
        parameters=ApplicationQuestionRankingAPI.get_parameters(),
        responses=ApplicationQuestionRankingAPI.get_response(),
        tags=[_("Home page")],
    )
    class ApplicationQuestionRanking(APIView):
        authentication_classes = [TokenAuth]

        def get(self, request: Request, workspace_id: str, current_page: int, page_size: int):
            return result.success(HomePageSerializer.ApplicationQuestionRanking(
                data={'user_id': request.user.id, 'workspace_id': workspace_id})
                                  .ranking(request.auth, current_page, page_size))

    class UserTokensRanking(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Top users by token consumption"),
            summary=_("Top users by token consumption"),
            operation_id="homepage_user_tokens_ranking",
            parameters=UserTokensRankingAPI.get_parameters(),
            responses=UserTokensRankingAPI.get_response(),
            tags=[_("Home page")],
        )
        def get(self, request: Request, workspace_id: str, current_page: int, page_size: int):
            return result.success(HomePageSerializer.ApplicationUserTokenRanking(
                data={'user_id': request.user.id, 'workspace_id': workspace_id})
                                  .ranking(request.auth, current_page, page_size))

    class ApplicationMonitoring(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Dialogue-related statistical trends'),
            summary=_('Dialogue-related statistical trends'),
            operation_id='Dialogue-related statistical trends',  # type: ignore
            parameters=ApplicationStatsAPI.get_parameters(),
            responses=ApplicationStatsAPI.get_response(),
            tags=[_('Home page')]  # type: ignore
        )
        def get(self, request: Request, workspace_id: str):
            return result.success(
                HomePageSerializer.ApplicationMonitoring(
                    data={'application_id': request.query_params.get("application_id"),
                          "user_id": request.user.id,
                          'workspace_id': workspace_id,
                          'start_time': request.query_params.get(
                              'start_time'),
                          'end_time': request.query_params.get(
                              'end_time')
                          }).get_chat_record_aggregate_trend(request.auth))

    class ApplicationAggregation(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Application data aggregation"),
            summary=_("Application data aggregation"),
            operation_id="homepage_application_aggregation",
            parameters=ApplicationAggregationAPI.get_parameters(),
            responses=ApplicationAggregationAPI.get_response(),
            tags=[_("Home page")],
        )
        def get(self, request: Request, workspace_id: str):
            return result.success(
                HomePageSerializer.Application(
                    data={'workspace_id': workspace_id, 'user_id': request.user.id}).aggregation(
                    request.auth))

    class KnowledgeAggregation(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Knowledge data aggregation"),
            summary=_("Knowledge data aggregation"),
            operation_id="homepage_knowledge_aggregation",
            parameters=KnowledgeAggregationAPI.get_parameters(),
            responses=KnowledgeAggregationAPI.get_response(),
            tags=[_("Home page")],
        )
        def get(self, request: Request, workspace_id: str):
            return result.success(
                HomePageSerializer.Knowledge(
                    data={'workspace_id': workspace_id, 'user_id': request.user.id}).aggregation(
                    request.auth))

    class ToolAggregation(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Tool data aggregation"),
            summary=_("Tool data aggregation"),
            operation_id="homepage_tool_aggregation",
            parameters=ToolAggregationAPI.get_parameters(),
            responses=ToolAggregationAPI.get_response(),
            tags=[_("Home page")],
        )
        def get(self, request: Request, workspace_id: str):
            return result.success(
                HomePageSerializer.Tool(
                    data={'workspace_id': workspace_id, 'user_id': request.user.id}).aggregation(
                    request.auth))

    class ModelAggregation(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Model data aggregation"),
            summary=_("Model data aggregation"),
            operation_id="homepage_model_aggregation",
            parameters=ModelAggregationAPI.get_parameters(),
            responses=ModelAggregationAPI.get_response(),
            tags=[_("Home page")],
        )
        def get(self, request: Request, workspace_id: str):
            return result.success(
                HomePageSerializer.Model(
                    data={'workspace_id': workspace_id, 'user_id': request.user.id}).aggregation(
                    request.auth))
